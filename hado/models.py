# -*- coding: utf-8; -*-
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.http import urlquote
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import Sum
from django.db.models.signals import post_init, post_save, pre_save
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.sites.models import Site

from hado.managers import HackDoUserManager

from dateutil.relativedelta import relativedelta
from utils import send_email
import urllib
import hashlib
import datetime
import calendar
import os


def get_image_path(instance, filename):
    now = datetime.datetime.now()
    newfilename = hashlib.md5(now.strftime("%I%M%S") + filename).hexdigest()\
        + os.path.splitext(filename)[1]
    return 'user_avatars/%s/%s' % (instance.username, newfilename)

DISPATCH_UID_PREFIX = settings.DISPATCH_UID_PREFIX
EMAIL_SUBJECT_PREFIX = settings.EMAIL_SUBJECT_PREFIX
USER_TYPES = (
    ('MEM', 'Member'),
    ('SPO', 'Sponsor'),
    ('DON', 'Donation'),
)
CONTRACT_STATUSES = (
    ('ACT', 'Active'),
    ('LAP', 'Lapsed'),
    ('TER', 'Terminated'),
    ('PEN', 'Pending')
)
PAYMENT_METHODS = (
    ('EFT', 'Electronic Fund Transfer'),
    ('CHK', 'Cheque'),
    ('CSH', 'Cash'),
    ('OTH', 'Others')
)
PAYMENT_STATUSES = (
    ('VFD', 'Verified'),
    ('RJD', 'Rejected'),
    ('PEN', 'Pending')
)
TRANSACTION_TYPE = (
    ('DPT', 'Deposit'),
    ('WTD', 'Withdrawal'),
)


class HackDoUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model, extending Django's AbstractBaseUser
    """

    # Django User required attribute
    username = models.CharField(
        _('username'),
        max_length=40,
        unique=True,
        db_index=True,
        help_text=_('primary index for user'),
    )
    email = models.EmailField(
        _('email'),
        max_length=255,
        db_index=True,
        help_text=_('email linked with user'),
    )
    first_name = models.CharField(
        _('first name'),
        max_length=30,
        blank=True,
        help_text=_('user first name'),
    )
    last_name = models.CharField(
        _('last name'),
        max_length=30,
        blank=True,
        help_text=_('user last name'),
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
        help_text=_('user joined time'),
    )
    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user \
                    can log into django admin site.')
    )
    is_active = models.BooleanField(
        _('active'), default=False,
        help_text=_('Desingates whether the user \
                    is a verified hackspacesg member.')
    )

    # HackDo User required attribute
    profile_image = models.ImageField(
        _('profile image'),
        upload_to=get_image_path,
        blank=True,
        help_text=_('user profile image'),
    )

    is_gravatar_enabled = models.BooleanField(
        _('gravatar_enabled'), default=True,
        help_text=_('Desingates whether the user \
                    uses gravatar as profile image.')
    )

    utype = models.CharField(
        _('member type'),
        max_length=3,
        choices=USER_TYPES,
        default='MEM',
        help_text=_('user member type'),
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = HackDoUserManager()

    # Django User required method
    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the username
        """
        return self.get_username()

    def get_absolute_url(self):
        """
        Returns the user default url -- /users/username
        """
        return "/users/%s/" % urlquote(self.get_username())

    def __unicode__(self):
        """
        Returns the user full name if any, else returns username
        """
        if self.first_name and self.last_name:
            return self.get_full_name()
        return self.username

    # HackDo method
    @property
    def user_avatar_url(self, size=20):
        """
        Returns user avatar url
        """
        default = "http://%s/static/img/default_avatar.png" % (
            Site.objects.get_current().domain
        )
        if self.is_gravatar_enabled:
            return "http://www.gravatar.com/avatar/%s?%s" % (
                hashlib.md5(self.email.lower()).hexdigest(),
                urllib.urlencode({'d': 'mm', 's': str(size)})
            )
        else:
            if self.profile_image:
                return self.profile_image.url
            return default

    @property
    def most_recent_payment(self):
        """
        Returns most recent payment if any
        """
        p = self.payments_made.all().order_by('-date_paid')
        return p[0] if p else None

    def total_paid(self, ptype=None):
        """
        Returns the total amount the User has paid either in total,
        or for a specified Contract type
        """
        # Construct the appropriate Queryset
        if ptype is not None:
            payments = self.payments_made.filter(contract__ctype__desc=ptype)
        else:
            payments = self.payments_made

        return payments.aggregate(Sum('amount'))['amount__sum'] or 0.0

    def membership_status(self, pretty=False):
        """
        Returns string (see Contract::CONTRACT_STATUSES)
        indicating latest Membership status of this User
        """
        try:
            if not hasattr(self, '__latest_membership'):
                lm = self.contracts.filter(ctype__desc='Membership')\
                    .exclude(status='PEN').latest('start')
                self.__latest_membership = lm

            return self.__latest_membership.get_status_display() \
                if pretty else self.__latest_membership.status

        except Contract.DoesNotExist:
            self.__latest_membership = None
            return None

    def member_since(self):
        """
        Returns datetime object representing
        start date of earliest Membership Contract if found, None otherwise
        """
        try:
            if not hasattr(self, '__member_since'):
                ms = self.contracts.filter(ctype__desc='Membership')\
                    .order_by('start')[0:1]
                if len(ms) > 0:
                    self.__member_since = ms[0].start
                else:
                    self.__member_since = None

            return self.__member_since

        except Contract.DoesNotExist:
            return None

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class ContractType(models.Model):
    """
    Stores an contract type:
        1. Membership
        2. Locker
        3. Registered Address
    """

    desc = models.CharField(
        _('description'),
        max_length=128,
        blank=False,
        null=True,
        help_text=_('contract type description')
    )

    def __unicode__(self):
        """
        Returns contract type description
        """
        return self.desc


