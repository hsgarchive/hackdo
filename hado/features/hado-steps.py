from lettuce import step, world
from lettuce.django import django_url
#from nose.tools import assert_equals, assert_true, assert_false,\
    #assert_not_equals, assert_in


@step('I am on the login page')
def home_page(step):
    world.browser.visit(django_url('/'))


@step('I go to "([^"]*)" url')
def go_to_url(step, uri):
    world.browser.visit(django_url(uri))


@step('I am on "([^"]*)" page')
def am_on_this_page(step, uri):
    world.browser.visit(django_url(uri))


@step('I click on "([^"]*)"')
def i_click_on(step, link_text):
    world.browser.driver.implicitly_wait(10)
    world.browser.find_link_by_text(link_text).click()
