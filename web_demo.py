"""Local-only GhostQueue web demo. Run after python train.py."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from ghostqueue.core import triage

ROOT = Path(__file__).resolve().parent
HTML = (ROOT / "web" / "index.html").read_bytes()
EXAMPLES = (ROOT / "examples" / "events.json").read_bytes()

class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self._send(200, HTML, "text/html; charset=utf-8")
        elif self.path in ("/static/app.js", "/static/style.css"):
            name = self.path.rsplit("/", 1)[-1]
            mime = "text/javascript" if name.endswith(".js") else "text/css"
            self._send(200, (ROOT / "web" / "static" / name).read_bytes(), mime + "; charset=utf-8")
        elif self.path == "/api/examples":
            self._send(200, EXAMPLES, "application/json")
        else:
            self._send(404, b'{"error":"not found"}', "application/json")

    def do_POST(self):
        if self.path != "/api/analyze":
            return self._send(404, b'{"error":"not found"}', "application/json")
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 12000:
                raise ValueError("request size must be 1–12000 bytes")
            event = json.loads(self.rfile.read(size))
            result = triage(event)
            body = json.dumps(result).encode()
            self._send(200, body, "application/json")
        except (ValueError, KeyError, TypeError, FileNotFoundError) as exc:
            self._send(400, json.dumps({"error":str(exc)}).encode(), "application/json")

if __name__ == "__main__":
    print("GhostQueue local demo: http://127.0.0.1:8765", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
