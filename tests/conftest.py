import pytest
from sqlalchemy import create_engine

from src.adapters.database.tables import patients_table, appointments_table


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
