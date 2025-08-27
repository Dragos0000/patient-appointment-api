from datetime import datetime, timedelta
import pytest

from src.utils.appointment_utils import (
    parse_duration,
    get_appointment_end_time,
    is_appointment_overdue
)


def test_parse_duration_valid():
    """Test parsing valid duration strings."""
    test_cases = [
        ("1h", timedelta(hours=1)),
        ("30m", timedelta(minutes=30)),
        ("1h 30m", timedelta(hours=1, minutes=30)),
        ("2h 45m", timedelta(hours=2, minutes=45)),
        ("15m", timedelta(minutes=15)),
        ("3h", timedelta(hours=3)),
    ]
    
    for duration_str, expected in test_cases:
        result = parse_duration(duration_str)
        assert result == expected, f"Expected {expected} for '{duration_str}', got {result}"


def test_parse_duration_invalid():
    """Test parsing invalid duration strings."""
    invalid_durations = [
        "",
        "abc",
        "1x",
        "30s",
        "1h 30s",
        "h",
        "m",
        "0h 0m",
        "1.5h",
        "-1h",
    ]
    
    for duration_str in invalid_durations:
        result = parse_duration(duration_str)
        assert result is None, f"Expected None for '{duration_str}', got {result}"


def test_parse_duration_edge_cases():
    """Test edge cases for duration parsing."""
    assert parse_duration(" 1h 30m ") == timedelta(hours=1, minutes=30)
    assert parse_duration("1h  30m") == timedelta(hours=1, minutes=30)
    
    assert parse_duration(None) is None


def test_get_appointment_end_time_valid():
    """Test calculating appointment end time."""
    start_time = datetime(2024, 1, 15, 10, 0) 
    
    test_cases = [
        ("1h", datetime(2024, 1, 15, 11, 0)),      
        ("30m", datetime(2024, 1, 15, 10, 30)),    
        ("1h 30m", datetime(2024, 1, 15, 11, 30)), 
        ("2h 15m", datetime(2024, 1, 15, 12, 15)), 
    ]
    
    for duration_str, expected_end in test_cases:
        result = get_appointment_end_time(start_time, duration_str)
        assert result == expected_end, f"Expected {expected_end} for '{duration_str}', got {result}"


def test_get_appointment_end_time_invalid():
    """Test calculating end time with invalid duration."""
    start_time = datetime(2024, 1, 15, 10, 0)
    
    invalid_durations = ["", "abc", "1x", None]
    
    for duration_str in invalid_durations:
        result = get_appointment_end_time(start_time, duration_str)
        assert result is None, f"Expected None for '{duration_str}', got {result}"


def test_is_appointment_overdue():
    """Test checking if appointment is overdue."""
    start_time = datetime(2024, 1, 15, 10, 0)  # 10:00 AM
    duration = "1h"  # 1 hour appointment
    # End time would be 11:00 AM
    
    # Test cases with different current times
    test_cases = [
        (datetime(2024, 1, 15, 9, 30), False),   # Before start
        (datetime(2024, 1, 15, 10, 30), False),  # During appointment
        (datetime(2024, 1, 15, 11, 0), False),   # Exactly at end time
        (datetime(2024, 1, 15, 11, 1), True),    # 1 minute overdue
        (datetime(2024, 1, 15, 12, 0), True),    # 1 hour overdue
    ]
    
    for current_time, expected_overdue in test_cases:
        result = is_appointment_overdue(start_time, duration, current_time)
        assert result == expected_overdue, f"Expected {expected_overdue} for {current_time}, got {result}"


def test_is_appointment_overdue_invalid_duration():
    """Test overdue check with invalid duration."""
    start_time = datetime(2024, 1, 15, 10, 0)
    current_time = datetime(2024, 1, 15, 12, 0)
    
    # Invalid duration should return False (not overdue)
    result = is_appointment_overdue(start_time, "invalid", current_time)
    assert result is False


def test_is_appointment_overdue_default_current_time():
    """Test overdue check with default current time (now)."""
    # Create an appointment that started 2 hours ago with 1 hour duration
    start_time = datetime.now() - timedelta(hours=2)
    duration = "1h"
    
  
    result = is_appointment_overdue(start_time, duration)
    assert result is True
    
   
    future_start = datetime.now() + timedelta(hours=1)
    result = is_appointment_overdue(future_start, duration)
    assert result is False
