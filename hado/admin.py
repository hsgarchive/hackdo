from django.contrib import admin
from django.contrib.auth.models import User
from django import forms


admin.site.unregister(User) # Deregister the built-in User model

import datetime
from hado.models import  *
from hado.forms import *


# Inline classes
class PaymentInline(admin.TabularInline):
	model = Payment
	extra = 0


class TierInline(admin.TabularInline):
	model = Tier

class ContractInline(admin.TabularInline):
	model = Contract
	extra = 0
	inlines = [ PaymentInline, ]


# ModelAdmin classes
class PaymentAdmin(admin.ModelAdmin):
	form = PaymentAdminForm


class ContractAdmin(admin.ModelAdmin):
	inlines = [ PaymentInline, ]


class UserAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'email')
	list_display_links = ('__unicode__',)
	inlines = [ ContractInline, PaymentInline ]
	fieldsets = (
		(None, {
			'fields': ('username', ('first_name', 'last_name'), 'email')
		}),
	)


admin.site.register(User, UserAdmin)
admin.site.register(ContractType)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Tier)
admin.site.register(Payment, PaymentAdmin)