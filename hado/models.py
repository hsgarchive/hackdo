# -*- coding: utf-8; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Sum, F
from django.db.models.signals import pre_save, post_save, post_init, pre_init
from django.contrib.auth.models import User, UserManager
from django.core.exceptions import ValidationError

from dateutil.relativedelta import relativedelta

import datetime, calendar


# Create your models here.

def get_image_path(instance, filename):
	return os.path.join('users', instance.id, filename)


class User(User):
	"""Custom User model, extending Django's default User"""
	USER_TYPES = (
		('MEM', 'Member'),
		('SPO', 'Sponsor'),
		('DON', 'Donation')
	)

	profile_image = models.ImageField(upload_to=get_image_path, blank=True)
	utype = models.CharField(max_length=3, choices=USER_TYPES, default='MEM')

	objects = UserManager()

	@property
	def most_recent_payment(self):
		p = self.payments_made.all().order_by('-date_paid')
		return p[0] if p else None


	def total_paid(self, ptype=None):
		'''Returns the total amount the User has paid either in total, or for a specified Contract type'''

		# Construct the appropriate Queryset
		if ptype is not None:
			payments = self.payments_made.filter(contract__ctype__desc=ptype)
		else:
			payments = self.payments_made

		return payments.aggregate(Sum('amount'))['amount__sum'] or 0.0


	def membership_status(self, pretty=False):
		'''Returns string (see Contract::CONTRACT_STATUSES) indicating latest Membership status of this User'''
		try:
			if not hasattr(self, '__latest_membership'):
				lm = self.contracts.filter(ctype__desc='Membership').exclude(status='PEN').latest('start')
				self.__latest_membership = lm

			return self.__latest_membership.get_status_display() if pretty else self.__latest_membership.status

		except Contract.DoesNotExist:
			self.__latest_membership = None
			return None


	def member_since(self):
		'''Returns datetime object representing start date of earliest Membership Contract if found, None otherwise'''

		try:
			if not hasattr(self, '__member_since'):
				ms = self.contracts.filter(ctype__desc='Membership').order_by('start')[0:1]
				if len(ms) > 0:
					self.__member_since = ms[0].start
				else:
					self.__member_since = None

			return self.__member_since

		except Contract.DoesNotExist:
			return None


	def __unicode__(self):
		if self.first_name and self.last_name:
			return self.get_full_name()
		else:
			return self.username



class ContractType(models.Model):
	desc = models.CharField(max_length=128, blank=False, null=True)

	def __unicode__(self):
		return self.desc


