from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('programs/', include('programs.urls')),
    path('news/', include('news.urls')),
    path('gallery/', include('gallery.urls')),
    path('volunteers/', include('volunteers.urls')),
    path('donations/', include('donations.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
