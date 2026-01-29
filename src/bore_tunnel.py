"""
Bore tunnel manager
"""

import subprocess
import time
import re
import signal
import threading
from typing import Optional
from queue import Queue, Empty


class BoreTunnel:
    """Manages bore tunnel connection"""
    
    def __init__(self, local_port: int, server: str, remote_port: int = 0, secret: str = ""):
        self.local_port = local_port
        self.server = server
        self.remote_port = remote_port
        self.secret = secret
        self.process: Optional[subprocess.Popen] = None
        self.public_port: Optional[int] = None
    
    def _read_stream(self, stream, queue, name):
        """Read from stream in a separate thread"""
        try:
            for line in iter(stream.readline, ''):
                if line:
                    queue.put((name, line.strip()))
        except:
            pass
        finally:
            stream.close()
    
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
        
        print(f"[bore] Starting tunnel with command: {' '.join(cmd)}")
        
        # Start bore process
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Create queue for reading output
        output_queue = Queue()
        
        # Start threads to read stdout and stderr
        stdout_thread = threading.Thread(
            target=self._read_stream,
            args=(self.process.stdout, output_queue, 'stdout'),
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=self._read_stream,
            args=(self.process.stderr, output_queue, 'stderr'),
            daemon=True
        )
        
        stdout_thread.start()
        stderr_thread.start()
        
        # Wait for tunnel to establish and capture port number
        timeout = 30
        start_time = time.time()
        all_output = []
        
        while time.time() - start_time < timeout:
            # Check if process has exited
            if self.process.poll() is not None:
                # Process exited - collect remaining output
                while not output_queue.empty():
                    try:
                        stream_name, line = output_queue.get_nowait()
                        all_output.append(f"[{stream_name}] {line}")
                    except Empty:
                        break
                
                all_output_str = '\n'.join(all_output)
                raise RuntimeError(
                    f"Bore process exited unexpectedly with code {self.process.returncode}:\n{all_output_str}"
                )
            
            # Try to get output from queue
            try:
                stream_name, line = output_queue.get(timeout=0.1)
                all_output.append(f"[{stream_name}] {line}")
                print(f"[bore:{stream_name}] {line}")
                
                # Look for port assignment in various formats
                
                # Format 1: "listening at bore.pub:12345"
                match = re.search(r'listening at ([^:]+):(\d+)', line, re.IGNORECASE)
                if match:
                    self.public_port = int(match.group(2))
                    print(f"[bore] ✓ Tunnel established at {match.group(1)}:{self.public_port}")
                    return self.public_port
                
                # Format 2: "forwarding to bore.pub:12345" or "forwarding at..."
                match = re.search(r'forwarding (?:to|at) ([^:]+):(\d+)', line, re.IGNORECASE)
                if match:
                    self.public_port = int(match.group(2))
                    print(f"[bore] ✓ Tunnel established at {match.group(1)}:{self.public_port}")
                    return self.public_port
                
                # Format 3: "bore.pub:12345" or similar (host:port pattern)
                match = re.search(r'([a-zA-Z0-9.-]+):(\d{4,5})', line)
                if match and match.group(1) == self.server:
                    self.public_port = int(match.group(2))
                    print(f"[bore] ✓ Tunnel established at {match.group(1)}:{self.public_port}")
                    return self.public_port
                
                # Format 4: Just port number mentioned
                match = re.search(r'(?:port|on)\s+(\d{4,5})', line, re.IGNORECASE)
                if match:
                    self.public_port = int(match.group(1))
                    print(f"[bore] ✓ Tunnel established on port {self.public_port}")
                    return self.public_port
                
                # Format 5: Check for error messages
                if 'error' in line.lower() or 'failed' in line.lower():
                    print(f"[bore] ⚠ Error detected: {line}")
                
            except Empty:
                # No output yet, continue waiting
                continue
        
        # Timeout reached
        self.stop()
        all_output_str = '\n'.join(all_output)
        raise TimeoutError(
            f"Failed to establish bore tunnel within {timeout} seconds.\n"
            f"Command: {' '.join(cmd)}\n"
            f"Output:\n{all_output_str if all_output_str else '(no output captured)'}"
        )
    
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
