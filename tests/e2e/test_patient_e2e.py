import pytest


async def test_create_patient_success(async_client, sample_patient_data):
    """Test successful patient creation."""
    response = await async_client.post("/patients", json=sample_patient_data)
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["message"] == "Patient created successfully"
    assert data["data"]["nhs_number"] == sample_patient_data["nhs_number"]
    assert data["data"]["name"] == sample_patient_data["name"]
    assert data["data"]["date_of_birth"] == sample_patient_data["date_of_birth"]
    assert data["data"]["postcode"] == sample_patient_data["postcode"]


async def test_create_patient_validation_error(async_client, invalid_patient_data):
    """Test patient creation with validation errors."""
    response = await async_client.post("/patients", json=invalid_patient_data)
    
    assert response.status_code == 422
    data = response.json()
    
    assert "detail" in data
    # Should have multiple validation errors
    assert len(data["detail"]) > 0


async def test_get_patient_not_found(async_client):
    """Test getting non-existent patient."""
    response = await async_client.get("/patients/9999999999")
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


async def test_get_patient_success(async_client, sample_patient_data):
    """Test successful patient retrieval."""
    # Create patient first
    create_response = await async_client.post("/patients", json=sample_patient_data)
    assert create_response.status_code == 201
    
    # Get patient
    nhs_number = sample_patient_data["nhs_number"]
    response = await async_client.get(f"/patients/{nhs_number}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "Patient retrieved successfully"
    assert data["data"]["nhs_number"] == nhs_number
    assert data["data"]["name"] == sample_patient_data["name"]


async def test_get_all_patients(async_client, sample_patient_data):
    """Test getting all patients with pagination."""
    # Create patient first
    create_response = await async_client.post("/patients", json=sample_patient_data)
    assert create_response.status_code == 201
    
    # Get all patients
    response = await async_client.get("/patients")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "Patients retrieved successfully"
    assert "data" in data
    assert "pagination" in data
    assert data["pagination"]["limit"] == 50
    assert data["pagination"]["offset"] == 0
    assert isinstance(data["pagination"]["has_next"], bool)


async def test_update_patient_success(async_client, sample_patient_data):
    """Test successful patient update."""
    # Create patient first
    create_response = await async_client.post("/patients", json=sample_patient_data)
    assert create_response.status_code == 201
    
    # Update patient
    update_data = {
        "name": "Jane Smith Updated",
        "postcode": "M1 2AA"
    }
    
    nhs_number = sample_patient_data["nhs_number"]
    response = await async_client.put(f"/patients/{nhs_number}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "Patient updated successfully"
    assert data["data"]["name"] == update_data["name"]
    assert data["data"]["postcode"] == update_data["postcode"]
    # Original fields should remain
    assert data["data"]["nhs_number"] == nhs_number
    assert data["data"]["date_of_birth"] == sample_patient_data["date_of_birth"]


async def test_update_patient_not_found(async_client):
    """Test updating non-existent patient."""
    update_data = {"name": "Updated Name"}
    
    response = await async_client.put("/patients/9999999999", json=update_data)
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


async def test_delete_patient_success(async_client, sample_patient_data):
    """Test successful patient deletion."""
    # Create patient first
    create_response = await async_client.post("/patients", json=sample_patient_data)
    assert create_response.status_code == 201
    
    # Delete patient
    nhs_number = sample_patient_data["nhs_number"]
    response = await async_client.delete(f"/patients/{nhs_number}")
    
    assert response.status_code == 204
    
    # Verify patient is deleted
    get_response = await async_client.get(f"/patients/{nhs_number}")
    assert get_response.status_code == 404


async def test_delete_patient_not_found(async_client):
    """Test deleting non-existent patient."""
    response = await async_client.delete("/patients/9999999999")
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


async def test_get_patient_appointments(async_client, sample_patient_data, sample_appointment_data):
    """Test getting appointments for a patient."""
    # Create patient first
    create_patient_response = await async_client.post("/patients", json=sample_patient_data)
    assert create_patient_response.status_code == 201
    
    # Create appointment for patient
    create_appointment_response = await async_client.post("/appointments", json=sample_appointment_data)
    assert create_appointment_response.status_code == 201
    
    # Get patient appointments
    nhs_number = sample_patient_data["nhs_number"]
    response = await async_client.get(f"/patients/{nhs_number}/appointments")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == "Patient appointments retrieved successfully"
    assert len(data["data"]) == 1
    assert data["data"][0]["patient"] == nhs_number
    assert "pagination" in data


