# -*- coding: utf-8 -*-
import datetime

from django.contrib.admin.sites import AdminSite
from django.db.models import Q
from django.forms.models import modelformset_factory
from hado.models import *
from hado.forms import PaymentFormAdmin
from utils import render

# Subclassing a custom admin to provide a custom interface
class HackdoAdmin(AdminSite):

	def index(self, request):
		'''This view forms the admin dashboard for HackDo'''
		
		# Members stats
		members = {}
		users = User.objects.select_related('contracts')
		members['total'] = len(users)

		members['active'] = Contract.objects.filter(ctype__desc='Membership', status='ACT').count()
		members['lapsed'] = Contract.objects.filter(ctype__desc='Membership', status='LAP').count()

		# Income stats
		income = {}
		this_month = datetime.date.today().month
		payments_this_month = Payment.objects.filter(date_paid__month=this_month)
		# Get ContracTypes
		ctypes = ContractType.objects.all()		
		for c in ctypes:
			income[c.desc] = payments_this_month.filter(contract__ctype__desc=c.desc).aggregate(Sum('amount'))['amount__sum'] or 0.0
		
		
		# Supposed income this month
		income['summary'] = {}
		income['summary']['supposed'] = Contract.objects.filter(Q(status='ACT') | Q(status='LAP')).aggregate(Sum('tier__fee'))['tier__fee__sum'] or 0.0
		income['summary']['actual'] = payments_this_month.aggregate(Sum('amount'))['amount__sum'] or 0.0
		income['summary']['shortfall'] = income['summary']['supposed'] - income['summary']['actual']
		
		
		# Incoming Payments pending verification
		PaymentFormAdminFormset = modelformset_factory(Payment, extra=0)
		pformset = PaymentFormAdminFormset(queryset=Payment.objects.filter(verified=False))
		
		return render(request, 'admin/index.html', {'members':members, 'income':income, 'pformset':pformset})



	def lapsed_contracts(self, request):
		'''Shows details about lapsed contracts'''
		pass
		
	
	