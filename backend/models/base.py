"""Common model helpers."""
from __future__ import annotations

from datetime import datetime, timezone

from extensions import db


def utcnow() -> datetime:
    """Timezone-aware UTC now (datetime.utcnow is deprecated in 3.12+)."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Adds created_at / updated_at to a model."""

    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
