Feature: Patient Management
  As a healthcare system user
  I want to manage patient records
  So that I can store and retrieve patient information

  Scenario: Create a new patient
    Given I have valid patient data
    When I submit a request to create the patient
    Then the patient should be successfully created
    And the patient should be retrievable by NHS number

  Scenario: Retrieve patient by NHS number
    Given I have valid patient data
    And I submit a request to create the patient
    When I request the patient by NHS number
    Then I should receive the complete patient information
    And all patient fields should be correctly formatted

  Scenario: Update patient information
    Given I have valid patient data
    And I submit a request to create the patient
    When I submit updated patient information
    Then the patient details should be successfully updated
    And the updated patient information should be retrievable

  Scenario: Delete a patient
    Given I have valid patient data
    And I submit a request to create the patient
    When I submit a request to delete the patient
    Then the patient should be successfully deleted
    And the patient should no longer be retrievable

  Scenario: Create patient with invalid NHS number
    Given I have patient data with an invalid NHS number
    When I submit a request to create the patient
    Then no patient should be created
    And the request should be rejected with validation error

  Scenario: Create patient with invalid postcode
    Given I have patient data with an invalid postcode
    When I submit a request to create the patient
    Then no patient should be created
    And the request should be rejected with validation error

  Scenario: Create patient with missing required fields
    Given I have patient data with missing required fields
    When I submit a request to create the patient
    Then no patient should be created
    And the request should be rejected with validation error

  Scenario: Cannot create duplicate patient
    Given I have valid patient data
    And a patient already exists with the same NHS number
    When I submit a request to create the patient
    Then no patient should be created
    And the request should be rejected with conflict error
    And the error message should indicate the patient already exists

  Scenario: Retrieve non-existent patient
    When I request a patient with NHS number "9999999999"
    Then the request should be rejected with validation error
    And the error message should indicate patient not found

  Scenario: Update non-existent patient
    Given I have valid patient data
    When I submit updated patient information
    Then the request should be rejected with validation error
    And the error message should indicate patient not found

  Scenario: Delete non-existent patient
    When I submit a request to delete the patient
    Then the request should be rejected with validation error
    And the error message should indicate patient not found

  Scenario: List all patients
    Given I have valid patient data
    And I submit a request to create the patient
    When I request all patients
    Then I should receive a list of patients
    And the response should include pagination information

  Scenario: List patients with pagination
    Given I have valid patient data
    And I submit a request to create the patient
    When I request patients with pagination limit 10 and offset 0
    Then I should receive a list of patients
    And the response should include pagination information
    And the patient list should be limited to 10 items
