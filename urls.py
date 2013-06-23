from django.conf.urls import include, patterns

from django.contrib import admin
admin.autodiscover()

from hado.admin import hdadmin

urlpatterns = patterns(
    '',
    (r'^amedia/jsi18n', 'django.views.i18n.javascript_catalog'),
    (r'^hdadmin/doc/', include('django.contrib.admindocs.urls')),
    (r'^hdadmin/', include(hdadmin.urls)),
    (r'', include('hado.urls')),
)
