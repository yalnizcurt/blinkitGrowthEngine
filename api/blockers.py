from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path

BLOCKERS_PATH = Path("data/weekly/blockers.json")

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        data = {}
        if BLOCKERS_PATH.exists():
            try:
                with open(BLOCKERS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass

        self.wfile.write(json.dumps(data).encode("utf-8"))
