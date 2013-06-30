from django.conf.urls import include, patterns
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

from hado.admin import hdadmin

urlpatterns = patterns(
    '',
    (r'^amedia/jsi18n', 'django.views.i18n.javascript_catalog'),
    (r'^hdadmin/doc/', include('django.contrib.admindocs.urls')),
    (r'^hdadmin/', include(hdadmin.urls)),
    (r'', include('hado.urls')),
    (r'^static/(?P<path>.*)$',
     'django.views.static.serve',
     {'document_root': settings.STATIC_ROOT}),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