class Contract(models.Model):
	CONTRACT_STATUSES = (
		('ACT', 'Active'),
		('LAP', 'Lapsed'),
		('TER', 'Terminated'),
		('PEN', 'Pending')
	)

	start = models.DateField()
	end = models.DateField(blank=True, null=True)
	valid_till = models.DateField(editable=False)
	ctype = models.ForeignKey(ContractType, blank=False, null=True, verbose_name="Contract type", help_text="Locker and Address Use Contracts must use their respective Tiers. Membership contracts can accept all other Tiers")
	tier = models.ForeignKey("Tier", blank=False, null=True)
	user = models.ForeignKey(User, blank=False, null=True, related_name="contracts")
	status = models.CharField(max_length=3, choices=CONTRACT_STATUSES)
	desc = models.CharField(max_length=1024, blank=True, help_text="Enter company name if Contract is for Address Use. May use for general remarks for other Contract types")


	def __extend_by(self, num_months):
		'''Extends the validity of this Contract by specified number of months. THIS METHOD DOES NOT save() AUTOMATICALLY'''

		# We subtract one day, such that if we start on the first of a month, eg. datetime.date(2011, 02, 01), extending the validity
		# by 5 months, won't give us an end date of datetime.date(2011, 07, 01) [which is wrong], but datetime.date(2011, 06, 30) [which is right]
		delta = {
			'months': num_months,
			'days': -1
		}
		self.valid_till = self.valid_till + relativedelta(**delta)

		# Normalise date to end of that month
		self.valid_till = datetime.date(self.valid_till.year, self.valid_till.month, calendar.monthrange(self.valid_till.year, self.valid_till.month)[1])


	def __month_diff(self, end, start):
		'''Returns the months (inclusive of part thereof) between two dates'''

		r = relativedelta(end + relativedelta(days=+1), start)
		return r.months + (r.years * 12 if r.years else 0) + (1 if r.days else 0)


	@property
	def total_paid(self):
		'''Returns total amount paid due to this Contract'''

		return self.payments.aggregate(Sum('amount'))['amount__sum'] or 0.0


	def sync(self):
		'''Looks at the total amount paid to this Contract and recalculates its proper expiry (end) date, taking a month's deposit into account'''

		# Reset the clock
		self.valid_till = self.start

		months_paid = self.total_paid / self.tier.fee

		if months_paid > 0:
			self.__extend_by(int(months_paid))

		self.save()


	def balance(self, in_months=False):
		'''Looks at how much has been paid for this Contract and determines if there is any balance owed by (-ve) / owed to (+ve) the Member'''
		balance = 0
		duration_in_months = 0

		# Calculate number of months Contract has been in effect, ie. not Terminated
		if self.status == 'TER':
			duration_in_months += self.__month_diff(self.end, self.start)
		else:
			duration_in_months += self.__month_diff(datetime.date.today(), self.start)

		balance = self.total_paid - (self.tier.fee * duration_in_months)

		if in_months:
			return balance / self.tier.fee

		else:
			return balance


	def update_with_payment(self, p):
		# Takes a Payment object, calculates how many month's worth it is, and extends the contract end date accordingly
		if isinstance(p, Payment):
			# Get number of multiples of Contract for this Payment
			multiples = int(p.amount / self.tier.fee)

			self.__extend_by(multiples)
			self.save()

			# sync() the Contract if this is the first Payment being made on this Contract
			if self.payments.count() == 1:
				self.sync()

		else:
			return False


	def save(self, *args, **kwargs):
		# Overridden save() forces the date of self.end to be the last day of that given month.
		# Eg. if self.end is initially declared as 5 May 2010, we now force it to become 31 May 2010 before actually save()'ing the object.

		# But first, is self.end even specified?
		if not self.valid_till:
			self.valid_till = self.start

		last_day = calendar.monthrange(self.valid_till.year, self.valid_till.month)[1]
		self.valid_till = datetime.date(self.valid_till.year, self.valid_till.month, last_day)

		# Force start date to be normalised as 1st day of the month
		if self.start.day != 1:
			self.start = datetime.date(self.start.year, self.start.month, 1)

		# If we notice the Contract is now Terminated, and the end date has not been set, set the end date
		if self.status == 'TER' and self.end is None:
			today = datetime.date.today()
			self.end = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

		# If the model has been saved already, ie. has an id, force it to update
		# otherwise, insert a new record
		if self.id:
			kwargs['force_update'] = True
			kwargs['force_insert'] = False
		else:
			kwargs['force_insert'] = True
			kwargs['force_update'] = False

		super(Contract, self).save(*args, **kwargs)


	def clean(self):
		# Model validation to ensure that validates that contract and tier are allowed
		if self.ctype != self.tier.ctype:
			raise ValidationError(_("Contract type and tier mismatched"))

	def __unicode__(self):
		return "%s %s | %s to %s" % (self.tier, self.ctype, self.start.strftime('%b %Y'), self.valid_till.strftime('%b %Y'))


class Tier(models.Model):
	fee = models.FloatField(default=0.0)
	desc = models.CharField(max_length=255)
	ctype = models.ForeignKey("ContractType", blank=False, null=True)

	def __unicode__(self):
		return self.desc

class Payment(models.Model):
	PAYMENT_METHODS = (
		('EFT', 'Electronic Fund Transfer'),
		('CHK', 'Cheque'),
		('CSH', 'Cash'),
		('OTH', 'Others')
	)

#	PAYMENT_TYPES = (
#		('DPT', 'Deposit'),
#		('FEE', 'Membership Fees'),
#		('DNT', 'Donation')
#	)

#	MONTHS = (
#		('1', 'Jan'),
#		('2', 'Feb'),
#		('3', 'Mar'),
#		('4', 'Apr'),
#		('5', 'May'),
#		('6', 'Jun'),
#		('7', 'Jul'),
#		('8', 'Aug'),
#		('9', 'Sep'),
#		('10', 'Oct'),
#		('11', 'Nov'),
#		('12', 'Dec')
#	)

