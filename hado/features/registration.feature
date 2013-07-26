Feature: User Registration Feature
    Anonymous user should be able to register on our website, and after sucessful registration, user should be in pending mode and have one correct type of contract attached to him/her.

    Scenario: Registration Page UI - registration page should be displayed correctly
        When I visit "accounts/register/" page
        Then I should be on "accounts/register/" page
        And I should see hackdo registration page displayed
