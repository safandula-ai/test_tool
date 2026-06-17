Feature: Mock Login Contract
  As a maintainer
  I want a readable contract test for the generic login page object
  So that local selector behavior stays stable without a live website

  Scenario: demo credentials submit through the mock login form
    Given the mock login form is rendered
    When the user signs in with username "demo" and password "demo"
    Then the mock welcome banner should say "Welcome"
