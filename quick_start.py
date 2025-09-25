#!/usr/bin/env python3
"""
Quick start script - launches the dashboard with minimal setup.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_frontend():
    """Check if frontend files exist."""
    frontend_dir = Path("frontend")
    index_file = frontend_dir / "index.html"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory missing!")
        return False
    
    if not index_file.exists():
        print("❌ index.html missing!")
        return False
    
    print("✅ Frontend files found")
    return True

def run_data_pipeline():
    """Run the data pipeline quickly."""
    print("📊 Running quick data setup...")
    
    try:
        # Run the local data script
        result = subprocess.run([sys.executable, 'run_local.py'], 
                              capture_output=True, text=True, timeout=60)
        
        if "225 records" in result.stdout or "Ingested" in result.stdout:
            print("✅ Market data ready!")
            return True
        else:
            print("⚠️ Data setup completed with warnings")
            return True
            
    except subprocess.TimeoutExpired:
        print("⚠️ Data setup taking too long, continuing...")
        return True
    except Exception as e:
        print(f"⚠️ Data setup issue: {e}")
        return True

def start_dashboard():
    """Start the dashboard server."""
    print("🌐 Starting dashboard server...")
    
    try:
        # Try the simple server first
        subprocess.run([sys.executable, 'simple_server.py'])
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        
        # Fallback: try Python's built-in server
        print("🔄 Trying fallback server...")
        try:
            os.chdir("frontend")
            subprocess.run([sys.executable, '-m', 'http.server', '8080'])
        except Exception as e2:
            print(f"❌ Fallback server also failed: {e2}")

def main():
    """Main function."""
    print("🚀 Quick Start - AI Insider Trading Detector")
    print("=" * 60)
    
    # Check frontend
    if not check_frontend():
        print("❌ Frontend setup incomplete")
        return
    
    # Quick data setup
    run_data_pipeline()
    
    # Start dashboard
    print("\n🌐 Launching dashboard...")
    print("📱 The dashboard will open in your browser automatically")
    print("🎯 If it doesn't open, go to: http://localhost:8080")
    print("\n🔄 Press Ctrl+C to stop the server")
    
    start_dashboard()

if __name__ == "__main__":
    main()