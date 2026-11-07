import os
import sys
from http.server import HTTPServer

# Servidor local para desarrollo: expone api/compile.py en http://localhost:3000/api/compile
# (en Vercel no se usa; allá cada archivo de /api es una función serverless)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.compile import handler  # noqa: E402

PORT = int(os.environ.get("PORT", "3000"))


class DevHandler(handler):
    def log_message(self, format, *args):
        sys.stderr.write(f"[api] {self.command} {self.path} -> {args[1] if len(args) > 1 else ''}\n")


if __name__ == "__main__":
    print(f"API del compilador en http://localhost:{PORT}/api/compile")
    HTTPServer(("127.0.0.1", PORT), DevHandler).serve_forever()
