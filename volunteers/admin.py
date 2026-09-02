from django.contrib import admin
from .models import Volunteer, TeamMember, BloodDonor
from core.email_utils import send_system_email

@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'full_name', 'phone', 'blood_group', 'is_public_details', 'status', 'application_date')
    list_filter = ('status', 'blood_group', 'is_public_details')
    search_fields = ('member_id', 'full_name', 'email', 'phone', 'blood_group')
    list_per_page = 20

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
        if is_new and obj.email:
            try:
                subject = f"Hello Naogaon - পরিচালনা পর্ষদ / টিম মেম্বার হিসেবে আপনাকে স্বাগতম!"
                paragraphs = [
                    f"হ্যালো নওগাঁ (Hello Naogaon)-এর পরিচালনা পর্ষদ / টিম মেম্বার ({obj.effective_role}) হিসেবে যুক্ত হওয়ায় আপনাকে আন্তরিক মোবারকবাদ ও শুভেচ্ছা!",
                    "সংগঠনকে সামনের দিকে এগিয়ে নিতে এবং মানবতার সেবায় কার্যকর ভূমিকা পালনে আপনার সক্রিয় সহযোগিতা আমাদের জন্য অত্যন্ত গর্বের।"
                ]
                login_info = None
                if obj.user:
                    login_info = {
                        'username': obj.user.username,
                        'role': obj.effective_role,
                    }
                send_system_email(
                    subject=subject,
                    recipient_list=[obj.email],
                    recipient_name=obj.name,
                    greeting="আসসালামু আলাইকুম",
                    headline="পরিচালনা পর্ষদ ও টিম সদস্য নিবন্ধন",
                    message_paragraphs=paragraphs,
                    team_member=obj,
                    login_info=login_info,
                    request=request,
                    footer_note="আপনার অ্যাকাউন্টের নিরাপত্তা রক্ষার্থে প্রথমবার লগইন করার পর পাসওয়ার্ড পরিবর্তন করে নিন।",
                    fail_silently=True
                )
            except Exception:
                pass

@admin.register(BloodDonor)
class BloodDonorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'member_id', 'blood_group', 'phone', 'location', 'last_donated', 'is_public_details', 'is_available')
    list_filter = ('blood_group', 'is_available', 'is_public_details', 'location')
    search_fields = ('full_name', 'member_id', 'phone', 'location')
    list_editable = ('is_available', 'is_public_details')
    list_per_page = 20
