from http.server import BaseHTTPRequestHandler
from pathlib import Path

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        file_path = Path(__file__).parent.parent / "data" / "results" / "insight_engine_results.csv"
        if file_path.exists():
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.send_header("Content-Disposition", 'attachment; filename="insight_engine_results.csv"')
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write("CSV File Not Found".encode("utf-8"))
