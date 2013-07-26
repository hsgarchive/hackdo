from django.contrib.auth import get_user_model

from hado import models
from hado.models import CONTRACT_STATUSES
from hado.models import PAYMENT_METHODS, PAYMENT_STATUSES

from utils import random_string, random_date

import factory
import random
import datetime

User = get_user_model()
# NOTE: ContractType and Tier has fixture as they are fixed data


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    username = factory.LazyAttribute(lambda a: random_string(5))

    is_superuser = False
    is_staff = False
    is_active = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', 'password')
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class SuperUserFactory(UserFactory):
    username = 'alice'
    first_name = 'World'
    last_name = 'Alice'
    email = factory.LazyAttribute(lambda a:
                                  '{0}.{1}@test.sg'.format(
                                      a.first_name, a.last_name).lower())
    is_superuser = True
    is_staff = True
    is_active = True


class StaffUserFactory(UserFactory):
    username = 'bob'
    first_name = 'World'
    last_name = 'Bob'
    email = factory.LazyAttribute(lambda a:
                                  '{0}.{1}@example.sg'.format(
                                      a.first_name, a.last_name).lower())
    is_superuser = False
    is_staff = True
    is_active = True


class NormalUserFactory(UserFactory):
    username = 'charlie'
    first_name = 'World'
    last_name = 'Charlie'
    email = factory.LazyAttribute(lambda a:
                                  '{0}.{1}@hackspace.sg'.format(
                                      a.first_name, a.last_name).lower())
    is_superuser = False
    is_staff = False
    is_active = True


class PendingUserFactory(UserFactory):
    username = 'dave'
    first_name = 'World'
    last_name = 'Dave'
    email = factory.LazyAttribute(lambda a:
                                  '{0}.{1}@hackspace.sg'.format(
                                      a.first_name, a.last_name).lower())
    is_superuser = False
    is_staff = False
    is_active = False


class MembershipReviewFactory(factory.Factory):
    FACTORY_FOR = models.MembershipReview

    applicant = factory.SubFactory(PendingUserFactory)
    referrer = factory.SubFactory(UserFactory)
    reviewed = False


class ContractFactory(factory.Factory):
    FACTORY_FOR = models.Contract

    start = random_date()
    end = datetime.datetime(start.year, start.month + 1, start.day)
    user = factory.SubFactory(UserFactory)
    status = random.choice(CONTRACT_STATUSES)
    desc = factory.LazyAttribute(lambda a: random_string(1024))
    # NOTE: ctype and tier need to be created with your own needs


class PaymentFactory(factory.Factory):
    FACTORY_FOR = models.Payment

    date_paid = random_date()
    amount = 200.88
    method = random.choice(PAYMENT_METHODS)
    contract = factory.SubFactory(ContractFactory)
    desc = factory.LazyAttribute(lambda a: random_string(255))
    user = factory.SubFactory(UserFactory)
    verified = random.choice(PAYMENT_STATUSES)


class LockerFactory(factory.Factory):
    FACTORY_FOR = models.Locker

    user = factory.SubFactory(UserFactory)
    num = random.randint(1, 1000)
