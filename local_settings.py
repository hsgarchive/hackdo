# Local settings
import os

# Live site settings (others should override in local_settings.py)
ROOT_PATH = os.path.dirname(__file__)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hackdo',
        'TEST_NAME': 'hackdo_test',
        'USER': 'hackdo',
        'PASSWORD': 'hackdo',
        'HOST': '',
        'PORT': '',
    }
}

import sys
if 'test' in sys.argv or 'harvest' in sys.argv:
    import subprocess
    current_branch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
    if current_branch != 'master':
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
        }

DEBUG = True
TEMPLATE_DEBUG = DEBUG
