from django.contrib import admin
from .models import Volunteer, TeamMember

class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'status', 'application_date')
    list_filter = ('status',)
    search_fields = ('full_name', 'email', 'phone')

class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'order')
    list_editable = ('order',)

admin.site.register(Volunteer, VolunteerAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
