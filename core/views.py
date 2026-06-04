from django.shortcuts import render, redirect
from django.contrib import messages
from programs.models import Program, Event, SuccessStory
from news.models import Article
from gallery.models import Photo
from volunteers.models import TeamMember
from .models import SiteSetting, ContactMessage

def home(request):
    site_setting = SiteSetting.objects.first()
    upcoming_events = Event.objects.order_by('date')[:3]
    recent_news = Article.objects.filter(is_published=True).order_by('-publish_date')[:3]
    ongoing_programs = Program.objects.filter(status='ongoing')[:3]
    gallery_photos = Photo.objects.all().order_by('-id')[:6]
    success_stories = SuccessStory.objects.order_by('-date')[:3]

    context = {
        'site_setting': site_setting,
        'upcoming_events': upcoming_events,
        'recent_news': recent_news,
        'ongoing_programs': ongoing_programs,
        'gallery_photos': gallery_photos,
        'success_stories': success_stories,
    }
    return render(request, 'core/home.html', context)

def about(request):
    site_setting = SiteSetting.objects.first()
    team_members = TeamMember.objects.all()
    context = {
        'site_setting': site_setting,
        'team_members': team_members,
    }
    return render(request, 'core/about.html', context)

def contact(request):
    site_setting = SiteSetting.objects.first()
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if name and email and message:
            ContactMessage.objects.create(
                name=name, email=email, subject=subject, message=message
            )
            messages.success(request, 'আপনার বার্তা সফলভাবে পাঠানো হয়েছে। ধন্যবাদ!')
            return redirect('core:contact')
        else:
            messages.error(request, 'দয়া করে সমস্ত প্রয়োজনীয় ফিল্ড পূরণ করুন।')

    context = {
        'site_setting': site_setting,
    }
    return render(request, 'core/contact.html', context)
