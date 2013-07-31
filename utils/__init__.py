# Various utility functions
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

import random
import string
import datetime


def render(request, template,
           dictionary={}, context_instance=None, mimetype='text/html'):

    t = loader.get_template(template)
    c = RequestContext(request, dictionary)

    return HttpResponse(t.render(c), mimetype)


def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))


def random_date(year_start=1950, year_end=2300):
    return datetime.datetime(
        random.choice(range(year_start, year_end)),
        random.choice(range(1, 11)),
        random.choice(range(1, 28)))


def send_email(subject_template, plain_template, html_template,
               fields, to_emails,
               from_email=settings.DEFAULT_FROM_EMAIL):
    subject = render_to_string(subject_template, fields)
    subject = ''.join(subject.splitlines())
    msg = EmailMultiAlternatives(subject,
                                 render_to_string(plain_template, fields),
                                 from_email,
                                 to_emails)
    msg.attach_alternative(render_to_string(html_template, fields),
                           "text/html")
    msg.send()
