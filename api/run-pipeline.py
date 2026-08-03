from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        self.send_response(403)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        response = {
            "message": "Live scraping & NLP pipeline execution is disabled on the public demo instance to prevent API abuse. To fetch fresh reviews and run the 10-step discovery flow, run ReviewLens locally with a dedicated Python server."
        }
        self.wfile.write(json.dumps(response).encode("utf-8"))
