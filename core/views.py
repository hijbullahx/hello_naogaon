from django.shortcuts import render
from programs.models import Program, Event
from news.models import Article
from gallery.models import Photo

def home(request):
    upcoming_events = Event.objects.order_by('date')[:3]
    recent_news = Article.objects.filter(is_published=True).order_by('-publish_date')[:3]
    ongoing_programs = Program.objects.filter(status='ongoing')[:3]
    gallery_photos = Photo.objects.all().order_by('-id')[:4]

    context = {
        'upcoming_events': upcoming_events,
        'recent_news': recent_news,
        'ongoing_programs': ongoing_programs,
        'gallery_photos': gallery_photos,
    }
    return render(request, 'core/home.html', context)
