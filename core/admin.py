from django.contrib import admin
from .models import SiteSetting, StatCounter, AboutImage

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('title', 'tagline', 'contact_phone', 'contact_email')
    fieldsets = (
        ('সাধারণ তথ্য (General Info)', {
            'fields': ('title', 'tagline', 'logo')
        }),
        ('হিরো সেকশন (Hero Section)', {
            'fields': ('hero_badge', 'hero_title', 'hero_subtitle', 'hero_image')
        }),
        ('আমাদের সম্পর্কে (About Section)', {
            'fields': ('about_heading', 'about_text', 'mission_text', 'vision_text')
        }),
        ('কল টু অ্যাকশন (CTA Banner)', {
            'fields': ('cta_banner_title', 'cta_banner_button_text')
        }),
        ('যোগাযোগ ও ফুটার (Contact & Footer)', {
            'fields': ('contact_phone', 'contact_email', 'contact_address', 'facebook_url', 'youtube_url', 'whatsapp_number', 'footer_about', 'google_map_embed_url')
        }),
    )
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


