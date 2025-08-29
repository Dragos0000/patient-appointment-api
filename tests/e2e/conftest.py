import asyncio
import os
import pytest
import time
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi.testclient import TestClient
from dotenv import load_dotenv

from src.entrypoints.main import app
from src.adapters.database.init_db import reset_database

load_dotenv()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing against real API."""
    api_host = os.getenv("API_HOST", "0.0.0.0:8000")
    base_url = f"http://{api_host}"
    
    # Wait for API to be ready
    await _wait_for_api(base_url)
    
    async with AsyncClient(base_url=base_url, timeout=30.0) as client:
        yield client


async def _wait_for_api(base_url: str, max_retries: int = 30, delay: float = 1.0):
    """Wait for the API to be ready."""
    for attempt in range(max_retries):
        try:
            async with AsyncClient(base_url=base_url, timeout=5.0) as client:
                response = await client.get("/health")
                if response.status_code == 200:
                    print(f"API is ready at {base_url}")
                    return
        except Exception as e:
            if attempt == 0:
                print(f"Waiting for API at {base_url} to be ready...")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            else:
                raise RuntimeError(f"API at {base_url} is not ready after {max_retries} attempts. Last error: {e}")
    
    raise RuntimeError(f"API at {base_url} is not ready after {max_retries} attempts")


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing."""
    import random
    import uuid
    import sqlite3

    # Generate a larger pool of valid NHS numbers to support all 37 tests
    def generate_valid_nhs_pool(count=50):
        conn = sqlite3.connect('patient_appointments.db')
        cursor = conn.cursor()
        cursor.execute('SELECT nhs_number FROM patients')
        existing_set = set([row[0] for row in cursor.fetchall()])
        conn.close()
        
        valid_nhs_numbers = []
        for sequence_number in range(8000, 9999):  # Use range 8000-9999
            nhs_base = f'987654{sequence_number}'[:9]
            if len(nhs_base) != 9:
                continue
                
            checksum_total = 0
            for position, digit in enumerate(nhs_base):
                multiplier = 10 - position
                checksum_total += int(digit) * multiplier
            remainder = checksum_total % 11
            check_digit = 11 - remainder
            
            if check_digit == 11:
                check_digit = 0
            elif check_digit == 10:
                continue  # Skip invalid check digits
                
            nhs_number = nhs_base + str(check_digit)
            
            if len(nhs_number) == 10 and nhs_number not in existing_set:
                valid_nhs_numbers.append(nhs_number)
                existing_set.add(nhs_number)
                if len(valid_nhs_numbers) >= count:
                    break
        return valid_nhs_numbers

    # Generate pool of NHS numbers
    nhs_pool = generate_valid_nhs_pool(50)
    
    # Base patient templates
    base_patients = [
        {
            "name": "\u0905\u0928\u0928\u094d\u092f\u093e \u0936\u093f\u0930\u094b\u0933\u0947",
            "date_of_birth": "1989-04-07",
            "postcode": "S5C 2BS"
        },
        {
            "name": "Douglas Wilson",
            "date_of_birth": "1987-04-09",
            "postcode": "S9W 9DS"
        }
    ]

    # Choose random patient template and NHS number
    patient = random.choice(base_patients).copy()
    patient["nhs_number"] = random.choice(nhs_pool)
    
    # Make name unique
    unique_id = str(uuid.uuid4())[:8]
    patient["name"] = f"{patient['name']} E2E-{unique_id}"

    return patient


@pytest.fixture
def sample_appointment_data(sample_patient_data):
    """Sample appointment data for testing."""
    from datetime import datetime, timezone, timedelta
    import uuid
    
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    unique_id = str(uuid.uuid4())[:8]
    
    return {
        "patient": sample_patient_data["nhs_number"],
        "status": "scheduled",
        "time": future_time.isoformat(),
        "duration": "30m",
        "clinician": f"Dr. E2E Test {unique_id}",
        "department": "e2e_testing",
        "postcode": "SW1A 1AA"
    }


@pytest.fixture
def invalid_patient_data():
    """Invalid patient data for testing validation."""
    return {
        "nhs_number": "1234567890", 
        "name": "", 
        "date_of_birth": "invalid-date",
        "postcode": "INVALID"
    }


@pytest.fixture
def invalid_appointment_data():
    """Invalid appointment data for testing validation."""
    return {
        "patient": "1234567890", 
        "status": "invalid_status",
        "time": "2024-12-15T10:00:00",  
        "duration": "invalid",
        "clinician": "",
        "department": "",
        "postcode": "INVALID"
    }