# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from hado.views import *

urlpatterns = patterns('',

	url(r'^$', index, name='index'),
#
#	# User methods
#	url(r'user/(?P<username>\w+)/?$', user_profile, name="hado.user.show"),
#
	url(r'login/$', 'django.contrib.auth.views.login', {'template_name' : 'user/login.html'}),
	url(r'logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),

	url(r'users/(?P<username>[a-zA-Z0-9]+)/invoice/(?P<year>\d{4})/(?P<month>\d{2})/?', user_invoices, name='user_invoices'),
	url(r'users/(?P<username>[a-zA-Z0-9]+)', user_profile, name='user_profile'),

	url(r'arrears/?$', arrears, name='arrears'),

	url(r'invoice/?$', invoice, name='invoice'),

#
#	url(r'debug/$', debug, name='hado.debug'),

)