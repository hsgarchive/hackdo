# -*- coding: utf-8; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import widgets
from django.forms.models import modelformset_factory
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from hado.models import Payment, Contract


class HackDoAuthenticationForm(forms.Form):
    """
    HackDo class for authenticating users.
    Allow inactive user for user with membership request.
    """
    username = forms.CharField(max_length=254)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Please enter a correct %(username)s and password. "
                           "Note that both fields may be case-sensitive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(HackDoAuthenticationForm, self).__init__(*args, **kwargs)

        # Set the label for the "username" field.
        UserModel = get_user_model()
        self.username_field = UserModel._meta.get_field(
            UserModel.USERNAME_FIELD)
        if self.fields['username'].label is None:
            self.fields['username'].label = self.username_field.verbose_name

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'] % {
                        'username': self.username_field.verbose_name
                    })
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class PaymentFormAdmin(forms.ModelForm):

    class Meta:
        model = Payment

    def clean(self):
        cd = self.cleaned_data

        if cd.get('contract'):
            if cd.get('user') and cd.get('user') != cd.get('contract').user:
                self._errors['user'] = self.error_class(
                    [_('Payment User does not match the Contract User.')])
                self._errors['contract'] = self.error_class(
                    [_('Payment User does not match the Contract User.')])

        return cd


class PaymentForm(PaymentFormAdmin):

    class Meta:
        model = Payment
        exclude = ['user', 'verified']
        # Hide the 'verified' field from the User

    def __init__(self, by_user=None, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)

        if by_user is not None:
            self.fields['contract'] = forms.ModelChoiceField(
                queryset=Contract.objects
                .filter(user__username=by_user)
                .exclude(status='TER')
                .order_by('-start'),
                empty_label=None)

PaymentFormAdminFormset = modelformset_factory(Payment, extra=0)
