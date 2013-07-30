# -*- coding: utf-8; -*-
import datetime

from django.contrib.admin.sites import AdminSite
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotAllowed, HttpResponseRedirect

from hado.models import Contract, Payment, ContractType, Sum
from hado.forms import PaymentFormAdminFormset, UserFormAdminFormset

import logging
logger = logging.getLogger("hado.admin")


User = get_user_model()


# Subclassing a custom admin to provide a custom interface
class HackdoAdmin(AdminSite):

    def index(self, request):
        '''This view forms the admin dashboard for HackDo'''

        # Members stats
        members = {}
        users = User.objects.select_related('contracts')
        members['total'] = len(users)

        members['active'] = Contract.objects.filter(
            ctype__desc='Membership',
            status='ACT').count()
        members['lapsed'] = Contract.objects.filter(ctype__desc='Membership',
                                                    status='LAP').count()

        # Income stats
        income = {}
        this_month = datetime.date.today().month
        payments_this_month = Payment.objects.filter(
            date_paid__month=this_month)
        # Get ContracTypes
        ctypes = ContractType.objects.all()
        for c in ctypes:
            income[c.desc] = payments_this_month \
                .filter(contract__ctype__desc=c.desc) \
                .aggregate(Sum('amount'))['amount__sum'] or 0.0

        # Supposed income this month
        income['summary'] = {}
        income['summary']['supposed'] = \
            Contract.objects \
            .filter(Q(status='ACT') | Q(status='LAP')) \
            .aggregate(Sum('tier__fee'))['tier__fee__sum'] or 0.0

        income['summary']['actual'] = \
            payments_this_month.aggregate(Sum('amount'))['amount__sum'] or 0.0

        income['summary']['shortfall'] = \
            income['summary']['supposed'] - income['summary']['actual']

        # Create new formsets
        pformset = PaymentFormAdminFormset(
            queryset=Payment.objects.filter(verified='PEN'))

        uformset = UserFormAdminFormset(
            queryset=User.objects.filter(is_active=False))

        return render(request, 'admin/index.html',
                      {
                          'title': 'HackDo',
                          'members': members,
                          'income': income,
                          'pformset': pformset,
                          'uformset': uformset
                      })

    def payment_verify(self, request):
        if request.method != 'POST':
            return HttpResponseNotAllowed(permitted_methods=('POST',))
        # Incoming Payments pending verification
        pformset = PaymentFormAdminFormset(
            request.POST, queryset=Payment.objects.filter(verified='PEN'))
        if len(pformset.forms) > 0:
            if pformset.is_valid():
                pformset.save()
                messages.success(request, "Payments updated.")
                #TODO: send out email to user
            else:
                messages.error(
                    request,
                    "Error process request. %s" % pformset.errors)
                logger.error(pformset.errors)
        return HttpResponseRedirect(reverse('admin:index'))

    def user_active(self, request):
        if request.method != 'POST':
            return HttpResponseNotAllowed(permitted_methods=('POST',))
        # Incoming User active request
        uformset = UserFormAdminFormset(
            request.POST, queryset=User.objects.filter(is_active=False))
        if len(uformset.forms) > 0:
            if uformset.is_valid():
                uformset.save()
                messages.success(request, "Users updated.")
                #TODO: send out email to user
            else:
                messages.error(
                    request,
                    "Error process request. %s" % uformset.errors)
                logger.error(uformset.errors)
        return HttpResponseRedirect(reverse('admin:index'))
