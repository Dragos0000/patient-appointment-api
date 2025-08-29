from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from src.services.appointment_service import AppointmentBusinessService
from src.models.appointment import Appointment, AppointmentCreate, AppointmentUpdate, AppointmentStatus


def test_appointment_service_init(mock_connection):
    """Test appointment service initialization."""
    service = AppointmentBusinessService(mock_connection)
    assert service.adapter is not None


async def test_create_appointment(appointment_service, sample_appointment):
    """Test creating an appointment."""
    appointment_data = AppointmentCreate(
        patient="9434765919",
        status=AppointmentStatus.SCHEDULED,
        time=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),
        duration="1h",
        clinician="Dr. Smith",
        department="cardiology",
        postcode="SW1A 1AA"
    )
    
    appointment_service.adapter.create_appointment = AsyncMock(return_value=sample_appointment)
    
    result = await appointment_service.create_appointment(appointment_data)
    
    assert result == sample_appointment
    appointment_service.adapter.create_appointment.assert_called_once_with(appointment_data)


async def test_update_appointment_status_success(appointment_service, sample_appointment):
    """Test updating appointment status successfully."""
    appointment_service.adapter.get_appointment_by_id = AsyncMock(return_value=sample_appointment)
    updated_appointment = Appointment(**sample_appointment.model_dump())
    updated_appointment.status = AppointmentStatus.ATTENDED
    appointment_service.adapter.update_appointment_status = AsyncMock(return_value=updated_appointment)
    
    result = await appointment_service.update_appointment_status("test-id", AppointmentStatus.ATTENDED)
    
    assert result.status == AppointmentStatus.ATTENDED
    appointment_service.adapter.get_appointment_by_id.assert_called_once_with("test-id")
    appointment_service.adapter.update_appointment_status.assert_called_once_with("test-id", AppointmentStatus.ATTENDED)


async def test_update_appointment_status_not_found(appointment_service):
    """Test updating status of non-existent appointment."""
    appointment_service.adapter.get_appointment_by_id = AsyncMock(return_value=None)
    
    result = await appointment_service.update_appointment_status("non-existent", AppointmentStatus.ATTENDED)
    
    assert result is None
    appointment_service.adapter.get_appointment_by_id.assert_called_once_with("non-existent")


async def test_update_appointment_status_cancelled_cannot_reinstate(appointment_service, cancelled_appointment):
    """Test business rule: cancelled appointments cannot be reinstated."""
    appointment_service.adapter.get_appointment_by_id = AsyncMock(return_value=cancelled_appointment)
    

    with pytest.raises(ValueError, match="Cancelled appointments cannot be reinstated"):
        await appointment_service.update_appointment_status("cancelled-id", AppointmentStatus.SCHEDULED)
    

    with pytest.raises(ValueError, match="Cancelled appointments cannot be reinstated"):
        await appointment_service.update_appointment_status("cancelled-id", AppointmentStatus.ATTENDED)
    



async def test_update_appointment_status_cancelled_to_cancelled_allowed(appointment_service, cancelled_appointment):
    """Test that cancelled appointments can remain cancelled."""
    appointment_service.adapter.get_appointment_by_id = AsyncMock(return_value=cancelled_appointment)
    appointment_service.adapter.update_appointment_status = AsyncMock(return_value=cancelled_appointment)
    
    result = await appointment_service.update_appointment_status("cancelled-id", AppointmentStatus.CANCELLED)
    
    assert result == cancelled_appointment
    appointment_service.adapter.update_appointment_status.assert_called_once_with("cancelled-id", AppointmentStatus.CANCELLED)


async def test_cancel_appointment(appointment_service, sample_appointment):
    """Test cancelling an appointment."""
    cancelled = Appointment(**sample_appointment.model_dump())
    cancelled.status = AppointmentStatus.CANCELLED
    
    appointment_service.adapter.get_appointment_by_id = AsyncMock(return_value=sample_appointment)
    appointment_service.adapter.update_appointment_status = AsyncMock(return_value=cancelled)
    
    result = await appointment_service.cancel_appointment("test-id")
    
    assert result.status == AppointmentStatus.CANCELLED
    appointment_service.adapter.update_appointment_status.assert_called_once_with("test-id", AppointmentStatus.CANCELLED)


