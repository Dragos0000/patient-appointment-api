from unittest.mock import AsyncMock, MagicMock

from src.adapters.database.patient_adapter import PatientDatabaseAdapter
from src.models.patient import Patient, PatientUpdate


def test_patient_adapter_init(mock_connection):
    """Test patient adapter initialization."""
    adapter = PatientDatabaseAdapter(mock_connection)
    assert adapter.connection == mock_connection


async def test_create_patient(patient_adapter, mock_connection, sample_patient_create, sample_patient_data):
    """Test creating a new patient."""
 
    mock_connection.execute = AsyncMock()
    
    result = await patient_adapter.create_patient(sample_patient_create)
    
    assert isinstance(result, Patient)
    assert result.nhs_number == sample_patient_data["nhs_number"]
    assert result.name == sample_patient_data["name"]
    assert result.date_of_birth == sample_patient_data["date_of_birth"]
    assert result.postcode == sample_patient_data["postcode"]
    
    mock_connection.execute.assert_called_once()


async def test_get_patient_by_nhs_number_found(patient_adapter, mock_connection, sample_patient_data):
    """Test getting patient by NHS number when patient exists."""
 
    mock_row = MagicMock()
    mock_row._asdict.return_value = sample_patient_data
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_connection.execute = AsyncMock(return_value=mock_result)
    
    result = await patient_adapter.get_patient_by_nhs_number("1234567890")
    
 
    assert isinstance(result, Patient)
    assert result.nhs_number == sample_patient_data["nhs_number"]
    assert result.name == sample_patient_data["name"]
    mock_connection.execute.assert_called_once()


async def test_get_patient_by_nhs_number_not_found(patient_adapter, mock_connection):
    """Test getting patient by NHS number when patient doesn't exist."""

    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_connection.execute = AsyncMock(return_value=mock_result)

    result = await patient_adapter.get_patient_by_nhs_number("9999999999")

    assert result is None
    mock_connection.execute.assert_called_once()


async def test_get_all_patients(patient_adapter, mock_connection, sample_patient_data):
    """Test getting all patients."""

    mock_row1 = MagicMock()
    mock_row1._asdict.return_value = sample_patient_data
    mock_row2 = MagicMock()
    mock_row2._asdict.return_value = {
        **sample_patient_data,
        "nhs_number": "0987654321",
        "name": "Jane Smith"
    }
    
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [mock_row1, mock_row2]
    mock_connection.execute = AsyncMock(return_value=mock_result)

    result = await patient_adapter.get_all_patients()
    
    assert len(result) == 2
    assert all(isinstance(patient, Patient) for patient in result)
    assert result[0].nhs_number == "1234567890"
    assert result[1].nhs_number == "0987654321"
    mock_connection.execute.assert_called_once()


async def test_get_all_patients_empty(patient_adapter, mock_connection):
    """Test getting all patients when no patients exist."""

    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    mock_connection.execute = AsyncMock(return_value=mock_result)

    result = await patient_adapter.get_all_patients()
    
    assert result == []
    mock_connection.execute.assert_called_once()


async def test_update_patient_success(patient_adapter, mock_connection, sample_patient_data):
    """Test updating patient successfully."""

    mock_update_result = MagicMock()
    mock_update_result.rowcount = 1
    
    mock_row = MagicMock()
    updated_data = {**sample_patient_data, "name": "John Updated"}
    mock_row._asdict.return_value = updated_data
    mock_get_result = MagicMock()
    mock_get_result.fetchone.return_value = mock_row
    
    mock_connection.execute = AsyncMock(side_effect=[mock_update_result, mock_get_result])
    
    update_data = PatientUpdate(name="John Updated")
    result = await patient_adapter.update_patient("1234567890", update_data)
    
    assert isinstance(result, Patient)
    assert result.name == "John Updated"
    assert mock_connection.execute.call_count == 2


async def test_update_patient_not_found(patient_adapter, mock_connection):
    """Test updating patient that doesn't exist."""

    mock_result = MagicMock()
    mock_result.rowcount = 0
    mock_connection.execute = AsyncMock(return_value=mock_result)
    
    update_data = PatientUpdate(name="John Updated")
    result = await patient_adapter.update_patient("9999999999", update_data)
    
    assert result is None
    mock_connection.execute.assert_called_once()


async def test_update_patient_no_changes(patient_adapter, mock_connection, sample_patient_data):
    """Test updating patient with no actual changes."""

    mock_row = MagicMock()
    mock_row._asdict.return_value = sample_patient_data
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_connection.execute = AsyncMock(return_value=mock_result)
    
    update_data = PatientUpdate()  # No fields set
    result = await patient_adapter.update_patient("1234567890", update_data)
    
    assert isinstance(result, Patient)
    assert result.nhs_number == sample_patient_data["nhs_number"]
    mock_connection.execute.assert_called_once()


async def test_delete_patient_success(patient_adapter, mock_connection):
    """Test deleting patient successfully."""

    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_connection.execute = AsyncMock(return_value=mock_result)
    
    result = await patient_adapter.delete_patient("1234567890")
    
    assert result is True
    mock_connection.execute.assert_called_once()


async def test_delete_patient_not_found(patient_adapter, mock_connection):
    """Test deleting patient that doesn't exist."""

    mock_result = MagicMock()
    mock_result.rowcount = 0
    mock_connection.execute = AsyncMock(return_value=mock_result)
    
    result = await patient_adapter.delete_patient("9999999999")
    
    assert result is False
    mock_connection.execute.assert_called_once()


async def test_patient_exists_true(patient_adapter, mock_connection):
    """Test patient exists when patient is found."""

    mock_row = MagicMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_connection.execute = AsyncMock(return_value=mock_result)
    
    result = await patient_adapter.patient_exists("1234567890")
    
    assert result is True
    mock_connection.execute.assert_called_once()


async def test_patient_exists_false(patient_adapter, mock_connection):
    """Test patient exists when patient is not found."""

    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_connection.execute = AsyncMock(return_value=mock_result)
    
    result = await patient_adapter.patient_exists("9999999999")
    
    assert result is False
    mock_connection.execute.assert_called_once()
