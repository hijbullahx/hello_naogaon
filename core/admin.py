from django.contrib import admin
from .models import SiteSetting, StatCounter, AboutImage, ContactMessage

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('title', 'tagline', 'contact_phone', 'contact_email')
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(StatCounter)
class StatCounterAdmin(admin.ModelAdmin):
    list_display = ('title', 'value', 'icon_class', 'badge_color', 'order', 'is_active')
    list_editable = ('value', 'order', 'is_active')

@admin.register(AboutImage)
class AboutImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'is_featured', 'order')
    list_editable = ('is_featured', 'order')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_per_page = 20

