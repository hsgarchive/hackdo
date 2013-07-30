# -*- coding: utf-8; -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from hado.models import Payment, Contract, Tier,\
    ContractType, MembershipReview
from hado.forms import PaymentFormAdmin, HackDoUserCreationForm,\
    HackDoUserChangeForm
from hado.admin_site import HackdoAdmin

hdadmin = HackdoAdmin()
User = get_user_model()


# Inline classes
class PaymentInline(admin.TabularInline):
    model = Payment
    form = PaymentFormAdmin
    extra = 1

    fields = ('date_paid', 'amount', 'contract', 'method', 'desc', 'verified')
    raw_id_fields = ('contract',)


class TierInline(admin.TabularInline):
    model = Tier


class ContractInline(admin.TabularInline):
    model = Contract
    extra = 0
    inlines = [PaymentInline, ]


# ModelAdmin classes
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentFormAdmin
    fieldsets = (
        (None, {
            'fields': ('user', ('date_paid', 'amount', 'method', 'contract', ),
                       'desc', 'verified')
        }),
    )
    raw_id_fields = ('contract', 'user')


class ContractAdmin(admin.ModelAdmin):
    inlines = [PaymentInline, ]
    raw_id_fields = ('user',)
    search_fields = [
        'ctype__desc', 'tier__desc', 'user__username', 'user__email']


class HackDoUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2')
        }),
    )
    add_form = HackDoUserCreationForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'email',
            'profile_image', 'is_gravatar_enabled',
        )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    form = HackDoUserChangeForm
    list_display = ('username', 'email', 'is_staff', 'is_superuser',
                    'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    inlines = [ContractInline, PaymentInline, ]
    readonly_fields = ['last_login', 'date_joined']


class MembershipReviewAdmin(admin.ModelAdmin):
    raw_id_fields = ('applicant', 'referrer')
    list_display = ('applicant', 'referrer', 'reviewed')
    search_fields = ['applicant__username']


hdadmin.register(User, HackDoUserAdmin)
hdadmin.register(Contract, ContractAdmin)
hdadmin.register(Payment, PaymentAdmin)
hdadmin.register(MembershipReview, MembershipReviewAdmin)
hdadmin.register(ContractType)
hdadmin.register(Tier)
