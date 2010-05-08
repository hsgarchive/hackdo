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
	profile_image = models.ImageField(upload_to=get_image_path, blank=True)
	
	objects = UserManager()

	@property
	def most_recent_payment(self):
		return self.payments.all()[0]

	@property
	def payments(self):
		return self.payments_made.order_by('-for_year', '-for_month').all()
	
	def __unicode__(self):
		if self.first_name and self.last_name:
			return self.get_full_name()
		else:
			return self.username
			

class Membership(models.Model):
	start = models.DateField()
	end = models.DateField()
	tier = models.ForeignKey("Tier", blank=False, null=True)
	user = models.ForeignKey(User, blank=False, null=True, related_name="memberships")
	
	def __unicode__(self):
		return self.user.__unicode__() + u": " + self.tier.__unicode__()
		

class Tier(models.Model):
	fee = models.FloatField()
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
	
	PAYMENT_TYPES = (
		('DPT', 'Deposit'),
		('FEE', 'Membership Fees'),
		('DNT', 'Donation')
	)

	MONTHS = (
		('1', 'Jan'),
		('2', 'Feb'),
		('3', 'Mar'),
		('4', 'Apr'),
		('5', 'May'),
		('6', 'Jun'),
		('7', 'Jul'),
		('8', 'Aug'),
		('9', 'Sep'),
		('10', 'Oct'),
		('11', 'Nov'),
		('12', 'Dec')
	)
	
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

	YEARS = (
		('2010', '2010'),
	)

	date_paid = models.DateField()
	method = models.CharField(max_length=3, choices=PAYMENT_METHODS, default='EFT')
	category = models.CharField(max_length=3, choices=PAYMENT_TYPES, default='FEE')
	for_month = models.CharField(max_length=2, blank=False, choices=MONTHS, default=datetime.date.today().month)
	for_year = models.CharField(max_length=4, blank=False, choices=YEARS, default=datetime.date.today().year)
	desc = models.CharField(max_length=255, blank=True)
	user = models.ForeignKey(User, blank=False, related_name="payments_made")
	membership = models.ForeignKey(Membership, blank=False, related_name="membership_payments")
	
	def __unicode__(self):
		return self.membership.__unicode__() + u" " + unicode(self.date_paid)
		

	