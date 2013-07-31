# -*- coding: utf-8; -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.conf.urls.defaults import patterns
from django.contrib import messages
from django.shortcuts import render

from hado.models import Payment, Contract, Tier,\
    ContractType, MembershipReview, BankLog
from hado.forms import PaymentFormAdmin, HackDoUserCreationForm,\
    HackDoUserChangeForm, BankLogUploadForm
from hado.admin_site import HackdoAdmin
from datetime import datetime
import csv

hdadmin = HackdoAdmin()
User = get_user_model()


# Inline classes
class PaymentInline(admin.TabularInline):
    model = Payment
    form = PaymentFormAdmin
    extra = 1

    fields = ('date_paid', 'amount', 'contract', 'method', 'desc', 'verified')


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
            'fields': ('user', ('date_paid', 'amount', 'method', 'contract', ),
                       'desc', 'verified', 'bank_log')
        }),
    )
    list_display = (
        'user', 'contract', 'bank_log',
        'date_paid', 'amount', 'method', 'desc', 'verified')
    raw_id_fields = ('contract', 'user', 'bank_log')


class ContractAdmin(admin.ModelAdmin):
    inlines = [PaymentInline, ]
    raw_id_fields = ('user',)
    search_fields = [
        'ctype__desc', 'tier__desc', 'user__username', 'user__email']


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


class MembershipReviewAdmin(admin.ModelAdmin):
    raw_id_fields = ('applicant', 'referrer')
    list_display = ('applicant', 'referrer', 'reviewed')
    search_fields = ['applicant__username']


def _handle_csv_file(f, exclude_first_line=True):
    """@params f: filehandler"""

    # Split lines of the Files
    raw_data = f.read().splitlines()

    # Remove first line
    if exclude_first_line:
        del raw_data[0]

    # Convert into a CSV file
    uploaded_csv = csv.reader(raw_data)

    # Create the banklog object
    for row in uploaded_csv:
        if row[3].strip() == "" and row[4].strip() == "":
            raise Exception("Bank Log is not correct!")
        elif row[3].strip() == "":
            amount = float(row[4].strip())
            t_type = "WTD"
        else:
            amount = float(row[3].strip())
            t_type = "DPT"
        log = BankLog(
            date=datetime.strptime(row[0].strip(), "%d/%m/%Y").date(),
            desc=row[1].strip(),
            currency=row[2].strip(),
            amount=amount,
            t_type=t_type,
        )
        log.save()


def import_bank_log_csv(request):
    if request.method == 'POST':
        form = BankLogUploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['csv_file']
            exclude_first_line = request.POST.get('exclude_first_line', False)
            try:
                _handle_csv_file(f, exclude_first_line)
            except Exception:
                error = "There are errors in your bank log file."
                messages.error(request, error)
            else:
                status = "The bank log file has been saved correctly."
                messages.success(request, status)
    else:
        form = BankLogUploadForm()

    return render(
        request,
        'admin/banklog-upload.html',
        {
            'form': form,
            'title': 'Research Keyword CSV Upload',
        })


class BankLogAdmin(admin.ModelAdmin):
    list_display = ('date', 'desc', 'currency', 'amount', 't_type')
    search_fields = ['des', 'date']
    change_list_template = 'admin/banklog-changelist.html'

    def get_urls(self):
        urls = super(BankLogAdmin, self).get_urls()
        return patterns(
            '',
            (r'^upload/$', self.admin_site.admin_view(import_bank_log_csv)))\
            + urls


hdadmin.register(User, HackDoUserAdmin)
hdadmin.register(Contract, ContractAdmin)
hdadmin.register(Payment, PaymentAdmin)
hdadmin.register(MembershipReview, MembershipReviewAdmin)
hdadmin.register(BankLog, BankLogAdmin)
hdadmin.register(ContractType)
hdadmin.register(Tier)
