# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.shortcuts import *
from utils import render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Models
from hado.models import *
from hado.forms import PaymentForm



@login_required
def index(request):
	return HttpResponseRedirect(request.user.get_absolute_url())


@login_required
def user_profile(request, username):

	if not request.user.username == username:
		return HttpResponseRedirect(request.user.get_absolute_url())
	
	u = User.objects.get(username=username)
	contracts = u.contracts.all().order_by("ctype")
	
	paid_to_date = u.total_paid()
	
	# Calculate total account balance
	account_balance = 0.0
	for c in contracts:
		account_balance += c.balance()
	
	# Retrieve payment history
	payment_history = u.payments_made.order_by('-date_paid')
	
	# Form for submitting payment
	if request.method == 'POST':
		pform = PaymentForm(u.username, request.POST)
		if pform.is_valid():
			p = pform.save(commit=False)
			p.user = request.user
			p.save()
			
			# Create a new form now that the previous entry has been saved
			pform = PaymentForm(u.username)
			
			# On success, add a note
			messages.success(request, "Payment submitted for verification")
	else:		
		# Create a new form
		pform = PaymentForm(u.username)
	
	return render(request, 'user/profile.html', {'u':u, 'contracts':contracts, 'paid_to_date': paid_to_date, "account_balance": account_balance, "payment_history": payment_history, 'pform': pform })
