# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest
from django.utils.translation import ugettext as _
from django.shortcuts import *
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

# Models
from hado.models import *
from hado.forms import PaymentForm

import itertools
import json
import calendar

from dateutil.relativedelta import relativedelta


@login_required
def index(request):
	return HttpResponseRedirect(request.user.get_absolute_url())


@login_required
def user_profile(request, username):

	if not request.user.is_superuser and request.user.username != username:
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


@login_required
def arrears(request):
	'''Calculate arrears for all members'''

	# Find all current, ie. non-terminated Contracts, sorted by member
	contracts = Contract.objects.exclude(Q(status='PEN')).select_related('user', 'ctype', 'tier').order_by('user__first_name')

	return render(request, 'reports/arrears.html', {'contracts': contracts})


@login_required
def user_invoices(request, username, year, month):

	# Provided we are either admins or the proper user
	if not request.user.is_superuser and request.user.username != username:
		return HttpResponseRedirect(request.user.get_absolute_url())

	try:
		# For the given user
		u = User.objects.get(username=username) if request.user.username != username else request.user

		# For the given month and year,
		try:
			year = int(year)
			month = int(month)

			# Normalize date to beginning of the month
			this_month = datetime.date(year, month, 1)

		except ValueError as e:
			return HttpResponseBadRequest("Malformed date request")

		try:
			invoice = Invoice.objects.select_related('currency').get(
				client=u, date_for=this_month)
			item_sum = invoice.items.aggregate(sum=Sum('amount'))['sum']

		except Invoice.DoesNotExist:
			currency = Currency.objects.get_or_create(abbrev='SGD')[0]
			invoice = Invoice.objects.create(client=u,
			                                 currency=currency,
			                                 date_for=this_month,
			                                 date_issued=datetime.date.today(),
			                                 tax=0)

			active_contracts = u.contracts.select_related('ctype', 'tier') \
			    .filter(start__lte=this_month) \
			    .exclude(status='TER') \
			    .exclude(status='PEN')
			item_sum = 0
			for contract in active_contracts:
				item_sum += contract.tier.fee
				invoice.items.create(desc=contract.ctype.desc,
				                     amount=contract.tier.fee,
				                     contract=contract)

		# Render to template
		data = {
			'id': invoice.visible_id,
			'client': u,
			'currency': invoice.currency,
			'date_requested': invoice.date_for,
			'date_issued': invoice.date_issued,
			'date_due': invoice.date_due,
			'items': invoice.items.all(),
			'item_sum': item_sum,
			'tax': invoice.tax,
			'vendor': {
				'name': "Hackerspace.SG Pte Ltd",
				'registration': "200919232E",
				'bank': {
					'number': 7144,
					'branch': '057',
					'account': 5701304090
				},
				'address': "70A Bussorah Street<br>Singapore 199483"
			}

		}

		return render(request, 'invoices/invoice.html', {'data': data})

	except User.DoesNotExist as e:
		return HttpResponseNotFound("User not found")


def invoice(request):
	'''Returns a JSON list of members, their monthly fee, and past arrears'''

	# Find all current, ie. non-terminated Contracts, sorted by member
	contracts = Contract.objects.exclude(Q(status='PEN')|Q(status='TER')).select_related('user', 'ctype', 'tier').order_by('-start').order_by('user__first_name')

	users = []

	cc = itertools.groupby(contracts, key=lambda x: x.user.get_full_name())
	for c in cc:
		ud = {} # User detail dictionary
		ud['name'] = c[0]
		ud['contracts'] = []
		for k in c[1]: # c[1] is the iterator of Contracts for this User
			ud['contracts'].append({
					'contract': k.tier.desc,
					'fee': k.tier.fee,
					'balance': k.balance(),
					'start': unicode(k.start),
					'end': unicode(k.end) if k.end else "N/A"
				})
		ud['id'] = k.user.id
		ud['email'] = k.user.email # Use the last instance of k
		ud['membership_status'] = k.user.membership_status(pretty=True)
		ud['monthly'] = k.user._User__latest_membership.tier.fee if hasattr(k.user, '_User__latest_membership') else "N/A"
		users.append(ud)


	return HttpResponse(json.dumps(users, indent=4), content_type='application/json')

