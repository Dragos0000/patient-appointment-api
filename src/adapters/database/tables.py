import os
from sqlalchemy import Table, Column, String, DateTime, Date, Enum
from uuid import uuid4
from dotenv import load_dotenv

from src.adapters.database.connection import metadata
from src.models.appointment import AppointmentStatus

# Load environment variables
load_dotenv()

# Get table names from environment variables
PATIENTS_TABLE_NAME = os.getenv("PATIENTS_TABLE_NAME", "patients")
APPOINTMENTS_TABLE_NAME = os.getenv("APPOINTMENTS_TABLE_NAME", "appointments")


# Patients table
patients_table = Table(
    PATIENTS_TABLE_NAME,
    metadata,
    Column("nhs_number", String(10), primary_key=True),  # 10 digit NHS number as primary key
    Column("name", String(255), nullable=False),
    Column("date_of_birth", Date, nullable=False),
    Column("postcode", String(10), nullable=False),  # UK postcode format
)

# Appointments table
appointments_table = Table(
    APPOINTMENTS_TABLE_NAME,
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid4())),
    Column("patient", String(10), nullable=False),  # Patient NHS number
    Column("status", Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.SCHEDULED),
    Column("time", DateTime(timezone=True), nullable=False),  # Timezone-aware appointment date and time
    Column("duration", String(20), nullable=False),  # Duration as string (e.g., "1h", "30m")
    Column("clinician", String(255), nullable=False),  # Clinician name
    Column("department", String(100), nullable=False),  # Department name
    Column("postcode", String(10), nullable=False),  # UK postcode format
)
