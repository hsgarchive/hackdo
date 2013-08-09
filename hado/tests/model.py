# -*- coding: utf-8; -*-
from dateutil.relativedelta import relativedelta
import datetime
import urllib
import hashlib

from django.test import TestCase
from django.contrib.sites.models import Site

from hado.tests.factories import UserFactory, ContractFactory,\
    PaymentFactory
from hado.models import ContractType, Tier, Contract, Sum,\
    get_image_path


class UserTest(TestCase):

    '''Test various User functions'''

    def setUp(self):
        self.test_user = UserFactory(username="testuser")

    def test_get_image_path(self):
        image_url = get_image_path(self.test_user, 'test_image')
        self.assertTrue(
            'user_avatars/%s' % self.test_user.username in image_url)

    def testUserName(self):
        '''
        Test that the User's fullname is returned
        if first_name and last_name are set,
        and username is returned otherwise
        '''
        username = 'testuser'
        fname = 'Test'
        lname = 'User'
        full_name = '%s %s' % (fname, lname)
        # Test get_username method
        self.assertEqual(unicode(self.test_user.get_username()), username)
        # Test get_short_name method
        self.assertEqual(unicode(self.test_user.get_short_name()), username)
        # Check that username is returned
        self.assertEqual(unicode(self.test_user), username)

        # Set first and last names
        self.test_user.first_name = fname
        self.test_user.last_name = lname
        self.test_user.save()

        # Test get_full_name method
        self.assertEqual(self.test_user.get_full_name(), full_name)
        # Check that fullname is returned
        self.assertEqual(unicode(self.test_user), full_name)

    def testUserAvatar(self):
        '''
        Test user should have correct gravatar/self defined avatar
        '''
        self.assertEqual(
            self.test_user.user_avatar_url,
            "http://www.gravatar.com/avatar/%s?%s" % (
                hashlib.md5(self.test_user.email.lower()).hexdigest(),
                urllib.urlencode({'d': 'mm', 's': str(20)})))
        self.test_user.is_gravatar_enabled = False
        self.test_user.save()
        self.assertEqual(
            self.test_user.user_avatar_url,
            "http://%s/static/img/default_avatar.png" % (
                Site.objects.get_current().domain))

    def testMemberSince(self):
        '''
        Test User::member_since
        returns the date the User joined as a member
        '''

        # Create a new User
        self.u = UserFactory()
        self.u.save()

        date_start = datetime.date(2010, 0o4, 0o1)
        date_month_end = datetime.date(2010, 0o4, 30)
        date_end = datetime.date(2010, 0o5, 31)

        # Attribute some membership Contracts
        self.u.contracts.create(
            start=date_start,
            end=date_end,
            ctype=ContractType.objects.get(desc='Membership'),
            tier=Tier.objects.get(desc='Regular'),
            status=u'TER'
        )

        # Ensure we only have the one Contract created so far
        self.assertEqual(self.u.contracts.count(), 1)
        self.assertEqual(self.u.contracts.all()[0].valid_till, date_month_end)

        self.u.contracts.create(
            start=datetime.date(2010, 0o6, 0o1),
            ctype=ContractType.objects.get(desc='Membership'),
            tier=Tier.objects.get(desc='Youth'),
            status=u'ACT'
        )

        # Now we have two
        self.assertEqual(self.u.contracts.count(), 2)
        self.assertEqual(date_start, self.u.member_since())

    def test_most_recent_payment(self):
        '''
        Test User::most_recent_payment
        returns the latest payment by user
        '''

        # Create user
        self.u = UserFactory()
        self.u.save()

        # No payment found now
        self.assertEquals(self.u.most_recent_payment, None)

        # Contract
        self.c = ContractFactory(
            start=datetime.date(2010, 0o4, 0o1),
            ctype=ContractType.objects.get(desc='Membership'),
            tier=Tier.objects.get(desc='Regular'),
            user=self.u, status='ACT')
        # Add some Payments
        # Initial deposit, plus first month (Apr)
        old_date = datetime.date(2010, 0o4, 14)
        new_date = datetime.date(2010, 0o5, 14)
        self.c.payments.create(
            date_paid=new_date,
            amount=256,
            user=self.u
        )
        self.c.payments.create(
            date_paid=old_date,
            amount=256,
            user=self.u
        )

        # Get latest payment
        self.assertEquals(self.u.most_recent_payment.date_paid, new_date)


