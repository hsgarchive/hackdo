# -*- coding: utf-8; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
import re

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import (
    UserCreationForm, UserChangeForm
)
from django import forms

import datetime
from hado.models import  *
from hado.forms import *
from hado.admin_site import HackdoAdmin

hdadmin = HackdoAdmin()

# Inline classes
class PaymentInline(admin.TabularInline):
    model = Payment
    form = PaymentFormAdmin
    extra = 1

    fields = ('date_paid', 'amount', 'contract', 'method', 'desc', 'verified')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "contract":

            # Assuming we're editing user in the address eg.
            # "/admin/hado/user/3/"
            # So we extract the user_id portion from that path and use it in our
            # queryset filter
            m = re.search("/.+\/(?P<id>\d+)\/?", request.path_info)
            if m is not None:
                user_id = m.group('id')
                kwargs["queryset"] = Contract.objects.filter(user__id = user_id)
                #.exclude(status = "TER")
                return db_field.formfield(**kwargs)
        return super(PaymentInline, self).formfield_for_foreignkey(db_field,
                                                                   request,
                                                                   **kwargs)



class TierInline(admin.TabularInline):
    model = Tier

class ContractInline(admin.TabularInline):
    model = Contract
    extra = 0
    inlines = [ PaymentInline, ]

# ModelAdmin classes
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentFormAdmin

    fieldsets = (
        (None, {
            'fields': ('user', ('date_paid', 'amount', 'contract', 'method'),
                       'desc', 'verified')
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "contract":
            # Assuming we're editing user in the address eg.
            # "/admin/hado/user/3/"
            # So we extract the user_id portion from that path and use it in our
            # queryset filter
            m = re.search("/.+\/(?P<id>\d+)\/?$", request.path_info)
            if m is not None:
                pid = m.group('id')
                kwargs["queryset"] = Contract.objects.filter(
                    user__id=Payment.objects.get(id=pid).user_id)
                #.exclude(status = "TER")
                kwargs['empty_label'] = None
                return db_field.formfield(**kwargs)
        return super(PaymentAdmin, self).formfield_for_foreignkey(db_field,
                                                                  request,
                                                                  **kwargs)


class ContractAdmin(admin.ModelAdmin):
    inlines = [ PaymentInline, ]


class HackDoUserCreationForm(UserCreationForm):

    class Meta:
        model = HackDoUser
        fields = ('username', 'email', )

class HackDoUserChangeForm(UserChangeForm):

    class Meta:
        # TODO: Find a better way to add all required fields into the form
        model = HackDoUser
        fields = (
            'username', 'email', 'is_active', 
            'first_name', 'last_name', 'groups',
            'is_staff', 'is_superuser', 'is_hackdo_admin',
            'user_permissions', 'last_login', 'date_joined',
        )

class HackDoUserAdmin(UserAdmin):
    form = HackDoUserChangeForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 
                                       'is_hackdo_admin', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
        ),
    )
    inlines = [ ContractInline, PaymentInline ]


hdadmin.register(HackDoUser, HackDoUserAdmin)
hdadmin.register(ContractType)
hdadmin.register(Contract, ContractAdmin)
hdadmin.register(Tier)
hdadmin.register(Payment, PaymentAdmin)
