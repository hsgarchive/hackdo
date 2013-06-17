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

DEBUG = True
TEMPLATE_DEBUG = DEBUG