async def test_mark_appointment_attended(appointment_service, sample_appointment):
    """Test marking appointment as attended."""
    attended = Appointment(**sample_appointment.model_dump())
    attended.status = AppointmentStatus.ATTENDED
    
    appointment_service.adapter.get_appointment_by_id = AsyncMock(return_value=sample_appointment)
    appointment_service.adapter.update_appointment_status = AsyncMock(return_value=attended)
    
    result = await appointment_service.mark_appointment_attended("test-id")
    
    assert result.status == AppointmentStatus.ATTENDED
    appointment_service.adapter.update_appointment_status.assert_called_once_with("test-id", AppointmentStatus.ATTENDED)


@patch('src.services.appointment_service.is_appointment_overdue')
async def test_mark_overdue_appointments_as_missed(mock_is_overdue, appointment_service):
    """Test marking overdue appointments as missed."""
    current_time = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)  # Noon
    
    # Create test appointments
    overdue_appointment = Appointment(
        id="overdue-id",
        patient="9434765919",
        status=AppointmentStatus.SCHEDULED,
        time=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc),  # 10 AM
        duration="1h",
        clinician="Dr. Smith",
        department="cardiology",
        postcode="SW1A 1AA"
    )
    
    not_overdue_appointment = Appointment(
        id="not-overdue-id",
        patient="9434765919",
        status=AppointmentStatus.SCHEDULED,
        time=datetime(2024, 1, 15, 13, 0, tzinfo=timezone.utc),  # 1 PM (future)
        duration="1h",
        clinician="Dr. Smith",
        department="cardiology",
        postcode="SW1A 1AA"
    )
    

    appointment_service.adapter.get_appointments_by_status = AsyncMock()
    appointment_service.adapter.get_appointments_by_status.side_effect = [
        [overdue_appointment, not_overdue_appointment],  
        []  
    ]
    

    def mock_overdue_check(start_time, duration, current):
        return start_time == datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
    
    mock_is_overdue.side_effect = mock_overdue_check
    

    missed_appointment = Appointment(**overdue_appointment.model_dump())
    missed_appointment.status = AppointmentStatus.MISSED
    appointment_service.adapter.update_appointment_status = AsyncMock(return_value=missed_appointment)
    
    result = await appointment_service.mark_overdue_appointments_as_missed(current_time)
    
    assert len(result) == 1
    assert result[0].status == AppointmentStatus.MISSED
    assert result[0].id == "overdue-id"
    

    assert appointment_service.adapter.get_appointments_by_status.call_count == 2
    appointment_service.adapter.update_appointment_status.assert_called_once_with("overdue-id", AppointmentStatus.MISSED)


async def test_update_appointment_with_status_change(appointment_service, sample_appointment):
    """Test updating appointment with status change."""
    update_data = AppointmentUpdate(
        status=AppointmentStatus.ATTENDED,
        clinician="Dr. Jones"
    )
    
    updated_appointment = Appointment(**sample_appointment.model_dump())
    updated_appointment.status = AppointmentStatus.ATTENDED
    updated_appointment.clinician = "Dr. Jones"
    

    appointment_service.adapter.get_appointment_by_id = AsyncMock(return_value=sample_appointment)
    appointment_service.adapter.update_appointment_status = AsyncMock(return_value=updated_appointment)
    appointment_service.adapter.update_appointment = AsyncMock(return_value=updated_appointment)
    
    result = await appointment_service.update_appointment("test-id", update_data)
    
    assert result.status == AppointmentStatus.ATTENDED
    assert result.clinician == "Dr. Jones"


async def test_update_appointment_cancelled_status_blocked(appointment_service, cancelled_appointment):
    """Test that updating cancelled appointment with status change is blocked."""
    update_data = AppointmentUpdate(
        status=AppointmentStatus.ATTENDED,
        clinician="Dr. Jones"
    )
    
    appointment_service.adapter.get_appointment_by_id = AsyncMock(return_value=cancelled_appointment)
    
    with pytest.raises(ValueError, match="Invalid status transition from cancelled to attended"):
        await appointment_service.update_appointment("cancelled-id", update_data)
