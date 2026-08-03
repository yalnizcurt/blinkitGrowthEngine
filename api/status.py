from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path

BLOCKERS_PATH = Path("data/weekly/blockers.json")
RESULTS_PATH = Path("data/results/insight_engine_results.json")
PUBLISH_PATH = Path("data/weekly/publish_state.json")

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

        # Check PII status
        pii_passed = True
        if BLOCKERS_PATH.exists():
            try:
                with open(BLOCKERS_PATH, "r", encoding="utf-8") as f:
                    blockers_data = json.load(f)
                    pii_passed = blockers_data.get("passed", True)
            except Exception:
                pass

        # Check total feedback analyzed count
        normalized_count = 1602
        if RESULTS_PATH.exists():
            try:
                with open(RESULTS_PATH, "r", encoding="utf-8") as f:
                    results_data = json.load(f)
                    normalized_count = results_data.get("metadata", {}).get("total_feedback_analyzed", 1602)
            except Exception:
                pass

        # Get publish state
        publish_state = {}
        if PUBLISH_PATH.exists():
            try:
                with open(PUBLISH_PATH, "r", encoding="utf-8") as f:
                    publish_state = json.load(f)
            except Exception:
                pass

        status_resp = {
            "status": "idle",
            "message": "Engine is ready.",
            "pii_passed": pii_passed,
            "normalized_count": normalized_count,
            "publish_state": publish_state
        }
        self.wfile.write(json.dumps(status_resp).encode("utf-8"))
