"""ReadEasy - Dyslexia-friendly iterative simplification prototype
 
    python app.py            serve on 8000
    python app.py --port 8001
"""
import os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
 
HERE = os.path.dirname(os.path.abspath(__file__))
 
 
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        with open(os.path.join(HERE, "index.html"), "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
 
    def log_message(self, *a):
        pass
 
 
if __name__ == "__main__":
    port = 8000
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    print(f"serving ReadEasy prototype on http://localhost:{port}")
    HTTPServer(("localhost", port), Handler).serve_forever()