from sqlalchemy import MetaData
from sqlalchemy.schema import CreateTable

from src.adapters.database.tables import patients_table, appointments_table
from src.models.appointment import AppointmentStatus


def test_patient_table_name():
    """Test patient table has correct name."""
    assert patients_table.name == "patients"


def test_patient_table_columns(expected_patient_columns):
    """Test patient table has correct columns."""
    column_names = [col.name for col in patients_table.columns]
    assert set(column_names) == set(expected_patient_columns)


def test_patient_primary_key():
    """Test NHS number is the primary key."""
    primary_keys = [col.name for col in patients_table.primary_key]
    assert primary_keys == ["nhs_number"]


def test_patient_column_types(patient_columns):
    """Test patient column types are correct."""
    # NHS number column
    assert str(patient_columns["nhs_number"].type) == "VARCHAR(10)"
    assert patient_columns["nhs_number"].primary_key is True
    
    # Name column
    assert str(patient_columns["name"].type) == "VARCHAR(255)"
    assert patient_columns["name"].nullable is False
    
    # Date of birth column
    assert str(patient_columns["date_of_birth"].type) == "DATE"
    assert patient_columns["date_of_birth"].nullable is False
    
    # Postcode column
    assert str(patient_columns["postcode"].type) == "VARCHAR(10)"
    assert patient_columns["postcode"].nullable is False


def test_appointment_table_name():
    """Test appointment table has correct name."""
    assert appointments_table.name == "appointments"


def test_appointment_table_columns(expected_appointment_columns):
    """Test appointment table has correct columns."""
    column_names = [col.name for col in appointments_table.columns]
    assert set(column_names) == set(expected_appointment_columns)


def test_appointment_primary_key():
    """Test ID is the primary key."""
    primary_keys = [col.name for col in appointments_table.primary_key]
    assert primary_keys == ["id"]


def test_appointment_column_types(appointment_columns):
    """Test appointment column types are correct."""
    # ID column
    assert str(appointment_columns["id"].type) == "VARCHAR(36)"
    assert appointment_columns["id"].primary_key is True
    
    # Patient column (NHS number reference)
    assert str(appointment_columns["patient"].type) == "VARCHAR(10)"
    assert appointment_columns["patient"].nullable is False
    
    # Status column (enum)
    assert "ENUM" in str(appointment_columns["status"].type) or "VARCHAR" in str(appointment_columns["status"].type)
    assert appointment_columns["status"].nullable is False
    
    # Time column
    assert str(appointment_columns["time"].type) == "DATETIME"
    assert appointment_columns["time"].nullable is False
    
    # Duration column
    assert str(appointment_columns["duration"].type) == "VARCHAR(20)"
    assert appointment_columns["duration"].nullable is False
    
    # Clinician column
    assert str(appointment_columns["clinician"].type) == "VARCHAR(255)"
    assert appointment_columns["clinician"].nullable is False
    
    # Department column
    assert str(appointment_columns["department"].type) == "VARCHAR(100)"
    assert appointment_columns["department"].nullable is False
    
    # Postcode column
    assert str(appointment_columns["postcode"].type) == "VARCHAR(10)"
    assert appointment_columns["postcode"].nullable is False


def test_appointment_status_enum(expected_appointment_statuses):
    """Test appointment status enum values."""
    actual_statuses = {status.value for status in AppointmentStatus}
    assert actual_statuses == expected_appointment_statuses


def test_create_tables_sql_generation(test_engine):
    """Test that CREATE TABLE SQL can be generated."""
    # Test patient table SQL generation
    patient_sql = str(CreateTable(patients_table).compile(test_engine))
    assert "CREATE TABLE patients" in patient_sql
    assert "nhs_number" in patient_sql
    assert "PRIMARY KEY" in patient_sql
    
    # Test appointment table SQL generation
    appointment_sql = str(CreateTable(appointments_table).compile(test_engine))
    assert "CREATE TABLE appointments" in appointment_sql
    assert "id" in appointment_sql
    assert "patient" in appointment_sql
    assert "PRIMARY KEY" in appointment_sql


def test_tables_can_be_created(test_engine):
    """Test that tables can actually be created in database."""
    metadata = MetaData()
    
    # Add tables to metadata
    patients_table_copy = patients_table.tometadata(metadata)
    appointments_table_copy = appointments_table.tometadata(metadata)
    
    # Create all tables - should not raise exception
    metadata.create_all(test_engine)
    
    # Verify tables exist
    inspector = test_engine.dialect.get_table_names(test_engine.connect())
    assert "patients" in inspector
    assert "appointments" in inspector


def test_patient_appointment_relationship():
    """Test that appointments reference patients correctly."""
    # Both tables should have compatible patient reference columns
    patient_nhs_col = patients_table.c.nhs_number
    appointment_patient_col = appointments_table.c.patient
    
    # Both should be string types with same length
    assert str(patient_nhs_col.type) == str(appointment_patient_col.type)
    assert str(patient_nhs_col.type) == "VARCHAR(10)"
