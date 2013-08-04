# -*- coding: utf-8; -*-
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import ugettext_lazy as _
from django.forms.models import modelformset_factory
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserChangeForm

from hado.models import Payment, Contract, MembershipReview

User = get_user_model()


class HackDoUserCreationForm(forms.ModelForm):
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    username = forms.RegexField(label=_("Username"), max_length=40,
                                regex=r'^[\w.@+-]+$',
                                help_text=_("Required. 40 characters or fewer "
                                            "Letters, digits and "
                                            "@/./+/-/_ only."),
                                error_messages={
                                    'invalid': _("This value may contain only "
                                                 "letters, numbers and "
                                                 "@/./+/-/_ characters.")})
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above,"
                                            " for verification."))

    def clean_username(self):
        # Since HackDoUser.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(HackDoUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'email',)


class HackDoUserChangeForm(UserChangeForm):
    username = forms.RegexField(
        label=_("Username"), max_length=40, regex=r"^[\w.@+-]+$",
        help_text=_("Required. 40 characters or fewer. Letters, digits and "
                    "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})

    def clean(self):
        cleaned_data = super(UserChangeForm, self).clean()
        change_is_active = cleaned_data.get("is_active")
        if self.instance.is_active is False and change_is_active is True:
            has_pending_reviews = MembershipReview.objects.filter(
                applicant=self.instance, reviewed=False).exists()
            if has_pending_reviews:
                msg = _("There still have pending membership review request\
                        for this user.")
                self._errors["is_active"] = self.error_class([msg])
                del cleaned_data["is_active"]
        return cleaned_data

    class Meta:
        model = User
        fields = (
            'username', 'email', 'is_active', 'password', 'utype',
            'profile_image', 'is_gravatar_enabled',
            'first_name', 'last_name', 'groups',
            'is_staff', 'is_superuser', 'user_permissions',
            'last_login', 'date_joined',
        )


class HackDoUserEmailChangeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(HackDoUserEmailChangeForm, self).__init__(*args, **kwargs)
        try:
            self.fields['email'].initial = self.instance.email
        except User.DoesNotExist:
            pass

    def save(self, *args, **kwargs):
        """
        Change email address before save form
        """
        u = self.instance
        u.email = self.cleaned_data['email']
        u.save()
        profile = super(HackDoUserEmailChangeForm, self).save(*args, **kwargs)
        return profile

    class Meta:
        model = User
        fields = ('email',)


class HackDoUserAvatarChangeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(HackDoUserAvatarChangeForm, self).__init__(*args, **kwargs)
        try:
            self.fields['profile_image'].initial = self.instance.profile_image
        except User.DoesNotExist:
            pass

    def save(self, *args, **kwargs):
        """
        Change email address before save form
        """
        u = self.instance
        u.profile_image = self.cleaned_data['profile_image']
        u.save()
        profile = super(HackDoUserAvatarChangeForm, self).save(*args, **kwargs)
        return profile

    class Meta:
        model = User
        fields = ('profile_image',)


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
        self.username_field = User._meta.get_field(
            User.USERNAME_FIELD)
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
        exclude = ['user', 'verified', 'bank_log']
        # Hide the 'verified' and 'bank_log' field from the User

    def __init__(self, by_user=None, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)

        if by_user is not None:
            self.fields['contract'] = forms.ModelChoiceField(
                queryset=Contract.objects
                .filter(user__username=by_user)
                .exclude(status='TER')
                .order_by('-start'),
                empty_label=None)


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
        username_used = User.objects.filter(username=data).exists()
        if username_used:
            raise forms.ValidationError(_('Username is already taken.'))
        return data

    def clean_refer_one(self):
        data = self.cleaned_data['refer_one']
        qs = User.objects.filter(username=data)
        try:
            u = qs.get()
        except User.DoesNotExist:
            raise forms.ValidationError(_('Referrer One is invalid.'))
        else:
            if not u.is_active:
                raise forms.ValidationError(_('Referrer One is inactive.'))
            self.refer_one_user = u
        return data

    def clean_refer_two(self):
        data = self.cleaned_data['refer_two']
        qs = User.objects.filter(username=data)
        try:
            u = qs.get()
        except User.DoesNotExist:
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


class BankLogUploadForm(forms.Form):
    csv_file = forms.FileField(label="CSV File: ", required=True)
    exclude_first_line = forms.BooleanField(initial=True, required=False)

    def clean(self):
        cleaned_data = super(BankLogUploadForm, self).clean()
        data = cleaned_data.get('csv_file')
        if data and (not data.name.endswith('.csv')):
            msg = u'You can only upload csv files.'
            self._errors['csv_file'] = self.error_class([msg])
            del cleaned_data['csv_file']

        return cleaned_data


PaymentFormAdminFormset = modelformset_factory(Payment, extra=0)
UserFormAdminFormset = modelformset_factory(
    User, form=HackDoUserChangeForm, extra=0)
