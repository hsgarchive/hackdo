# -*- coding: utf-8; -*-
from django.http import HttpResponseRedirect, HttpResponse,\
    HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import get_template
from django.template import Context

# Models
from hado.models import Contract, MembershipReview, Payment
from hado.forms import PaymentForm, NewAccountForm, HackDoPasswordChangeForm

from datetime import datetime
from dateutil.relativedelta import relativedelta
import itertools
import json
import xhtml2pdf.pisa as pisa
import cStringIO as StringIO
import cgi

import logging
logger = logging.getLogger("hado.views")

User = get_user_model()


# Login Required Views
@login_required
def index(request):
    """
    Root route:

    if user is verified - redirect to :view:`hado.user_home`

    else - redirect to :view:`hado.pending_user`
    """
    if request.user.is_superuser:
        return HttpResponseRedirect(reverse('admin:index'))
    elif request.user.is_active:
        return HttpResponseRedirect(request.user.get_absolute_url())
    return HttpResponseRedirect(reverse('pending_user'))


@login_required
def pending_user(request):
    """
    display :model:`hado.MembershipReview` status for current pending user

    **Context**

    ``RequestContext``

    ``reviews``

    Instances of :model:`hado.MemberRequest` contains user as applicant

    **Template:**

    :template:`user/pending_user.html`
    """
    template = 'user/pending_user.html'
    u = request.user
    if u.is_active:
        return HttpResponseRedirect(u.get_absolute_url())
    reviews = MembershipReview.objects.filter(applicant=u).all()
    return render(request, template,
                  {'reviews': reviews, })


@login_required
@ensure_csrf_cookie
def user_home(request, username):
    """
    User profile page, display :model:`hado.HackDoUser`

    if user is verified - display related :model:`hado.Contract`

    else - display related :model:`hado.MemberRequest`

    **Context**

    ``RequestContext``

    ``u``

    An instance of :model:`hado.HackDoUser`

    *user not verified:*

    ``member_req``

    Instance of :model:`hado.MemberRequest` related to user

    *user verified:*

    ``contracts``

    Instances of :model:`hado.Contract` related to user

    ``reviews``

    Instances of :model:`hado.MemberRequest` contains user as referrer

    ``paid_to_date``

    User contract end date

    ``account_balance``

    User account balance

    ``payment_history``

    Instances of :model:`hado.Payment` related to user

    ``pform``

    New payment form

    **Template:**

    :template:`user/profile.html`
    """
    template = 'user/profile.html'
    u = request.user
    if not u.is_active:
        return HttpResponseRedirect(reverse('pending_user'))

    if u.username != username:
        logger.info("user %s tried to access users/%s" % (u, username))
        return HttpResponseRedirect(u.get_absolute_url())

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

    # Membership Review request for current user as referrer
    reviews = MembershipReview.objects.filter(referrer=request.user).all()

    return render(request, template,
                  {'u': u,
                   'contracts': contracts,
                   'reviews': reviews,
                   'paid_to_date': paid_to_date,
                   'account_balance': account_balance,
                   'payment_history': payment_history,
                   'pform': pform})


@login_required
def user_settings(request, username=''):
    """
    User change email, password and TODO: avatar link.

    **Context**

    ``RequestContext``

    ``pcform``

    password change form

    ``pc_errors``

    password change form errors

    **Template:**

    :template:`user/settings.html`
    """
    #TODO:Allow user to have avatar just for hackdo, allow user to change email
    template = 'user/settings.html'
    user = request.user
    pc_errors = []
    if request.method == 'POST':
        pcform = HackDoPasswordChangeForm(user=user, data=request.POST)
        pc_errors = pcform.errors
        if pcform.is_valid():
            pcform.save()
            messages.success(
                request, "User %s's password successfully changed."
                % (user.username))
            return HttpResponseRedirect(reverse('logout'))
    pcform = HackDoPasswordChangeForm(user=user)
    return render(request, template,
                  {'pcform': pcform,
                   'pc_errors': pc_errors, })


@login_required
def invoice(request):
    """
    Return user current month verified payments invoice (type[json,html,pdf])

    **Context**

    ``RequestContext``

    ``payments``

    Instances of user current month verified :model:`hado.Payment`

    **Template:**

    :template:`reports/invoice.html`
    """
    template = 'reports/invoice.html'

    output = request.GET.get('type', 'html')
    now = datetime.now()
    first_day = datetime(now.year, now.month, 1)
    last_day = now + relativedelta(days=31)
    payments = Payment.objects.filter(
        verified='VFD',
        date_paid__lte=last_day,
        date_paid__gte=first_day,
    )
    context_dic = {'payments': payments}
    if output == 'pdf':
        return _render_to_pdf(template, context_dic)
    elif output == 'json':
        payments_json = []
        for p in payments:
            payment_json = {}
            payment_json['date_paid'] = unicode(p.date_paid)
            payment_json['amount'] = p.amount
            payment_json['method'] = p.method
            payment_json['contract'] = unicode(p.contract)
            payment_json['description'] = p.desc
            payment_json['user'] = unicode(p.user)
            payments_json.append(payment_json)
        return HttpResponse(
            json.dumps(payments_json, indent=4, sort_keys=True),
            mimetype='application/json',
            content_type='application/json')
    else:
        return render(request, template, context_dic)


