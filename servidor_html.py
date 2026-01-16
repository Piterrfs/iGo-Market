#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor HTTP simples para servir o arquivo HTML do iGo Market
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import sys

# Obter diretório base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'frontend', 'public')

# Verificar se o diretório existe
if not os.path.exists(PUBLIC_DIR):
    print(f"ERRO: Diretório não encontrado: {PUBLIC_DIR}")
    sys.exit(1)

print(f"Diretório base: {BASE_DIR}")
print(f"Diretório público: {PUBLIC_DIR}")
print(f"Diretório existe: {os.path.exists(PUBLIC_DIR)}")

# Listar arquivos disponíveis
if os.path.exists(PUBLIC_DIR):
    arquivos = os.listdir(PUBLIC_DIR)
    print(f"Arquivos disponíveis: {arquivos}")

class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Processa requisições GET"""
        # Limpar o caminho
        path = self.path.split('?')[0]  # Remover query string
        if path == '/':
            path = '/igo_market_comparador_precos.html'
        
        # Remover barra inicial
        if path.startswith('/'):
            path = path[1:]
        
        # Caminho completo do arquivo
        file_path = os.path.join(PUBLIC_DIR, path)
        
        # Log da requisição
        print(f"Requisição: {self.path} -> {file_path}")
        
        # Verificar se o arquivo existe
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            self.send_response(404)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write('<h1>404 - Arquivo não encontrado</h1>'.encode('utf-8'))
            return
        
        # Ler e enviar o arquivo
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Determinar content-type
            if file_path.endswith('.html'):
                content_type = 'text/html; charset=utf-8'
            elif file_path.endswith('.css'):
                content_type = 'text/css; charset=utf-8'
            elif file_path.endswith('.js'):
                content_type = 'application/javascript; charset=utf-8'
            else:
                content_type = 'application/octet-stream'
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(content)
            print(f"Arquivo enviado com sucesso: {path}")
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            error_msg = f'<h1>500 - Erro interno</h1><p>{str(e)}</p>'
            self.wfile.write(error_msg.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Log personalizado"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def run_server(port=8000):
    """Inicia o servidor HTTP"""
    server_address = ('', port)
    try:
        httpd = HTTPServer(server_address, CustomHandler)
        print("=" * 60)
        print(f"🚀 Servidor HTTP iniciado com sucesso!")
        print(f"📡 Porta: {port}")
        print(f"🌐 URL: http://localhost:{port}")
        print(f"📄 Arquivo principal: http://localhost:{port}/igo_market_comparador_precos.html")
        print("=" * 60)
        print("\nPressione Ctrl+C para parar o servidor\n")
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 10048:  # Porta já em uso no Windows
            print(f"ERRO: Porta {port} já está em uso!")
            print("Por favor, feche outros programas usando esta porta ou use outra porta.")
        else:
            print(f"ERRO ao iniciar servidor: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nServidor parado pelo usuário.")
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
