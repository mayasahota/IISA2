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
 
TYPED_MAX_LEVEL = 4      # levels available for text the user types or pastes
 
# Only approve a simplification if the checker is quite sure (about 80%).
# Set high: a missed meaning loss is worse than a false alarm.
RISK_THRESHOLD = 0.80

def check_meaning(original, simplified):

    """Simulated checker: score = how much of the original survives

    (square root of the word-count ratio, capped at 1), then compare with the threshold."""

    o, s = len(original.split()), len(simplified.split())

    score = round(min(1.0, (s / o) ** 0.5), 2) if o else 1.0

    return {"status": "risk" if score < RISK_THRESHOLD else "ok",

            "score": score, "threshold": RISK_THRESHOLD}
 
 
# Two different simulated documents. The last level in each list is the one
# the checker declines.
SAMPLES = {
    "ocr": {   # scanned appointment letter: 3 approved, 4th declined
        "text": (
            "Patients are required to arrive approximately fifteen minutes prior to their "
            "scheduled appointment in order to complete the necessary registration "
            "documentation. Failure to attend without providing at least twenty-four hours' "
            "notice may result in a charge being applied, and subsequent appointments may be "
            "subject to additional restrictions. Please bring a valid form of identification "
            "and a list of any medication currently being taken."
        ),
        "levels": [
            "Patients must arrive about fifteen minutes before their appointment time to fill "
            "in the registration forms. If you miss an appointment without telling us at least "
            "twenty-four hours before, you may be charged a fee. Later appointments may also "
            "have extra limits. Please bring photo identification and a list of the "
            "medication you take.",
 
            "Please arrive about fifteen minutes early to fill in the registration forms. If "
            "you miss an appointment without telling us at least twenty-four hours before, you "
            "may be charged a fee. Later appointments may also have extra limits. Please bring "
            "photo identification and a list of the medication you take.",
 
            "Please arrive about fifteen minutes early to fill in the forms. If you miss an "
            "appointment without telling us 24 hours before, you may be charged a fee. Later "
            "appointments may also have limits. Please bring photo identification and a list "
            "of your medication.",
 
            "Arrive fifteen minutes early to fill in forms. If you miss an appointment "
            "without telling us in time, you may be charged. Please bring identification and "
            "your medication list.",
        ],
        "alts": [
            "You need to arrive about fifteen minutes before your appointment to fill in the "
            "registration forms. If you do not come and have not told us at least twenty-four "
            "hours before, you may have to pay a fee. Your later appointments may also be "
            "limited. Please bring photo identification and a list of the medication you are "
            "taking.",
            "Please come about fifteen minutes early and fill in the registration forms. If you "
            "miss an appointment and have not told us at least twenty-four hours before, you "
            "may be charged a fee. Your later appointments may also be limited. Please bring "
            "photo identification and a list of your medication.",
            "Please come about fifteen minutes early to fill in the registration forms. Tell us "
            "at least 24 hours before if you cannot come, or you may be charged a fee. Later "
            "appointments may also have extra limits. Please bring photo identification and a "
            "list of your medication.",
            "Come fifteen minutes early to fill in the forms. If you cannot come, tell us at "
            "least 24 hours before, or you may have to pay a fee. Later visits may also have "
            "limits. Please bring photo identification and a list of your medication.",
        ],
    },
    "file": {  # uploaded coursework policy: 4 approved, 5th declined
        "text": (
            "Students who anticipate difficulty in meeting a coursework submission deadline "
            "must notify the module coordinator in writing prior to the stated closing date. "
            "Requests will only be considered where supporting evidence, such as medical "
            "documentation, is provided. Late submissions received without an approved "
            "extension will incur a penalty of ten percent per day, up to a maximum of five "
            "days, after which a mark of zero will be recorded. Students are therefore "
            "advised to seek guidance from the support team as early as possible."
        ),
        "levels": [
            "Students who think they may miss a coursework deadline must tell the module "
            "coordinator in writing before the closing date. Requests will only be considered "
            "where supporting evidence, such as medical documents, is provided. Late work "
            "handed in without an approved extension will lose ten percent per day, up to a "
            "maximum of five days, after which a mark of zero will be recorded. Students "
            "should therefore ask the support team for help as early as possible.",
 
            "If you think you may miss a coursework deadline, you must tell the module "
            "coordinator in writing before the closing date. Requests are only considered if "
            "you give evidence, such as medical documents. Late work without an approved "
            "extension loses ten percent of its mark per day, for up to five days. After "
            "that, the mark is zero. Students should ask the support team for help as early "
            "as possible.",
 
            "If you may miss a coursework deadline, you must tell the module coordinator in "
            "writing before the closing date. Requests are only considered if you give "
            "evidence, such as medical documents. Late work without an approved extension "
            "loses ten percent per day for up to five days. After that, the mark is zero. "
            "Students should ask the support team for help as early as possible.",
 
            "Tell the module coordinator in writing before the closing date if you may miss a "
            "deadline. Requests are only considered with evidence, such as medical documents. "
            "Late work without an approved extension loses ten percent per day for up to five "
            "days. After that, the mark is zero. Ask the support team for help as early as "
            "possible.",
 
            "Tell the module coordinator in writing before the deadline if you need more "
            "time. You may need to give evidence. Late work loses marks every day and may get "
            "zero. Ask the support team for help early.",
        ],
        "alts": [
            "Students who think they will have trouble meeting a coursework deadline must tell "
            "the module coordinator in writing before the closing date. Requests will only be "
            "looked at if you give supporting evidence, such as medical documents. Late work "
            "handed in without an approved extension loses ten percent each day, for up to five "
            "days. After that, a mark of zero will be given. Students are advised to ask the "
            "support team for help as early as possible.",
 
            "If you think you will miss a coursework deadline, tell the module coordinator in "
            "writing before the closing date. Requests are only looked at if you give evidence, "
            "such as medical documents. Late work without an approved extension loses ten "
            "percent each day, for up to five days. After that, you get zero. Please ask the "
            "support team for help as early as possible.",
 
            "Tell the module coordinator in writing before the closing date if you may miss a "
            "deadline. Requests are only looked at with evidence, such as medical documents. "
            "Late work without an approved extension loses ten percent each day, for up to five "
            "days. After that, the mark is zero. Please ask the support team for help as early "
            "as possible.",
 
            "If you may miss a deadline, tell the module coordinator in writing before the "
            "closing date. Give evidence, such as medical documents, or your request will not "
            "be looked at. Late work with no approved extension loses ten percent a day for up "
            "to five days. After that, the mark is zero. Ask the support team for help as early "
            "as you can.",
 
            "Tell the module coordinator in writing before the deadline if you may need more "
            "time. Give evidence, such as medical documents. Late work loses ten percent each "
            "day, for up to five days. After that, the mark is zero. Ask the support team for "
            "help early.",
        ],
    },
}
 
 
def find_sample(text):
    norm = " ".join(text.split())
    for s in SAMPLES.values():
        if norm == s["text"]:
            return s
    return None
 
 
