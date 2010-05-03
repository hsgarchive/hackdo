from django.contrib import admin
from django.contrib.auth.models import User

admin.site.unregister(User) # Deregister the built-in User model

from sodo.models import  User, Membership, Tier, Payment
admin.site.register(User)
admin.site.register(Membership)
admin.site.register(Tier)
admin.site.register(Payment)