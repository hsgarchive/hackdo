# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_save, post_save, post_init, pre_init
from django.contrib.auth.models import User, UserManager
from django.core.exceptions import ValidationError
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
		if pretty:
			return self.contracts.filter(ctype__desc='Membership').latest('start').get_status_display()
		else:
			return self.contracts.filter(ctype__desc='Membership').latest('start').status

	
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


	def __extend_by(self, num_months):
		'''Extends the validity of this Contract by specified number of months (Assume 1 month = 28 days). THIS METHOD DOES NOT save() AUTOMATICALLY'''
		
# 		year = s.year + ((s.month + num_months) / 12)
# 		month = ((s.month + num_months) % 12)		
# 		last_day = calendar.monthrange(self.end.year, self.end.month)[1]
		
		#self.end = datetime.date(year, month, last_day)
		self.valid_till = self.valid_till + datetime.timedelta(days=(28*num_months))
		
		# Normalise date to end of that month
		self.valid_till = datetime.date(self.valid_till.year, self.valid_till.month, calendar.monthrange(self.valid_till.year, self.valid_till.month)[1])
	


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
			# Take into account 1 month's deposit
			months_paid -= 1 			
			self.__extend_by(int(months_paid))

		self.save()
		
	

	def balance(self, in_months=False):
		'''Looks at how much has been paid for this Contract and determines if there is any balance owed by (-ve) / owed to (+ve) the Member'''
		balance = 0
		duration_in_months = 1
		
		# Calculate number of months Contract has been in effect, ie. not Terminated
		if self.status == 'TER':			
			duration_in_months = (self.end - self.start).days / 28 # Naive month calculation
		else: 
			duration_in_months = (datetime.date.today() - self.start).days / 28 # Naive month calculation
		
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
	
		
	def save(self):
		# Overridden save() forces the date of self.end to be the last day of that given month.
		# Eg. if self.end is initially declared as 5 May 2010, we now force it to become 31 May 2010 before actually save()'ing the object.
		
		# But first, is self.end even specified?
		if not self.valid_till:
			self.valid_till = self.start
		
		last_day = calendar.monthrange(self.valid_till.year, self.valid_till.month)[1]
		self.valid_till = datetime.date(self.valid_till.year, self.valid_till.month, last_day)
		
		#force start date to be normalised as 1st day of the month
		self.start = datetime.date(self.start.year, self.start.month, 1)
		super(Contract, self).save()
	
	def clean(self):
		# Model validation to ensure that validates that contract and tier are allowed
		if self.ctype != self.tier.ctype:
			raise ValidationError(_("Contract type and tier mismatched"))
			
	def __unicode__(self):
		return self.user.__unicode__() + u": " + self.ctype.__unicode__() + u" @ $" + unicode(self.tier.fee) + "/mth Start: " + u" " + unicode(self.start.strftime('%d %b %Y')) +  u" End: " + unicode(self.end.strftime('%d %b %Y'))	

class Tier(models.Model):
	fee = models.FloatField(default=0.0)
	desc = models.CharField(max_length=255)
	ctype = models.ForeignKey("ContractType", blank=False, null=True)
	
	def __unicode__(self):
		return self.desc + u": " + unicode(self.fee)

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
		return self.contract.__unicode__() + u" Paid: " + unicode(self.date_paid)
		


class Locker(models.Model):
	user = models.ForeignKey(User, blank=False, null=True, related_name="locker")
	num = models.IntegerField()
	

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
