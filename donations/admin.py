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
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'account_name', 'account_number', 'is_active')
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