class Tier(models.Model):
    """
    Stores an tier related to :model:`hado.ContractType`
    1. Trial
    2. Youth
    3. Regular
    4. Hotdesk
    5. Resident
    """

    fee = models.FloatField(
        _('tier fee'),
        default=0.0,
        help_text=_('tier fee'),
    )
    desc = models.CharField(
        _('description'),
        max_length=255,
        help_text=_('tier description'),
    )
    ctype = models.ForeignKey(
        ContractType,
        blank=False,
        null=True,
        help_text=_('linked contract type'),
    )

    def __unicode__(self):
        """
        Returns tier description
        """
        return self.desc


class MembershipReview(models.Model):
    """
    Stores an membership review request for model:`hado.HackDoUser`
    """
    applicant = models.ForeignKey(
        HackDoUser,
        related_name=_('applicant'),
        help_text=_('Membership applicant'),
    )

    referrer = models.ForeignKey(
        HackDoUser,
        related_name=_('referrer'),
        help_text=_('Membership referrer'),
    )

    reviewed = models.BooleanField(
        default=False,
        blank=False,
        help_text=_('Referrer reviewed?')
    )

    def __unicode__(self):
        """
        Returns applicant and referrer
        """
        return '%s requests hackspaceSG membership with %s as referrer.' % (
            self.applicant.username, self.referrer.username,)


class BankLog(models.Model):
    """
    Stores a bank transaction log related to :model:`hado.Contract`
    """
    date = models.DateField(
        help_text=_('transaction log date'),
    )
    desc = models.CharField(
        max_length=255,
        help_text=_('transaction log description'),
    )
    currency = models.CharField(
        max_length=5,
        help_text=_('currency code'),
    )
    amount = models.FloatField(
        help_text=_('locker number')
    )
    t_type = models.CharField(
        _('transaction type'),
        max_length=3,
        choices=TRANSACTION_TYPE,
        help_text=_('transaction type: \
        1. Deposit 2. Withdrawal'),
    )

    def __unicode__(self):
        """
        Returns date and description
        """
        return 'Bank log on %s for %s.' % (
            self.date, self.desc,)

    class Meta:
        unique_together = ("date", "desc")


