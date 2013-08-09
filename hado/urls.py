# -*- coding: utf-8; -*-
from django.conf.urls import patterns, url
from django.conf import settings
from hado.forms import HackDoAuthenticationForm

urlpatterns = patterns(
    '',
    # root url
    url(r'^$', 'hado.views.index', name='index'),
    # auth url
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'authentication_form': HackDoAuthenticationForm}, name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='logout'),
    url(r'^accounts/password-reset/$',
        'django.contrib.auth.views.password_reset',
        {'from_email': settings.DEFAULT_FROM_EMAIL}, name='password_reset'),
    url(r'^accounts/password-reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        name='password_reset_done'),
    url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^accounts/reset/done/$',
        'django.contrib.auth.views.password_reset_complete',
        name='password_reset_complete'),
    url(r'^accounts/register/$', 'hado.views.register', name='register'),
    url(r'^accounts/change-password/$', 'hado.views.change_password', name='change_password'),
    url(r'^accounts/change-email/$', 'hado.views.change_email', name='change_email'),
    url(r'^accounts/change-avatar/$', 'hado.views.change_avatar', name='change_avatar'),
    # pending user
    url(r'^pending-user/$', 'hado.views.pending_user', name='pending_user'),
    # user settings
    url(r'^users/(?P<username>[a-zA-Z0-9]+)/settings',
        'hado.views.user_settings', name='user_settings'),
    # user home
    url(r'^users/(?P<username>[a-zA-Z0-9]+)',
        'hado.views.user_home', name='user_home'),
    # list all contracts
    url(r'^contracts-list/$',
        'hado.views.contracts_list', name='contracts_list'),
    # arrears
    url(r'^arrears/$', 'hado.views.arrears', name='arrears'),
    # user current month invoice
    url(r'^invoice/$', 'hado.views.invoice', name='invoice'),
    # approve membership review ajax
    url(r'^review-membership/(?P<review_id>\d+)/$',
        'hado.views.review_membership', name='review_ajax'),
)
