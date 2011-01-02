from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import os
ROOT_PATH = os.path.dirname(__file__) # Handy for dynamic paths across Dev and Production

urlpatterns = patterns('',
	# Example:
	# (r'^hackdo/', include('hackdo.foo.urls')),

	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),

	
	(r'', include('hado.urls')),
	# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

)
