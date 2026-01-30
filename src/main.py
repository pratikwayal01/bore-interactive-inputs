#!/usr/bin/env python3
"""
Main entry point for Bore Interactive Inputs GitHub Action
"""

import os
import sys
import time
import signal
import json
import subprocess
import threading
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure output is flushed immediately
sys.stdout.reconfigure(line_buffering=True)

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from server import InteractiveInputsServer
from notifiers import SlackNotifier, DiscordNotifier
from bore_tunnel import BoreTunnel
from config import Config


class InteractiveInputsAction:
    """Main action orchestrator"""
    
    def __init__(self):
        self.config = Config.from_env()
        self.server = None
        self.tunnel = None
        self.notifiers = []
        self.tunnel_url = None
        
    def setup_notifiers(self):
        """Setup notification services"""
        if self.config.notifier_slack_enabled:
            slack = SlackNotifier(
                token=self.config.notifier_slack_token,
                channel=self.config.notifier_slack_channel,
                thread_ts=self.config.notifier_slack_thread_ts,
                bot_name=self.config.notifier_slack_bot
            )
            self.notifiers.append(slack)
            
        if self.config.notifier_discord_enabled:
            discord = DiscordNotifier(
                webhook_url=self.config.notifier_discord_webhook,
                thread_id=self.config.notifier_discord_thread_id,
                username=self.config.notifier_discord_username
            )
            self.notifiers.append(discord)
    
    def send_notification(self, status: str, message: str, url: Optional[str] = None):
        """Send notification to all configured notifiers"""
        for notifier in self.notifiers:
            try:
                notifier.send(
                    status=status,
                    message=message,
                    url=url,
                    workflow=self.config.github_workflow,
                    repository=self.config.github_repository,
                    run_id=self.config.github_run_id
                )
            except Exception as e:
                print(f"Failed to send notification via {notifier.__class__.__name__}: {e}")
    
    def start_tunnel(self, local_port: int) -> str:
        """Start bore tunnel and return public URL"""
        print(f"\n{'='*60}")
        print(f"Starting bore tunnel configuration:")
        print(f"  Local port: {local_port}")
        print(f"  Bore server: {self.config.bore_server}")
        print(f"  Remote port: {self.config.bore_port} (0 = random)")
        print(f"  Secret: {'***' if self.config.bore_secret else '(none)'}")
        print(f"{'='*60}\n")
        
        # Verify bore is installed
        try:
            import subprocess
            result = subprocess.run(['bore', '--version'], capture_output=True, text=True, timeout=5)
            print(f"[bore] Version check: {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError("bore command not found! Make sure bore is installed.")
        except Exception as e:
            print(f"[bore] Warning: Could not check bore version: {e}")
        
        self.tunnel = BoreTunnel(
            local_port=local_port,
            server=self.config.bore_server,
            remote_port=self.config.bore_port,
            secret=self.config.bore_secret
        )
        
        print(f"[bore] Starting tunnel...")
        public_port = self.tunnel.start()
        tunnel_url = f"http://{self.config.bore_server}:{public_port}"
        
        print(f"\n{'='*60}")
        print(f"✓ TUNNEL ESTABLISHED!")
        print(f"  Public URL: {tunnel_url}")
        print(f"{'='*60}\n")
        return tunnel_url
    
    def run(self):
        """Run the interactive inputs action"""
        try:
            # Create server instance
            self.server = InteractiveInputsServer(
                title=self.config.title,
                fields=self.config.interactive_fields,
                timeout=self.config.timeout
            )
            
            # Setup notifiers
            self.setup_notifiers()
            
            # Start the Flask server in background
            local_port = 5000
            print(f"\n{'='*60}")
            print(f"Starting Flask server on port {local_port}...")
            print(f"{'='*60}\n")
            sys.stdout.flush()
            
            server_thread = threading.Thread(
                target=self.server.run,
                kwargs={'port': local_port, 'debug': False},
                daemon=True
            )
            server_thread.start()
            
            # Wait for server to start and verify it's running
            print("[server] Waiting for Flask to be ready...")
            sys.stdout.flush()
            max_wait = 10
            for i in range(max_wait):
                time.sleep(1)
                # Check if the thread is alive
                if server_thread.is_alive():
                    # Try to connect to the server
                    try:
                        import urllib.request
                        urllib.request.urlopen(f'http://127.0.0.1:{local_port}/', timeout=1)
                        print(f"[server] ✓ Flask server is ready and responding")
                        sys.stdout.flush()
                        break
                    except:
                        if i < max_wait - 1:
                            print(f"[server] Waiting... ({i+1}/{max_wait})")
                            sys.stdout.flush()
                        continue
            else:
                # Extra sleep to be safe
                time.sleep(2)
            
            print(f"\n{'='*60}")
            print(f"Flask server started successfully")
            print(f"Now establishing bore tunnel to {self.config.bore_server}...")
            print(f"{'='*60}\n")
            sys.stdout.flush()
            
            # Start bore tunnel
            self.tunnel_url = self.start_tunnel(local_port)
            
            # Send initial notification
            workflow_url = f"{self.config.github_server_url}/{self.config.github_repository}/actions/runs/{self.config.github_run_id}"
            self.send_notification(
                status="waiting",
                message=f"Waiting for user input (timeout: {self.config.timeout}s)",
                url=self.tunnel_url
            )
            
            print(f"\n{'='*60}")
            print(f"Interactive Input Portal is ready!")
            print(f"{'='*60}")
            print(f"\n🌐 PUBLIC URL: {self.tunnel_url}")
            print(f"\n📋 Instructions:")
            print(f"   1. Open the URL above in your browser")
            print(f"   2. Fill out the form")
            print(f"   3. Submit to continue the workflow")
            print(f"\n⏱️  Timeout: {self.config.timeout} seconds")
            print(f"{'='*60}\n")
            
            # Wait for completion or timeout
            start_time = time.time()
            while time.time() - start_time < self.config.timeout:
                if self.server.is_completed():
                    break
                time.sleep(1)
            
            if self.server.is_completed():
                # Success - get results
                results = self.server.get_results()
                
                print(f"\n{'='*60}")
                print("Received results from form:")
                print(f"{'='*60}")
                for key, value in results.items():
                    print(f"  {key}: {value}")
                print(f"{'='*60}\n")
                sys.stdout.flush()
                
                # Set GitHub Action outputs
                self.set_outputs(results)
                
                self.send_notification(
                    status="success",
                    message="Interactive inputs completed successfully",
                    url=workflow_url
                )
                
                print(f"\n{'='*60}")
                print("✓ Interactive inputs completed successfully!")
                print(f"{'='*60}\n")
                
            else:
                # Timeout
                self.send_notification(
                    status="timeout",
                    message=f"Interactive inputs timed out after {self.config.timeout}s",
                    url=workflow_url
                )
                
                print(f"\n{'='*60}")
                print(f"✗ Timeout: No response received within {self.config.timeout} seconds")
                print(f"{'='*60}\n")
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.cleanup()
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            
            self.send_notification(
                status="error",
                message=f"Error: {str(e)}",
                url=None
            )
            
            self.cleanup()
            sys.exit(1)
        finally:
            self.cleanup()
    
    def set_outputs(self, results: Dict[str, Any]):
        """Set GitHub Action outputs"""
        github_output = os.getenv('GITHUB_OUTPUT')
        if not github_output:
            print("Warning: GITHUB_OUTPUT not set")
            return
        
        print(f"\n[outputs] Writing to: {github_output}")
        sys.stdout.flush()
        
        with open(github_output, 'a') as f:
            for key, value in results.items():
                # Handle different value types
                if isinstance(value, (list, dict)):
                    value_str = json.dumps(value)
                elif isinstance(value, bool):
                    value_str = str(value).lower()
                elif value is None or value == '':
                    value_str = ''
                else:
                    value_str = str(value)
                
                # Write output in multiline format if needed
                if '\n' in value_str:
                    delimiter = 'EOF'
                    f.write(f"{key}<<{delimiter}\n{value_str}\n{delimiter}\n")
                else:
                    f.write(f"{key}={value_str}\n")
                
                print(f"[outputs] Set output: {key} = {value_str[:100]}{'...' if len(value_str) > 100 else ''}")
                sys.stdout.flush()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.tunnel:
            try:
                self.tunnel.stop()
            except:
                pass


def main():
    """Main entry point"""
    action = InteractiveInputsAction()
    action.run()


if __name__ == '__main__':
    main()
