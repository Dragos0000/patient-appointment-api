Feature: Business Logic and Rules
  As a healthcare system
  I want to enforce business rules and validation
  So that data integrity and business processes are maintained

  Scenario: NHS Number Validation - Valid NHS number is accepted
    Given I have valid patient data
    When I submit a request to create the patient
    Then the patient should be successfully created

  Scenario: NHS Number Validation - Invalid NHS number is rejected
    Given I have patient data with an invalid NHS number
    When I submit a request to create the patient
    Then no patient should be created
    And the request should be rejected with validation error

  Scenario: UK Postcode Validation - Valid postcode is accepted and formatted
    Given I have valid patient data
    When I submit a request to create the patient
    Then the patient should be successfully created
    And all patient fields should be correctly formatted

  Scenario: UK Postcode Validation - Invalid postcode is rejected
    Given I have patient data with an invalid postcode
    When I submit a request to create the patient
    Then no patient should be created
    And the request should be rejected with validation error

  Scenario: Appointment Status Transition - Cancelled appointments cannot be reinstated
    Given a patient exists in the system
    Given a cancelled appointment exists
    When I attempt to change the status back to scheduled
    Then the request should be rejected with business rule error
    And the error message should indicate cancelled appointments cannot be reinstated
    And the appointment should remain cancelled

  Scenario: Appointment Status Transition - Scheduled to attended is allowed
    Given a patient exists in the system
    Given a scheduled appointment exists
    When I mark the appointment as attended
    Then the appointment status should be changed to attended
    And the status change should be confirmed in the response

  Scenario: Appointment Status Transition - Scheduled to cancelled is allowed
    Given a patient exists in the system
    Given a scheduled appointment exists
    When I submit a request to cancel the appointment
    Then the appointment status should be changed to cancelled
    And the cancellation should be confirmed in the response

  Scenario: Overdue Appointment Processing - Past scheduled appointments become missed
    Given a patient exists in the system
    Given a scheduled appointment exists in the past
    And the appointment has not been marked as attended
    When the background task processes overdue appointments
    Then the appointment status should be automatically changed to missed
    And the appointment should no longer be scheduled

  Scenario: Overdue Appointment Processing - Attended appointments remain attended
    Given a patient exists in the system
    Given an appointment exists in the past
    And the appointment has been marked as attended
    When the background task processes overdue appointments
    Then the appointment status should remain as attended
    And the appointment should not be changed to missed

  Scenario: Overdue Appointment Processing - Future appointments remain scheduled
    Given a patient exists in the system
    Given a scheduled appointment exists in the future
    When the background task processes overdue appointments
    Then the appointment status should remain as scheduled
    And the appointment should not be marked as missed

  Scenario: Patient Uniqueness - Cannot create duplicate patients
    Given I have valid patient data
    And a patient already exists with the same NHS number
    When I submit a request to create the patient
    Then no patient should be created
    And the request should be rejected with conflict error
    And the error message should indicate the patient already exists

  Scenario: Appointment Patient Reference - Must reference existing patient
    Given a patient exists in the system
    Given I have appointment with an invalid NHS number
    When I attempt to create the appointment
    Then no appointment should be created
    And the request should be rejected with validation error

  Scenario: Timezone Awareness - All appointment times include timezone information
    Given a patient exists in the system
    Given I have valid appointment
    When I submit a request to create the appointment
    And I request the appointment by ID
    Then I should receive the complete appointment information
    And all appointment fields should be correctly formatted

  Scenario: Duration Format Validation - Valid duration formats are accepted
    Given a patient exists in the system
    Given I have valid appointment
    When I submit a request to create the appointment
    Then the appointment should be successfully created
    And all appointment fields should be correctly formatted
