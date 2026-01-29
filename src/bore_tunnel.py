"""
Bore tunnel manager
"""

import subprocess
import time
import re
import signal
from typing import Optional


class BoreTunnel:
    """Manages bore tunnel connection"""
    
    def __init__(self, local_port: int, server: str, remote_port: int = 0, secret: str = ""):
        self.local_port = local_port
        self.server = server
        self.remote_port = remote_port
        self.secret = secret
        self.process: Optional[subprocess.Popen] = None
        self.public_port: Optional[int] = None
    
    def start(self) -> int:
        """
        Start the bore tunnel and return the public port number
        
        Returns:
            int: The public port number assigned by bore server
        """
        cmd = [
            'bore',
            'local',
            str(self.local_port),
            '--to', self.server
        ]
        
        # Add optional port
        if self.remote_port > 0:
            cmd.extend(['--port', str(self.remote_port)])
        
        # Add optional secret
        if self.secret:
            cmd.extend(['--secret', self.secret])
        
        # Start bore process
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Wait for tunnel to establish and capture port number
        timeout = 30
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.process.poll() is not None:
                # Process exited
                output = self.process.stdout.read()
                raise RuntimeError(f"Bore process exited unexpectedly: {output}")
            
            line = self.process.stdout.readline()
            if not line:
                time.sleep(0.1)
                continue
            
            print(f"[bore] {line.strip()}")
            
            # Look for port assignment in output
            # Example output: "listening at bore.pub:12345"
            match = re.search(r'listening at [^:]+:(\d+)', line)
            if match:
                self.public_port = int(match.group(1))
                print(f"[bore] Tunnel established on port {self.public_port}")
                return self.public_port
            
            # Alternative format: "forwarding to bore.pub:12345"
            match = re.search(r'(?:forwarding to|exposed at) [^:]+:(\d+)', line)
            if match:
                self.public_port = int(match.group(1))
                print(f"[bore] Tunnel established on port {self.public_port}")
                return self.public_port
        
        self.stop()
        raise TimeoutError("Failed to establish bore tunnel within timeout period")
    
    def stop(self):
        """Stop the bore tunnel"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except:
                pass
            finally:
                self.process = None
    
    def is_running(self) -> bool:
        """Check if tunnel is still running"""
        return self.process is not None and self.process.poll() is None
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
