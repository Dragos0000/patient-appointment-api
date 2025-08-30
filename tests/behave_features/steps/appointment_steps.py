from behave import given, when, then
from datetime import datetime, timezone, timedelta
from tests.behave_features.environment import run_async
from tests.behave_features.steps.patient_steps import get_sample_patient_data


def get_sample_appointment_data(patient_nhs_number):
    """Get sample appointment data."""
    import uuid
    
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    unique_id = str(uuid.uuid4())[:8]
    
    return {
        "patient": patient_nhs_number,
        "status": "scheduled",
        "time": future_time.isoformat(),
        "duration": "30m",
        "clinician": f"Dr. BDD Test {unique_id}",
        "department": "bdd_testing",
        "postcode": "SW1A 1AA"
    }


# Given steps
@given('a patient exists in the system')
def patient_exists_in_system(context):
    """Ensure a patient exists in the system."""
    context.patient_data = get_sample_patient_data()
    response = run_async(context, context.client.post("/patients", json=context.patient_data))
    assert response.status_code == 201
    context.created_patient_nhs = context.patient_data["nhs_number"]


@given('I have valid appointment')
def have_valid_appointment(context):
    """Set up valid appointment data."""
    if not hasattr(context, 'created_patient_nhs'):
        # Create a patient first if none exists
        patient_exists_in_system(context)
    context.appointment_data = get_sample_appointment_data(context.created_patient_nhs)


@given('an appointment exists in the API')
def appointment_exists_in_api(context):
    """Create an appointment that exists in the API."""
    # Ensure we have appointment data
    if not hasattr(context, 'appointment_data') or context.appointment_data is None:
        have_valid_appointment(context)
    
    response = run_async(context, context.client.post("/appointments", json=context.appointment_data))
    assert response.status_code == 201
    context.created_appointment_id = response.json()["data"]["id"]


@given('a scheduled appointment exists')
def scheduled_appointment_exists(context):
    """Create a scheduled appointment."""
    # Ensure patient exists first
    if not hasattr(context, 'created_patient_nhs'):
        patient_exists_in_system(context)
    
    context.appointment_data = get_sample_appointment_data(context.created_patient_nhs)
    context.appointment_data["status"] = "scheduled"
    response = run_async(context, context.client.post("/appointments", json=context.appointment_data))
    assert response.status_code == 201
    context.created_appointment_id = response.json()["data"]["id"]


@given('a cancelled appointment exists')
def cancelled_appointment_exists(context):
    """Create a cancelled appointment."""
    # First create a scheduled appointment
    scheduled_appointment_exists(context)
    
    # Then cancel it
    response = run_async(context, context.client.put(f"/appointments/{context.created_appointment_id}/cancel"))
    assert response.status_code == 200


@given('a scheduled appointment exists in the past')
def scheduled_appointment_in_past(context):
    """Create a scheduled appointment in the past."""
    # Ensure patient exists
    if not hasattr(context, 'created_patient_nhs'):
        patient_exists_in_system(context)
    
    past_time = datetime.now(timezone.utc) - timedelta(hours=2)
    appointment_data = {
        "patient": context.created_patient_nhs,
        "status": "scheduled",
        "time": past_time.isoformat(),
        "duration": "30m",
        "clinician": "Dr. Past",
        "department": "test",
        "postcode": "SW1A 1AA"
    }
    
    response = run_async(context, context.client.post("/appointments", json=appointment_data))
    assert response.status_code == 201
    context.created_appointment_id = response.json()["data"]["id"]


@given('the appointment has not been marked as attended')
def appointment_not_marked_attended(context):
    """Verify appointment is not marked as attended."""
    # This is implicit - we created it as scheduled
    pass


@given('an appointment exists in the past')
def appointment_exists_in_past(context):
    """Create an appointment in the past."""
    scheduled_appointment_in_past(context)


@given('the appointment has been marked as attended')
def appointment_marked_attended(context):
    """Mark the appointment as attended."""
    response = run_async(context, context.client.put(f"/appointments/{context.created_appointment_id}/attend"))
    assert response.status_code == 200


@given('I have appointment with an invalid NHS number')
def have_appointment_with_invalid_nhs(context):
    """Set up appointment data with invalid NHS number."""
    context.appointment_data = {
        "patient": "1234567890",  # Invalid NHS number
        "status": "scheduled",
        "time": "2024-12-15T10:00:00+00:00",
        "duration": "30m",
        "clinician": "Dr. Test",
        "department": "test",
        "postcode": "SW1A 1AA"
    }


@given('I have appointment details with an invalid NHS number')
def have_appointment_details_with_invalid_nhs(context):
    """Set up appointment data with invalid NHS number."""
    context.appointment_data = {
        "patient": "1234567890",  # Invalid NHS number
        "status": "scheduled",
        "time": "2024-12-15T10:00:00+00:00",
        "duration": "30m",
        "clinician": "Dr. Test",
        "department": "test",
        "postcode": "SW1A 1AA"
    }


