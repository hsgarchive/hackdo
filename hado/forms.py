# -*- coding: utf-8 -*-
from django import forms
#from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.forms.util import ErrorList
from django.contrib.admin import widgets

import datetime

from hado.models import *

# Found at http://www.smipple.net/snippet/IanLewis/Django%20Callable%20ChoiceField
class CallableChoiceField(forms.ChoiceField):
    """ A ChoiceField that can take a callable"""
    def _get_choices(self):
        if callable(self._choices):
			values = self._choices()
			self._choices = values
			return values
        return self._choices

    def _set_choices(self, value):
        self._choices = self.widget.choices = value

    choices = property(_get_choices, _set_choices)

class PaymentAdminForm(forms.ModelForm):
	
#	def year_range():
#		this_year = datetime.date.today().year
#		years = [ (unicode(this_year), unicode(this_year)) ]
#		
#		for i in xrange(0, 10):
#			years.insert(0, (unicode(this_year-i), unicode(this_year-i)))
#			years.append((unicode(this_year+i), unicode(this_year+i)))
#			
#		return years

#	for_month = forms.ChoiceField(choices=Payment.MONTHS,  initial=unicode(datetime.date.today().month))
	class Meta:
		model = Payment
		
		#exclude = ('for_month', 'for_year')				