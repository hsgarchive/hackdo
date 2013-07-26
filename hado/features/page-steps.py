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
