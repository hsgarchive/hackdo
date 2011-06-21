# -*- coding: utf-8 -*-
from django import forms
#from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.forms.util import ErrorList
from django.contrib.admin import widgets

import datetime

from hado.models import *

class PaymentFormAdmin(forms.ModelForm):
	class Meta:
		model = Payment
		
	def clean(self):
		cd = self.cleaned_data

		if cd.get('contract'):
			if cd.get('user') and cd.get('user') != cd.get('contract').user:
				self._errors['user'] = self.error_class([_('Payment User does not match the Contract User.')])
				self._errors['contract'] = self.error_class([_('Payment User does not match the Contract User.')])

# 			if (cd.get('amount') % cd.get('contract').tier.fee) != 0:
# 				self._errors['amount'] = self.error_class([_('Payment amount ($%s) is not a clean multiple of Contract Fee ($%s)' % (cd.get('amount'), cd.get('contract').tier.fee))])
				
		return cd
		
		

class PaymentForm(PaymentFormAdmin):

	class Meta:
		model = Payment
		exclude = ['user', 'verified'] # Hide the 'verified' field from the User

	def __init__(self, by_user=None, *args, **kwargs):
		super(PaymentForm, self).__init__(*args, **kwargs)
		self.fields['date_paid'].widget = widgets.AdminDateWidget()
		if by_user is not None:
			self.fields['contract'] = forms.ModelChoiceField(queryset=Contract.objects.filter(user__username=by_user).exclude(status='TER').order_by('-start'), empty_label=None)

		
