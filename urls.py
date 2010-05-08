from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^hackdo/', include('hackdo.foo.urls')),
	
	(r'', include('hado.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

# Serve static files in DEBUG = TRUE environment
if settings.DEBUG:
    urlpatterns = urlpatterns + patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/ruiwen/Projects/HackDo/hackdo/media/', 'show_indexes': True}),
    )