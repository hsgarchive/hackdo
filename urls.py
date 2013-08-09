from django.conf.urls import include, patterns, url
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib import admin
admin.autodiscover()

from hado.admin import hdadmin

urlpatterns = patterns(
    '',
    (r'^amedia/jsi18n', 'django.views.i18n.javascript_catalog'),
    (r'^hdadmin/doc/', include('django.contrib.admindocs.urls')),
    (r'^hdadmin/hado/$',
        lambda x: HttpResponseRedirect(reverse('admin:index'))),
    url(r'^hdadmin/payment-verify/$',
        hdadmin.payment_verify,
        name='payment_verify'),
    url(r'^hdadmin/user-active/$',
        hdadmin.user_active,
        name='user_active'),
    (r'^hdadmin/', include(hdadmin.urls)),
    (r'', include('hado.urls')),
    (r'^static/(?P<path>.*)$',
     'django.views.static.serve',
     {'document_root': settings.STATIC_ROOT}),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
