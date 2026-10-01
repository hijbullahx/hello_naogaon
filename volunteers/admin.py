from django.contrib import admin
from .models import Volunteer, TeamMember, BloodDonor
from core.email_utils import send_system_email

@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'full_name', 'phone', 'blood_group', 'registration_fee', 'payment_status', 'payment_method', 'status', 'application_date')
    list_filter = ('status', 'payment_status', 'blood_group', 'is_public_details')
    search_fields = ('member_id', 'full_name', 'email', 'phone', 'sender_account', 'trx_id')
    list_per_page = 20
    actions = ['approve_volunteers']

    @admin.action(description="✅ নির্বাচিত সদস্যদের অনুমোদন করুন (Approve & Generate ID & Send SMS/Email)")
    def approve_volunteers(self, request, queryset):
        from .views import send_member_notifications
        from .models import generate_unique_member_id
        from donations.models import FinancialTransaction, ProgramDonation
        from django.db.models import Q
        from datetime import date

        count = 0
        for vol in queryset:
            if vol.status != 'approved':
                vol.status = 'approved'
                vol.payment_status = 'paid'
                if not vol.member_id:
                    vol.member_id = generate_unique_member_id(prefix_str="")
                vol.save()

                linked_donation = ProgramDonation.objects.filter(
                    Q(membership_id=f"NEW_VOL_{vol.id}") | Q(tran_id=vol.tran_id) | Q(donor_phone=vol.phone, donation_type='volunteer_registration')
                ).first()
                if linked_donation:
                    linked_donation.status = 'approved'
                    linked_donation.membership_id = vol.member_id
                    linked_donation.save(update_fields=['status', 'membership_id'])

                trx_id = vol.trx_id or (linked_donation.trx_id if linked_donation else None) or f"REG{vol.id}"
                if not FinancialTransaction.objects.filter(trx_id=trx_id, transaction_type='income').exists():
                    FinancialTransaction.objects.create(
                        transaction_type='income',
                        title=f"সদস্য নিবন্ধন ফি ({vol.full_name}) - আইডি: {vol.member_id}",
                        category="সদস্য নিবন্ধন ফি",
                        amount=vol.registration_fee or 100.00,
                        payment_method=vol.payment_method or 'Manual',
                        trx_id=trx_id,
                        donor_name=vol.full_name,
                        date=date.today(),
                        note=f"সদস্য নিবন্ধন ফি | আইডি: {vol.member_id} | মোবাইল: {vol.phone}"
                    )

                try:
                    send_member_notifications(vol)
                except Exception:
                    pass
                count += 1
        self.message_user(request, f"{count} জন সদস্য সফলভাবে অনুমোদিত হয়েছে এবং তাদের আইডি ও নোটিফিকেশন পাঠানো হয়েছে।")

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        if is_new and obj.email:
            try:
                subject = f"Helpline Hello Naogaon - সদস্য নিবন্ধন সম্পন্ন (আইডি: {obj.member_id})"
                paragraphs = [
                    "Helpline Hello Naogaon-এ সদস্য/স্বেচ্ছাসেবক হিসেবে সফলভাবে নিবন্ধিত হওয়ার জন্য আপনাকে আন্তরিক মোবারকবাদ ও অভিনন্দন!",
                    "আমাদের সংগঠনের মূল লক্ষ্য মানবতার সেবায় নিঃস্বার্থভাবে কাজ করা এবং সমাজের অসহায় মানুষের পাশে দাঁড়ানো।"
                ]
                send_system_email(
                    subject=subject,
                    recipient_list=[obj.email],
                    recipient_name=obj.full_name,
                    greeting="প্রিয়",
                    headline="সদস্য ও রক্তদাতা নিবন্ধন সম্পন্ন",
                    message_paragraphs=paragraphs,
                    volunteer=obj,
                    request=request,
                    fail_silently=True
                )
            except Exception:
                pass

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'member_id', 'email', 'phone', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'role', 'member_id', 'email', 'phone')
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        if is_new:
            try:
                from .subscription_services import send_member_registration_notification
                send_member_registration_notification(obj)
            except Exception as e:
                pass

@admin.register(BloodDonor)
class BloodDonorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'member_id', 'blood_group', 'phone', 'location', 'last_donated', 'is_public_details', 'is_available')
    list_filter = ('blood_group', 'is_available', 'is_public_details', 'location')
    search_fields = ('full_name', 'member_id', 'phone', 'location')
    list_editable = ('is_available', 'is_public_details')
    list_per_page = 20
