# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
#from ragendja.template import render_to_response
from django.shortcuts import *
from utils import render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout

# Models
from hado.models import *
from hado.forms import PaymentForm


def index(request):
	
	userlist = User.objects.all()
	
	return render(request, 'index.html', {'userlist': userlist})


def user_profile(request, username):
	
	u = User.objects.get(username=username)
	contracts = u.contracts.all().order_by("ctype")
	member_since = u.contracts.filter(ctype__desc='Membership').order_by('start')[0].start
	current_status = u.contracts.filter(ctype__desc='Membership').order_by('-start')[0].get_status_display()
	
	paid_to_date = u.total_paid()
	
	# Retrieve 10 most recent payments
	payment_history = u.payments_made.order_by('-date_paid')[0:10]
	
	# Form for submitting payment
	pform = PaymentForm(username, initial={'user':u})
	
	return render(request, 'user/profile.html', {'u':u, 'contracts':contracts, 'member_since':member_since, 'current_status': current_status, 'paid_to_date': paid_to_date, "payment_history": payment_history, 'pform': pform })
