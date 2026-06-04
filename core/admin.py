from django.contrib import admin
from .models import SiteSetting, ContactMessage

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Allow only one SiteSetting instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject')
