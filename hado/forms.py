# -*- coding: utf-8 -*-
from django import forms
#from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.forms.util import ErrorList
from django.contrib.admin import widgets

import datetime

from hado.models import *

class PaymentForm(forms.ModelForm):
	class Meta:
		model = Payment
		
	def clean(self):
		cd = self.cleaned_data

		if cd.get('contract'):
			if cd.get('user') and cd.get('user') != cd.get('contract').user:
				self._errors['user'] = self.error_class([_('Payment User does not match the Contract User.')])
				self._errors['contract'] = self.error_class([_('Payment User does not match the Contract User.')])

			if (cd.get('amount') % cd.get('contract').tier.fee) != 0:
				self._errors['amount'] = self.error_class([_('Payment amount ($%s) is not a clean multiple of Contract Fee ($%s)' % (cd.get('amount'), cd.get('contract').tier.fee))])
				
		return cd