# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from hado.views import *

urlpatterns = patterns('',

	url(r'^$', index, name='hado.index'),	
#	
#	# User methods
#	url(r'user/(?P<username>\w+)/?$', user_profile, name="hado.user.show"),
#	
	url(r'login/$', 'django.contrib.auth.views.login', {'template_name' : 'user/login.html'}),
	url(r'logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
#	
#	url(r'debug/$', debug, name='hado.debug'),

)