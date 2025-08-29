import pytest
from datetime import datetime, timezone, timedelta


async def test_cancelled_appointment_cannot_be_reinstated(async_client, sample_patient_data, sample_appointment_data):
    """Test that cancelled appointments cannot be reinstated."""
    # Create patient and appointment
    await async_client.post("/patients", json=sample_patient_data)
    create_response = await async_client.post("/appointments", json=sample_appointment_data)
    assert create_response.status_code == 201
    
    appointment_id = create_response.json()["data"]["id"]
    
    # Cancel appointment
    cancel_response = await async_client.put(f"/appointments/{appointment_id}/cancel")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["data"]["status"] == "cancelled"
    
    # Try to reinstate (should fail)
    reinstate_data = {"status": "scheduled"}
    reinstate_response = await async_client.put(f"/appointments/{appointment_id}", json=reinstate_data)
    
    assert reinstate_response.status_code == 400
    data = reinstate_response.json()
    assert "cancelled appointments cannot be reinstated" in data["detail"].lower()


async def test_status_transitions_allowed(async_client, sample_patient_data, sample_appointment_data):
    """Test allowed status transitions."""
    # Create patient and appointment
    await async_client.post("/patients", json=sample_patient_data)
    create_response = await async_client.post("/appointments", json=sample_appointment_data)
    assert create_response.status_code == 201
    
    appointment_id = create_response.json()["data"]["id"]
    
    # Test allowed transitions: scheduled -> active
    update_response = await async_client.put(f"/appointments/{appointment_id}", json={"status": "active"})
    assert update_response.status_code == 200
    assert update_response.json()["data"]["status"] == "active"
    
    # active -> attended
    update_response = await async_client.put(f"/appointments/{appointment_id}", json={"status": "attended"})
    assert update_response.status_code == 200
    assert update_response.json()["data"]["status"] == "attended"


