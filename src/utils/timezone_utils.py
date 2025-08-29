"""Timezone utilities for handling timezone-aware datetime operations."""

from datetime import datetime, timezone
from typing import Optional


def get_utc_now() -> datetime:
    """
    Get current UTC time as timezone-aware datetime.
    """
    return datetime.now(timezone.utc)


def ensure_timezone_aware(dt: datetime, default_tz: Optional[timezone] = None) -> datetime:
    """
    Ensure datetime is timezone-aware.
    """
    if dt is None:
        raise ValueError("Datetime cannot be None")
    
    if dt.tzinfo is None:
        if default_tz is None:
            default_tz = timezone.utc
        return dt.replace(tzinfo=default_tz)
    
    return dt


def format_datetime_for_api(dt: datetime) -> str:
    """
    Format timezone-aware datetime for API responses.
    """
    if dt.tzinfo is None:
        raise ValueError("Cannot format datetime for API. Use ensure_timezone_aware() first.")
    
    return dt.isoformat()


def is_timezone_aware(dt: datetime) -> bool:
    """
    Check if datetime is timezone-aware.
    """
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None