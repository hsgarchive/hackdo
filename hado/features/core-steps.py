from lettuce import step, world
from lettuce.django import django_url
from selenium.common.exceptions import NoSuchElementException
from nose.tools import assert_equals, assert_false, \
    assert_true, assert_in, assert_is_not_none, assert_is_none
from django.contrib.auth import get_user_model

from hado.models import Contract, MembershipReview
from hado.tests.factories import SuperUserFactory, StaffUserFactory, \
    NormalUserFactory, PendingUserFactory, UserFactory

from datetime import date
import time
import logging
logger = logging.getLogger("hado.test")

User = get_user_model()


@step('I reload page')
def reload(step):
    world.browser.get(world.browser.current_url)


@step('I am logged out')
def logout(step):
    world.browser.get(django_url('/accounts/logout/'))


@step('I wait for (\d+) seconds')
def i_wait_for_x_seconds(step, seconds):
    time.sleep(float(seconds))


@step('I visit "([^"]*)" page')
def go_to_url(step, uri):
    world.browser.get(django_url(uri))


@step('I should be on "([^"]*)" page')
def be_on_url(step, uri):
    assert_equals(world.browser.current_url, django_url(uri))
# Browser Navigation Ends #


@step('I should see "([^"]*)" as site title')
def see_title(step, text):
    assert_equals(world.browser.title, text)


@step('I should not have element with "([^"]*)" of "([^"]*)" in page')
def not_have_elm(step, element_type, value):
    elm = get_elm(element_type, value)
    assert_is_none(elm)


@step('I should see element with "([^"]*)" of "([^"]*)" in page')
def see_elm(step, element_type, value):
    elm = get_elm(element_type, value)
    assert_is_not_none(elm)
    assert_true(elm.is_displayed())


@step('I should not see element with "([^"]*)" of "([^"]*)" in page')
def not_see_elm(step, element_type, value):
    elm = get_elm(element_type, value)
    if elm:
        assert_false(elm.is_displayed())


@step('I should see element with "([^"]*)" of "([^"]*)" in navbar')
def see_elm_in_navbar(step, element_type, value):
    navbar = get_elm("class_name", "navbar")
    assert_is_not_none(navbar)
    navbar_dropdown = get_elm("class_name", "dropdown-toggle", parent=navbar)
    assert_is_not_none(navbar_dropdown)
    navbar_dropdown.click()
    elm = get_elm(element_type, value, parent=navbar)
    assert_true(elm.is_displayed())
    navbar_dropdown.click()


@step('I should not see element with "([^"]*)" of "([^"]*)" in navbar')
def not_see_elm_in_navbar(step, element_type, value):
    navbar = get_elm("class_name", "navbar")
    assert_is_not_none(navbar)
    navbar_dropdown = get_elm("class_name", "dropdown-toggle", parent=navbar)
    assert_is_not_none(navbar_dropdown)
    navbar_dropdown.click()
    elm = get_elm(element_type, value, parent=navbar)
    if elm:
        assert_false(elm.is_displayed())
    navbar_dropdown.click()


@step('I check "([^"]*)"')
def i_check(step, name):
    checkbox = world.browser.find_element_by_name(name).click()
    assert_is_not_none(checkbox)
    if not checkbox.is_selected():
        checkbox.click()


@step('I uncheck "([^"]*)"')
def i_uncheck(step, name):
    checkbox = world.browser.find_element_by_name(name).click()
    assert_is_not_none(checkbox)
    if checkbox.is_selected():
        checkbox.click()


@step('I click on "([^"]*)"')
def i_click_on_link(step, link_text):
    link = world.browser.find_element_by_link_text(link_text)
    assert_is_not_none(link)
    link.click()


@step('I press "([^"]*)"')
def i_press(step, value):
    try:
        button = world.browser.find_element_by_xpath(
            '//input[@value="%s"]'
            % value)
    except NoSuchElementException:
        try:
            button = world.browser.find_element_by_xpath(
                '//button[text()="%s"]'
                % value)
        except NoSuchElementException:
            button = None
    assert_is_not_none(button)
    button.click()


