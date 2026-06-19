"""Small cross-cutting helpers (auth guards, slugify)."""
from __future__ import annotations

import re
from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def teacher_required(fn):
    """Require a valid JWT whose `role` claim is 'teacher'."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if get_jwt().get("role") != "teacher":
            return jsonify(error="teacher role required"), 403
        return fn(*args, **kwargs)

    return wrapper


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")
