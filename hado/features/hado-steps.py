from lettuce import step, world
from lettuce.django import django_url
from hado.tests.factories import SuperUserFactory, StaffUserFactory, \
    NormalUserFactory, PendingUserFactory, UserFactory

from nose.tools import assert_equals, assert_not_equals, assert_false, \
    assert_in

from datetime import date
import time
import logging
logger = logging.getLogger("hado.test")


@step('I reload page')
def reload(step):
    world.browser.reload()


@step('I am logged out')
def logout(step):
    world.browser.visit(django_url('/accounts/logout/'))


@step('I wait for (\d+) seconds')
def i_wait_for_x_seconds(step, seconds):
    time.sleep(float(seconds))


@step('I visit "([^"]*)" page')
def go_to_url(step, uri):
    world.browser.visit(django_url(uri))


@step('I should be on "([^"]*)" page')
def be_on_url(step, uri):
    assert_equals(world.browser.url, django_url(uri))


@step('I should see "([^"]*)" as site title')
def see_title(step, text):
    assert_equals(world.browser.title, text)


@step('I should see input with name "([^"]*)"')
def see_input(step, name):
    els = world.browser.find_by_name(name)
    assert_not_equals(len(els), 0)


@step('I should see (\d+) element with "([^"]*)" "([^"]*)"')
def see_elm_by_id(step, number, target_type, target_value):
    if target_type == 'id':
        els = world.browser.find_by_id(target_value)
    elif target_type == 'css':
        els = world.browser.find_by_css(target_value)
    else:
        raise KeyError
    assert_equals(len(els), int(number))


@step('I should see big hackspace logo')
def big_logo(step):
    step.given('I should see 1 element with "id" "logo-l"')
    els = world.browser.find_by_id('logo-l')
    big_logo = els[0]
    assert_in('img/hackerspacesg-long.png', big_logo['src'])
    assert_equals('HackerspaceSG', big_logo['title'])
    assert_equals('HackerspaceSG', big_logo['alt'])


@step('I should see hackdo footer')
def footer(step):
    els = world.browser.find_by_id('footer')
    assert_false(els.is_empty())
    footer = els[0]
    assert_equals(
        u'made for hackerspacesg |  mit licensed | \xa9 %s | contribute'
        % date.today().year,
        footer.text.strip())


@step('I click on link with text "([^"]*)"')
def i_click_on_link(step, link_text):
    world.browser.find_link_by_text(link_text).click()


@step('I accept the alert')
def accept_alert(step):
    world.browser.get_alert().accept()


@step('I cancel the alert')
def cancel_alert(step):
    world.browser.get_alert().dismiss()


@step('I should see alert with text "([^"]*)"')
def alert(step, text):
    alert_text = ' '.join(world.browser.get_alert().text.split())
    assert_equals(alert_text, text)


@step('Given the following users')
def create_users(step):
    for data in step.hashes:
        usertype = data['type']
        try:
            password = data['password']
        except KeyError:
            password = 'password'
        if usertype == 'superuser':
            SuperUserFactory(password=password)
        elif usertype == 'staff':
            StaffUserFactory(password=password)
        elif usertype == 'normal':
            NormalUserFactory(password=password)
        elif usertype == 'pending':
            PendingUserFactory(password=password)
        else:
            UserFactory(password=password)
