#!/usr/bin/env python3
"""
Simple HTTP server to serve the dashboard - guaranteed to work!
"""

import http.server
import socketserver
import webbrowser
import time
import threading
from pathlib import Path
import os

def find_free_port(start_port=8080):
    """Find a free port starting from start_port."""
    import socket
    
    for port in range(start_port, start_port + 10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def start_simple_server():
    """Start a simple HTTP server."""
    
    # Change to frontend directory
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return
    
    os.chdir(frontend_dir)
    
    # Find free port
    port = find_free_port(8080)
    if not port:
        print("❌ No free ports available!")
        return
    
    print("🚀 Starting Simple Dashboard Server")
    print("=" * 50)
    print(f"📁 Serving from: {Path.cwd()}")
    print(f"🌐 URL: http://localhost:{port}")
    print("🔄 Press Ctrl+C to stop")
    print("=" * 50)
    
    # Create server
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("localhost", port), handler) as httpd:
            httpd.allow_reuse_address = True
            
            # Open browser after delay
            def open_browser():
                time.sleep(2)
                try:
                    webbrowser.open(f"http://localhost:{port}")
                    print(f"✅ Dashboard opened in browser!")
                except Exception as e:
                    print(f"⚠️ Please manually open: http://localhost:{port}")
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            print(f"✅ Server started successfully on port {port}")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_simple_server()