#!/usr/bin/env python3
"""Simple static file server for the frontend during development."""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 3000
FRONTEND_DIR = Path(__file__).parent / "public"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def end_headers(self):
        """Add headers to prevent caching."""
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        """Handle GET requests with proper routing."""
        if self.path == "/" or self.path == "/index.html":
            self.path = "/index.html"
        elif self.path == "/training.html" or self.path == "/training":
            self.path = "/training.html"
        
        return super().do_GET()
    
    def log_message(self, format, *args):
        """Log HTTP requests."""
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == "__main__":
    os.chdir(FRONTEND_DIR)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"✓ Frontend server running on http://localhost:{PORT}")
        print(f"  Serving files from: {FRONTEND_DIR}")
        print(f"  Backend API: http://127.0.0.1:8001")
        print("\nPress Ctrl+C to stop...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✓ Server stopped.")
