"""Tests for appointment model validation."""

import pytest
from datetime import datetime

from src.models.appointment import (
    AppointmentUpdate, 
    AppointmentStatus, 
    validate_status_transition
)


def test_validate_status_transition_new_appointment():
    """Test status validation for new appointments (any status allowed)."""
    # New appointments can have any initial status
    assert validate_status_transition(None, AppointmentStatus.SCHEDULED) is True
    assert validate_status_transition(None, AppointmentStatus.ACTIVE) is True
    assert validate_status_transition(None, AppointmentStatus.ATTENDED) is True
    assert validate_status_transition(None, AppointmentStatus.MISSED) is True
    assert validate_status_transition(None, AppointmentStatus.CANCELLED) is True


def test_validate_status_transition_cancelled_blocked():
    """Test that cancelled appointments cannot be reinstated."""

    assert validate_status_transition(AppointmentStatus.CANCELLED, AppointmentStatus.SCHEDULED) is False
    assert validate_status_transition(AppointmentStatus.CANCELLED, AppointmentStatus.ACTIVE) is False
    assert validate_status_transition(AppointmentStatus.CANCELLED, AppointmentStatus.ATTENDED) is False
    assert validate_status_transition(AppointmentStatus.CANCELLED, AppointmentStatus.MISSED) is False
  
    assert validate_status_transition(AppointmentStatus.CANCELLED, AppointmentStatus.CANCELLED) is True


def test_validate_status_transition_other_statuses_allowed():
    """Test that all other status transitions are allowed."""
    other_statuses = [
        AppointmentStatus.SCHEDULED,
        AppointmentStatus.ACTIVE,
        AppointmentStatus.ATTENDED,
        AppointmentStatus.MISSED
    ]
    
    all_statuses = [
        AppointmentStatus.SCHEDULED,
        AppointmentStatus.ACTIVE,
        AppointmentStatus.ATTENDED,
        AppointmentStatus.MISSED,
        AppointmentStatus.CANCELLED
    ]
    
    # Test all combinations except CANCELLED -> other
    for current in other_statuses:
        for new in all_statuses:
            assert validate_status_transition(current, new) is True


def test_appointment_update_validate_status_transition_success():
    """Test successful status transition validation in AppointmentUpdate."""
    update_data = AppointmentUpdate(
        status=AppointmentStatus.ATTENDED,
        clinician="Dr. Smith"
    )
    
    # Should not raise exception for valid transitions
    update_data.validate_status_transition(AppointmentStatus.SCHEDULED)
    update_data.validate_status_transition(AppointmentStatus.ACTIVE)
    update_data.validate_status_transition(None)  # New appointment


def test_appointment_update_validate_status_transition_blocked():
    """Test blocked status transition validation in AppointmentUpdate."""
    update_data = AppointmentUpdate(
        status=AppointmentStatus.ATTENDED,
        clinician="Dr. Smith"
    )
    

    with pytest.raises(ValueError, match="Invalid status transition from cancelled to attended"):
        update_data.validate_status_transition(AppointmentStatus.CANCELLED)


def test_appointment_update_no_status_change():
    """Test that validation is skipped when status is not being updated."""
    update_data = AppointmentUpdate(
        clinician="Dr. Smith",
        department="cardiology"
    )
    

    update_data.validate_status_transition(AppointmentStatus.CANCELLED)


def test_appointment_update_cancelled_to_cancelled_allowed():
    """Test that cancelled appointments can remain cancelled."""
    update_data = AppointmentUpdate(
        status=AppointmentStatus.CANCELLED,
        clinician="Dr. Smith"
    )
    

    update_data.validate_status_transition(AppointmentStatus.CANCELLED)


def test_appointment_update_multiple_blocked_transitions():
    """Test multiple blocked transitions from cancelled status."""
    blocked_statuses = [
        AppointmentStatus.SCHEDULED,
        AppointmentStatus.ACTIVE,
        AppointmentStatus.ATTENDED,
        AppointmentStatus.MISSED
    ]
    
    for new_status in blocked_statuses:
        update_data = AppointmentUpdate(status=new_status)
        
        with pytest.raises(ValueError, match=f"Invalid status transition from cancelled to {new_status.value}"):
            update_data.validate_status_transition(AppointmentStatus.CANCELLED)
