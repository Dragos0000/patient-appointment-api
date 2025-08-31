# Patient Appointment API

A FastAPI-based API for managing patients and appointments.

**Test Report:** [https://dragos0000.github.io/patient-appointment-api/](https://dragos0000.github.io/patient-appointment-api/)

## Getting Started

### Running Without Docker (Local Development)

1. **Install dependencies:**
   ```bash
   make install-dependencies
   ```

2. **Start the API:**
   ```bash
   make run-api
   ```

The API will be available at `http://localhost:8000` using SQLite database.

### Running With Docker 

1. **Create environment file (optional):**
   ```bash
   cp env.example .env
   # Edit .env with your preferred values
   ```

2. **Start services:**
   ```bash
   make start-services
   ```

3. **Migrate existing data (optional):**
   ```bash
   # If you have existing SQLite data to migrate
   make migrate-sqlite-to-postgres
   ```

The API will be available at `http://localhost:8000` (or your configured `API_PORT`) using PostgreSQL database.

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

### API Configuration
- `API_HOST` - Host and port for API server (default: `0.0.0.0:8000`)

### Docker Configuration extra variables
- `POSTGRES_DB` - PostgreSQL database name 
- `POSTGRES_USER` - PostgreSQL username 
- `POSTGRES_PASSWORD` - PostgreSQL password 
- `POSTGRES_PORT` - PostgreSQL host port mapping 
- `API_PORT` - API host port mapping 
- `POSTGRES_HOST` - Postgres host (default is localhost) and it is used only for the migration script of the test database 

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Patients
- `GET /patients` - List all patients
- `POST /patients` - Create a new patient
- `GET /patients/{nhs_number}` - Get patient by NHS number
- `PUT /patients/{nhs_number}` - Update patient
- `DELETE /patients/{nhs_number}` - Delete patient
- `GET /patients/{nhs_number}/appointments` - Get all appointments for a patient

### Appointments
- `GET /appointments` - List all appointments
- `POST /appointments` - Create a new appointment
- `GET /appointments/{id}` - Get appointment by ID
- `PUT /appointments/{id}` - Update appointment
- `DELETE /appointments/{id}` - Delete appointment
- `PUT /appointments/{id}/cancel` - Cancel appointment
- `PUT /appointments/{id}/attend` - Mark appointment as attended
- `POST /appointments/mark-overdue-as-missed` - Process overdue appointments

## Features

- **Timezone-aware datetime handling** - All timestamps include timezone information
- **Automatic overdue appointment processing** - Background tasks mark overdue appointments as missed
- **NHS number validation** - Modulus 11 checksum validation
- **UK postcode formatting** - Automatic postcode validation and formatting
- **Business rule enforcement** - Cancelled appointments cannot be reinstated
- **CRUD API** - Full CRUD operations for patients and appointments
- **Appointment filtering** - Filter appointments by patient, status, department, or clinician
- **Pagination support** - Configurable pagination for large datasets
- **Patient appointment history** - View all appointments for a specific patient
- **Status management** - Track appointment status with flexible transitions 
- **Background service** - Automatic startup of background tasks
- **Validation** - Input validation for all API endpoints
- **Error handling** - Structured error responses with detailed messages
- **Database agnostic** - Works with any SQLAlchemy-supported relational database

### Background Tasks in Action

The API automatically processes overdue appointments every 5 minutes (configurable via `BACKGROUND_TASK_INTERVAL`). Here's an example of the background service working:

```
INFO:src.services.background_tasks:Background task service started (checking every 300 seconds)
INFO:src.entrypoints.main:Background task service started successfully!
INFO:     Application startup complete.
INFO:     172.18.0.1:50468 - "GET /docs HTTP/1.1" 200 OK
INFO:     172.18.0.1:33180 - "GET /appointments?limit=3 HTTP/1.1" 200 OK
INFO:src.services.background_tasks:Marked 4 overdue appointments as missed
INFO:src.services.background_tasks:  - Appointment 8932da00-a07d-44af-aec8-07f71a1746b5 (patient: 9434765838) marked as missed
INFO:src.services.background_tasks:  - Appointment 520b3cd8-7ac8-4bad-8fd8-32c5e3fcda72 (patient: 6187159780) marked as missed
INFO:src.services.background_tasks:  - Appointment da24e071-0019-4d40-92bc-366e48655612 (patient: 7973153918) marked as missed
INFO:src.services.background_tasks:  - Appointment e5f5b062-3359-490f-954a-13d5b40a434e (patient: 8201217543) marked as missed
```

The background service automatically identifies appointments that are past their scheduled time and haven't been marked as attended, then updates their status to "missed" with detailed logging.

## Testing

Run the test suite:
```bash
make install-test-dependencies # Install test dependencies 
make test           # All tests
make test-unit      # Unit tests only
make test-e2e       # End-to-end tests
make test-features  # BDD feature tests
```

## Future Improvements

### Enhanced Status Transition Rules
The current status management allows flexible transitions between most states. Future versions could implement stricter business rules:

**Proposed Status Flow:**
```
SCHEDULED → ATTENDED → ACTIVE → FINISHED
SCHEDULED → MISSED (automatic after appointment time)
SCHEDULED → CANCELLED (manual cancellation)
```

**Enhanced Validation Rules:**
- `SCHEDULED` can only transition to: `ATTENDED`, `CANCELLED`, or `MISSED`
- `ATTENDED` can only transition to: `ACTIVE` or `CANCELLED`
- `ACTIVE` can only transition to: `FINISHED` or `CANCELLED`
- `FINISHED` and `CANCELLED` are terminal states (no further transitions)
- `MISSED` could potentially transition to `ATTENDED` (late arrival handling)

### Internationalization & Localization
For expansion into foreign markets, the API would need comprehensive localization support:

**Error Message Localization:**
- Multi-language error messages (English, Spanish, French, German, etc.)
- Locale-specific validation messages
- Cultural adaptation of business rules and terminology

**Implementation Requirements:**
- `Accept-Language` header support in API requests
- Message translation framework (e.g., gettext, i18next)
- Localized validation error responses
- Database schema for storing translations
- Configuration for supported locales and fallback languages

**Regional Adaptations:**
- Country-specific patient ID formats (not just NHS numbers)
- Local postcode/postal code validation patterns
- Date/time formatting 
- Regulatory compliance per country (GDPR, HIPAA equivalents)

## Technical Commentary

### Implementation Challenges and Decisions

**Architecture:**
The project implements a clean architecture pattern with clear separation of concerns:

- **FastAPI** - Modern, high-performance web framework chosen for automatic OpenAPI documentation, built-in async support, and excellent type hints integration
- **Pydantic** - Data validation and serialization using Python type annotations, providing input validation 
- **Clean Architecture** - Organized into distinct layers:
  - `models/` - Domain and data validation (Pydantic models)
  - `services/` - Business logic and rules
  - `adapters/` - Database and external system interfaces
  - `entrypoints/` - API routes and HTTP handling
- **Async/Await** - Asynchronous implementation 
- **SQLAlchemy Core** - Database abstraction with async support



**BDD Testing Framework Choice:**  
I initially tried using `pytest-bdd` for behavior-driven development testing, but I ran into major issues with async/await support in step definitions. The framework struggled with asynchronous operations when testing FastAPI endpoints that needed async database connections. I switched to `behave`, which offered better async support through custom context management and `asyncio` integration in the `environment.py` setup.

**NHS Number Validation Implementation:**  
The official NHS Data Dictionary documentation at [datadictionary.nhs.uk](https://www.datadictionary.nhs.uk/attributes/nhs_number.html) has a critical error in Step 5 of the Modulus 11 validation algorithm. The documentation incorrectly states: *"Check the remainder matches the check digit"* - this is mathematically wrong.

**The Issue:** The remainder and check digit are complements that add up to 11 (except for special cases), so they will almost never be the same. For example, if the remainder is 2, the check digit is 9, and 2 is not equal to 9.

**Correct Implementation:** Fortunately, [Wikipedia's NHS number article](https://en.wikipedia.org/wiki/NHS_number) provides the right algorithm with a proper worked example using NHS number `943 476 5919`. The correct process calculates the check digit as `(11 - remainder)` with special handling for results of 10 (invalid) and 11 (which becomes 0). It then compares this calculated check digit to the 10th digit of the NHS number, not to the remainder itself.




