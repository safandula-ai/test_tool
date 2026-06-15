Feature: Login
  As a user
  I want to sign in with clear steps
  So that the scenario reads like a requirement

  Scenario: successful login
    Given the login form is visible
    When the user signs in with username "demo" and password "demo"
    Then the welcome banner should say "Welcome"
