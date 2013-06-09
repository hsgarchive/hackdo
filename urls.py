from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from hado.admin import hdadmin

urlpatterns = patterns(
    '',
    (r'^amedia/jsi18n', 'django.views.i18n.javascript_catalog'),

    (r'^admin/', include(hdadmin.urls)),
    (r'', include('hado.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
)
