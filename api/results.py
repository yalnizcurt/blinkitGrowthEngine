from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path

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

        file_path = Path(__file__).parent.parent / "data" / "results" / "insight_engine_results.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.wfile.write(content.encode("utf-8"))
        else:
            empty_resp = {"metadata": {"total_feedback_analyzed": 0}, "themes": []}
            self.wfile.write(json.dumps(empty_resp).encode("utf-8"))
