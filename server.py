#!/usr/bin/env python3
"""캘린더 공유 일정 API — nginx 정적 서버 대신 사용.
GET  /            → index.html
GET  /api/events  → 일정 JSON
POST /api/events  → 일정 저장 (body: 일정 배열, 대체)
"""
import json
import os
import re
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DATA_DIR = os.environ.get("DATA_DIR", "/data")
EVENTS_FILE = os.path.join(DATA_DIR, "events.json")
INDEX_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
lock = threading.Lock()


def load_events():
    try:
        with open(EVENTS_FILE, encoding="utf-8") as f:
            arr = json.load(f)
        return arr if isinstance(arr, list) else []
    except (OSError, ValueError):
        return []


def save_events(arr):
    os.makedirs(DATA_DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(arr, f, ensure_ascii=False)
    os.replace(tmp, EVENTS_FILE)


def valid_event(e):
    return (
        isinstance(e, dict)
        and isinstance(e.get("id"), str)
        and isinstance(e.get("title"), str) and e["title"]
        and isinstance(e.get("date"), str) and DATE_RE.match(e["date"])
        and (e.get("time") in (None, "") or (isinstance(e.get("time"), str) and TIME_RE.match(e["time"])))
        and isinstance(e.get("color"), str) and COLOR_RE.match(e["color"])
    )


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code, body=b"", ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/api/events"):
            with lock:
                body = json.dumps(load_events(), ensure_ascii=False).encode()
            self._send(200, body)
        elif self.path in ("/", "/index.html"):
            try:
                with open(INDEX_FILE, "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            except OSError:
                self._send(500, b"index.html missing", "text/plain")
        else:
            self._send(404, b'{"error":"not found"}')

    def do_POST(self):
        if not self.path.startswith("/api/events"):
            self._send(404, b'{"error":"not found"}')
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n)
            arr = json.loads(raw)
            if not isinstance(arr, list) or not all(valid_event(e) for e in arr):
                raise ValueError("invalid")
        except (ValueError, OSError):
            self._send(400, b'{"error":"invalid payload"}')
            return
        with lock:
            save_events(arr)
        self._send(200, json.dumps({"ok": True, "count": len(arr)}).encode())

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "80"))
    print(f"calendar API listening on :{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
