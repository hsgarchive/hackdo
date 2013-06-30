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

# For testing
import sys
if 'test' in sys.argv or 'harvest' in sys.argv:
    import subprocess
    current_branch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
    if current_branch != 'master':
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }

# Site ID, details check fixtures/initial_data.json
SITE_ID = 4

# Debug
DEBUG = True
TEMPLATE_DEBUG = DEBUG
