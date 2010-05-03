# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User, UserManager
# Create your models here.

def get_image_path(instance, filename):
	return os.path.join('users', instance.id, filename) 


class User(User):
	"""Custom User model, extending Django's default User"""
	profile_image = models.ImageField(upload_to=get_image_path, blank=True)

	
	objects = UserManager()
	
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
		return self.desc + u": " + self.desc


class Payment(models.Model):
	PAYMENT_TYPES = (
		('EFT', 'Electronic Fund Transfer'),
		('CHK', 'Cheque'),
		('CSH', 'Cash'),
		('OTH', 'Others')
	)

	date_paid = models.DateField(auto_now_add=True)
	method = models.CharField(max_length=3, choices=PAYMENT_TYPES, default='EFT')
	desc = models.CharField(max_length=255, blank=True)
	user = models.ForeignKey(User, blank=False)
	membership = models.ForeignKey(Membership, blank=False)
	
	def __unicode__(self):
		return self.membership.__unicode__() + u" " + self.date_paid
		

	