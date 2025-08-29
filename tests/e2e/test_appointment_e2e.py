import pytest
from datetime import datetime, timezone


async def test_create_appointment_success(async_client, sample_patient_data, sample_appointment_data):
    """Test successful appointment creation."""
    # Create patient first
    patient_response = await async_client.post("/patients", json=sample_patient_data)
    assert patient_response.status_code == 201
    
    # Create appointment
    response = await async_client.post("/appointments", json=sample_appointment_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["message"] == "Appointment created successfully"
    assert data["data"]["patient"] == sample_appointment_data["patient"]
    assert data["data"]["status"] == sample_appointment_data["status"]
    assert data["data"]["duration"] == sample_appointment_data["duration"]
    assert data["data"]["clinician"] == sample_appointment_data["clinician"]
    assert data["data"]["department"] == sample_appointment_data["department"]
    assert data["data"]["postcode"] == sample_appointment_data["postcode"]


async def test_create_appointment_validation_error(async_client, invalid_appointment_data):
    """Test appointment creation with validation errors."""
    response = await async_client.post("/appointments", json=invalid_appointment_data)
    
    assert response.status_code == 422
    data = response.json()
    
    assert "detail" in data
    assert len(data["detail"]) > 0


async def test_create_appointment_without_timezone(async_client, sample_patient_data):
    """Test appointment creation fails without timezone-aware datetime."""
    # Create patient first
    patient_response = await async_client.post("/patients", json=sample_patient_data)
    assert patient_response.status_code == 201
    
    # Try to create appointment with  datetime
    appointment_data = {
        "patient": sample_patient_data["nhs_number"],
        "status": "scheduled",
        "time": "2024-12-15T10:00:00", 
        "clinician": "Dr. Smith",
        "department": "cardiology",
        "postcode": "SW1A 1AA"
    }
    
    response = await async_client.post("/appointments", json=appointment_data)
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


async def test_get_appointment_success(async_client, sample_patient_data, sample_appointment_data):
    """Test successful appointment retrieval."""
    # Create patient first
    patient_response = await async_client.post("/patients", json=sample_patient_data)
    assert patient_response.status_code == 201
    
    # Create appointment
    create_response = await async_client.post("/appointments", json=sample_appointment_data)
    assert create_response.status_code == 201
    appointment_id = create_response.json()["data"]["id"]
    
    # Get appointment
    response = await async_client.get(f"/appointments/{appointment_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "Appointment retrieved successfully"
    assert data["data"]["id"] == appointment_id
    assert data["data"]["patient"] == sample_appointment_data["patient"]


async def test_get_appointment_not_found(async_client):
    """Test getting non-existent appointment."""
    response = await async_client.get("/appointments/00000000-0000-0000-0000-000000000000")
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


async def test_get_all_appointments(async_client, sample_patient_data):
    """Test getting all appointments with pagination."""
    # Create patient
    patient_response = await async_client.post("/patients", json=sample_patient_data)
    assert patient_response.status_code == 201
    
    # Get initial count of appointments
    initial_response = await async_client.get("/appointments")
    assert initial_response.status_code == 200
    initial_count = len(initial_response.json()["data"])
    
    # Create multiple appointments
    appointments_data = [
        {
            "patient": sample_patient_data["nhs_number"],
            "status": "scheduled",
            "time": "2024-12-15T10:00:00+00:00",
            "duration": "30m",
            "clinician": "Dr. E2E Smith",
            "department": "e2e_cardiology",
            "postcode": "SW1A 1AA"
        },
        {
            "patient": sample_patient_data["nhs_number"],
            "status": "scheduled",
            "time": "2024-12-16T14:00:00+00:00",
            "duration": "1h",
            "clinician": "Dr. E2E Johnson",
            "department": "e2e_neurology",
            "postcode": "M1 1AA"
        }
    ]
    
    created_appointments = []
    for appointment_data in appointments_data:
        response = await async_client.post("/appointments", json=appointment_data)
        assert response.status_code == 201
        created_appointments.append(response.json()["data"]["id"])
    
    # Get all appointments
    response = await async_client.get("/appointments")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "Appointments retrieved successfully"
    assert len(data["data"]) == initial_count + 2
    assert data["pagination"]["total"] == initial_count + 2
    
    # Cleanup
    for appointment_id in created_appointments:
        await async_client.delete(f"/appointments/{appointment_id}")
    await async_client.delete(f"/patients/{sample_patient_data['nhs_number']}")


async def test_filter_appointments_by_patient(async_client, sample_patient_data):
    """Test filtering appointments by patient."""
    # Create patient
    patient_response = await async_client.post("/patients", json=sample_patient_data)
    assert patient_response.status_code == 201
    
    # Create appointment for patient
    appointment_data = {
        "patient": sample_patient_data["nhs_number"],
        "status": "scheduled",
        "time": "2024-12-15T10:00:00+00:00",
        "duration": "30m",
        "clinician": "Dr. E2E Filter",
        "department": "e2e_filter_test",
        "postcode": "SW1A 1AA"
    }
    
    create_response = await async_client.post("/appointments", json=appointment_data)
    assert create_response.status_code == 201
    appointment_id = create_response.json()["data"]["id"]
    
    # Filter appointments by patient
    response = await async_client.get(f"/appointments?patient={sample_patient_data['nhs_number']}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "Appointments retrieved successfully"
    # Should contain at least 1 appointment
    patient_appointments = [apt for apt in data["data"] if apt["patient"] == sample_patient_data["nhs_number"]]
    assert len(patient_appointments) >= 1
    
    # Cleanup
    await async_client.delete(f"/appointments/{appointment_id}")
    await async_client.delete(f"/patients/{sample_patient_data['nhs_number']}")


async def test_filter_appointments_by_status(async_client, sample_patient_data):
    """Test filtering appointments by status."""
    # Create patient
    patient_response = await async_client.post("/patients", json=sample_patient_data)
    assert patient_response.status_code == 201
    
    # Create appointments with different statuses
    appointments_data = [
        {
            "patient": sample_patient_data["nhs_number"],
            "status": "scheduled",
            "time": "2024-12-15T10:00:00+00:00",
            "duration": "30m",
            "clinician": "Dr. E2E Status1",
            "department": "e2e_status_test",
            "postcode": "SW1A 1AA"
        },
        {
            "patient": sample_patient_data["nhs_number"],
            "status": "scheduled",
            "time": "2024-12-16T14:00:00+00:00",
            "duration": "1h",
            "clinician": "Dr. E2E Status2",
            "department": "e2e_status_test",
            "postcode": "M1 1AA"
        }
    ]
    
    created_appointments = []
    for appointment_data in appointments_data:
        response = await async_client.post("/appointments", json=appointment_data)
        assert response.status_code == 201
        created_appointments.append(response.json()["data"]["id"])
    
    # Filter by status
    response = await async_client.get("/appointments?status=scheduled")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "Appointments retrieved successfully"
    # All returned appointments should have 'scheduled' status
    for appointment in data["data"]:
        assert appointment["status"] == "scheduled"
    
    # Cleanup
    for appointment_id in created_appointments:
        await async_client.delete(f"/appointments/{appointment_id}")
    await async_client.delete(f"/patients/{sample_patient_data['nhs_number']}")


async def test_update_appointment_success(async_client, sample_patient_data, sample_appointment_data):
    """Test successful appointment update."""
    # Create patient first
    patient_response = await async_client.post("/patients", json=sample_patient_data)
    assert patient_response.status_code == 201
    
    # Create appointment
    create_response = await async_client.post("/appointments", json=sample_appointment_data)
    assert create_response.status_code == 201
    appointment_id = create_response.json()["data"]["id"]
    
    # Update appointment
    update_data = {
        "clinician": "Dr. Updated",
        "duration": "1h"
    }
    
    response = await async_client.put(f"/appointments/{appointment_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "Appointment updated successfully"
    assert data["data"]["clinician"] == update_data["clinician"]
    assert data["data"]["duration"] == update_data["duration"]
    # Original fields should remain
    assert data["data"]["patient"] == sample_appointment_data["patient"]
    assert data["data"]["status"] == sample_appointment_data["status"]


async def test_update_appointment_not_found(async_client):
    """Test updating non-existent appointment."""
    update_data = {"clinician": "Dr. Updated"}
    
    response = await async_client.put("/appointments/00000000-0000-0000-0000-000000000000", json=update_data)
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


async def test_delete_appointment_success(async_client, sample_patient_data, sample_appointment_data):
    """Test successful appointment deletion."""
    # Create patient first
    patient_response = await async_client.post("/patients", json=sample_patient_data)
    assert patient_response.status_code == 201
    
    # Create appointment
    create_response = await async_client.post("/appointments", json=sample_appointment_data)
    assert create_response.status_code == 201
    appointment_id = create_response.json()["data"]["id"]
    
    # Delete appointment
    response = await async_client.delete(f"/appointments/{appointment_id}")
    
    assert response.status_code == 204
    
    # Verify appointment is deleted
    get_response = await async_client.get(f"/appointments/{appointment_id}")
    assert get_response.status_code == 404


async def test_delete_appointment_not_found(async_client):
    """Test deleting non-existent appointment."""
    response = await async_client.delete("/appointments/00000000-0000-0000-0000-000000000000")
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


async def test_cancel_appointment_success(async_client, sample_patient_data, sample_appointment_data):
    """Test successful appointment cancellation."""
    # Create patient first
    patient_response = await async_client.post("/patients", json=sample_patient_data)
    assert patient_response.status_code == 201
    
    # Create appointment
    create_response = await async_client.post("/appointments", json=sample_appointment_data)
    assert create_response.status_code == 201
    appointment_id = create_response.json()["data"]["id"]
    
    # Cancel appointment
    response = await async_client.put(f"/appointments/{appointment_id}/cancel")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "Appointment cancelled successfully"
    assert data["data"]["status"] == "cancelled"


async def test_mark_appointment_attended(async_client, sample_patient_data, sample_appointment_data):
    """Test marking appointment as attended."""
    # Create patient first
    patient_response = await async_client.post("/patients", json=sample_patient_data)
    assert patient_response.status_code == 201
    
    # Create appointment
    create_response = await async_client.post("/appointments", json=sample_appointment_data)
    assert create_response.status_code == 201
    appointment_id = create_response.json()["data"]["id"]
    
    # Mark as attended
    response = await async_client.put(f"/appointments/{appointment_id}/attend")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "Appointment marked as attended"
    assert data["data"]["status"] == "attended"


