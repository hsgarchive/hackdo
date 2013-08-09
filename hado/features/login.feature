Feature: User Login Feature
    Existing user should be able to login and they should be redirected to correct page after login

    Background:
        Given I am logged out

    Scenario: Login Page UI - login page should be displayed correctly
        When I visit "accounts/login" page
        Then I should be on "accounts/login/" page
        And I should see hackdo login page displayed

    Scenario: Wrong Login - non-existing user should not be able to login
        Given the following users:
        | type       | password |
        | super      | password |
        | staff      | password |
        | normal     | password |
        | pending    | password |
        When I visit "accounts/login" page
        And I press "login"
        Then I should see "username" in form error message
        And I should see "password" in form error message
        When I fill "username" with "alice"
        And I fill "password" with "wrong-password"
        And I press "login"
        Then I should see "Please enter a correct username and password. Note that both fields may be case-sensitive." in form error message
        When I fill "username" with "john"
        And I fill "password" with "password"
        And I press "login"
        Then I should see "Please enter a correct username and password. Note that both fields may be case-sensitive." in form error message

    Scenario: Super User Login - superuser should be redirect to admin page
        Given the following users:
        | type       | password |
        | super      | password |
        When I visit "accounts/login" page
        And I fill "username" with "alice"
        And I fill "password" with "password"
        And I press "login"
        Then I should be on "hdadmin/" page
        And I should see hackdo admin page displayed

    Scenario: Staff User Login - staff user should be redirect to user profile page with link to admin page
        Given the following users:
        | type       | password |
        | staff      | password |
        When I visit "accounts/login" page
        And I fill "username" with "bob"
        And I fill "password" with "password"
        And I press "login"
        Then I should be on "users/bob/" page
        And I should see user profile page displayed
        And I should see element with "link_text" of "Admin" in navbar

    Scenario: Normal User Login - normal user should be redirect to user profile page
        Given the following users:
        | type       | password |
        | normal     | password |
        When I visit "accounts/login" page
        And I fill "username" with "charlie"
        And I fill "password" with "password"
        And I press "login"
        Then I should be on "users/charlie/" page
        And I should see user profile page displayed
        And I should not see element with "link_text" of "Admin" in navbar

    Scenario: Pending User Login - pending user should be redirect to pending user page
        Given the following users:
        | type       | password |
        | pending    | password |
        When I visit "accounts/login" page
        And I fill "username" with "dave"
        And I fill "password" with "password"
        And I press "login"
        Then I should be on "pending-user/" page
        And I should see pending user page displayed
        And I should not see element with "link_text" of "Admin" in navbar
