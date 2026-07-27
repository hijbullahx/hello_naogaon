from django.contrib import admin
from .models import DonationMethod

@admin.register(DonationMethod)
class DonationMethodAdmin(admin.ModelAdmin):
    list_display = ('method_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('method_name',)
