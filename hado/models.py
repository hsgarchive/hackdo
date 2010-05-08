# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User, UserManager
import datetime
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
		return self.payments.all()[0]

#	@property
#	def payments(self):
#		return self.payments_made.order_by('-for_year', '-for_month').all()
	
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

	start = models.DateField(auto_now_add=True)
	end = models.DateField(auto_now_add=True)
	ctype = models.ForeignKey(ContractType, blank=False, null=True)
	tier = models.ForeignKey("Tier", blank=False, null=True)
	user = models.ForeignKey(User, blank=False, null=True, related_name="memberships")
	status = models.CharField(max_length=3, choices=CONTRACT_STATUSES)
	
	def __unicode__(self):
		return self.user.__unicode__() + u": " + self.ctype.__unicode__() + u" " + " End :" + unicode(self.end)
		

class Tier(models.Model):
	fee = models.FloatField(default=0.0)
	desc = models.CharField(max_length=255)
	
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
	desc = models.CharField(max_length=255, blank=True)
	user = models.ForeignKey(User, blank=False, null=True, related_name="payments_made")
	
	def __unicode__(self):
		return self.contract.__unicode__() + u" " + unicode(self.date_paid)
		


class Locker(models.Model):
	user = models.ForeignKey(User, blank=False, null=True, related_name="locker")
	num = models.IntegerField()
	