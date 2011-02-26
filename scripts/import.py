# -*- coding: utf-8 -*-
#!/bin/python

import csv
import datetime
from hado.models import *

######
# 
#   Usage:
#   
#   Run the import script from the root of the Django project via ./manage.py shell
#   
#   Import the methods below via:
#   
#   >>> from import_scripts import *
#   
#   Run import_members(), import_contracts(), then import_payments(), in that order.
#   
#   After running each method, check in XXX_REJECTS, where 'XXX' is one of MEMBER, CONTRACT or PAYMENT.
#   These arrays contain the objects that failed to be save properly. On the shell, take the time to diagnose the problem and fix if necessary.
#   
#   Finally. check in the Django admin to ensure sanity.
#
#######


MEMBER_REJECTS = []
CONTRACT_REJECTS = []
PAYMENT_REJECTS = []

def import_payments(interactive=False):

	pread = csv.reader(open('test/payments.csv', 'r'))

	for p in pread:
		
		print p
		
		pp = Payment()

		try:
			pp.id = int(float(p[1]))
			pp.date_paid = datetime.datetime.strptime(p[0],  '%d-%b-%Y')

			pp.amount = float(p[4])
			if pp.amount <= 0:
				continue			
			
			contract = Contract.objects.get(id=p[2])
			user = User.objects.get(id=p[3])
			if contract.user == user:
				pp.contract = contract
				pp.user = user
			else:
				print "User and Contract do not match!"
				PAYMENT_REJECTS.append([pp, "User and Contract don't match"])
				continue
				
			try:
				pp.desc = p[6]
			except IndexError:
				pp.desc = ''
			
			pp.verified = True
			
			# Summary
			print "Payment summary\n"
			print "Date paid: %s" % pp.date_paid
			print "Amount: %s" % pp.amount
			print "User: %s" % pp.user
			print "Contract: %s" % pp.contract
			print "Desc: %s" % pp.desc
			print "Verified: %s" % pp.verified
			
			
			if interactive:
				print "\nOk?"
				ok = raw_input("[Y/n] >>> ")
				
				if ok.lower() == 'n' or ok.lower() == 'no':
					print "Aborting for %s" % pp
					continue
				
				
			pp.save()
			print "Saved\n\n"		

		except Exception as e:
			print e

			try:
				print "Payment %s failed" % pp
			except:
				pass
				
			PAYMENT_REJECTS.append(pp)	



def import_contracts(interactive=False):

	cread = csv.reader(open('test/contracts.csv', 'r'))
	
	for c in cread:
		print c
		
		cc = Contract()
		
		cc.id = c[0]
		cc.user = User.objects.get(id=c[1]) 
		cc.start = datetime.datetime.strptime(c[2], '%d-%b-%Y')
		
		if c[3]:
			cc.end = datetime.datetime.strptime(c[3], '%d-%b-%Y')
			cc.status = 'TER'
		else:
			cc.status = 'ACT' # Assume a default of Active
		
		cc.tier = Tier.objects.get(fee=c[4])
		cc.ctype = ContractType.objects.get(desc='Membership')
		
		# Summary
		print "Contract summary:\n"
		print "User: %s" % cc.user.get_full_name()
		print "Start: %s" % cc.start
		print "End: %s" % cc.end
		print "Status: %s" % cc.status
		print "Type: %s" % cc.ctype
		print "Tier: %s" % cc.tier
		
		if interactive:
			print "\nOk?"
			ok = raw_input("[Y/n] >>> ")
			
			if ok.lower() == 'n' or ok.lower() == 'no':
				print "Aborting for %s" % cc
				continue
			
			
		try:
			cc.save()
			print "Saved\n\n"		
		except:
			print "Contract %s failed" % cc
			CONTRACT_REJECTS.append(u)


def import_members(interactive=False):
	
	mread = csv.reader(open('test/members.csv', 'r'))
	
	for m in mread:
		print m
		
		u = User()
		u.id = m[0]
		
		namebits = m[1].split(" ")
		if len(namebits) >= 3:
			print m[1]
			print "Name unknown.\nEnter first name"
			u.first_name = raw_input(">>>")
			print "Enter last name"
			u.last_name = raw_input(">>>")
			print "Name is %s %s" % (u.first_name, u.last_name)
	
		else:
			u.first_name = namebits[0]
			u.last_name = namebits[1]
		
		u.email = m[2]
		
		u.username = u.first_name + u.last_name
		u.username = u.username.lower().replace(" ", "").replace("-", "")[0:6]
		
		u.set_password('hackdo')
	
		u.is_active = True
		
		# Summary
		print "User summary\n"
		print "First name: %s" % u.first_name
		print "Last name: %s" % u.last_name
		print "Username: %s" % u.username
		print "Email: %s" % u.email
		print "Password: %s" % u.password
		
		
		if interactive:
			print "\nOk?"
			ok = raw_input("[Y/n] >>> ")
			
			if ok.lower() == 'n' or ok.lower() == 'no':
				print "Aborting for %s %s" % (u.first_name, u.last_name)	
				continue
			
			
		try:
			u.save()
			print "Saved\n\n"		
		except:
			print "Member %s %s failed" % (u.first_name, u.last_name)
			MEMBER_REJECTS.append(u)
		