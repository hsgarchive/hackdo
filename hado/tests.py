"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

from dateutil import relativedelta

from hado.models import *

import datetime


class UserTest(TestCase):
	'''Test various User functions'''
	
	fixtures = ['contracttype', 'tier']
	
	def setUp(self):
		pass
		
	def testUserName(self):
		'''Test that the User's fullname is returned if first_name and last_name are set, and username is returned otherwise'''
		
		# Create a new User
		u = User(username="testuser")
		u.set_password('testtest')
		u.save()
		
		# Check that username is returned
		self.assertEqual(unicode(u), "testuser")
		
		# Set first and last names
		u.first_name = 'Test'
		u.last_name = 'User'
		u.save()
		
		# Check that fullname is returned
		self.assertEqual(unicode(u), "Test User")


	def testMemberSince(self):
		'''Test that User::member_since returns the date the User joined as a member'''
		
		# Create a new User
		u = User(username="testuser")
		u.set_password('testtest')
		u.save()

		date_start = datetime.date(2010, 04, 01)
		date_end = datetime.date(2010, 05, 31)

		# Attribute some membership Contracts
		u.contracts.create(
			start = date_start,
			end = date_end,
			ctype = ContractType.objects.get(desc='Membership'),
			tier = Tier.objects.get(desc='Regular'),
			status = u'TER'
		)

		# Ensure we only have the one Contract created so far
		self.assertEqual(u.contracts.all().count(), 1)

		u.contracts.create(
			start = datetime.date(2010, 06, 01),
			ctype = ContractType.objects.get(desc='Membership'),
			tier = Tier.objects.get(desc='Youth'),
			status = u'ACT'
		)

		# Now we have two
		self.assertEqual(u.contracts.all().count(), 2)

		self.assertEqual(date_start, u.member_since())


class ContractTest(TestCase):

	fixtures = ['contracttype', 'tier']

	def setUp(self):
		
		# Set up some trial data
		
		# User
		self.u = User(username='testuser', first_name="Test", last_name="User", email="testuser@testtest.com")
		self.u.set_password('testtest')
		self.u.save()
		
		# Contract
		self.c = Contract(start=datetime.date(2010, 04, 01), ctype=ContractType.objects.get(desc='Membership'), tier=Tier.objects.get(desc='Regular'), user=self.u, status='ACT')


		# Add some Payments
		
		# Initial deposit, plus first month (Apr)
		self.c.payments.create(
			date_paid = datetime.date(2010, 04, 14),
			amount = 256,
			user = self.u
		)
		
		# Payment for May and June
		self.c.payments.create(
			date_paid = datetime.date(2010, 06, 01),
			amount = 256,
			user = self.u
		)

		# Payment due for July, paid in October
		self.c.payments.create(
			date_paid = datetime.date(2010, 10, 05),
			amount = 128,
			user = self.u
		)
		
		
	def testContractTotalPaid(self):
		'''Test that we can retrieve the total amount paid for this Contract'''
		
		self.assertEqual(self.c.total_paid, self.c.payments.aggregate(Sum('amount'))['amount__sum'])
		self.assertEqual(self.c.total_paid, 640)
		
	
	def testContractStatusLapsed(self):
		'''After the initial Payments added in setUp(), Contract.status should be LAPSED'''
		
		self.assertEqual(self.c.status, 'LAP')
		
	
	def testContractValidTill(self):
		'''After initial Payments added in setUp(), valid_till ought to be 31 July 2010, non-inclusive of deposit'''
		
		self.c.sync()
		self.assertEqual(self.c.valid_till, datetime.date(2010, 07, 31))
		
	
	def testContractSync(self):
		'''After initial Payments added in setUp(), and sync() is run, valid_till ought to be 31 July 2010'''
		
		self.assertEqual(self.c.valid_till, datetime.date(2010, 07, 31))
		
	
	def testContractBalance(self):
		'''After initial Payments added in setUp(), Contract should be <arrear_months> * 128 in arrears'''
		
		# Calculate arrears from Contract.valid_till till today
		arrears_months = relativedelta.relativedelta(datetime.date.today(), self.c.valid_till).months # Naive month calculation
		
		self.assertEqual(self.c.balance(), -(arrears_months*128))
		self.assertEqual(self.c.balance(in_months=True), -arrears_months)
		
	
	def testContractExtendWithPayment(self):
		'''Test that Contract valid_till dates are extended according to the quantum paid, eg. extended 3 months for 3 months paid'''
		# Get the baseline valid_till month
		bmonth = self.c.valid_till.month
		
		# Let's make a Payment
		QUANTUM = 3
		amt = QUANTUM * self.c.tier.fee
		p = Payment(date_paid=datetime.datetime(2010, 11, 16), amount=amt, contract=self.c, user=self.u)
		p.save()
		
		# Check the new valid_till month
		nmonth = self.c.valid_till.month
		
		self.assertEqual(nmonth-bmonth, QUANTUM)
		
		
	def testContractCheckLapsed(self):
		'''Test that instantiating a Contract causes it to check its own status and update it based on valid_till if necessary'''
		
		# This Contract should be Lapsed
		self.assertEqual(self.c.status, u'LAP')
		
		# Make it active
		self.c.status = u'ACT'
		self.c.save()
		
		# Grab another copy from the database and show that its changed back to being Lapsed
		cc = Contract.objects.get(id=self.c.id)
		self.assertEqual(cc.status, u'LAP')
		
		
		# Shift valid_till forward past today() so that we can cause it to shift back to being Active
		t = datetime.datetime.today()
		cc.valid_till = t +  datetime.timedelta(days=30) # Shift date 30 days forward
		cc.save()
		
		# Retrieve it from the database again and show that it's gone Active
		ccc = Contract.objects.get(id=cc.id)
		self.assertEqual(ccc.status, u'ACT')
		
		