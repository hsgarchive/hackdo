# Local settings
import os

# Live site settings (others should override in local_settings.py)
ROOT_PATH = os.path.dirname(__file__)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'hackdo', # Or path to database file if using sqlite3.
        'TEST_NAME': 'hackdo_test',
        'USER': 'hackdo', # Not used with sqlite3.
        'PASSWORD': 'hackdo', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

DEBUG = True
TEMPLATE_DEBUG = DEBUG
