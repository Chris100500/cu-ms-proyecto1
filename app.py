
#!/usr/bin/env python3
"""
Servidor HTTP simple que responde Hola Mundo y consume datos de otro microservicio
"""
import http.server
import socketserver
import sys
import os
import json
from datetime import datetime
import requests  # Para consumir el servicio externo

PORT = 3005

# URL del microservicio externo (puedes configurarlo por variable de entorno)
MICROSERVICE_URL = os.environ.get('MICROSERVICE_URL', 'cu-ms-payments.chris100500-dev.svc.cluster.local:3000/users')

def get_users():
    """Consume datos desde otro microservicio en lugar de la base de datos"""
    try:
        response = requests.get(MICROSERVICE_URL, timeout=5)
        response.raise_for_status()
        return response.json()  # Devuelve el JSON del microservicio
    except requests.exceptions.RequestException as e:
        return {"error": f"No se pudo obtener datos del microservicio: {str(e)}"}

class HolaMundoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Solicitud GET recibida", file=sys.stdout)
        print(f"[{timestamp}] Path: {self.path}", file=sys.stdout)

        if self.path == '/startup':
            self._send_text_response('OK')
        elif self.path == '/liveness':
            self._send_text_response('OK')
        elif self.path == '/readiness':
            self._send_text_response('OK')
        elif self.path == '/users':
            print(f"[{timestamp}] se llamó al endpoint /users", file=sys.stdout)
            sys.stdout.flush()
            result = get_users()
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        else:
            self._send_text_response('<h1>Hola Mundo</h1>')

    def _send_text_response(self, text):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))

    def log_message(self, format, *args):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {self.address_string()} - {format % args}", file=sys.stdout)
        sys.stdout.flush()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), HolaMundoHandler) as httpd:
        print(f"Servidor corriendo en puerto {PORT}")
        print("Presiona Ctrl+C para detener")
        httpd.serve_forever()
