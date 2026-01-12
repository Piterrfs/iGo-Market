#!/usr/bin/env python3
"""
Servidor HTTP simples para servir o arquivo HTML do iGo Market
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        public_dir = os.path.join(base_dir, 'frontend', 'public')
        super().__init__(*args, directory=public_dir, **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, CustomHandler)
    print(f"🚀 Servidor HTTP rodando em http://localhost:{port}")
    print(f"📄 Acesse: http://localhost:{port}/igo_market_comparador_precos.html")
    print(f"📄 Ou a página principal: http://localhost:{port}/")
    print("\nPressione Ctrl+C para parar o servidor")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServidor parado.")
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
