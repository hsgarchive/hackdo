import re 

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
	fields = ('date_paid', 'amount', 'contract', 'method', 'desc')
	
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "contract":

			# Assuming we're editing user in the address eg. "/admin/hado/user/3/"
			# So we extract the user_id portion from that path and use it in our queryset filter
			m = re.search("/.+\/(?P<id>\d+)\/?", request.path_info)
			if m is not None:
				user_id = m.groupdict()['id']

			kwargs["queryset"] = Contract.objects.filter(user__id = user_id)
			return db_field.formfield(**kwargs)
		return super(PaymentInline, self).formfield_for_foreignkey(db_field, request, **kwargs)



class TierInline(admin.TabularInline):
	model = Tier

class ContractInline(admin.TabularInline):
	model = Contract
	extra = 0
	inlines = [ PaymentInline, ]

# ModelAdmin classes
class PaymentAdmin(admin.ModelAdmin):
	form = PaymentAdminForm
	fields = ('user', 'contract', 'date_paid', 'amount', 'method', 'desc')
	
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "contract":
		    kwargs["queryset"] = Contract.objects.exclude(status = "TER")
		    return db_field.formfield(**kwargs)
		return super(PaymentAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


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
