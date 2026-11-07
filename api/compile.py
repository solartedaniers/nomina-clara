import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Vercel ejecuta este archivo desde /api: se agrega la raíz del proyecto para importar el paquete compiler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from compiler import compile_source  # noqa: E402

MAX_SOURCE_LENGTH = 20000
MAX_EMPLOYEES = 200


class handler(BaseHTTPRequestHandler):
    """Función serverless de Vercel: POST /api/compile."""

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self._send_json(204, {})

    def do_GET(self) -> None:
        self._send_json(200, {"service": "nomina-clara-compiler", "usage": "POST {source, employees}"})

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", 0))
            request = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._send_json(400, {"ok": False, "errors": [{"phase": "request", "message": "JSON inválido"}]})
            return

        source = request.get("source", "")
        employees = request.get("employees", [])
        if not isinstance(source, str) or not isinstance(employees, list):
            self._send_json(400, {"ok": False, "errors": [{"phase": "request", "message": "Formato de petición inválido"}]})
            return
        if len(source) > MAX_SOURCE_LENGTH or len(employees) > MAX_EMPLOYEES:
            self._send_json(413, {"ok": False, "errors": [{"phase": "request", "message": "Programa o lista de empleados demasiado grande"}]})
            return

        self._send_json(200, compile_source(source, employees))
