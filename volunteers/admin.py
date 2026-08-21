from django.contrib import admin
from .models import Volunteer, TeamMember, BloodDonor

@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'full_name', 'phone', 'blood_group', 'is_public_details', 'status', 'application_date')
    list_filter = ('status', 'blood_group', 'is_public_details')
    search_fields = ('member_id', 'full_name', 'email', 'phone', 'blood_group')
    list_per_page = 20

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'order')
    list_editable = ('order',)
    list_per_page = 20

@admin.register(BloodDonor)
class BloodDonorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'blood_group', 'phone', 'location', 'last_donated', 'is_available')
    list_filter = ('blood_group', 'is_available', 'location')
    search_fields = ('full_name', 'phone', 'location')
    list_editable = ('is_available',)
    list_per_page = 20
