from django.contrib import admin
from .models import Program, Event, SuccessStory

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'target_amount', 'raised_amount', 'icon_class', 'order')
    list_editable = ('status', 'target_amount', 'order')
    list_filter = ('status',)
    search_fields = ('title', 'description', 'short_description')

    def save_model(self, request, obj, form, change):
        old_target = None
        if change:
            old_obj = Program.objects.filter(pk=obj.pk).first()
            old_target = old_obj.target_amount if old_obj else None
        super().save_model(request, obj, form, change)
        if obj.target_amount and float(obj.target_amount) > 0:
            if old_target is None or float(old_target) == 0 or float(old_target) != float(obj.target_amount):
                from .program_notifications import notify_members_volunteers_program_fund
                notify_members_volunteers_program_fund(obj, request=request)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'date')
    search_fields = ('title', 'location')

@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title', 'content')
