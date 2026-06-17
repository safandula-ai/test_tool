Feature: SauceDemo Login
  As a SauceDemo user
  I want to sign in with the standard account
  So that the inventory screen is available

  Scenario: standard user can sign in
    Given the SauceDemo login page is open
    When the standard SauceDemo user signs in
    Then the inventory page is shown
