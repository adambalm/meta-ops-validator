#!/usr/bin/env python3
"""
MetaOps Validator Web Server
Serves both Streamlit GUI and presentation dashboard
"""
import http.server
import socketserver
import threading
import subprocess
import os
import sys
import time
from pathlib import Path

PORT_MAIN = 8080
PORT_STREAMLIT = 8090
PRESENTATION_PORT = 8082

class PresentationHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="presentation/demo-app/src", **kwargs)

def start_streamlit():
    """Start Streamlit in background"""
    env = os.environ.copy()
    env['PYTHONPATH'] = '/home/ed/meta-ops-validator/src'
    
    # Activate virtual environment and start Streamlit
    cmd = [
        "bash", "-c",
        f"source .venv/bin/activate && streamlit run streamlit_business_demo.py --server.port {PORT_STREAMLIT} --server.address 0.0.0.0 --server.headless true"
    ]
    
    return subprocess.Popen(cmd, env=env, cwd="/home/ed/meta-ops-validator")

def start_presentation_server():
    """Start presentation server"""
    os.chdir("/home/ed/meta-ops-validator")
    with socketserver.TCPServer(("0.0.0.0", PRESENTATION_PORT), PresentationHandler) as httpd:
        print(f"Presentation dashboard at http://0.0.0.0:{PRESENTATION_PORT}/demo.html")
        httpd.serve_forever()

def main():
    print("Starting MetaOps Validator Web Services...")
    print("=" * 50)
    
    # Ensure we're in the right directory
    os.chdir("/home/ed/meta-ops-validator")
    
    # Start Streamlit
    print(f"Starting Streamlit GUI on port {PORT_STREAMLIT}...")
    streamlit_proc = start_streamlit()
    
    # Give Streamlit time to start
    time.sleep(3)
    
    # Start presentation server in thread
    print(f"Starting Presentation server on port {PRESENTATION_PORT}...")
    presentation_thread = threading.Thread(target=start_presentation_server, daemon=True)
    presentation_thread.start()
    
    print("\n" + "=" * 50)
    print("🚀 MetaOps Validator Services Running:")
    print(f"📊 Business Demo GUI:  http://100.111.114.84:{PORT_STREAMLIT}")
    print(f"📋 Dashboard:          http://100.111.114.84:{PRESENTATION_PORT}/demo.html")
    print(f"📄 Executive Report:   http://100.111.114.84:{PRESENTATION_PORT}/../reports/executive_summary.html")
    print(f"🎨 CSS Styles:         http://100.111.114.84:{PRESENTATION_PORT}/tufte-overrides.css")
    print("\n📁 Sample files available in: data/samples/onix_samples/")
    print("⏹️  Press Ctrl+C to stop all services")
    print("=" * 50)
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        if streamlit_proc:
            streamlit_proc.terminate()
        print("All services stopped.")

if __name__ == "__main__":
    main()