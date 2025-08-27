from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import uuid

from src.adapters.database.appointment_adapter import AppointmentDatabaseAdapter
from src.models.appointment import Appointment, AppointmentUpdate, AppointmentStatus


def test_appointment_adapter_init(mock_connection):
    """Test appointment adapter initialization."""
    adapter = AppointmentDatabaseAdapter(mock_connection)
    assert adapter.connection == mock_connection


@patch('uuid.uuid4')
async def test_create_appointment(mock_uuid, appointment_adapter, mock_connection, sample_appointment_create, sample_appointment_create_data):
    """Test creating a new appointment."""

    mock_uuid.return_value = "generated-uuid"
    mock_connection.execute = AsyncMock()
    

    result = await appointment_adapter.create_appointment(sample_appointment_create)
    

    assert isinstance(result, Appointment)
    assert result.id == "generated-uuid"
    assert result.patient == sample_appointment_create_data["patient"]
    assert result.status == sample_appointment_create_data["status"]
    assert result.time == sample_appointment_create_data["time"]
    assert result.duration == sample_appointment_create_data["duration"]
    assert result.clinician == sample_appointment_create_data["clinician"]
    assert result.department == sample_appointment_create_data["department"]
    assert result.postcode == sample_appointment_create_data["postcode"]
    

    mock_connection.execute.assert_called_once()


async def test_get_appointment_by_id_found(appointment_adapter, mock_connection, sample_appointment_data):
    """Test getting appointment by ID when appointment exists."""

    mock_row = MagicMock()
    mock_row._asdict.return_value = sample_appointment_data
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_connection.execute = AsyncMock(return_value=mock_result)
    

    result = await appointment_adapter.get_appointment_by_id("test-appointment-id")
    

    assert isinstance(result, Appointment)
    assert result.id == sample_appointment_data["id"]
    assert result.patient == sample_appointment_data["patient"]
    mock_connection.execute.assert_called_once()


async def test_get_appointment_by_id_not_found(appointment_adapter, mock_connection):
    """Test getting appointment by ID when appointment doesn't exist."""

    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_connection.execute = AsyncMock(return_value=mock_result)
    

    result = await appointment_adapter.get_appointment_by_id("nonexistent-id")
    

    assert result is None
    mock_connection.execute.assert_called_once()


async def test_get_appointments_by_patient(appointment_adapter, mock_connection, sample_appointment_data):
    """Test getting appointments by patient NHS number."""

    mock_row1 = MagicMock()
    mock_row1._asdict.return_value = sample_appointment_data
    mock_row2 = MagicMock()
    mock_row2._asdict.return_value = {
        **sample_appointment_data,
        "id": "second-appointment-id",
        "time": datetime(2024, 6, 16, 10, 0)
    }
    
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [mock_row1, mock_row2]
    mock_connection.execute = AsyncMock(return_value=mock_result)
    

    result = await appointment_adapter.get_appointments_by_patient("1234567890")
    

    assert len(result) == 2
    assert all(isinstance(appointment, Appointment) for appointment in result)
    assert result[0].id == "test-appointment-id"
    assert result[1].id == "second-appointment-id"
    mock_connection.execute.assert_called_once()


async def test_get_appointments_by_patient_empty(appointment_adapter, mock_connection):
    """Test getting appointments by patient when no appointments exist."""

    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    mock_connection.execute = AsyncMock(return_value=mock_result)
    

    result = await appointment_adapter.get_appointments_by_patient("9999999999")
    

    assert result == []
    mock_connection.execute.assert_called_once()


async def test_get_appointments_by_status(appointment_adapter, mock_connection, sample_appointment_data):
    """Test getting appointments by status."""

    mock_row = MagicMock()
    mock_row._asdict.return_value = sample_appointment_data
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [mock_row]
    mock_connection.execute = AsyncMock(return_value=mock_result)
    

    result = await appointment_adapter.get_appointments_by_status(AppointmentStatus.SCHEDULED)
    

    assert len(result) == 1
    assert isinstance(result[0], Appointment)
    assert result[0].status == AppointmentStatus.SCHEDULED
    mock_connection.execute.assert_called_once()


async def test_get_all_appointments(appointment_adapter, mock_connection, sample_appointment_data):
    """Test getting all appointments."""

    mock_row = MagicMock()
    mock_row._asdict.return_value = sample_appointment_data
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [mock_row]
    mock_connection.execute = AsyncMock(return_value=mock_result)
    

    result = await appointment_adapter.get_all_appointments()
    

    assert len(result) == 1
    assert isinstance(result[0], Appointment)
    mock_connection.execute.assert_called_once()


