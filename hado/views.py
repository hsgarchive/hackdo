# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
#from ragendja.template import render_to_response
from django.shortcuts import *
from utils import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout

# Models
from hado.models import *


def index(request):
	
	userlist = User.objects.all()
	
	return render_to_response(request, 'index.html', {'userlist': userslist})