class Contract(models.Model):
    """
    Stores an contract related to :model:`hado.ContractType`, \
    :model:`hado.HackDoUser` and :model: `hado.Tier`
    """

    start = models.DateField(
        help_text=_('contract starting time'),
    )
    end = models.DateField(
        blank=True, null=True,
        help_text=_('contract ending time'),
    )
    valid_till = models.DateField(
        editable=False,
        help_text=_('contract valid until time'),
    )
    ctype = models.ForeignKey(
        ContractType,
        blank=False,
        null=True,
        verbose_name=_('Contract type'),
        help_text=_('Locker and Address Use Contracts must use \
        their respective Tiers.\
        Membership contracts can accept all other Tiers'),
    )
    tier = models.ForeignKey(
        Tier, blank=False, null=True,
        help_text=_('Linked tier'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        null=True,
        related_name=_('contracts'),
    )
    status = models.CharField(
        max_length=3, choices=CONTRACT_STATUSES,
        help_text=_('contract status: \
        1. Active 2. Lapsed \
        3. Terminated 4.Pending'),
    )
    desc = models.CharField(
        max_length=1024,
        blank=True,
        help_text=_('Enter company name if Contract is for Address Use.\
        May use for general remarks for other Contract types')
    )

    def __extend_by(self, num_months):
        """
        Extends the validity of this Contract by specified number of months.\
        THIS METHOD DOES NOT save() AUTOMATICALLY
        """
        # We subtract one day, such that if we start on the first of a month,
        # eg. datetime.date(2011, 02, 01), extending the validity
        # by 5 months, won't give us an end date of datetime.date(2011, 07, 01)
        # [which is wrong], but datetime.date(2011, 06, 30) [which is right]
        delta = {
            'months': num_months,
            'days': -1
        }
        self.valid_till = self.valid_till + relativedelta(**delta)

        # Normalise date to end of that month
        self.valid_till = datetime.date(self.valid_till.year,
                                        self.valid_till.month,
                                        calendar.monthrange(
                                            self.valid_till.year,
                                            self.valid_till.month)[1])

    def __month_diff(self, end, start):
        """
        Returns the months (inclusive of part thereof) between two dates
        """

        r = relativedelta(end + relativedelta(days=+1), start)
        return r.months + \
            (r.years * 12 if r.years else 0) + (1 if r.days else 0)

    @property
    def total_paid(self):
        """
        Returns total amount paid due to this :model:`hado.Contract`
        """
        return self.payments.aggregate(Sum('amount'))['amount__sum'] or 0.0

    def sync(self):
        """
        Looks at the total amount paid to this :model:`hado.Contract` \
        and recalculates its proper expiry (end) date, taking a month's \
        deposit into account
        """
        # Reset the clock
        self.valid_till = self.start

        months_paid = self.total_paid / self.tier.fee

        if months_paid > 0:
            self.__extend_by(int(months_paid))

        self.save()

    def balance(self, in_months=False):
        """
        Looks at how much has been paid for this :model:`hado.Contract` \
        and determines if there is any balance owed by (-ve) / \
        owed to (+ve) the Member
        """
        balance = 0
        duration_in_months = 0

        # Calculate number of months Contract has been in effect,
        # ie. not Terminated
        if self.status == 'TER':
            duration_in_months += self.__month_diff(self.end, self.start)
        else:
            duration_in_months += self.__month_diff(datetime.date.today(),
                                                    self.start)

        balance = self.total_paid - (self.tier.fee * duration_in_months)

        if in_months:
            return balance / self.tier.fee

        else:
            return balance

    def update_with_payment(self, p):
        """
        Takes a :model:`hado.Payment`, \
        calculates how many month's worth it is, \
        and extends the contract end date accordingly
        """
        if isinstance(p, Payment):
            # Get number of multiples of Contract for this Payment
            multiples = int(p.amount / self.tier.fee)

            self.__extend_by(multiples)
            self.save()

            # sync() the Contract if this is the first Payment
            # being made on this Contract
            if self.payments.count() == 1:
                self.sync()

            else:
                return False

    def save(self, *args, **kwargs):
        """
        Overridden save() forces the date of self.end \
        to be the last day of that given month. \
        Eg. if self.end is initially declared as 5 May 2010, \
        we now force it to become 31 May 2010 \
        before actually save()'ing the object.
        """
        # But first, is self.end even specified?
        if not self.valid_till:
            self.valid_till = self.start

        today = datetime.date.today()
        last_day = calendar.monthrange(self.valid_till.year,
                                       self.valid_till.month)[1]
        self.valid_till = datetime.date(self.valid_till.year,
                                        self.valid_till.month, last_day)

        # Force start date to be normalised as 1st day of the month
        if self.start.day != 1:
            self.start = datetime.date(self.start.year, self.start.month, 1)

        # If we notice the Contract is now Terminated,
        # and the end date has not been set, set the end date
        if self.status == 'TER' and self.end is None:
            self.end = datetime.date(today.year,
                                     today.month,
                                     calendar.monthrange(today.year,
                                                         today.month)[1])

        # If the model has been saved already,
        # ie. has an id, force it to update
        # otherwise, insert a new record
        if self.id:
            kwargs['force_update'] = True
            kwargs['force_insert'] = False
        else:
            kwargs['force_insert'] = True
            kwargs['force_update'] = False

        if self.status == 'PEN':
            return super(Contract, self).save(*args, **kwargs)

        if self.valid_till > today:
            self.status = u'ACT'

        super(Contract, self).save(*args, **kwargs)

    def clean(self):
        """
        Model validation to ensure that \
        validates that :model:`hado.ContractType` \
        and :model:`hado.Tier` are allowed
        """
        if self.ctype != self.tier.ctype:
            raise ValidationError(_("Contract type and tier mismatched"))

    def __unicode__(self):
        """
        Returns :model:`hado.Tier` desc, :model:`hado.ContractType` desc \
        start time and valid time
        """
        return "%s %s | %s to %s" % (self.tier,
                                     self.ctype,
                                     self.start.strftime('%b %Y'),
                                     self.valid_till.strftime('%b %Y'))


class Payment(models.Model):
    """
    Stores a payment related to :model:`hado.Contract` \
    and :model:`hado.HackDoUser`
    """
    date_paid = models.DateField(
        _('date of payment'),
        help_text=_('date of payment'),
    )
    amount = models.FloatField(
        default=0.0,
        help_text=_('payment amount'),
    )
    method = models.CharField(
        max_length=3,
        choices=PAYMENT_METHODS,
        default='EFT',
        help_text=_('payment method: \
        1. Electronic Fund Transfer 2. Cheque \
        3. Cash 4. Others'),
    )
    contract = models.ForeignKey(
        Contract,
        blank=False,
        null=True,
        related_name=_('payments'),
    )
    desc = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Eg. Cheque or transaction number,\
        if applicable'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        null=True,
        related_name=_('payments_made'),
    )
    verified = models.CharField(
        max_length=3,
        choices=PAYMENT_STATUSES,
        default='PEN',
        help_text=_('payment status: \
        1. Verified 2. Rejected 3. Pending'),
    )
    bank_log = models.OneToOneField(
        BankLog,
        blank=True,
        null=True,
        help_text=_('linked bank log')
    )

    def __unicode__(self):
        """
        Returns :model:`hado.HackDoUser`, :model:`hado.Tier` desc, \
        :model:`hado.ContractType` desc, amount and date of payment \
        """
        return u"%s | %s %s | %s, %s" % (self.user,
                                         self.contract.tier,
                                         self.contract.ctype,
                                         self.amount,
                                         self.date_paid.strftime('%d %b %Y'))


