from django.shortcuts import render, redirect
from django.contrib import messages
from programs.models import Program, Event, SuccessStory
from news.models import Article
from gallery.models import Photo
from volunteers.models import TeamMember, BloodDonor
from donations.models import Bank, QRCode, DonationMethod
from .models import SiteSetting, StatCounter, AboutImage


def home(request):
    from core.views_dashboard import ensure_default_stat_counters
    ensure_default_stat_counters()
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
    team_members = TeamMember.objects.all().order_by('order', 'id')
    context = {
        'site_setting': site_setting,
        'team_members': team_members,
    }
    return render(request, 'core/about.html', context)


import random
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from core.email_utils import send_system_email
from core.sms_utils import send_sms

def submit_complaint(request):
    """
    Handles citizen reports/complaints about injustice, irregularities, and corruption.
    CRITICAL REQUIREMENT: This data is NOT stored in the database or admin panel.
    Instead, a unique complaint tracking number is generated, an email with the details
    is sent to the organization admin, and an SMS confirmation is sent to the complainant's phone.
    """
    if request.method != 'POST':
        return redirect('core:home')

    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or 'application/json' in request.headers.get('Accept', '')
    )

    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()
    address = request.POST.get('address', '').strip()
    details = request.POST.get('details', '').strip()

    if not name or not phone or not details:
        error_msg = "অনুগ্রহ করে নাম, মোবাইল নম্বর এবং বিস্তারিত তথ্য পূরণ করুন।"
        if is_ajax:
            return JsonResponse({'success': False, 'message': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect('core:home')

    # Generate unique complaint tracking number (e.g. HNC-260913-7482)
    current_time = timezone.now()
    time_prefix = current_time.strftime('%y%m%d')
    rand_code = random.randint(1000, 9999)
    complaint_no = f"HNC-{time_prefix}-{rand_code}"

    # Prepare Admin Email recipient (admin@helplinehellonaogaon.com)
    admin_email = getattr(settings, 'SERVER_EMAIL', 'admin@helplinehellonaogaon.com') or 'admin@helplinehellonaogaon.com'
    recipients = [admin_email]

    # Formatted submission time string
    submission_time_str = current_time.strftime('%d-%m-%Y %I:%M %p')

    # Dispatch Email to Admin
    email_subject = f"[জরুরি অভিযোগ/তথ্য] অভিযোগ নং #{complaint_no} - হেল্পলাইন হ্যালো নওগাঁ"
    email_details = [
        {'label': 'অভিযোগ ট্র্যাকিং নং', 'value': complaint_no},
        {'label': 'তথ্য প্রদানকারীর নাম', 'value': name},
        {'label': 'মোবাইল নম্বর', 'value': phone},
        {'label': 'ঠিকানা', 'value': address if address else 'উল্লেখ করা হয়নি'},
        {'label': 'দাখিলের তারিখ ও সময়', 'value': submission_time_str},
        {'label': 'অভিযোগ / তথ্যের বিবরণ', 'value': details},
    ]

    try:
        send_system_email(
            subject=email_subject,
            recipient_list=recipients,
            headline="অন্যায়, অনিয়ম ও দুর্নীতির নতুন তথ্য প্রাপ্তি",
            greeting="শ্রদ্ধেয় অ্যাডমিন,",
            message_paragraphs=[
                f"ওয়েবসাইটে একজন নাগরিক নতুন একটি অভিযোগ/তথ্য দাখিল করেছেন। অভিযোগের ট্র্যাকিং আইডি: #{complaint_no}।",
                "তথ্যের সর্বোচ্চ নিরাপত্তা নিশ্চিত করতে এই তথ্যটি ডাটাবেজে সংরক্ষণ করা হয়নি, সরাসরি আপনার অফিসিয়াল ইমেইলে প্রেরণ করা হলো।"
            ],
            details=email_details,
            footer_note="সতর্কতা: অভিযোগকারীর পরিচয় ও তথ্যের পূর্ণ গোপনীয়তা বজায় রাখুন।",
            fail_silently=True,
            request=request,
        )
    except Exception:
        pass

    # Dispatch SMS to Complainant
    sms_text = f"Helpline Hello Naogaon: আপনার তথ্য/অভিযোগ সফলভাবে গৃহীত হয়েছে। অভিযোগ ট্র্যাকিং নং: {complaint_no}। তথ্যের গোপনীয়তা রক্ষা করা হবে। ধন্যবাদ।"
    try:
        send_sms(phone, sms_text)
    except Exception:
        pass

    success_msg = f"আপনার তথ্য/অভিযোগ সফলভাবে দাখিল করা হয়েছে! আপনার ট্র্যাকিং নম্বর: {complaint_no}। আপনার ফোনে নিশ্চিতকরণ বার্তা পাঠানো হয়েছে।"
    if is_ajax:
        return JsonResponse({
            'success': True,
            'complaint_no': complaint_no,
            'message': success_msg,
            'phone': phone,
        })

    messages.success(request, success_msg)
    return redirect('core:home')

