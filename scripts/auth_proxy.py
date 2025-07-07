#!/usr/bin/env python3
"""
Simple authentication proxy for handling Windows Integrated Auth in GitHub Actions
"""

import os
import requests
from requests_ntlm import HttpNtlmAuth
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading
import time

class AuthProxyHandler(BaseHTTPRequestHandler):
    """HTTP proxy that handles NTLM authentication"""
    
    def do_GET(self):
        # Get the target URL from the request
        target_url = self.path.lstrip('/')
        if not target_url.startswith('http'):
            target_url = 'https://' + target_url
            
        print(f"Proxying request to: {target_url}")
        
        try:
            # Get credentials from environment
            username = os.getenv('METRO_EMAIL')
            password = os.getenv('METRO_PASSWORD')
            
            # Make authenticated request
            session = requests.Session()
            session.auth = HttpNtlmAuth(username, password)
            
            # Add headers to look more like a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = session.get(target_url, headers=headers, timeout=30)
            
            # Forward the response
            self.send_response(response.status_code)
            
            # Forward headers
            for header, value in response.headers.items():
                if header.lower() not in ['transfer-encoding', 'connection']:
                    self.send_header(header, value)
            
            self.end_headers()
            
            # Send content
            self.wfile.write(response.content)
            
        except Exception as e:
            print(f"Proxy error: {e}")
            self.send_error(500, f"Proxy error: {e}")
    
    def do_POST(self):
        # Handle POST requests similarly
        self.do_GET()
    
    def log_message(self, format, *args):
        # Suppress logging for cleaner output
        pass

def start_auth_proxy(port=8080):
    """Start the authentication proxy server"""
    server = HTTPServer(('localhost', port), AuthProxyHandler)
    print(f"Starting auth proxy on port {port}")
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    return server

def get_proxy_url(original_url, proxy_port=8080):
    """Convert original URL to use the proxy"""
    parsed = urllib.parse.urlparse(original_url)
    return f"http://localhost:{proxy_port}/{parsed.netloc}{parsed.path}"

if __name__ == "__main__":
    # Test the proxy
    proxy = start_auth_proxy()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down proxy...")
        proxy.shutdown() 