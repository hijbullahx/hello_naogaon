from django.contrib import admin
from .models import Volunteer, TeamMember

@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'status', 'application_date')
    list_filter = ('status',)
    search_fields = ('full_name', 'email', 'phone')
    list_per_page = 20

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'order')
    list_editable = ('order',)
    list_per_page = 20