async def test_overdue_appointments_marked_as_missed(async_client, sample_patient_data):
    """Test that overdue appointments are marked as missed."""
    # Create patient
    await async_client.post("/patients", json=sample_patient_data)
    
    # Create appointment in the past
    past_time = datetime.now(timezone.utc) - timedelta(hours=2)
    appointment_data = {
        "patient": sample_patient_data["nhs_number"],
        "status": "scheduled",
        "time": past_time.isoformat(),
        "duration": "30m",
        "clinician": "Dr. Overdue",
        "department": "e2e_overdue",
        "postcode": "SW1A 1AA"
    }
    
    create_response = await async_client.post("/appointments", json=appointment_data)
    assert create_response.status_code == 201
    appointment_id = create_response.json()["data"]["id"]
    
    # Trigger overdue check
    overdue_response = await async_client.post("/appointments/mark-overdue-as-missed")
    assert overdue_response.status_code == 200
    
    # Verify appointment is now marked as missed
    get_response = await async_client.get(f"/appointments/{appointment_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["status"] == "missed"


async def test_future_appointments_not_marked_overdue(async_client, sample_patient_data):
    """Test that future appointments are not marked as overdue."""
    # Create patient
    await async_client.post("/patients", json=sample_patient_data)
    
    # Create appointment in the future
    future_time = datetime.now(timezone.utc) + timedelta(hours=2)
    appointment_data = {
        "patient": sample_patient_data["nhs_number"],
        "status": "scheduled",
        "time": future_time.isoformat(),
        "duration": "30m",
        "clinician": "Dr. Future",
        "department": "e2e_future",
        "postcode": "SW1A 1AA"
    }
    
    create_response = await async_client.post("/appointments", json=appointment_data)
    assert create_response.status_code == 201
    appointment_id = create_response.json()["data"]["id"]
    
    # Trigger overdue check
    overdue_response = await async_client.post("/appointments/mark-overdue-as-missed")
    assert overdue_response.status_code == 200
    
    # Verify appointment is still scheduled
    get_response = await async_client.get(f"/appointments/{appointment_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["status"] == "scheduled"


async def test_attended_appointments_not_marked_overdue(async_client, sample_patient_data):
    """Test that attended appointments are not marked as overdue."""
    # Create patient
    await async_client.post("/patients", json=sample_patient_data)
    
    # Create appointment in the past
    past_time = datetime.now(timezone.utc) - timedelta(hours=2)
    appointment_data = {
        "patient": sample_patient_data["nhs_number"],
        "status": "scheduled",
        "time": past_time.isoformat(),
        "duration": "30m",
        "clinician": "Dr. Attended",
        "department": "e2e_attended",
        "postcode": "SW1A 1AA"
    }
    
    create_response = await async_client.post("/appointments", json=appointment_data)
    assert create_response.status_code == 201
    appointment_id = create_response.json()["data"]["id"]
    
    # Mark as attended first
    attend_response = await async_client.put(f"/appointments/{appointment_id}/attend")
    assert attend_response.status_code == 200
    
    # Trigger overdue check
    overdue_response = await async_client.post("/appointments/mark-overdue-as-missed")
    assert overdue_response.status_code == 200
    
    # Verify appointment is still attended (not missed)
    get_response = await async_client.get(f"/appointments/{appointment_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["status"] == "attended"


async def test_timezone_aware_overdue_calculation(async_client, sample_patient_data):
    """Test that overdue calculation works with timezone-aware datetimes."""
    # Create patient
    await async_client.post("/patients", json=sample_patient_data)
    
    # Create appointment 2 hours ago in UTC
    past_time_utc = datetime.now(timezone.utc) - timedelta(hours=2)
    appointment_data = {
        "patient": sample_patient_data["nhs_number"],
        "status": "scheduled",
        "time": past_time_utc.isoformat(),
        "duration": "30m",
        "clinician": "Dr. Timezone",
        "department": "e2e_timezone",
        "postcode": "SW1A 1AA"
    }
    
    create_response = await async_client.post("/appointments", json=appointment_data)
    assert create_response.status_code == 201
    appointment_id = create_response.json()["data"]["id"]
    
    # Trigger overdue check
    overdue_response = await async_client.post("/appointments/mark-overdue-as-missed")
    assert overdue_response.status_code == 200
    
    # Verify appointment is marked as missed
    get_response = await async_client.get(f"/appointments/{appointment_id}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["status"] == "missed"


async def test_nhs_number_validation_in_workflow(async_client, sample_patient_data):
    """Test NHS number validation throughout the workflow."""
    # Try to create patient with invalid NHS number
    invalid_patient = {
        "nhs_number": "1234567890",  # Invalid checksum
        "name": "Invalid Patient",
        "date_of_birth": "1985-01-01",
        "postcode": "SW1A 1AA"
    }
    
    patient_response = await async_client.post("/patients", json=invalid_patient)
    assert patient_response.status_code == 422
    
    # Create valid patient using the fixture
    patient_response = await async_client.post("/patients", json=sample_patient_data)
    assert patient_response.status_code == 201
    
    # Try to create appointment with invalid NHS number
    invalid_appointment = {
        "patient": "1234567890",  # Invalid NHS number
        "status": "scheduled",
        "time": "2024-12-15T10:00:00+00:00",
        "duration": "30m",
        "clinician": "Dr. Smith",
        "department": "cardiology",
        "postcode": "SW1A 1AA"
    }
    
    appointment_response = await async_client.post("/appointments", json=invalid_appointment)
    # Should return 422 for invalid NHS number
    assert appointment_response.status_code == 422
    
    error_data = appointment_response.json()
    assert "detail" in error_data
    # Check that the error mentions NHS number validation
    error_message = str(error_data["detail"])
    assert "NHS number" in error_message or "patient" in error_message.lower()


async def test_postcode_validation_and_formatting(async_client):
    """Test postcode validation and formatting."""
    # Test various postcode formats
    postcode_tests = [
        ("sw1a1aa", "SW1A 1AA"),  # Should be formatted
        ("M11AA", "M1 1AA"),      # Should be formatted
        ("SW1A 1AA", "SW1A 1AA"), # Already formatted
        ("INVALID", None),        # Invalid format
    ]
    
    for test_index, (input_postcode, expected_output) in enumerate(postcode_tests):
        # Generate unique NHS number for each test
        import random
        import uuid
        
        unique_part = str(random.randint(1000000, 9999999))[:7]
        base_nhs = f"943{unique_part}"[:9]
        
        # Calculate check digit using NHS algorithm
        checksum_total = 0
        for position, digit in enumerate(base_nhs):
            multiplier = 10 - position
            checksum_total += int(digit) * multiplier
        
        remainder = checksum_total % 11
        check_digit = 11 - remainder
        
        if check_digit == 11:
            check_digit = 0
        elif check_digit == 10:
            continue  # Skip this iteration
        
        nhs_number = base_nhs + str(check_digit)
        unique_id = str(uuid.uuid4())[:8]
        
        patient_data = {
            "nhs_number": nhs_number,
            "name": f"Test Patient {unique_id}",
            "date_of_birth": "1985-01-01",
            "postcode": input_postcode
        }
        
        response = await async_client.post("/patients", json=patient_data)
        
        if expected_output:
            assert response.status_code == 201
            assert response.json()["data"]["postcode"] == expected_output
        else:
            assert response.status_code == 422


async def test_concurrent_appointment_operations(async_client, sample_patient_data):
    """Test concurrent operations on appointments."""
    # Create patient
    await async_client.post("/patients", json=sample_patient_data)
    
    # Create appointment
    appointment_data = {
        "patient": sample_patient_data["nhs_number"],
        "status": "scheduled",
        "time": "2024-12-15T10:00:00+00:00",
        "duration": "30m",
        "clinician": "Dr. Smith",
        "department": "cardiology",
        "postcode": "SW1A 1AA"
    }
    
    create_response = await async_client.post("/appointments", json=appointment_data)
    assert create_response.status_code == 201
    appointment_id = create_response.json()["data"]["id"]
    
      # Update and cancel simultaneously
    update_response = await async_client.put(f"/appointments/{appointment_id}", json={"clinician": "Dr. Updated"})
    cancel_response = await async_client.put(f"/appointments/{appointment_id}/cancel")
    
    # Both should succeed (order dependent)
    assert update_response.status_code == 200
    assert cancel_response.status_code == 200
    
    # Check final state
    final_response = await async_client.get(f"/appointments/{appointment_id}")
    assert final_response.status_code == 200
    final_data = final_response.json()["data"]
    
    # Should be cancelled (last operation wins)
    assert final_data["status"] == "cancelled"


async def test_api_health_check(async_client):
    """Test API health check endpoint."""
    response = await async_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "background_tasks" in data


async def test_error_handling(async_client):
    """Test error handling."""
    
    # 1. Non-existent patient
    response = await async_client.get("/patients/9999999999")
    assert response.status_code == 404
    
    # 2. Non-existent appointment
    response = await async_client.get("/appointments/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    
    # 3. Invalid data
    response = await async_client.post("/patients", json={"invalid": "data"})
    assert response.status_code == 422
    
    # 4. Invalid appointment data
    response = await async_client.post("/appointments", json={"invalid": "data"})
    assert response.status_code == 422
    
    # 5. System should still be healthy after errors
    health_response = await async_client.get("/health")
    assert health_response.status_code == 200