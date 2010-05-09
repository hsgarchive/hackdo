# -*- coding: utf-8 -*-
from django import forms
#from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.forms.util import ErrorList
from django.contrib.admin import widgets

import datetime

from hado.models import *

class PaymentAdminForm(forms.ModelForm):
	class Meta:
		model = Payment
