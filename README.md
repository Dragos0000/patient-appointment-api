# Patient Appointment API

A FastAPI-based API for managing patients and appointments with timezone-aware datetime handling and automatic background processing.

## Environment Variables

The following environment variables can be configured via a `.env` file in the project root:

### Database Configuration
- `DATABASE_URL` - Database connection string (default: `sqlite+aiosqlite:///./patient_appointments.db`)
- `DB_ECHO` - Enable SQLAlchemy query logging (default: `false`)
- `PATIENTS_TABLE_NAME` - Name for the patients table (default: `patients`)
- `APPOINTMENTS_TABLE_NAME` - Name for the appointments table (default: `appointments`)

### Background Task Configuration
- `BACKGROUND_TASK_INTERVAL` - How often to check for overdue appointments in seconds (default: `300`)
  - `60` = 1 minute
  - `300` = 5 minutes (default)
  - `900` = 15 minutes
  - `1800` = 30 minutes

## Features

- ✅ **Timezone-aware datetime handling** - All timestamps include timezone information
- ✅ **Automatic overdue appointment processing** - Background tasks mark overdue appointments as missed
- ✅ **NHS number validation** - Modulus 11 checksum validation
- ✅ **UK postcode formatting** - Automatic postcode validation and formatting
- ✅ **Business rule enforcement** - Cancelled appointments cannot be reinstated
- ✅ **CRUD API** - Full CRUD operations for patients and appointments

## Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Modify the `.env` file with your desired configuration

3. Install dependencies and run the API:
   ```bash
   make install-dependencies
   make run-api
   ```

## Demo Database

This repository includes a demo SQLite database (`patient_appointments.db`) with sample data for testing and demonstration purposes:

- **2 demo patients** with valid NHS numbers and UK postcodes
- **Sample appointments** showing different statuses and timezone handling
- **Clean test data** - no sensitive information

### Important Notes:
- This is a **demo/test database only**
- Contains **no real patient data**

