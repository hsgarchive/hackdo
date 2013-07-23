# Local settings

# Live site settings for ROOT PATH
import os
ROOT_PATH = os.path.dirname(__file__)

# Allowed hosts
# Change to server url
ALLOWED_HOSTS = ['*']

import dj_database_url

# For sqlite3
# Use memory: sqlite://:memory:
# Use file: sqlite:////full_path/file.sqlite
DATABASES = {'default': dj_database_url.parse(
    'sqlite://:memory:')}

# For mysql
'''
DATABASES = {'default': dj_database_url.parse(
    'mysql://user:password@host:port/database')}
'''

# For postgresql
'''
DATABASES = {'default': dj_database_url.parse(
    'postgres://user:password@host:port/database')}
'''

#EMAIL_HOST_USER = 'user here'
#EMAIL_HOST_PASSWORD = 'password here'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# use localhost
SITE_ID = 4

# Enable Debug mode
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# django_coverage settings
COVERAGE_USE_CACHE = True
COVERAGE_CUSTOM_REPORTS = False
COVERAGE_REPORT_HTML_OUTPUT_DIR = "%s/coverage_report/" % ROOT_PATH
