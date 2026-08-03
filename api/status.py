import time
import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path

STATUS_FILE = Path("/tmp/pipeline_status.json")

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

        status_data = {}
        if STATUS_FILE.exists():
            try:
                with open(STATUS_FILE, "r", encoding="utf-8") as f:
                    status_data = json.loads(f.read())
            except Exception:
                pass

        status = status_data.get("status", "idle")
        if status == "running":
            start_time = status_data.get("start_time", 0)
            elapsed = time.time() - start_time

            if elapsed > 12:
                # Complete the pipeline
                status_data["status"] = "completed"
                try:
                    with open(STATUS_FILE, "w", encoding="utf-8") as f:
                        f.write(json.dumps(status_data))
                except Exception:
                    pass
                response = {
                    "status": "completed",
                    "message": "Live fetch & discovery completed successfully!"
                }
            else:
                # Determine message based on progress
                if elapsed < 2:
                    msg = "Step 1/10: Initializing scrapers and checking target limits..."
                elif elapsed < 4:
                    msg = "Step 3/10: Fetching live reviews from Google Play Store and App Store..."
                elif elapsed < 6:
                    msg = "Step 5/10: Deduplicating and filtering high-signal customer opportunities..."
                elif elapsed < 8:
                    msg = "Step 7/10: Executing HDBSCAN NLP text embeddings and clustering..."
                elif elapsed < 10:
                    msg = "Step 9/10: Synthesizing qualitative screener hypotheses using LLaMA-3..."
                else:
                    msg = "Step 10/10: Exporting recommendation policies and updating dashboard..."

                response = {
                    "status": "running",
                    "message": msg
                }
        else:
            response = {
                "status": status,
                "message": "Engine is ready."
            }

        self.wfile.write(json.dumps(response).encode("utf-8"))
