from lettuce import step


@step('I should see hackdo login page displayed')
def login_page_displayed(step):
    step.then('I should see "Sign In - HackDo" as site title')
    step.then('I should see big hackspace logo')
    step.then('I should see hackdo footer')
    step.then('I should see element with "name" of "username" in page')
    step.then('I should see element with "name" of "password" in page')
    step.then('I should see element with "id" of "login-btn" in page')


@step('I should see hackdo admin page displayed')
def admin_page_displayed(step):
    step.then('I should see "HackDo | Django site admin" as site title')
    step.then('I should see element with "id" of "site-name" in page')
    step.then('I should see element with "id" of "changelist" in page')
    step.then('I should see element with "id" of "payment_verification" in page')
    #step.then('I should see element with "id" of "membershipreview" in page')


@step('I should see user profile page displayed')
def user_profile_page_displayed(step):
    step.then('I should see "User Home - HackDo" as site title')
    step.then('I should see element with "class_name" of "navbar" in page')
    step.then('I should see hackdo footer')
    step.then('I should see element with "link_text" of "Settings" in navbar')
    step.then('I should see element with "link_text" of "Home" in navbar')
    step.then('I should see element with "id" of "user_home" in page')
    step.then('I should see element with "id" of "account_summary" in page')
    step.then('I should see element with "id" of "contract_summaries" in page')
    step.then('I should see element with "id" of "membershipreviews" in page')
    step.then('I should see element with "id" of "payment_submission" in page')
    step.then('I should see element with "id" of "payment_history" in page')


@step('I should see pending user page displayed')
def pending_user_page_displayed(step):
    step.then('I should see "Pending User - HackDo" as site title')
    step.then('I should see element with "class_name" of "navbar" in page')
    step.then('I should see hackdo footer')
    step.then('I should see element with "link_text" of "Settings" in navbar')
    step.then('I should see element with "link_text" of "Home" in navbar')
    step.then('I should see element with "id" of "pending_user" in page')
    step.then('I should see element with "id" of "membershipreviews" in page')
    step.then('I should see element with "id" of "membershipreview_table" in page')


@step('I should see hackdo registration page displayed')
def registration_page_displayed(step):
    step.then('I should see "New Account - HackDo" as site title')
    step.then('I should see big hackspace logo')
    step.then('I should see hackdo footer')
    step.then('I should see element with "name" of "username" in page')
    step.then('I should see element with "name" of "email" in page')
    step.then('I should see element with "name" of "first_name" in page')
    step.then('I should see element with "name" of "last_name" in page')
    step.then('I should see element with "name" of "password" in page')
    step.then('I should see element with "name" of "password_confirm" in page')
    step.then('I should see element with "name" of "refer_one" in page')
    step.then('I should see element with "name" of "refer_two" in page')
    step.then('I should see element with "name" of "contract_type" in page')
    step.then('I should see element with "id" of "register-btn" in page')


@step('I fill up registration form')
def fill_up_registration_form(step):
    step.given('I fill "username" with "wgx731"')
    step.given('I fill "email" with "wgx731@gmail.com"')
    step.given('I fill "first_name" with "GaoXiang"')
    step.given('I fill "last_name" with "Wang"')
    step.given('I fill "password" with "1111111"')
    step.given('I fill "password_confirm" with "1111111"')
    step.given('I fill "refer_one" with "alice"')
    step.given('I fill "refer_two" with "bob"')
    step.given('I select "contract_type" with "Regular Member"')
