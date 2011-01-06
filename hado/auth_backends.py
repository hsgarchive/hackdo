from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model
from django.contrib.auth.models import User as oUser

from hado.models import User as cUser

class UserModelBackend(ModelBackend):
	def authenticate(self, username=None, password=None):
		try:
			user = self.user_class.objects.get(username=username)
			if user.check_password(password):
				return user
		except self.user_class.DoesNotExist:
			try:
				ouser = oUser.objects.get(username=username)
				u = cUser()
				
				if ouser.check_password(password):
					u.password = ouser.password
				else:
					return None # Abort
				
				# Clone the User				
				u.id = ouser.id
				u.username = ouser.username
				u.first_name = ouser.first_name
				u.last_name = ouser.last_name
				u.email = ouser.email
				u.is_active = ouser.is_active				
				u.is_staff = ouser.is_staff
				u.is_superuser = ouser.is_superuser
				u.last_login = ouser.last_login
				u.date_joined = ouser.date_joined
				
				# Perform the switch over
				ouser.delete()
				u.save()
				
				return u

			except oUser.DoesNotExist:
				return None


	def get_user(self, user_id):
		try:
			return self.user_class.objects.get(pk=user_id)
		except self.user_class.DoesNotExist:
			return None

	@property
	def user_class(self):
		if not hasattr(self, '_user_class'):
			self._user_class = get_model(*settings.CUSTOM_USER_MODEL.split('.', 2))
			if not self._user_class:
				raise ImproperlyConfigured('Could not get custom user model')
		return self._user_class