class ContractTest(TestCase):

    fixtures = ['contracttype', 'tier']

    def setUp(self):

        # Set up some trial data

        # User
        self.u = UserFactory(
            username='testuser',
            first_name="Test", last_name="User",
            email="testuser@testtest.com")
        self.u.set_password('testtest')
        self.u.save()

        # Contract
        self.c = ContractFactory(
            start=datetime.date(2010, 0o4, 0o1),
            ctype=ContractType.objects.get(desc='Membership'),
            tier=Tier.objects.get(desc='Regular'),
            user=self.u, status='ACT')
        # Add some Payments
        # Initial deposit, plus first month (Apr)
        self.c.payments.create(
            date_paid=datetime.date(2010, 0o4, 14),
            amount=256,
            user=self.u
        )

        # Payment for May and June
        self.c.payments.create(
            date_paid=datetime.date(2010, 0o6, 0o1),
            amount=256,
            user=self.u
        )

        # Payment due for July, paid in October
        self.c.payments.create(
            date_paid=datetime.date(2010, 10, 0o5),
            amount=128,
            user=self.u
        )

    def testContractTotalPaid(self):
        '''
        Test that we can retrieve the total amount paid for this Contract
        '''

        self.assertEqual(self.c.total_paid,
                         self.c.payments.aggregate(
                             Sum('amount'))['amount__sum'])
        self.assertEqual(self.c.total_paid, 640)

    def testContractStatusLapsed(self):
        '''
        After the initial Payments added in setUp(),
        Contract.status should be LAPSED
        '''
        self.assertEqual(self.c.status, 'LAP')

    def testContractValidTill(self):
        '''
        After initial Payments added in setUp(),
        valid_till ought to be 31 Aug 2010, inclusive of deposit
        '''

        self.c.sync()
        self.assertEqual(self.c.valid_till, datetime.date(2010, 8, 31))

    def testContractSync(self):
        '''
        After initial Payments added in setUp(),
        and sync() is run, valid_till ought to be 31 Aug 2010
        '''

        # Intentionally disrupt the valid_till date
        self.c.valid_till = datetime.date(2010, 5, 12)

        self.c.sync()

        self.assertEqual(self.c.valid_till, datetime.date(2010, 8, 31))

    def testContractBalance(self):
        '''
        After initial Payments added in setUp(),
        Contract should be <arrear_months> * 128 in arrears
        '''

        # Calculate arrears from Contract.valid_till till today
        r = relativedelta(datetime.date.today(), self.c.valid_till)
        # Naive month calculation
        arrears_months = r.months + (r.years * 12 if r.years else 0)\
            + (1 if r.days else 0)

        self.assertEqual(self.c.balance(), -(arrears_months * 128))
        self.assertEqual(self.c.balance(in_months=True), -arrears_months)

    def testContractExtendWithPayment(self):
        '''
        Test that Contract valid_till dates are extended
        according to the quantum paid, eg. extended 3 months for 3 months paid
        '''
        # Get the baseline valid_till month
        bmonth = self.c.valid_till.month

        # Let's make a Payment
        QUANTUM = 3
        amt = QUANTUM * self.c.tier.fee
        p = PaymentFactory(
            date_paid=datetime.datetime(2010, 11, 16),
            amount=amt, contract=self.c, user=self.u)
        p.save()

        # Check the new valid_till month
        nmonth = self.c.valid_till.month

        self.assertEqual(nmonth - bmonth, QUANTUM)

    def testContractCheckLapsed(self):
        '''
        Test that instantiating a Contract causes it to check
        its own status and update it based on valid_till if necessary
        '''

        # This Contract should be Lapsed
        self.assertEqual(self.c.status, u'LAP')

        # Make it active
        self.c.status = u'ACT'
        self.c.save()

        # Grab another copy from the database
        # and show that its changed back to being Lapsed
        cc = Contract.objects.get(id=self.c.id)
        self.assertEqual(cc.status, u'LAP')

        # Shift valid_till forward past today()
        # so that we can cause it to shift back to being Active
        t = datetime.datetime.today()
        # Shift date 30 days forward
        cc.valid_till = t + datetime.timedelta(days=30)
        cc.save()

        # Retrieve it from the database again and show that it's gone Active
        ccc = Contract.objects.get(id=cc.id)
        self.assertEqual(ccc.status, u'ACT')