#	@property
#	def year_range(self):
#		this_year = datetime.today().year
#		years = ( (unicode(this_year), unicode(this_year)) )
#
#		for i in xrange(0, 10):
#			years.insert(0, (unicode(this_year-i), unicode(this_year-i)))
#			years.append((unicode(this_year+i), unicode(this_year+i)))
#
#		return years

#	YEARS = (
#		('2010', '2010'),
#	)

	date_paid = models.DateField()
	amount = models.FloatField(default=0.0)
	method = models.CharField(max_length=3, choices=PAYMENT_METHODS, default='EFT')
	contract = models.ForeignKey(Contract, blank=False, null=True, related_name="payments")
	desc = models.CharField(max_length=255, blank=True, help_text="Eg. Cheque or transaction number, if applicable")
	user = models.ForeignKey(User, blank=False, null=True, related_name="payments_made")
	verified = models.BooleanField(default=False, blank=False, help_text="Has this Payment been verified/approved by an Admin?")

	def __unicode__(self):
		return u"%s | %s %s | %s, %s" % (self.user, self.contract.tier, self.contract.ctype, self.amount, self.date_paid.strftime('%d %b %Y'))


class Locker(models.Model):
	user = models.ForeignKey(User, blank=False, null=True, related_name="locker")
	num = models.IntegerField()

class Currency(models.Model):
	"""List of available currencies"""
	abbrev= models.CharField(max_length=3, unique=True)
	desc = models.CharField(max_length=255)

	def __unicode__(self):
		return unicode(self.abbrev)

class Invoice(models.Model):
	"""Saved invoices"""
	visible_id = models.CharField(max_length=255, editable=False, unique=True,
	                              null=True, default=None)
	client = models.ForeignKey(User, null=False)
	currency = models.ForeignKey(Currency)

	date_for = models.DateField()
	date_issued = models.DateField()
	date_due = models.DateField(null=False, blank=True)
	tax = models.FloatField()

	def __unicode__(self):
		return unicode(self.visible_id)

	def save(self, *args, **kwargs):
		"""
		Overridden model.save() function to automatically generate visible_id
		"""
		if not self.date_due:
			self.date_due = self.date_issued + datetime.timedelta(days=30)

		if not self.pk:
			super(Invoice, self).save(*args, **kwargs)

		if not self.visible_id:
			hex_id = hex(int(self.pk)).upper()
			hex_id = '0' * (10 - len(hex_id)) + hex_id

			self.visible_id = "HSG-" + hex_id

			kwargs['force_update'] = True
			kwargs['force_insert'] = False
			super(Invoice, self).save(*args, **kwargs)

	def clean(self):
		"""Ensure that date_for is normalized to the beginning of the month"""
		if self.date_for.day != 1:
			self.date_for = datetime.date(self.date_for.year,
			                              self.date_for.month, 1)

class InvoiceItem(models.Model):
	invoice = models.ForeignKey(Invoice, related_name='items')
	desc = models.CharField(max_length=255)
	amount = models.DecimalField(decimal_places=2, max_digits=10)

	contract = models.ForeignKey(Contract, null=True)

# Attaching a post_save signal handler to the Payment model to update the appropriate Contract
def update_contract_with_payments(sender, **kwargs):
	payment = kwargs['instance']
	c = payment.contract
	c.update_with_payment(payment)

post_save.connect(update_contract_with_payments, sender=Payment)

def lapsed_check(sender, **kwargs):
	'''Checks the end date of active contract and compares it with today. If contract is lapsed, update the contract status to lapsed.'''

	contract = kwargs['instance']

	# If this is a new Contract, check if we have a valid_till date set
	if not contract.id and not contract.valid_till:
		contract.valid_till = contract.start

	if contract.status == u'ACT':
		if contract.valid_till < datetime.date.today():
			contract.status = u'LAP'
			contract.save()

	elif contract.status == u'LAP' and contract.valid_till > datetime.date.today():
		contract.status = u'ACT'
		contract.save()

post_init.connect(lapsed_check, sender=Contract)
