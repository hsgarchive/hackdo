Feature: User Registration Feature
    Anonymous user should be able to register on our website, and after sucessful registration, user should be in pending mode and have one correct type of contract attached to him/her.

    Scenario: Registration Page UI - registration page should be displayed correctly
        Given the following users:
        | type       | password |
        | super      | password |
        When I visit "accounts/register/" page
        Then I should be on "accounts/register/" page
        And I should see hackdo registration page displayed
        When I fill "refer_one" with "a"
        Then I should see element with "class_name" of "typeahead" in page
        And I should see element with "link_text" of "alice" in page

    Scenario: Wrong Registration - anonymous user pass in wrong value during registration should fail in registration process
        Given the following users:
        | type       | password |
        | super      | password |
        | staff      | password |
        | normal     | password |
        | pending    | password |
        When I visit "accounts/register/" page
        And I press "Register"
        Then I should see error in page
        And I should be on "accounts/register/" page
        When I reload page
        And I fill "username" with "alice"
        And I fill "email" with "wgx731@gmail.com"
        Then I should see error in page
        When I reload page
        And I fill up registration form
        And I fill "refer_one" with "dave"
        And I press "Register"
        Then I should see error in page
        And I should be on "accounts/register/" page

    Scenario: Success Registration - anonymous user should be able to register as an pending user with one contract
        Given the following users:
        | type       | password |
        | super      | password |
        | staff      | password |
        When I visit "accounts/register" page
        And I fill up registration form
        And I press "Register"
        Then I should be on "accounts/login/" page
        And I should see hackdo login page displayed
        And I should see "New pending user wgx731 created." in success alert message
        And user "wgx731@gmail.com" should have 2 unreviewed membershipreview requests
        And user "wgx731@gmail.com" should have 1 "PEN" contracts
