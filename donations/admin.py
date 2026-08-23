from django.contrib import admin
from .models import (
    DonationPageContent,
    Campaign,
    DonationImpact,
    EmergencyAppeal,
    DonationMethod,
    Bank,
    QRCode,
    FAQ,
    DonationStatistic
)

@admin.register(DonationPageContent)
class DonationPageContentAdmin(admin.ModelAdmin):
    list_display = ('hero_title', 'intro_title')

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'goal_amount', 'raised_amount', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title',)

@admin.register(DonationImpact)
class DonationImpactAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'is_active')
    list_filter = ('is_active',)

@admin.register(EmergencyAppeal)
class EmergencyAppealAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title',)

@admin.register(DonationMethod)
class DonationMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_number', 'account_type', 'is_active')
    list_filter = ('is_active', 'account_type')
    search_fields = ('name', 'account_number')

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'account_name', 'account_number', 'branch', 'is_active')
    list_filter = ('is_active', 'bank_name')
    search_fields = ('bank_name', 'account_number')

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('method', 'details', 'is_active')
    list_filter = ('is_active', 'method')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('question',)

@admin.register(DonationStatistic)
class DonationStatisticAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'is_active')
    list_filter = ('is_active',)


from .models import ProgramDonation, PaymentGatewaySetting, FinancialTransaction

@admin.register(PaymentGatewaySetting)
class PaymentGatewaySettingAdmin(admin.ModelAdmin):
    list_display = ('provider', 'store_id', 'is_sandbox', 'is_active', 'updated_at')
    list_filter = ('provider', 'is_sandbox', 'is_active')
    search_fields = ('store_id',)

@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'transaction_type', 'category', 'amount', 'payment_method', 'trx_id', 'donor_name', 'date')
    list_filter = ('transaction_type', 'category', 'payment_method', 'date')
    search_fields = ('title', 'donor_name', 'trx_id', 'note')
    ordering = ('-date', '-id')

@admin.register(ProgramDonation)
class ProgramDonationAdmin(admin.ModelAdmin):
    list_display = ('donor_name', 'donation_type', 'frequency', 'amount', 'payment_method', 'membership_id', 'donor_phone', 'status', 'created_at')
    list_filter = ('status', 'donation_type', 'frequency', 'payment_method', 'program', 'created_at')
    search_fields = ('donor_name', 'donor_phone', 'donor_email', 'membership_id', 'trx_id', 'tran_id', 'bank_tran_id', 'program__title')
    ordering = ('-created_at',)
