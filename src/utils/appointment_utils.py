import re
from datetime import datetime, timedelta
from typing import Optional

from src.utils.timezone_utils import get_utc_now, ensure_timezone_aware


def parse_duration(duration_str: str) -> Optional[timedelta]:
    """
    Parse duration string to timedelta object.
    """
    if not duration_str:
        return None
    
    # Pattern for duration: optional hours and/or minutes
    pattern = r'^(?:(\d+)h)?(?:\s*(\d+)m)?$'
    match = re.match(pattern, duration_str.strip())
    
    if not match:
        return None
    
    hours_str, minutes_str = match.groups()
    
    hours = int(hours_str) if hours_str else 0
    minutes = int(minutes_str) if minutes_str else 0
    
    # At least one of hours or minutes must be specified
    if hours == 0 and minutes == 0:
        return None
    
    return timedelta(hours=hours, minutes=minutes)


def get_appointment_end_time(start_time: datetime, duration_str: str) -> Optional[datetime]:
    """
    Calculate appointment end time from start time and duration.

        start_time: Timezone-aware appointment start time
        duration_str: Duration string (e.g., "1h", "30m")
    """
    # Ensure start_time is timezone-aware
    start_time = ensure_timezone_aware(start_time)
    
    duration = parse_duration(duration_str)
    if duration is None:
        return None
    
    return start_time + duration


def is_appointment_overdue(start_time: datetime, duration_str: str, current_time: Optional[datetime] = None) -> bool:
    """
    Check if an appointment is overdue 
    
    """
    if current_time is None:
        current_time = get_utc_now()
    
    # Ensure both times are timezone-aware
    start_time = ensure_timezone_aware(start_time)
    current_time = ensure_timezone_aware(current_time)
    
    end_time = get_appointment_end_time(start_time, duration_str)
    if end_time is None:
        return False
    
    return current_time > end_time
