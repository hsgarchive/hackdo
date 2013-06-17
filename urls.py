from django.conf.urls.defaults import include, patterns

from django.contrib import admin
admin.autodiscover()

from hado.admin import hdadmin

urlpatterns = patterns(
    '',
    (r'^amedia/jsi18n', 'django.views.i18n.javascript_catalog'),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(hdadmin.urls)),
    (r'', include('hado.urls')),
)
