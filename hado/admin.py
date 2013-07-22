# -*- coding: utf-8; -*-
import re

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django import forms

from hado.models import Payment, Contract, Tier,\
    HackDoUser, ContractType, MembershipReview
from hado.forms import PaymentFormAdmin
from hado.admin_site import HackdoAdmin

hdadmin = HackdoAdmin()


# Inline classes
class PaymentInline(admin.TabularInline):
    model = Payment
    form = PaymentFormAdmin
    extra = 1

    fields = ('date_paid', 'amount', 'contract', 'method', 'desc', 'verified')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "contract":

            # Assuming we're editing user in the address eg.
            # "/admin/hado/user/3/"
            # So we extract the user_id portion
            # from that path and use it in our
            # queryset filter
            m = re.search("/.+\/(?P<id>\d+)\/?", request.path_info)
            if m is not None:
                user_id = m.group('id')
                kwargs["queryset"] = Contract.objects.filter(
                    user__id=user_id)
                #.exclude(status = "TER")
                return db_field.formfield(**kwargs)
        return super(PaymentInline, self).formfield_for_foreignkey(db_field,
                                                                   request,
                                                                   **kwargs)


class TierInline(admin.TabularInline):
    model = Tier


class ContractInline(admin.TabularInline):
    model = Contract
    extra = 0
    inlines = [PaymentInline, ]


# ModelAdmin classes
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentFormAdmin

    fieldsets = (
        (None, {
            'fields': ('user', ('date_paid', 'amount', 'contract', 'method'),
                       'desc', 'verified')
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "contract":
            # Assuming we're editing user in the address eg.
            # "/admin/hado/user/3/"
            # So we extract the user_id portion
            # from that path and use it in our
            # queryset filter
            m = re.search("/.+\/(?P<id>\d+)\/?$", request.path_info)
            if m is not None:
                pid = m.group('id')
                kwargs["queryset"] = Contract.objects.filter(
                    user__id=Payment.objects.get(id=pid).user_id)
                #.exclude(status = "TER")
                kwargs['empty_label'] = None
                return db_field.formfield(**kwargs)
        return super(PaymentAdmin, self).formfield_for_foreignkey(db_field,
                                                                  request,
                                                                  **kwargs)


class ContractAdmin(admin.ModelAdmin):
    inlines = [PaymentInline, ]


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
            HackDoUser._default_manager.get(username=username)
        except HackDoUser.DoesNotExist:
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
        model = HackDoUser
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
        cleaned_data = super(HackDoUserChangeForm, self).clean()
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
        model = HackDoUser
        fields = (
            'username', 'email', 'is_active',
            'profile_image', 'is_gravatar_enabled',
            'first_name', 'last_name', 'groups',
            'is_staff', 'is_superuser', 'user_permissions',
            'last_login', 'date_joined',
        )


class HackDoUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2')
        }),
    )
    add_form = HackDoUserCreationForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'email',
            'profile_image', 'is_gravatar_enabled',
        )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    form = HackDoUserChangeForm
    list_display = ('username', 'email', 'is_staff', 'is_superuser',
                    'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    inlines = [ContractInline, PaymentInline, ]
    readonly_fields = ['last_login', 'date_joined']


hdadmin.register(HackDoUser, HackDoUserAdmin)
hdadmin.register(Contract, ContractAdmin)
hdadmin.register(Payment, PaymentAdmin)
hdadmin.register(ContractType)
hdadmin.register(MembershipReview)
hdadmin.register(Tier)
