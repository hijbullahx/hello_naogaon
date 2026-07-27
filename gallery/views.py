from django.shortcuts import render
from .models import Photo

def gallery_view(request):
    """
    Displays all photos in the gallery.
    """
    photos = Photo.objects.all().order_by('-id')
    context = {'photos': photos}
    return render(request, 'gallery/gallery.html', context)