def max_level_for(text):
    s = find_sample(text)
    return len(s["levels"]) if s else TYPED_MAX_LEVEL
 
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

# Second choice of words, used when the user flags a typed-text simplification
ALT_SYN = {
    "approximately": "around", "difficult": "tough", "difficulty": "problems",
    "complex": "involved", "commence": "begin", "assist": "support",
    "numerous": "lots of", "additional": "more", "require": "have to",
    "required": "have to", "requires": "has to", "sufficient": "plenty",
    "purchase": "pay for", "however": "yet",
}
 
def swap_words(text, variant=0):
    table = {**SYN, **ALT_SYN} if variant % 2 else SYN
    def sub(m):
        w = m.group(0)
        r = table.get(w.lower())
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
 
 
def rule_based(text, level, variant=0):
    out = swap_words(text, variant)
    if level >= 2:
        out = tidy(" ".join(break_up(s) for s in sentences(out)))
    if level >= 3:
        sents = [first_clause(s) for s in sentences(out)]
        if level >= 4:
            sents = sents[:max(1, len(sents) // 2)]   # keep the first half
        out = " ".join(sents)
    return out
 
 
def simplify(text, level, variant=0):
    """variant 0 = first version, odd = regenerated (after Flag Incorrect)."""
    s = find_sample(text)
    level = max(1, min(level, max_level_for(text)))
    if s:
        versions = s["alts"] if variant % 2 else s["levels"]
        return versions[level - 1]
    return rule_based(text, level, variant)

def same(a, b):
    return " ".join(a.split()) == " ".join(b.split())
 
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
            if self.path == "/load":            # simulated OCR / file upload
                source = data.get("source", "ocr")
                res = {"text": SAMPLES.get(source, SAMPLES["ocr"])["text"], "source": source}
            elif self.path == "/simplify":
                text = data.get("text", "")
                max_level = max_level_for(text)
                level = max(1, min(int(data.get("level", 1)), max_level))
                variant = int(data.get("variant", 0))
                out = simplify(text, level, variant)
                if variant:   # regenerating: compare with the version being replaced
                    before = simplify(text, level, variant - 1)
                else:
                    before = simplify(text, level - 1) if level > 1 else text
                res = {"simplified": out,
                       "level": level,
                       "max_level": max_level,
                       "unchanged": same(out, before),
                       "check": check_meaning(text, out)}
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