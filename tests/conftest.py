import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date, datetime
from sqlalchemy import create_engine

from src.adapters.database.tables import patients_table, appointments_table
from src.adapters.database.patient_adapter import PatientDatabaseAdapter
from src.adapters.database.appointment_adapter import AppointmentDatabaseAdapter
from src.services.appointment_service import AppointmentBusinessService
from src.models.patient import Patient, PatientCreate, PatientUpdate
from src.models.appointment import Appointment, AppointmentCreate, AppointmentUpdate, AppointmentStatus


@pytest.fixture
def test_engine():
    """Create in-memory SQLite engine for testing."""
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def patient_columns():
    """Get patient table columns as dictionary."""
    return {col.name: col for col in patients_table.columns}


@pytest.fixture
def appointment_columns():
    """Get appointment table columns as dictionary."""
    return {col.name: col for col in appointments_table.columns}


@pytest.fixture
def expected_patient_columns():
    """Expected patient table column names."""
    return ["nhs_number", "name", "date_of_birth", "postcode"]


@pytest.fixture
def expected_appointment_columns():
    """Expected appointment table column names."""
    return ["id", "patient", "status", "time", "duration", "clinician", "department", "postcode"]


@pytest.fixture
def expected_appointment_statuses():
    """Expected appointment status values."""
    return {"scheduled", "attended", "active", "missed", "cancelled"}


# Adapter test fixtures
@pytest.fixture
def mock_connection():
    """Mock async database connection."""
    return AsyncMock()


@pytest.fixture
def patient_adapter(mock_connection):
    """Create patient adapter with mock connection."""
    return PatientDatabaseAdapter(mock_connection)


@pytest.fixture
def appointment_adapter(mock_connection):
    """Create appointment adapter with mock connection."""
    return AppointmentDatabaseAdapter(mock_connection)


@pytest.fixture
def appointment_service(mock_connection):
    """Create appointment business service with mock connection."""
    return AppointmentBusinessService(mock_connection)


# Patient test data fixtures
@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing."""
    return {
        "nhs_number": "9434765919",  # Valid NHS number with correct checksum
        "name": "John Doe",
        "date_of_birth": date(1990, 1, 15),
        "postcode": "SW1A 1AA"
    }


@pytest.fixture
def sample_patient_create(sample_patient_data):
    """Sample PatientCreate model."""
    return PatientCreate(**sample_patient_data)


@pytest.fixture
def sample_patient(sample_patient_data):
    """Sample Patient model."""
    return Patient(**sample_patient_data)


# Appointment test data fixtures
@pytest.fixture
def sample_appointment_data():
    """Sample appointment data for testing."""
    return {
        "id": "test-appointment-id",
        "patient": "1234567890",
        "status": AppointmentStatus.SCHEDULED,
        "time": datetime(2024, 6, 15, 14, 30),
        "duration": "1h",
        "clinician": "Dr. Smith",
        "department": "cardiology",
        "postcode": "SW1A 1AA"
    }


@pytest.fixture
def sample_appointment_create_data():
    """Sample appointment create data (without id)."""
    return {
        "patient": "1234567890",
        "status": AppointmentStatus.SCHEDULED,
        "time": datetime(2024, 6, 15, 14, 30),
        "duration": "1h",
        "clinician": "Dr. Smith",
        "department": "cardiology",
        "postcode": "SW1A 1AA"
    }


@pytest.fixture
def sample_appointment_create(sample_appointment_create_data):
    """Sample AppointmentCreate model."""
    return AppointmentCreate(**sample_appointment_create_data)


# Business service test fixtures
@pytest.fixture
def sample_appointment():
    """Sample appointment for testing."""
    return Appointment(
        id="test-appointment-id",
        patient="9434765919",
        status=AppointmentStatus.SCHEDULED,
        time=datetime(2024, 1, 15, 10, 0),
        duration="1h",
        clinician="Dr. Smith",
        department="cardiology",
        postcode="SW1A 1AA"
    )


@pytest.fixture
def cancelled_appointment():
    """Sample cancelled appointment for testing."""
    return Appointment(
        id="cancelled-appointment-id",
        patient="9434765919",
        status=AppointmentStatus.CANCELLED,
        time=datetime(2024, 1, 15, 10, 0),
        duration="1h",
        clinician="Dr. Smith",
        department="cardiology",
        postcode="SW1A 1AA"
    )
