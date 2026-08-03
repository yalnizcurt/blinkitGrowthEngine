from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path

RATE_LIMIT_FILE = Path("/tmp/rate_limits.json")

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        # Extract client IP
        client_ip = self.headers.get("x-forwarded-for") or self.headers.get("x-real-ip") or self.client_address[0]
        if client_ip and "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()

        # Load existing rate limits
        rate_limits = {}
        if RATE_LIMIT_FILE.exists():
            try:
                with open(RATE_LIMIT_FILE, "r", encoding="utf-8") as f:
                    rate_limits = json.loads(f.read())
            except Exception:
                pass

        count = rate_limits.get(client_ip, 0)
        if count >= 4:
            self.send_response(429)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "message": "Rate limit exceeded. To prevent API abuse, you are permitted to trigger the discovery flow at most 4 times per IP address on this demo instance."
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        # Increment and save
        rate_limits[client_ip] = count + 1
        try:
            with open(RATE_LIMIT_FILE, "w", encoding="utf-8") as f:
                f.write(json.dumps(rate_limits))
        except Exception:
            pass

        self.send_response(403)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        response = {
            "message": f"Rate limit check passed ({count + 1}/4 fetches used). However, live scraping & NLP pipeline execution is disabled on the public demo instance to prevent API abuse. To fetch fresh reviews and run the 10-step discovery flow, run ReviewLens locally with a dedicated Python server."
        }
        self.wfile.write(json.dumps(response).encode("utf-8"))
