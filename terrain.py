from lettuce import before, after, world
from selenium import webdriver

from django.db import transaction
from django.core.management import call_command
from django.conf import settings
from lettuce.django import mail

import Queue

import logging
logger = logging.getLogger("hado.lettuce")


def start_browser():
    driver = getattr(settings, 'PREFERRED_WEBDRIVER', 'firefox')
    if driver == 'firefox':
        world.browser = webdriver.Firefox()
    elif driver == 'chrome':
        world.browser = webdriver.Chrome()
    else:
        raise NotImplementedError('driver not implement yet. :(')
    world.browser.maximize_window()


def clear_outbox():
    while 1:
        try:
            mail.queue.get(timeout=1)
        except Queue.Empty:
            break


@transaction.commit_manually
def flush_transaction():
    # stale data here, so flush current transaction to get the latest.
    transaction.commit()


@before.handle_request
def override_email_backend(httpd, server):
    settings.EMAIL_BACKEND = 'lettuce.django.mail.backends.QueueEmailBackend'


@before.harvest
def initial_setup(server):
    call_command('syncdb', interactive=False, verbosity=0)


@after.harvest
def cleanup(server):
    call_command('flush', interactive=False, verbosity=0)


@before.each_scenario
def before_scenario(scenario):
    clear_outbox()


@after.each_scenario
def after_scenario(scenario):
    call_command('flush', interactive=False, verbosity=0)


@before.each_feature
def before_feature(feature):
    start_browser()


@after.each_feature
def after_feature(feature):
    world.browser.quit()


@after.all
def teardown_browser(total):
    try:
        world.browser.quit()
    except:
        pass  # browser probably already shut down
