Feature: Appointment Management
  As a healthcare system user
  I want to manage patient appointments
  So that I can schedule, update, and track patient visits

  Background:
    Given a patient exists in the system

  Scenario: Create a new appointment
    Given I have valid appointment
    When I submit a request to create the appointment
    Then the appointment should be successfully created
    And the appointment should be retrievable by ID

  Scenario: Retrieve appointment by ID
    Given an appointment exists in the API
    When I request the appointment by ID
    Then I should receive the complete appointment information
    And all appointment fields should be correctly formatted

  Scenario: Update appointment information
    Given a scheduled appointment exists
    When I submit updated appointment information
    Then the appointment details should be successfully updated
    And the updated appointment information should be retrievable
    And the response should confirm the appointment update

  Scenario: Cancel an appointment
    Given a scheduled appointment exists
    When I submit a request to cancel the appointment
    Then the appointment status should be changed to cancelled
    And the cancellation should be confirmed in the response
    And the appointment should remain in the system as cancelled

  Scenario: Cannot reinstate cancelled appointment
    Given a cancelled appointment exists
    When I attempt to change the status back to scheduled
    Then the request should be rejected with business rule error
    And the error message should indicate cancelled appointments cannot be reinstated
    And the appointment should remain cancelled

  Scenario: Mark appointment as attended
    Given a scheduled appointment exists
    When I mark the appointment as attended
    Then the appointment status should be changed to attended
    And the status change should be confirmed in the response

  Scenario: Automatic marking of overdue appointments as missed
    Given a scheduled appointment exists in the past
    And the appointment has not been marked as attended
    When the background task processes overdue appointments
    Then the appointment status should be automatically changed to missed
    And the appointment should no longer be scheduled

  Scenario: Attended appointments are not marked as missed
    Given an appointment exists in the past
    And the appointment has been marked as attended
    When the background task processes overdue appointments
    Then the appointment status should remain as attended
    And the appointment should not be changed to missed

  Scenario: Future appointments are not marked as missed
    Given a scheduled appointment exists in the future
    When the background task processes overdue appointments
    Then the appointment status should remain as scheduled
    And the appointment should not be marked as missed

  Scenario: Create appointment with invalid NHS number
    Given I have appointment with an invalid NHS number
    When I attempt to create the appointment
    Then no appointment should be created
    And the request should be rejected with validation error

  Scenario: Create appointment with invalid patient reference
    Given I have appointment details with an invalid NHS number
    When I attempt to create the appointment
    Then no appointment should be created
    And the request should be rejected with validation error
