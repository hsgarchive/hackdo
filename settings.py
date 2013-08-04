DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('wgx731', 'wgx731@gmail.com'),
)

MANAGERS = ADMINS

TIME_ZONE = 'Asia/Singapore'

LANGUAGE_CODE = 'en-us'

# sites:
# 1. hackdo.hackerspace.sg (main)
# 2. hackdo.herokuapp.com (heroku)
# 3. 127.0.0.1:8924 (test)
# 4. 127.0.0.1:8000 (local)
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'overwrite in local_settings.py'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'south',
    'django_coverage',
    'django_extensions',
    'lettuce.django',

    'hado',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/hado.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'NOTSET',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

AUTH_USER_MODEL = 'hado.HackDoUser'
LOGIN_REDIRECT_URL = '/'

# Email Settings
DEFAULT_FROM_EMAIL = 'no-reply@hackspace.sg'
SERVER_EMAIL = 'admin@hackspace.sg'
EMAIL_SUBJECT_PREFIX = '[Hackspace HackDo]'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587

# Task Dispatch UID PREFIX
DISPATCH_UID_PREFIX = 'hado.tasks'

import os
# ROOT_PATH, DATABASES will be override in local_settings.py
ROOT_PATH = os.path.dirname(__file__)

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES = {'default': dj_database_url.config()}

import subprocess
try:
    current_branch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
except Exception:
    IS_MASTER_BRANCH = True
else:
    if current_branch == 'master':
        IS_MASTER_BRANCH = True
    else:
        IS_MASTER_BRANCH = False

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "hado.context_processors.globals",
)

# Django settings for hackdo project.
try:
    LOCAL_SETTINGS
except NameError:
    try:
        from local_settings import *
    except ImportError:
        pass

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = "%s/hado/media/" % ROOT_PATH

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory that holds static files.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '%s/static/' % ROOT_PATH

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# A list of locations of additional static files
STATICFILES_DIRS = (
    ('js', '%s/static/js' % ROOT_PATH),
    ('css', '%s/static/css' % ROOT_PATH),
    ('misc', '%s/static/misc' % ROOT_PATH),
    ('img', '%s/static/img' % ROOT_PATH)
)

TEMPLATE_DIRS = (
    "%s/templates" % ROOT_PATH,
    "%s/hado/templates" % ROOT_PATH,
)

# django_coverage settings
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'common.views.test', '__init__', 'django',
    'migrations', 'fixtures', 'templates', 'wsgi$',
    'features', 'media']
COVERAGE_CODE_EXCLUDES = [
    'def get_absolute_url\(self\):',
    'from .* import .*', 'import .*', ]
COVERAGE_USE_STDOUT = True

# if not on master, change database to sqlite3 for testing
import sys
if any(['test' in sys.argv,
        'test_coverage' in sys.argv]):
    if not IS_MASTER_BRANCH:
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