async def test_update_appointment_success(appointment_adapter, mock_connection, sample_appointment_data):
    """Test updating appointment successfully."""

    mock_update_result = MagicMock()
    mock_update_result.rowcount = 1
    

    mock_row = MagicMock()
    updated_data = {**sample_appointment_data, "clinician": "Dr. Updated"}
    mock_row._asdict.return_value = updated_data
    mock_get_result = MagicMock()
    mock_get_result.fetchone.return_value = mock_row
    
    mock_connection.execute = AsyncMock(side_effect=[mock_update_result, mock_get_result])
    

    update_data = AppointmentUpdate(clinician="Dr. Updated")
    result = await appointment_adapter.update_appointment("test-appointment-id", update_data)
    

    assert isinstance(result, Appointment)
    assert result.clinician == "Dr. Updated"
    assert mock_connection.execute.call_count == 2


async def test_update_appointment_not_found(appointment_adapter, mock_connection):
    """Test updating appointment that doesn't exist."""

    mock_result = MagicMock()
    mock_result.rowcount = 0
    mock_connection.execute = AsyncMock(return_value=mock_result)
    

    update_data = AppointmentUpdate(clinician="Dr. Updated")
    result = await appointment_adapter.update_appointment("nonexistent-id", update_data)
    

    assert result is None
    mock_connection.execute.assert_called_once()


async def test_update_appointment_no_changes(appointment_adapter, mock_connection, sample_appointment_data):
    """Test updating appointment with no actual changes."""

    mock_row = MagicMock()
    mock_row._asdict.return_value = sample_appointment_data
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_connection.execute = AsyncMock(return_value=mock_result)
    

    update_data = AppointmentUpdate()  # No fields set
    result = await appointment_adapter.update_appointment("test-appointment-id", update_data)
    

    assert isinstance(result, Appointment)
    assert result.id == sample_appointment_data["id"]

    mock_connection.execute.assert_called_once()


async def test_update_appointment_status_success(appointment_adapter, mock_connection, sample_appointment_data):
    """Test updating appointment status successfully."""

    mock_update_result = MagicMock()
    mock_update_result.rowcount = 1
    

    mock_row = MagicMock()
    updated_data = {**sample_appointment_data, "status": AppointmentStatus.ATTENDED}
    mock_row._asdict.return_value = updated_data
    mock_get_result = MagicMock()
    mock_get_result.fetchone.return_value = mock_row
    
    mock_connection.execute = AsyncMock(side_effect=[mock_update_result, mock_get_result])
    

    result = await appointment_adapter.update_appointment_status("test-appointment-id", AppointmentStatus.ATTENDED)
    

    assert isinstance(result, Appointment)
    assert result.status == AppointmentStatus.ATTENDED
    assert mock_connection.execute.call_count == 2


async def test_update_appointment_status_not_found(appointment_adapter, mock_connection):
    """Test updating appointment status when appointment doesn't exist."""

    mock_result = MagicMock()
    mock_result.rowcount = 0
    mock_connection.execute = AsyncMock(return_value=mock_result)
    

    result = await appointment_adapter.update_appointment_status("nonexistent-id", AppointmentStatus.ATTENDED)
    

    assert result is None
    mock_connection.execute.assert_called_once()


async def test_delete_appointment_success(appointment_adapter, mock_connection):
    """Test deleting appointment successfully."""

    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_connection.execute = AsyncMock(return_value=mock_result)
    

    result = await appointment_adapter.delete_appointment("test-appointment-id")
    

    assert result is True
    mock_connection.execute.assert_called_once()


async def test_delete_appointment_not_found(appointment_adapter, mock_connection):
    """Test deleting appointment that doesn't exist."""

    mock_result = MagicMock()
    mock_result.rowcount = 0
    mock_connection.execute = AsyncMock(return_value=mock_result)
    

    result = await appointment_adapter.delete_appointment("nonexistent-id")
    

    assert result is False
    mock_connection.execute.assert_called_once()


async def test_appointment_exists_true(appointment_adapter, mock_connection):
    """Test appointment exists when appointment is found."""

    mock_row = MagicMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_connection.execute = AsyncMock(return_value=mock_result)
    

    result = await appointment_adapter.appointment_exists("test-appointment-id")
    

    assert result is True
    mock_connection.execute.assert_called_once()


async def test_appointment_exists_false(appointment_adapter, mock_connection):
    """Test appointment exists when appointment is not found."""

    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_connection.execute = AsyncMock(return_value=mock_result)
    
    
    result = await appointment_adapter.appointment_exists("nonexistent-id")
    

    assert result is False
    mock_connection.execute.assert_called_once()