def _render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(
        StringIO.StringIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(
            result.getvalue(), mimetype='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>'
                        % cgi.escape(html))


#TODO: Finish arrears
@login_required
def arrears(request):
    """
    Calculate arrears for all members

    **Context**

    ``RequestContext``

    ``contracts``

    Instances of :model:`hado.Contract` related to user

    **Template:**

    :template:`reports/arrears.html`
    """
    template = 'reports/arrears.html'

    # Find all current, ie. non-terminated Contracts, sorted by member
    contracts = Contract.objects.exclude(Q(status='PEN'))\
        .select_related('user', 'ctype', 'tier') \
        .order_by('user__first_name')

    return render(request, template, {'contracts': contracts})


@staff_member_required
def contracts_list(request):
    """
    Returns a JSON list of members, their monthly fee, and past arrears
    """
    # Find all current, ie. non-terminated Contracts, sorted by member
    contracts = Contract.objects.exclude(Q(status='PEN') | Q(status='TER')) \
        .select_related('user', 'ctype', 'tier') \
        .order_by('-start') \
        .order_by('user__first_name')

    users = []

    cc = itertools.groupby(contracts, key=lambda x: unicode(x.user))
    for c in cc:
        ud = {}  # User detail dictionary
        ud['name'] = c[0]
        ud['contracts'] = []
        for k in c[1]:  # c[1] is the iterator of Contracts for this User
            ud['contracts'].append({
                'contract': k.tier.desc,
                'fee': k.tier.fee,
                'balance': k.balance(),
                'start': unicode(k.start),
                'end': unicode(k.end) if k.end else "N/A"
            })
            ud['id'] = k.user.id
            ud['email'] = k.user.email  # Use the last instance of k
            ud['membership_status'] = k.user.membership_status(pretty=True)
            ud['monthly'] = k.user._User__latest_membership.tier.fee \
                if hasattr(k.user, '_User__latest_membership') \
                else "N/A"
            users.append(ud)

    return HttpResponse(
        json.dumps(users, indent=4, sort_keys=True),
        mimetype='application/json',
        content_type='application/json')


# Ajax Views
def review_membership(request, review_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(permitted_methods=('POST',))
    success = True
    errors = {}
    try:
        review = MembershipReview.objects.get(pk=review_id)
    except MembershipReview.DoesNotExist:
        success = False
        errors['message'] = "Can't find membership review"
        logger.info("Can't find membership review with id %s"
                    % (review_id))
        return _generate_ajax_response(request, success, errors)
    review.reviewed = True
    try:
        review.save()
    except Exception as e:
        logger.error("Error: %s" % (e))
        success = False
        errors['message'] = "Error saving membership review"
        return _generate_ajax_response(request, success, errors)
    else:
        return _generate_ajax_response(request, success, errors)


# TODO: move helper functions out of views
def _generate_ajax_response(request, success, errors,
                            data=None, redirect_url=None):
    if request.is_ajax():
        result = {"success": success}
        if errors:
            result["errors"] = errors
        if data:
            result["data"] = data
        return HttpResponse(
            json.dumps(result, indent=4, sort_keys=True),
            mimetype='application/json',
            content_type='application/json')
    else:
        if redirect_url:
            return HttpResponseRedirect(redirect_url)
        return HttpResponse(
            "Accept Ajax Request Only.", content_type="text/plain")


# Public Views
def register(request):
    """
    New account page, create new :model:`hado.HackDoUser`
    with two :model:`hado.MembershipReview`

    **Context**

    ``RequestContext``

    ``form``

    The new account form

    **Template:**

    :template:`registration/register.html`
    """
    template = 'registration/register.html'
    names = User.objects.values_list('username', flat=True)
    user_list = "'[\"%s\"]'" % ('","'.join([n.encode('utf-8') for n in names]))
    if request.method == 'POST':
        form = NewAccountForm(request.POST)
        if form.is_valid():
            try:
                cd = form.cleaned_data
                new_user = User.objects.create_user(
                    username=cd['username'],
                    email=cd['email'],
                    password=cd['password'],
                )
                if cd['first_name']:
                    new_user.first_name = cd['first_name']
                if cd['last_name']:
                    new_user.last_name = cd['last_name']
                new_user.save()
                m1 = MembershipReview(
                    applicant=new_user,
                    referrer=form.refer_one_user,
                )
                m2 = MembershipReview(
                    applicant=new_user,
                    referrer=form.refer_two_user,
                )
                m1.save()
                m2.save()
            except Exception as e:
                logger.error("Error: %s" % (e))
            else:
                messages.success(
                    request,
                    'New pending user %s created.'
                    % (new_user.username))
                return HttpResponseRedirect(reverse('login'))
    else:
        form = NewAccountForm()
    return render(request, template, {
        'form': form,
        'user_list': user_list,
    })
