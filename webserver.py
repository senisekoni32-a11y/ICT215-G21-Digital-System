# Simple web server for dashboard

import socket
import json
import time

class WebServer:
    def __init__(self, port=80):
        self.port = port
        self.sock = None
        self.stats = {
            'fill_percentage': 0,
            'lid_openings': 0,
            'last_emptied': 'Never',
            'status': 'OK'
        }
    
    def start(self):
        """Start the web server"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('', self.port))
            self.sock.listen(1)
            self.sock.setblocking(False)
            print(f"Web server started on port {self.port}")
            return True
        except Exception as e:
            print(f"Failed to start web server: {e}")
            return False
    
    def stop(self):
        """Stop the web server"""
        try:
            if self.sock:
                self.sock.close()
                print("Web server stopped")
        except Exception as e:
            print(f"Error stopping server: {e}")
    
    def update_stats(self, fill_percentage, lid_openings, status):
        """Update statistics"""
        self.stats['fill_percentage'] = round(fill_percentage, 1)
        self.stats['lid_openings'] = lid_openings
        self.stats['status'] = status
    
    def mark_emptied(self):
        """Mark bin as emptied"""
        t = time.localtime()
        self.stats['last_emptied'] = f"{t[3]:02d}:{t[4]:02d}:{t[5]:02d}"
        self.stats['fill_percentage'] = 0
        print("Bin marked as emptied")
    
    def handle_request(self):
        """Handle incoming HTTP requests (non-blocking)"""
        try:
            conn, addr = self.sock.accept()
            conn.settimeout(1.0)
            
            try:
                request = conn.recv(1024).decode()
                
                if 'GET / ' in request or 'GET /index' in request:
                    response = self._serve_html_file()
                elif 'GET /api/stats' in request:
                    response = self._generate_json()
                elif 'POST /api/empty' in request:
                    self.mark_emptied()
                    response = self._generate_json()
                else:
                    response = self._generate_404()
                
                conn.send(response.encode())
            finally:
                conn.close()
                
        except OSError:
            pass
        except Exception as e:
            print(f"Server error: {e}")
    
    def _serve_html_file(self):
        """Serve the HTML file from disk"""
        try:
            with open('dashboard.html', 'r') as f:
                html_content = f.read()
            
            response = f"HTTP/1.1 200 OK\r\n"
            response += f"Content-Type: text/html\r\n"
            response += f"Content-Length: {len(html_content)}\r\n"
            response += f"\r\n"
            response += html_content
            return response
            
        except OSError:
            return self._generate_404("dashboard.html not found")
    
    def _generate_json(self):
        """Generate JSON API response"""
        json_data = json.dumps(self.stats)
        response = f"HTTP/1.1 200 OK\r\n"
        response += f"Content-Type: application/json\r\n"
        response += f"Content-Length: {len(json_data)}\r\n"
        response += f"\r\n"
        response += json_data
        return response
    
    def _generate_404(self, message="Page not found"):
        """Generate 404 response"""
        response = f"HTTP/1.1 404 Not Found\r\n"
        response += f"Content-Type: text/plain\r\n"
        response += f"Content-Length: {len(message)}\r\n"
        response += f"\r\n"
        response += message
        return response