@given('a scheduled appointment exists in the future')
def scheduled_appointment_exists_in_future(context):
    """Create a scheduled appointment in the future."""
    # Ensure patient exists
    if not hasattr(context, 'created_patient_nhs'):
        patient_exists_in_system(context)
    
    future_time = datetime.now(timezone.utc) + timedelta(hours=2)
    appointment_data = {
        "patient": context.created_patient_nhs,
        "status": "scheduled",
        "time": future_time.isoformat(),
        "duration": "30m",
        "clinician": "Dr. Future",
        "department": "test",
        "postcode": "SW1A 1AA"
    }
    
    response = run_async(context, context.client.post("/appointments", json=appointment_data))
    assert response.status_code == 201
    context.created_appointment_id = response.json()["data"]["id"]


# When steps
@when('I submit a request to create the appointment')
def submit_create_appointment_request(context):
    """Submit request to create appointment."""
    context.response = run_async(context, context.client.post("/appointments", json=context.appointment_data))
    # Set appointment ID if creation was successful
    if context.response.status_code == 201:
        response_data = context.response.json()
        context.created_appointment_id = response_data["data"]["id"]


@when('I request the appointment by ID')
def request_appointment_by_id(context):
    """Request appointment by ID."""
    response = run_async(context, context.client.get(f"/appointments/{context.created_appointment_id}"))
    context.response = response


@when('I submit updated appointment information')
def submit_updated_appointment_info(context):
    """Submit updated appointment information."""
    updated_data = {"clinician": "Dr. Updated"}
    context.put_appointment_response = run_async(context, context.client.put(f"/appointments/{context.created_appointment_id}", json=updated_data))
    context.response = context.put_appointment_response  # Set for compatibility with existing steps


@when('I submit a request to cancel the appointment')
def submit_cancel_appointment_request(context):
    """Submit request to cancel appointment."""
    context.response = run_async(context, context.client.put(f"/appointments/{context.created_appointment_id}/cancel"))


@when('I attempt to change the status back to scheduled')
def attempt_change_status_to_scheduled(context):
    """Attempt to change cancelled appointment back to scheduled."""
    update_data = {"status": "scheduled"}
    context.reinstate_response = run_async(context, context.client.put(f"/appointments/{context.created_appointment_id}", json=update_data))
    context.response = context.reinstate_response  # Set for compatibility
    # Debug: print the actual response
    print(f"Reinstate attempt status: {context.reinstate_response.status_code}")
    if context.reinstate_response.status_code != 422:
        print(f"Response content: {context.reinstate_response.text}")


@when('I mark the appointment as attended')
def mark_appointment_attended(context):
    """Mark appointment as attended."""
    context.attend_response = run_async(context, context.client.put(f"/appointments/{context.created_appointment_id}/attend"))
    context.response = context.attend_response  # Set for compatibility


@when('the background task processes overdue appointments')
def background_task_processes_overdue(context):
    """Trigger background task to process overdue appointments."""
    context.response = run_async(context, context.client.post("/appointments/mark-overdue-as-missed"))


@when('I attempt to create the appointment')
def attempt_create_appointment(context):
    """Attempt to create appointment (expecting failure)."""
    context.response = run_async(context, context.client.post("/appointments", json=context.appointment_data))


# Then steps
@then('the appointment should be successfully created')
def appointment_successfully_created(context):
    """Verify appointment was successfully created."""
    assert context.response.status_code == 201
    response_data = context.response.json()
    assert "created successfully" in response_data["message"].lower()
    context.created_appointment_id = response_data["data"]["id"]


@then('the appointment should be retrievable by ID')
def appointment_retrievable_by_id(context):
    """Verify appointment can be retrieved by ID."""
    response = run_async(context, context.client.get(f"/appointments/{context.created_appointment_id}"))
    assert response.status_code == 200


@then('I should receive the complete appointment information')
def receive_complete_appointment_info(context):
    """Verify complete appointment information is received."""
    assert context.response.status_code == 200
    response_data = context.response.json()
    appointment_data = response_data["data"]
    required_fields = ["id", "patient", "status", "time", "duration", "clinician", "department", "postcode"]
    for field in required_fields:
        assert field in appointment_data


@then('all appointment fields should be correctly formatted')
def appointment_fields_correctly_formatted(context):
    """Verify appointment fields are correctly formatted."""
    response_data = context.response.json()
    appointment_data = response_data["data"]
    # Time should include timezone info
    assert "+" in appointment_data["time"] or "Z" in appointment_data["time"]
    # Duration should be in correct format
    assert "m" in appointment_data["duration"] or "h" in appointment_data["duration"]


@then('the appointment details should be successfully updated')
def appointment_successfully_updated(context):
    """Verify appointment was successfully updated."""
    # Use the put_appointment_response from the update step
    if hasattr(context, 'put_appointment_response'):
        assert context.put_appointment_response.status_code == 200
        response_data = context.put_appointment_response.json()
        assert "updated successfully" in response_data["message"].lower()
    else:
        # Fallback to generic response
        assert context.response.status_code == 200
        response_data = context.response.json()
        assert "updated successfully" in response_data["message"].lower()


