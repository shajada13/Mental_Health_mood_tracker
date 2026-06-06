# ============================================================
#  MindFlow — Pure Python HTTP Server
#  server.py  |  stdlib http.server + custom router
#  No Flask · No Django · No external web framework
#
#  Run:   python server.py
#  Port:  5000 (configurable via PORT env var)
# ============================================================

import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("mindflow.server")

# ── Import route handlers ────────────────────────────────────
from backend.routes.auth_routes import (
    register        as auth_register,
    login           as auth_login,
    logout          as auth_logout,
    me              as auth_me,
    change_password as auth_change_password,
    logout_all      as auth_logout_all,
)

# ── Route table: (METHOD, PATH) → handler function ──────────
ROUTES: dict[tuple, callable] = {
    ("POST",  "/api/auth/register"):         auth_register,
    ("POST",  "/api/auth/login"):            auth_login,
    ("POST",  "/api/auth/logout"):           auth_logout,
    ("GET",   "/api/auth/me"):               auth_me,
    ("POST",  "/api/auth/change-password"):  auth_change_password,
    ("POST",  "/api/auth/logout-all"):       auth_logout_all,
}

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500").split(",")


# ── Request Handler ──────────────────────────────────────────
class MindFlowHandler(BaseHTTPRequestHandler):
    """
    Single handler class dispatching all requests to registered
    route functions.  Each function receives a `request` dict and
    returns (status_code, body_str, extra_headers).
    """

    server_version = "MindFlow/1.0"
    log_message    = lambda self, *a: None   # silence default access log

    # ── CORS pre-flight ──────────────────────────────────────
    def do_OPTIONS(self):
        self._send_cors_headers(204, b"")

    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")

    def do_PUT(self):
        self._dispatch("PUT")

    def do_DELETE(self):
        self._dispatch("DELETE")

    # ── Core dispatcher ──────────────────────────────────────
    def _dispatch(self, method: str):
        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/") or "/"
        query  = {k: (v[0] if len(v) == 1 else v) for k, v in parse_qs(parsed.query).items()}

        # Parse JSON body (if present)
        body = {}
        content_len = int(self.headers.get("Content-Length", 0) or 0)
        if content_len:
            raw = self.rfile.read(content_len)
            try:
                body = json.loads(raw.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send_json(400, {"success": False, "message": "Invalid JSON body."})
                return

        # Build headers dict for handlers
        headers_dict = {k: v for k, v in self.headers.items()}

        request = {
            "method":  method,
            "path":    path,
            "body":    body,
            "headers": headers_dict,
            "query":   query,
        }

        # Lookup route
        handler = ROUTES.get((method, path))
        if handler is None:
            self._send_json(404, {"success": False, "message": f"Route {method} {path} not found."})
            return

        # Execute handler
        try:
            result = handler(request)
            if isinstance(result, tuple) and len(result) == 3:
                status, body_str, extra_headers = result
                self._send_raw(status, body_str.encode("utf-8"), extra_headers)
            else:
                logger.error("Handler %s returned unexpected type", handler.__name__)
                self._send_json(500, {"success": False, "message": "Internal handler error."})
        except Exception as exc:
            logger.exception("Unhandled exception in %s %s: %s", method, path, exc)
            self._send_json(500, {"success": False, "message": "Internal server error."})

    # ── Response helpers ─────────────────────────────────────
    def _send_raw(self, status: int, body: bytes, extra_headers: dict = None):
        self.send_response(status)
        self._write_cors_headers()
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        logger.info("%s %s %s", self.command, self.path, status)

    def _send_json(self, status: int, data: dict):
        body = json.dumps(data, default=str).encode("utf-8")
        self._send_raw(status, body, {"Content-Type": "application/json; charset=utf-8"})

    def _send_cors_headers(self, status: int, body: bytes):
        self.send_response(status)
        self._write_cors_headers()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_cors_headers(self):
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin",      origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, Cookie")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options",         "DENY")


# ── Entry point ──────────────────────────────────────────────
def run():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))

    httpd = HTTPServer((host, port), MindFlowHandler)
    logger.info("=" * 60)
    logger.info("  MindFlow API Server")
    logger.info("  http://%s:%s", host if host != "0.0.0.0" else "localhost", port)
    logger.info("  Auth endpoints:")
    for method, path in ROUTES:
        logger.info("    %s  %s", f"{method:<6}", path)
    logger.info("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped.")
        httpd.server_close()
        sys.exit(0)


if __name__ == "__main__":
    run()
