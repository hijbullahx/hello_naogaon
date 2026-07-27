from django.contrib import admin
from .models import Category, Article

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'publish_date', 'is_published')
    list_filter = ('is_published', 'category')
    search_fields = ('title', 'content')
    list_per_page = 20
