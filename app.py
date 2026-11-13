"""SimplyRead - Dyslexia-friendly iterative simplification prototype
 
    python app.py            serve on 8000
    python app.py --port 8001
 
The "LLM" is SIMULATED: canned outputs for the default text, and simple
word/sentence rules for anything else. Swap simplify() for a real model
call later without changing the front end.
"""
import json, os, re, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
 
HERE = os.path.dirname(os.path.abspath(__file__))
 
MAX_LEVEL = 3
 
DEFAULT_TEXT = (
    "Individuals who experience dyslexia frequently encounter considerable difficulty when "
    "attempting to comprehend lengthy documents, particularly those containing specialised "
    "terminology and convoluted sentence structures. Consequently, it is advisable to obtain "
    "additional support, which may include assistive technology, in order to facilitate "
    "understanding and reduce the time required to complete reading tasks."
)
 
DEFAULT_LEVELS = {
    1: "People with dyslexia often find it hard to understand long documents. This is especially "
       "true for texts with specialist words and complicated sentences. Extra support, such as "
       "assistive technology, can make understanding easier and save time when reading.",
    2: "People with dyslexia often find long documents hard. Specialist words and complicated "
       "sentences make this worse. Extra help, such as assistive technology, makes reading "
       "easier and quicker.",
    3: "Reading can be hard. Tools can help.",
}
 
# ---- simple rule-based simplifier for any other text ----
SYN = {
    "utilize": "use", "utilise": "use", "approximately": "about",
    "difficult": "hard", "difficulty": "trouble", "complex": "tricky",
    "commence": "start", "assist": "help", "individuals": "people",
    "numerous": "many", "additional": "extra", "demonstrate": "show",
    "require": "need", "required": "needed", "requires": "needs",
    "obtain": "get", "sufficient": "enough", "purchase": "buy",
    "however": "but", "therefore": "so", "consequently": "so",
    "furthermore": "also", "subsequently": "then", "regarding": "about",
    "indicate": "show", "attempt": "try", "attempting": "trying",
    "comprehend": "understand", "frequently": "often", "residence": "home",
    "facilitate": "help", "advisable": "a good idea", "encounter": "face",
}
 
 
def swap_words(text):
    def sub(m):
        w = m.group(0)
        r = SYN.get(w.lower())
        if not r:
            return w
        return r.capitalize() if w[0].isupper() else r
    return re.sub(r"[A-Za-z]+", sub, text)
 
 
def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]
 
 
def tidy(text):
    parts = [p[:1].upper() + p[1:] for p in sentences(text)]
    return " ".join(p if p[-1] in ".!?" else p + "." for p in parts)
 
 
def break_up(s):
    s = re.sub(r",\s+which\s+", ". This ", s)
    s = re.sub(r",\s+but\s+", ". But ", s)
    return re.sub(r";\s+|,\s+and\s+", ". ", s)
 
 
def first_clause(s):
    head = re.split(r",|;", s)[0].strip()
    return (head if len(head.split()) >= 4 else s).rstrip(".!?, ") + "."
 
 
def rule_based(text, level):
    out = swap_words(text)
    if level >= 2:
        out = tidy(" ".join(break_up(s) for s in sentences(out)))
    if level >= 3:
        out = " ".join(first_clause(s) for s in sentences(out))
    return out
 
 
def simplify(text, level):
    level = max(1, min(level, MAX_LEVEL))
    if " ".join(text.split()) == DEFAULT_TEXT:
        return DEFAULT_LEVELS[level]
    return rule_based(text, level)
 
 
class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
 
    def do_GET(self):
        with open(os.path.join(HERE, "index.html"), "rb") as f:
            self._send(200, f.read(), "text/html; charset=utf-8")
 
    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
            if self.path == "/simplify":
                level = int(data.get("level", 1))
                res = {"simplified": simplify(data.get("text", ""), level),
                       "level": max(1, min(level, MAX_LEVEL)),
                       "max_level": MAX_LEVEL}
            else:
                res = {"error": "unknown endpoint"}
            self._send(200, json.dumps(res).encode("utf-8"))
        except Exception as e:
            self._send(500, json.dumps({"error": str(e)}).encode("utf-8"))
 
    def log_message(self, *a):
        pass
 
 
if __name__ == "__main__":
    port = 8000
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    print(f"serving SimplyRead prototype on http://localhost:{port}")
    HTTPServer(("localhost", port), Handler).serve_forever()