from settings import *

# Lettuce set the DEBUG=False (by default)
# to debug use the --debug-mode or -d option while harvest instead.

SOUTH_TESTS_MIGRATE = False
TEST_NAME = 'test_' + DATABASES['default']['NAME']

DATABASES['default']['NAME'] = TEST_NAME

LETTUCE_APPS = (
    'hado',
)

PIPELINE_ENABLED = False
