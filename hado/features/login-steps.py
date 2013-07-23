from lettuce import step
#from lettuce.django import django_url

#from nose.tools import assert_equals, assert_false,\
    #assert_in
import logging
logger = logging.getLogger("hado.test")


@step('I should see hackdo login page displayed')
def login_page_displayed(step):
    step.then('I should see "Sign In - HackDo" as site title')
    step.then('I should see big hackspace logo')
    step.then('I should see hackdo footer')
    step.then('I should see input with name "username"')
    step.then('I should see input with name "password"')
    step.then('I should see input with name "loginbtn"')
