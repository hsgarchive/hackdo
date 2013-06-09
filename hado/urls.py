# -*- coding: utf-8; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
from django.conf.urls.defaults import *
from hado.views import *

urlpatterns = patterns('',
url(r'^$', index, name='index'),
url(r'login/$', 'django.contrib.auth.views.login', {'template_name' : 'user/login.html'}),
url(r'logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
url(r'users/(?P<username>[a-zA-Z0-9]+)', user_profile, name='user_profile'),
url(r'arrears/?$', arrears, name='arrears'),
url(r'invoice/?$', invoice, name='invoice'),
)