@then('the appointment status should be changed to cancelled')
def appointment_status_changed_to_cancelled(context):
    """Verify appointment status is changed to cancelled."""
    assert context.response.status_code == 200
    response_data = context.response.json()
    assert response_data["data"]["status"] == "cancelled"


@then('the cancellation should be confirmed in the response')
def cancellation_confirmed_in_response(context):
    """Verify cancellation is confirmed."""
    response_data = context.response.json()
    assert "cancelled successfully" in response_data["message"].lower()


@then('the appointment should remain in the system as cancelled')
def appointment_remains_cancelled(context):
    """Verify appointment remains in system as cancelled."""
    response = run_async(context, context.client.get(f"/appointments/{context.created_appointment_id}"))
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "cancelled"


@then('the error message should indicate cancelled appointments cannot be reinstated')
def error_indicates_cannot_reinstate(context):
    """Verify error message about reinstatement."""
    # Check the reinstate response from the attempt to change status back
    if hasattr(context, 'reinstate_response'):
        assert context.reinstate_response.status_code == 400
        response_data = context.reinstate_response.json()
        error_message = response_data["detail"].lower()
        assert "cancelled" in error_message and "reinstat" in error_message
    else:
        assert context.response.status_code == 400
        response_data = context.response.json()
        error_message = response_data["detail"].lower()
        assert "cancelled" in error_message and "reinstat" in error_message


@then('the appointment should remain cancelled')
def appointment_remains_cancelled_status(context):
    """Verify appointment status remains cancelled."""
    response = run_async(context, context.client.get(f"/appointments/{context.created_appointment_id}"))
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "cancelled"


@then('the appointment status should be changed to attended')
def appointment_status_changed_to_attended(context):
    """Verify appointment status is changed to attended."""
    assert context.response.status_code == 200
    response_data = context.response.json()
    assert response_data["data"]["status"] == "attended"


@then('the status change should be confirmed in the response')
def status_change_confirmed(context):
    """Verify status change is confirmed."""
    # Check the attend response from marking as attended
    if hasattr(context, 'attend_response'):
        assert context.attend_response.status_code == 200
        response_data = context.attend_response.json()
        # Check for either "successfully" or "marked as attended" in the message
        message_lower = response_data["message"].lower()
        assert "successfully" in message_lower or "marked as attended" in message_lower
    else:
        assert context.response.status_code == 200
        response_data = context.response.json()
        message_lower = response_data["message"].lower()
        assert "successfully" in message_lower or "marked as attended" in message_lower


@then('the appointment status should be automatically changed to missed')
def appointment_status_changed_to_missed(context):
    """Verify appointment status is automatically changed to missed."""
    assert context.response.status_code == 200
    
    # Check the appointment status
    response = run_async(context, context.client.get(f"/appointments/{context.created_appointment_id}"))
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "missed"


@then('the appointment should no longer be scheduled')
def appointment_no_longer_scheduled(context):
    """Verify appointment is no longer scheduled."""
    response = run_async(context, context.client.get(f"/appointments/{context.created_appointment_id}"))
    assert response.status_code == 200
    assert response.json()["data"]["status"] != "scheduled"


@then('the appointment status should remain as attended')
def appointment_status_remains_attended(context):
    """Verify appointment status remains attended."""
    response = run_async(context, context.client.get(f"/appointments/{context.created_appointment_id}"))
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "attended"


@then('the appointment should not be changed to missed')
def appointment_not_changed_to_missed(context):
    """Verify appointment is not changed to missed."""
    response = run_async(context, context.client.get(f"/appointments/{context.created_appointment_id}"))
    assert response.status_code == 200
    assert response.json()["data"]["status"] != "missed"


@then('the appointment status should remain as scheduled')
def appointment_status_remains_scheduled(context):
    """Verify appointment status remains scheduled."""
    response = run_async(context, context.client.get(f"/appointments/{context.created_appointment_id}"))
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "scheduled"


@then('the appointment should not be marked as missed')
def appointment_not_marked_missed(context):
    """Verify appointment is not marked as missed."""
    response = run_async(context, context.client.get(f"/appointments/{context.created_appointment_id}"))
    assert response.status_code == 200
    assert response.json()["data"]["status"] != "missed"


@then('no appointment should be created')
def no_appointment_created(context):
    """Verify no appointment was created."""
    # The response should be 422, indicating validation failure
    assert context.response.status_code == 422


@then('the request should be rejected with business rule error')
def request_rejected_with_business_rule_error(context):
    """Verify request is rejected with business rule error (400)."""
    assert context.response.status_code == 400


@then('the updated appointment information should be retrievable')
def updated_appointment_info_retrievable(context):
    """Verify updated appointment information can be retrieved."""
    response = run_async(context, context.client.get(f"/appointments/{context.created_appointment_id}"))
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["data"]["clinician"] == "Dr. Updated"


@then('the response should confirm the appointment update')
def response_confirms_appointment_update(context):
    """Verify response confirms appointment update."""
    if hasattr(context, 'put_appointment_response'):
        response_data = context.put_appointment_response.json()
        assert "updated successfully" in response_data["message"].lower()
    else:
        response_data = context.response.json()
        assert "updated successfully" in response_data["message"].lower()
