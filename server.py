import os
import json
import logging
import threading
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import config
from main import run_pipeline
from analysis.chat_engine import generate_chat_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("PORT", 8080))
pipeline_lock = threading.Lock()
pipeline_status = {"status": "idle", "message": "Engine is ready."}

class InsightEngineRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path == "/":
            return str(config.BASE_DIR / "static" / "index.html")
        elif path.startswith("/static/"):
            rel_path = path[len("/static/"):]
            return str(config.BASE_DIR / "static" / rel_path)
        return super().translate_path(path)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/results":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            json_file = config.FINAL_RESULTS_JSON
            if json_file.exists():
                with open(json_file, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            else:
                empty_resp = {"metadata": {"total_feedback_analyzed": 0}, "themes": []}
                self.wfile.write(json.dumps(empty_resp).encode("utf-8"))
            return

        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(pipeline_status).encode("utf-8"))
            return

        elif self.path == "/api/download-csv":
            csv_file = config.FINAL_RESULTS_CSV
            if csv_file.exists():
                self.send_response(200)
                self.send_header("Content-Type", "text/csv")
                self.send_header("Content-Disposition", 'attachment; filename="insight_engine_results.csv"')
                self.end_headers()
                with open(csv_file, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "CSV File Not Found")
            return

        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            messages = []
            if content_length > 0:
                try:
                    body_bytes = self.rfile.read(content_length)
                    body_data = json.loads(body_bytes.decode("utf-8"))
                    messages = body_data.get("messages", [])
                except Exception as e:
                    logger.warning(f"Could not parse Chat POST JSON: {e}")

            if not messages:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No messages provided."}).encode("utf-8"))
                return

            chat_reply = generate_chat_response(messages)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(chat_reply).encode("utf-8"))
            return

        elif self.path == "/api/run-pipeline":
            content_length = int(self.headers.get("Content-Length", 0))
            body_params = {}
            if content_length > 0:
                try:
                    body_bytes = self.rfile.read(content_length)
                    body_params = json.loads(body_bytes.decode("utf-8"))
                except Exception as e:
                    logger.warning(f"Could not parse POST JSON: {e}")

            ps_count = body_params.get("playstore_count", 500)
            as_count = body_params.get("appstore_count", 500)
            reddit_terms = body_params.get("reddit_terms", ["blinkit", "quick commerce"])
            sources = body_params.get("sources", ["playstore", "appstore", "reddit"])

            if pipeline_lock.locked():
                self.send_response(409)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "running", "message": "Pipeline execution is already in progress."}).encode("utf-8"))
                return

            def worker():
                global pipeline_status
                with pipeline_lock:
                    pipeline_status = {"status": "running", "message": "Fetching live reviews and executing 10-step discovery..."}
                    try:
                        run_pipeline(
                            playstore_count=ps_count,
                            appstore_count=as_count,
                            reddit_terms=reddit_terms,
                            sources=sources
                        )
                        pipeline_status = {"status": "completed", "message": "Live fetch & discovery completed successfully!"}
                    except Exception as e:
                        logger.error(f"Pipeline worker error: {e}")
                        pipeline_status = {"status": "error", "message": str(e)}

            threading.Thread(target=worker, daemon=True).start()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            resp = {"status": "started", "message": f"Live fetch started for sources: {', '.join(sources)}."}
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        self.send_error(404)

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, InsightEngineRequestHandler)
    logger.info(f"Insight Engine Web Dashboard is running on http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
