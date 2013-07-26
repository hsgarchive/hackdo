# -*- coding: utf-8; -*-
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import ugettext_lazy as _
from django.forms.models import modelformset_factory
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from hado.models import Payment, Contract

UserModel = get_user_model()


class HackDoPasswordChangeForm(PasswordChangeForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        min_length=7,
        max_length=128,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        widget=forms.PasswordInput,
        min_length=7,
        max_length=128,
    )


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


class NewAccountForm(forms.Form):

    CONTRACT_TYPE_CHOICES = (
        ('TMEM', 'Trial Member'),
        ('YMEM', 'Youth Member'),
        ('RMEM', 'Regular Member'),
    )

    username = forms.CharField(
        required=True,
        label=_('Username'),
        max_length=40,
        help_text=_('unique identifier'),
    )
    email = forms.EmailField(
        required=True,
        label=_('Email'),
        max_length=255,
        help_text=_('password reset email'),
    )
    first_name = forms.CharField(
        required=False,
        label=_('First Name'),
        max_length=30,
    )
    last_name = forms.CharField(
        required=False,
        label=_('Last Name'),
        max_length=30,
    )
    password = forms.CharField(
        required=True,
        label=_('Passowrd'),
        widget=forms.PasswordInput,
        min_length=7,
        max_length=128,
        help_text=_('minimum is 7 characters'),
    )
    password_confirm = forms.CharField(
        required=True,
        label=_('Passowrd Confirm'),
        widget=forms.PasswordInput,
        min_length=7,
        max_length=128,
    )
    refer_one = forms.CharField(
        required=True,
        label=_('Referrer One Username'),
        max_length=40,
    )
    refer_two = forms.CharField(
        required=True,
        label=_('Referrer Two Username'),
        max_length=40,
    )
    contract_type = forms.ChoiceField(
        required=True,
        label=_('Contract Type'),
        choices=CONTRACT_TYPE_CHOICES,
    )

    def clean_username(self):
        data = self.cleaned_data['username']
        username_used = UserModel.objects.filter(username=data).exists()
        if username_used:
            raise forms.ValidationError(_('Username is already taken.'))
        return data

    def clean_refer_one(self):
        data = self.cleaned_data['refer_one']
        qs = UserModel.objects.filter(username=data)
        try:
            u = qs.get()
        except UserModel.DoesNotExist:
            raise forms.ValidationError(_('Referrer One is invalid.'))
        else:
            if not u.is_active:
                raise forms.ValidationError(_('Referrer One is inactive.'))
            self.refer_one_user = u
        return data

    def clean_refer_two(self):
        data = self.cleaned_data['refer_two']
        qs = UserModel.objects.filter(username=data)
        try:
            u = qs.get()
        except UserModel.DoesNotExist:
            raise forms.ValidationError(_('Referrer Two is invalid.'))
        else:
            if not u.is_active:
                raise forms.ValidationError(_('Referrer Two is inactive.'))
            self.refer_two_user = u
        return data

    def clean(self):
        password_error = _('Password doesn\'t match the confirmation.')
        referrer_error = _('Referrer must be different.')
        cleaned_data = super(NewAccountForm, self).clean()
        p_data = cleaned_data.get('password')
        pc_data = cleaned_data.get('password_confirm')
        if (p_data and pc_data) and (p_data != pc_data):
            self._errors['password_confirm'] = self.error_class(
                [password_error])
            del cleaned_data['password']
            del cleaned_data['password_confirm']
        r1_data = cleaned_data.get('refer_one')
        r2_data = cleaned_data.get('refer_two')
        if (r1_data and r2_data) and (r1_data == r2_data):
            self._errors['refer_one'] = self.error_class(
                [referrer_error])
            self._errors['refer_two'] = self.error_class(
                [referrer_error])
            del cleaned_data['refer_one']
            del cleaned_data['refer_two']
        return cleaned_data
