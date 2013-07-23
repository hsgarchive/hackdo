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
PREFERRED_WEBDRIVER = 'zope.testbrowser'

# databse settings
import subprocess
current_branch = subprocess.check_output(
    ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
if current_branch != 'master':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_hackdo',
    }
