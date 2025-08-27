from sqlalchemy import Table, Column, String, DateTime, Date, Enum
from uuid import uuid4

from src.adapters.database.connection import metadata
from src.models.appointment import AppointmentStatus


# Patients table
patients_table = Table(
    "patients",
    metadata,
    Column("nhs_number", String(10), primary_key=True),  # 10 digit NHS number as primary key
    Column("name", String(255), nullable=False),
    Column("date_of_birth", Date, nullable=False),
    Column("postcode", String(10), nullable=False),  # UK postcode format
)

# Appointments table
appointments_table = Table(
    "appointments",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid4())),
    Column("patient", String(10), nullable=False),  # Patient NHS number
    Column("status", Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.SCHEDULED),
    Column("time", DateTime, nullable=False),  # Appointment date and time
    Column("duration", String(20), nullable=False),  # Duration as string (e.g., "1h", "30m")
    Column("clinician", String(255), nullable=False),  # Clinician name
    Column("department", String(100), nullable=False),  # Department name
    Column("postcode", String(10), nullable=False),  # UK postcode format
)