class Locker(models.Model):
    """
    Stores a locker related to :model:`hado.HackDoUser`
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        null=True,
        related_name=_('locker')
    )
    num = models.IntegerField(
        help_text=_('locker number')
    )


# Attaching a post_save signal handler to the Payment model
# to update the appropriate Contract
def update_contract_with_payments(sender, **kwargs):
    payment = kwargs['instance']
    c = payment.contract
    c.update_with_payment(payment)

post_save.connect(
    update_contract_with_payments,
    sender=Payment,
    dispatch_uid="%s.update_contract_with_payments"
    % DISPATCH_UID_PREFIX)


# Attaching a pre_save signal handler to the Payment model
# to send out notification email when payment status changed
def send_payment_status_change_notification(sender, **kwargs):
    new = kwargs['instance']
    if not new.id:
        return
    old = Payment.objects.get(id=new.id)
    if old.verified == "PEN" and (new.verified in ["VFD", "RJD"]):
        if new.verified == "VFD":
            status = "Verified"
        elif new.verified == "RJD":
            status = "Rejected"
        else:
            status = "Pending"
        fields = {
            "prefix": EMAIL_SUBJECT_PREFIX,
            "user": old.user,
            "date": old.date_paid,
            "amount": old.amount,
            "status": status,
        }
        send_email(
            'email/payments/payment-notification-subject.txt',
            'email/payments/payment-notification.txt',
            'email/payments/payment-notification.html',
            fields,
            [old.user.email])

pre_save.connect(
    send_payment_status_change_notification,
    sender=Payment,
    dispatch_uid="%s.send_payment_status_change_notification"
    % DISPATCH_UID_PREFIX)


def lapsed_check(sender, **kwargs):
    '''
    Checks the end date of active contract and compares it with today.
    If contract is lapsed, update the contract status to lapsed.
    '''

    contract = kwargs['instance']

    # If this is a new Contract, check if we have a valid_till date set
    if not contract.id and not contract.valid_till:
        contract.valid_till = contract.start

    if contract.status == u'ACT':
        if contract.valid_till < datetime.date.today():
            contract.status = u'LAP'
            contract.save()

        elif contract.status == u'LAP' and \
                contract.valid_till > datetime.date.today():
            contract.status = u'ACT'
            contract.save()

post_init.connect(
    lapsed_check,
    sender=Contract,
    dispatch_uid="%s.lapsed_check"
    % DISPATCH_UID_PREFIX)
