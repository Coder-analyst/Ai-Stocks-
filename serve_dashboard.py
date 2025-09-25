#!/usr/bin/env python3
"""
Simple web server to serve the dashboard and API endpoints.
"""

import http.server
import socketserver
import webbrowser
import threading
import time
from pathlib import Path
import json
import pandas as pd
from urllib.parse import urlparse, parse_qs


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for the dashboard with API endpoints."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="frontend", **kwargs)
    
    def end_headers(self):
        """Add CORS headers to all responses."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/status':
            self.send_api_response(self.get_system_status())
        elif parsed_path.path == '/api/tickers':
            self.send_api_response(self.get_ticker_data())
        elif parsed_path.path == '/api/anomalies':
            self.send_api_response(self.get_anomalies())
        else:
            # Serve static files
            super().do_GET()
    
    def send_api_response(self, data):
        """Send JSON API response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_system_status(self):
        """Get system status."""
        data_dir = Path("data")
        tick_files = list((data_dir / "ticks").glob("*.csv")) if (data_dir / "ticks").exists() else []
        
        total_records = 0
        for file in tick_files:
            try:
                df = pd.read_csv(file)
                total_records += len(df)
            except:
                pass
        
        return {
            "status": "online",
            "total_tickers": len(tick_files),
            "total_records": total_records,
            "total_anomalies": 0,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_ticker_data(self):
        """Get ticker data from CSV files."""
        data_dir = Path("data/ticks")
        tickers = {}
        
        if data_dir.exists():
            for file in data_dir.glob("*.csv"):
                try:
                    df = pd.read_csv(file)
                    if not df.empty:
                        ticker = file.stem
                        latest = df.iloc[-1]
                        previous = df.iloc[-2] if len(df) > 1 else latest
                        
                        price = float(latest['Close'])
                        prev_price = float(previous['Close'])
                        change = price - prev_price
                        
                        tickers[ticker] = {
                            "price": round(price, 2),
                            "change": round(change, 2),
                            "change_percent": round((change / prev_price) * 100, 2),
                            "volume": int(latest['Volume']),
                            "last_updated": latest['Datetime']
                        }
                except Exception as e:
                    print(f"Error reading {file}: {e}")
        
        return tickers
    
    def get_anomalies(self):
        """Get anomalies data."""
        anomalies_file = Path("data/anomalies/anomalies.json")
        
        # First try to load real anomalies from file
        real_anomalies = []
        if anomalies_file.exists():
            try:
                with open(anomalies_file, 'r') as f:
                    real_anomalies = json.load(f)
            except:
                pass
        
        # If no real anomalies, return sample anomalies for demo
        if not real_anomalies:
            return [
                {
                    "id": 1,
                    "ticker": "RELIANCE.NS",
                    "timestamp": "2025-09-24T14:30:00Z",
                    "score": 0.95,
                    "severity": "high",
                    "model": "IsolationForest + Autoencoder",
                    "explanation": "Massive volume spike (4.2σ above normal) detected 15 minutes before market close, combined with unusual price momentum. Pattern similar to historical insider trading cases.",
                    "reason": {
                        "volume_spike": 4.2,
                        "price_momentum": 2.8,
                        "unusual_timing": True
                    }
                },
                {
                    "id": 2,
                    "ticker": "TCS.NS",
                    "timestamp": "2025-09-24T11:45:00Z",
                    "score": 0.87,
                    "severity": "high",
                    "model": "Statistical Analysis",
                    "explanation": "Synchronized trading pattern detected across TCS and related IT stocks. Unusual correlation suggests coordinated activity.",
                    "reason": {
                        "cross_correlation": 2.9,
                        "volume_pattern": 3.4,
                        "price_synchronization": True
                    }
                },
                {
                    "id": 3,
                    "ticker": "HDFCBANK.NS",
                    "timestamp": "2025-09-24T09:20:00Z",
                    "score": 0.73,
                    "severity": "medium",
                    "model": "Time Series Analysis",
                    "explanation": "Unusual pre-market trading activity with concentrated volume from limited sources. Timing suggests potential information advantage.",
                    "reason": {
                        "pre_market_activity": 2.1,
                        "volume_concentration": 1.8,
                        "timing_anomaly": True
                    }
                }
            ]
        
        return real_anomalies


def start_server(port=8080):
    """Start the web server."""
    try:
        # Try to bind to the port first
        with socketserver.TCPServer(("localhost", port), DashboardHandler) as httpd:
            httpd.allow_reuse_address = True
            print(f"🌐 Dashboard server running at http://localhost:{port}")
            print(f"📊 Open your browser to view the dashboard")
            print(f"🔄 Press Ctrl+C to stop the server")
            
            # Auto-open browser after a short delay
            def open_browser():
                time.sleep(3)
                try:
                    webbrowser.open(f"http://localhost:{port}")
                    print(f"✅ Browser opened automatically")
                except Exception as e:
                    print(f"⚠️ Could not open browser: {e}")
                    print(f"🌐 Please manually open: http://localhost:{port}")
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if "Address already in use" in str(e) or "WinError 10048" in str(e):
            print(f"❌ Port {port} is already in use. Trying port {port + 1}...")
            start_server(port + 1)
        else:
            print(f"❌ Error starting server: {e}")
            print(f"💡 Try running on a different port: python serve_dashboard.py {port + 1}")


if __name__ == "__main__":
    print("🚀 AI-Powered Insider Trading Detector - Dashboard Server")
    print("=" * 60)
    start_server(8082)