@step('I fill "([^"]*)" with "([^"]*)"')
def i_fill(step, name, text):
    try:
        input_field = world.browser.find_element_by_name(name)
    except NoSuchElementException:
        input_field = None
    assert_is_not_none(input_field)
    input_field.send_keys(text)


@step('I select "([^"]*)" with "([^"]*)"')
def i_select(step, name, option_text):
    try:
        select_field = world.browser.find_element_by_name(name)
    except NoSuchElementException:
        select_field = None
    assert_is_not_none(select_field)
    for option in select_field.find_elements_by_tag_name('option'):
        if option.text == option_text:
            option.click()


@step('I should see "([^"]*)" in success alert message')
def i_see_alert__message(step, message):
    alert = world.browser.find_element_by_css_selector('.alert-success')
    assert_is_not_none(alert)
    assert_in(message, alert.text)


@step('I should see "([^"]*)" in form error message')
def i_see_form_error_message(step, message):
    form_error = world.browser.find_element_by_css_selector('.alert-error')
    assert_is_not_none(form_error)
    assert_in(message, form_error.text)


@step('I should see error in page')
def i_see_error_in_page(step):
    errors = world.browser.find_elements_by_css_selector('.error')
    assert_true(len(errors) > 0)


def get_elm(element_type, value, parent=None, wait_time=0):
    world.browser.implicitly_wait(wait_time)
    if not parent:
        parent = world.browser
    try:
        if element_type == 'id':
            elm = parent.find_element_by_id(value)
        elif element_type == 'xpath':
            elm = parent.find_element_by_xpath(value)
        elif element_type == 'link_text':
            elm = parent.find_element_by_link_text(value)
        elif element_type == 'name':
            elm = parent.find_element_by_name(value)
        elif element_type == 'tag_name':
            elm = parent.find_element_by_tag_name(value)
        elif element_type == 'class_name':
            elm = parent.find_element_by_class_name(value)
        elif element_type == 'css_selector':
            elm = parent.find_element_by_css_selector(value)
        else:
            raise NameError('wrong element type given.')
    except NoSuchElementException:
        elm = None
    return elm
# Element function Ends #


@step('Given the following users')
def create_users(step):
    for data in step.hashes:
        usertype = data.get('type', 'normal')
        password = data.get('password', 'password')
        if usertype == 'super':
            SuperUserFactory(password=password)
        elif usertype == 'staff':
            StaffUserFactory(password=password)
        elif usertype == 'normal':
            NormalUserFactory(password=password)
        elif usertype == 'pending':
            PendingUserFactory(password=password)
        else:
            UserFactory(password=password)


@step('user "([^"]*)" should have (\d+) "([^"]*)" contracts')
def assert_contracts(step, user_email, number, c_status):
    u = User.objects.get(email=user_email)
    assert_equals(
        Contract.objects.filter(user=u, status=c_status).count(),
        int(number))


@step('user "([^"]*)" should have (\d+) unreviewed membershipreview requests')
def assert_membershipreviews(step, user_email, number):
    u = User.objects.get(email=user_email)
    assert_equals(
        MembershipReview.objects.filter(applicant=u, reviewed=False).count(),
        int(number))


@step('I should see big hackerspace logo')
def big_logo(step):
    step.given('I should see element with "id" of "logo-l" in page')
    big_logo = world.browser.find_element_by_id('logo-l')
    assert_in('img/hackerspacesg-long.png', big_logo.get_attribute('src'))
    assert_equals('HackerspaceSG', big_logo.get_attribute('title'))
    assert_equals('HackerspaceSG', big_logo.get_attribute('alt'))


@step('I should see hackdo footer')
def footer(step):
    step.given('I should see element with "id" of "push" in page')
    step.given('I should see element with "id" of "footer" in page')
    footer = world.browser.find_element_by_id('footer')
    assert_equals(
        u'made for hackerspacesg | mit licensed | \xa9 %s | contribute'
        % date.today().year,
        footer.text.strip())
# HackDo Function Ends #
