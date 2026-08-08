from django.shortcuts import render, redirect
from django.contrib import messages
from programs.models import Program, Event, SuccessStory
from news.models import Article
from gallery.models import Photo
from volunteers.models import TeamMember, BloodDonor
from donations.models import Bank, QRCode, DonationMethod
from .models import SiteSetting, StatCounter, AboutImage, ContactMessage

def home(request):
    site_setting = SiteSetting.objects.first()
    stat_counters = StatCounter.objects.filter(is_active=True).order_by('order')
    
    about_featured_image = AboutImage.objects.filter(is_featured=True).first()
    about_grid_images = AboutImage.objects.filter(is_featured=False).order_by('order')[:4]

    ongoing_programs = Program.objects.filter(status='ongoing').order_by('order', '-id')[:5]
    if not ongoing_programs.exists():
        ongoing_programs = Program.objects.all().order_by('order', '-id')[:5]

    recent_news = Article.objects.filter(is_published=True).order_by('-publish_date')[:3]
    banks = Bank.objects.filter(is_active=True)
    qrcodes = QRCode.objects.filter(is_active=True)
    donation_methods = DonationMethod.objects.filter(is_active=True)
    gallery_photos = Photo.objects.all().order_by('-id')[:6]

    context = {
        'site_setting': site_setting,
        'stat_counters': stat_counters,
        'about_featured_image': about_featured_image,
        'about_grid_images': about_grid_images,
        'ongoing_programs': ongoing_programs,
        'recent_news': recent_news,
        'banks': banks,
        'qrcodes': qrcodes,
        'donation_methods': donation_methods,
        'gallery_photos': gallery_photos,
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
