#!/usr/bin/env python3
"""
serve.py - run a consumer as the webhook live-ocr posts to.

    python serve.py example 8000
    python serve.py --dir ../other-consumers my_consumer 8001
    python serve.py --set mode=fast my_consumer 8002

A consumer is a module with handle(event) -> dict | None, found next to this
file or in --dir. A returned dict is sent back as the HTTP response; if it has
a "message", live-ocr shows it in its log.

--set passes a setting to the consumer as an environment variable, upper-cased
and prefixed with the consumer's name: --set mode=fast on the consumer
"example" becomes EXAMPLE_MODE=fast. Standard library only.
"""

import argparse
import importlib
import os
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


def make_handler(consumer):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
            try:
                reply = consumer.handle(json.loads(raw))
                status = 200
            except json.JSONDecodeError:
                reply, status = {"error": "invalid json"}, 400
            except Exception as e:  # one bad event must not kill the server
                reply, status = {"error": str(e)}, 500
            body = json.dumps(reply or {"ok": True}).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            if reply and "message" in reply:
                print(reply["message"])

        def log_message(self, *args):
            pass

    return Handler


def main():
    ap = argparse.ArgumentParser(description="Run a live-ocr consumer.")
    ap.add_argument("consumer", help="module name, e.g. example")
    ap.add_argument("port", nargs="?", type=int, default=8000)
    ap.add_argument("--dir", default=str(Path(__file__).resolve().parent),
                    help="folder containing the consumer module")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="a setting for the consumer, e.g. --set mode=fast")
    a = ap.parse_args()

    for pair in a.set:
        key, _, value = pair.partition("=")
        os.environ[f"{a.consumer.upper()}_{key.strip().upper()}"] = value.strip()

    sys.path.insert(0, str(Path(a.dir).resolve()))
    consumer = importlib.import_module(a.consumer)
    server = HTTPServer(("127.0.0.1", a.port), make_handler(consumer))
    print(f"{a.consumer} consumer on http://127.0.0.1:{a.port}/  (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
