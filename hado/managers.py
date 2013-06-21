from django.utils import timezone
from django.contrib.auth.models import BaseUserManager


class HackDoUserManager(BaseUserManager):
    """
    username, email and password are required.
    """

    def get_user_unsaved(self, username, email, password, **extra_fields):
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=False, his_active=False, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        u = self.get_user_unsaved(username, email, password, **extra_fields)
        u.save(using=self._db)
        return u

    def create_superuser(self, username, email, password, **extra_fields):
        """
        Creates and saves a Super User with the given username,
        email and password.
        """
        u = self.get_user_unsaved(username, email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u
