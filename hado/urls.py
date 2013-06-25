# -*- coding: utf-8; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
from django.conf.urls import patterns, url
from hado.forms import HackDoAuthenticationForm

urlpatterns = patterns(
    '',
    # root url
    url(r'^$', 'hado.views.index', name='index'),
    # auth url
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'authentication_form': HackDoAuthenticationForm}, name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    url(r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^accounts/password_reset/done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^accounts/reset/done/$', 'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),
    url(r'^accounts/register/$', 'hado.views.register', name='register'),
    # pending user
    url(r'^pending_user/?$', 'hado.views.pending_user', name='pending_user'),
    # user profile
    url(r'^users/(?P<username>[a-zA-Z0-9]+)',
        'hado.views.user_profile', name='user_profile'),
    # arrears
    url(r'^arrears/?$', 'hado.views.arrears', name='arrears'),
    # invoice
    url(r'^invoice/?$', 'hado.views.invoice', name='invoice'),
    # approve membership review ajax
    url(r'^review_membership/(?P<review_id>\d+)/$', 'hado.views.review_membership', name='review_ajax'),
)
