from django.contrib import admin
from .models import Album, Photo

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title',)
    inlines = [PhotoInline]

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('album', 'caption')
    list_filter = ('album',)
    search_fields = ('caption',)
