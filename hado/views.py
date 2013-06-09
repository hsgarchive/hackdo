# -*- coding: utf-8; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.shortcuts import *
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model

# Models
from hado.models import *
from hado.forms import PaymentForm

import itertools
import json

User = get_user_model()

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

    return render(request, 'user/profile.html',
                  {'u': u,
                   'contracts':contracts,
                   'paid_to_date': paid_to_date,
                   'account_balance': account_balance,
                   'payment_history': payment_history,
                   'pform': pform})


@login_required
def arrears(request):
    '''Calculate arrears for all members'''

    # Find all current, ie. non-terminated Contracts, sorted by member
    contracts = Contract.objects.exclude(Q(status='PEN')) \
            .select_related('user', 'ctype', 'tier') \
            .order_by('user__first_name')

    return render(request, 'reports/arrears.html', {'contracts': contracts})


def invoice(request):
    '''Returns a JSON list of members, their monthly fee, and past arrears'''

    # Find all current, ie. non-terminated Contracts, sorted by member
    contracts = Contract.objects.exclude(Q(status='PEN')|Q(status='TER')) \
            .select_related('user', 'ctype', 'tier') \
            .order_by('-start') \
            .order_by('user__first_name')

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
            ud['monthly'] = k.user._User__latest_membership.tier.fee \
                    if hasattr(k.user, '_User__latest_membership') \
                    else "N/A"
            users.append(ud)

    return HttpResponse(json.dumps(users, indent=4),
                        content_type='application/json')
