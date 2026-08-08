from django.contrib import admin
from .models import Program, Event, SuccessStory

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'icon_class', 'badge_color', 'order')
    list_editable = ('status', 'order')
    list_filter = ('status',)
    search_fields = ('title', 'description', 'short_description')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'date')
    search_fields = ('title', 'location')

@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title', 'content')
