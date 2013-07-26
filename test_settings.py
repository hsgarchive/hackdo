from settings import *
# Lettuce set the DEBUG=False (by default)
# to debug use the --debug-mode or -d option while harvest instead.

# Use testserver site
SITE_ID = 3

# Remove not needed apps in testing
OMMITED_APPS = (
    'south',
)
INSTALLED_APPS = tuple(i for i in INSTALLED_APPS if i not in OMMITED_APPS)

# lettuce settings
LETTUCE_SERVER_PORT = 8924
LETTUCE_APPS = (
    'hado',
)

# test browser (firefox, chrome, PhantomJS)
# NOTE:
# to use chrome you need install chrome driver
# to use PhantomJS you need install PhantomJS driver
PREFERRED_WEBDRIVER = 'chrome'

# databse settings
if not IS_MASTER_BRANCH:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_hackdo',
    }
