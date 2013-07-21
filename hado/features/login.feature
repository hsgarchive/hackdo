Feature: User Login Feature
    Existing user should be able to login and they should be redirected to correct page after login

    Background:
        Given the following users
            | username | first_name | last_name | email                 | password | type       |
            | alice    | world      | alice     | alice@hackspace.sg    | password | superuser  |
            | bob      | world      | bob       | bob@hackspace.sg      | password | staff      |
            | charlie  | world      | charlie   | charlie@hackspace.sg  | password | normal     |
            | dave     | world      | dave      | dave@hackspace.sg     | password | pending    |
        And I am logged out

    Scenario: Login Page UI - login page should be displayed correct
        When I visit "accounts/login" page
        Then I should be on "accounts/login/" page
        And I should see hackdo login page displayed

    Scenario: Wrong Login - non-existing user should not be able to login
        When I visit "accounts/login" page
        And I click "login" button
        Then I should see form error with "username" in error message
        Then I should see form error with "password" in error message
        When I fill "username" with "alice"
        And I fill "password" with "wrong-password"
        And I click "login" button
        Then I should not see form error with "Please enter a correct username and password. Note that both fields may be case-sensitive." in error message
        When I fill "username" with "nash"
        And I fill "password" with "password"
        And I click "login" button
        Then I should not see form error with "Please enter a correct username and password. Note that both fields may be case-sensitive." in error message

    Scenario: Super User Login - superuser should be redirect to admin page
        When I visit "accounts/login" page
        And I fill "username" with "alice"
        And I fill "password" with "password"
        And I click "login" button
        Then I should be on "hdadmin/" page
        And I should see hackdo admin page displayed

    Scenario: Staff User Login - staff user should be redirect to user profile page with link to admin page
        When I visit "accounts/login" page
        And I fill "username" with "bob"
        And I fill "password" with "password"
        And I click "login" button
        Then I should be on "users/bob/" page
        And I should see user profile page displayed
        And I should see "Admin" within navbar

    Scenario: Normal User Login - normal user should be redirect to user profile page
        When I visit "accounts/login" page
        And I fill "username" with "charlie"
        And I fill "password" with "password"
        And I click "login" button
        Then I should be on "users/charlie/" page
        And I should see user profile page displayed

    Scenario: Pending User Login - pending user should be redirect to pending user page
        When I visit "accounts/login" page
        And I fill "username" with "dave"
        And I fill "password" with "password"
        And I click "login" button
        Then I should be on "pending-user/" page
        And I should see pending user page displayed
