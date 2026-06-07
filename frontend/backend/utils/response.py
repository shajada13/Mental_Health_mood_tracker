# ============================================================
#  MindFlow — HTTP Response Helpers
#  utils/response.py  |  Pure Python http.server compatible
# ============================================================

import json
from http import HTTPStatus


def json_response(data: dict, status: int = 200) -> tuple[int, str, dict]:
    """
    Return (status_code, body_string, headers) tuple.
    The server layer (server.py) unpacks this.
    """
    body    = json.dumps(data, default=str, ensure_ascii=False)
    headers = {
        "Content-Type":  "application/json; charset=utf-8",
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
    }
    return status, body, headers


def ok(data: dict = None, message: str = "Success") -> tuple:
    payload = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return json_response(payload, 200)


def created(data: dict = None, message: str = "Created") -> tuple:
    payload = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return json_response(payload, 201)


def bad_request(message: str = "Bad request", errors: list = None) -> tuple:
    payload = {"success": False, "message": message}
    if errors:
        payload["errors"] = errors
    return json_response(payload, 400)


def unauthorized(message: str = "Unauthorized") -> tuple:
    return json_response({"success": False, "message": message}, 401)


def forbidden(message: str = "Forbidden") -> tuple:
    return json_response({"success": False, "message": message}, 403)


def not_found(message: str = "Not found") -> tuple:
    return json_response({"success": False, "message": message}, 404)


def conflict(message: str = "Conflict") -> tuple:
    return json_response({"success": False, "message": message}, 409)


def server_error(message: str = "Internal server error") -> tuple:
    return json_response({"success": False, "message": message}, 500)
