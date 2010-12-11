from django.core.management import setup_environ
from os.path import abspath, dirname, join
import sys

CURRENT_DIR = dirname(__file__)

sys.path.insert(0, abspath(join(CURRENT_DIR, '..', '..')))

import settings
setup_environ(settings)

from hado.models import User

def create_superuser(username, password):
	try:
		u = User()
		u.username = username
		u.set_password(password)
		u.is_superuser = True
		u.is_staff = True
		u.save()
		print 'User created.'
	except:
		print 'Error has occurred. User was not created.'
	
if __name__ == '__main__':
	username = raw_input('Enter username:')
	password = raw_input('Enter password:')
	create_superuser(username,password)