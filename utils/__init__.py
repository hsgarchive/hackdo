# Various utility functions
from django.http import HttpResponse
from django.template import RequestContext, loader

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
