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
    list_display = ('donor_name', 'donation_type', 'amount', 'payment_method', 'sender_account', 'trx_id', 'membership_id', 'donor_phone', 'status', 'created_at')
    list_filter = ('status', 'donation_type', 'frequency', 'payment_method', 'program', 'created_at')
    search_fields = ('donor_name', 'donor_phone', 'donor_email', 'membership_id', 'sender_account', 'trx_id', 'tran_id', 'bank_tran_id', 'program__title')
    ordering = ('-created_at',)
    actions = ['approve_donations', 'reject_donations']

    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            orig = ProgramDonation.objects.filter(pk=obj.pk).first()
            if orig:
                old_status = orig.status

        super().save_model(request, obj, form, change)

        # Status transition to Approved
        if obj.status == 'approved' and old_status != 'approved':
            try:
                from .views import process_successful_payment
                process_successful_payment(obj, {
                    'payment_method': obj.payment_method,
                    'trx_id': obj.trx_id or obj.tran_id,
                    'transaction_id': obj.trx_id or obj.tran_id,
                }, request=request)
            except Exception as e:
                pass
        # Status transition to Rejected or Cancelled
        elif obj.status in ['rejected', 'cancelled', 'failed'] and old_status not in ['rejected', 'cancelled', 'failed']:
            try:
                from .donation_notifications import notify_donor_donation_rejected
                notify_donor_donation_rejected(obj, reason=obj.note or 'তথ্য যাচাই ব্যর্থ হয়েছে', request=request)
            except Exception as e:
                pass

    @admin.action(description="✅ নির্বাচিত অনুদানসমূহ অনুমোদন করুন (Approve & Notify Donor)")
    def approve_donations(self, request, queryset):
        from .views import process_successful_payment
        approved_count = 0
        for item in queryset:
            if item.status != 'approved':
                item.status = 'approved'
                item.save()
                process_successful_payment(item, {
                    'payment_method': item.payment_method,
                    'trx_id': item.trx_id or item.tran_id,
                    'transaction_id': item.trx_id or item.tran_id,
                }, request=request)
                approved_count += 1
        self.message_user(request, f"{approved_count}টি অনুদান সফলভাবে অনুমোদন করা হয়েছে এবং দাতাদের কাছে নোটিফিকেশন পাঠানো হয়েছে।")

    @admin.action(description="❌ নির্বাচিত অনুদানসমূহ বাতিল করুন (Reject & Notify Donor)")
    def reject_donations(self, request, queryset):
        from .donation_notifications import notify_donor_donation_rejected
        rejected_count = 0
        for item in queryset:
            if item.status != 'rejected':
                item.status = 'rejected'
                item.save()
                notify_donor_donation_rejected(item, reason='অ্যাডমিন প্যানেল থেকে বাতিল করা হয়েছে', request=request)
                rejected_count += 1
        self.message_user(request, f"{rejected_count}টি অনুদান বাতিল করা হয়েছে এবং দাতাদের কাছে নোটিফিকেশন পাঠানো হয়েছে।")

