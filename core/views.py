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
    from django.db.models import Case, When, Value, IntegerField
    ensure_default_stat_counters()
    site_setting = SiteSetting.objects.first()
    stat_counters = StatCounter.objects.filter(is_active=True).order_by('order')
    
    about_featured_image = AboutImage.objects.filter(is_featured=True).first()
    about_grid_images = AboutImage.objects.filter(is_featured=False).order_by('order')[:4]

    # Programs: ongoing and all
    ongoing_programs = Program.objects.filter(status='ongoing').order_by('order', '-id')
    if not ongoing_programs.exists():
        ongoing_programs = Program.objects.all().order_by('order', '-id')
    all_programs = Program.objects.all().order_by('order', '-id')

    # Top Leadership & Council Members (Ordered strictly by hierarchy / krom onojai)
    from django.db.models import F
    role_priority = Case(
        When(role='সভাপতি', then=Value(1)),
        When(role__icontains='সহ-সভাপতি', then=Value(2)),
        When(role='সাধারণ সম্পাদক', then=Value(3)),
        When(role__icontains='যুগ্ম', then=Value(4)),
        When(role__icontains='সাংগঠনিক', then=Value(5)),
        When(role__in=['কোষাধ্যক্ষ', 'অর্থ সম্পাদক'], then=Value(6)),
        When(role='সাধারণ পরিষদ সদস্য', then=Value(7)),
        When(role__icontains='পরিষদ', then=Value(8)),
        When(role__icontains='দপ্তর', then=Value(9)),
        When(role__icontains='প্রচার', then=Value(10)),
        default=Value(20),
        output_field=IntegerField(),
    )
    effective_order = Case(
        When(order__gt=0, then=F('order')),
        default=Value(100) + F('role_priority'),
        output_field=IntegerField(),
    )
    leadership_members = TeamMember.objects.annotate(
        role_priority=role_priority,
        effective_order=effective_order
    ).order_by('effective_order', 'id')

    recent_news = Article.objects.filter(is_published=True).order_by('-publish_date')[:3]
    banks = Bank.objects.filter(is_active=True)
    qrcodes = QRCode.objects.filter(is_active=True)
    donation_methods = DonationMethod.objects.filter(is_active=True)
    bkash_method = DonationMethod.objects.filter(name__iexact='bKash', is_active=True).first()
    nagad_method = DonationMethod.objects.filter(name__iexact='Nagad', is_active=True).first()
    rocket_method = DonationMethod.objects.filter(name__iexact='Rocket', is_active=True).first()
    gallery_photos = Photo.objects.all().order_by('-id')[:6]

    context = {
        'site_setting': site_setting,
        'stat_counters': stat_counters,
        'about_featured_image': about_featured_image,
        'about_grid_images': about_grid_images,
        'ongoing_programs': ongoing_programs,
        'all_programs': all_programs,
        'leadership_members': leadership_members,
        'recent_news': recent_news,
        'banks': banks,
        'qrcodes': qrcodes,
        'donation_methods': donation_methods,
        'bkash_method': bkash_method,
        'nagad_method': nagad_method,
        'rocket_method': rocket_method,
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

def emergency_services(request):
    """
    Public National & District Emergency Directory View for Helpline Hello Naogaon.
    Features instant search, category filtering, click-to-call, and fast phone dialing.
    """
    from django.db.models import Prefetch
    from core.emergency_data import ensure_default_emergency_services
    from .models import EmergencyCategory, EmergencyService
    ensure_default_emergency_services()

    site_setting = SiteSetting.objects.first()
    categories = EmergencyCategory.objects.filter(is_active=True).prefetch_related(
        Prefetch('services', queryset=EmergencyService.objects.filter(is_active=True).order_by('order', 'id'))
    ).order_by('order', 'id')

    hotlines = EmergencyService.objects.filter(is_active=True, is_hotline=True).order_by('order', 'id')
    all_services = EmergencyService.objects.filter(is_active=True).select_related('category').order_by('category__order', 'order', 'id')

    context = {
        'site_setting': site_setting,
        'categories': categories,
        'hotlines': hotlines,
        'all_services': all_services,
    }
    return render(request, 'core/emergency_services.html', context)



import random
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from core.email_utils import send_system_email, get_admin_notification_emails
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
    subject_type = request.POST.get('subject_type', 'তথ্য ও সহায়তা আবেদন').strip() or 'তথ্য ও সহায়তা আবেদন'
    address = request.POST.get('address', '').strip()
    details = request.POST.get('details', '').strip()

    if not name or not phone or not details:
        error_msg = "অনুগ্রহ করে নাম, মোবাইল নম্বর এবং বিস্তারিত তথ্য পূরণ করুন।"
        if is_ajax:
            return JsonResponse({'success': False, 'message': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect('core:home')

    # Generate unique tracking number (e.g. HNC-260913-7482)
    current_time = timezone.now()
    time_prefix = current_time.strftime('%y%m%d')
    rand_code = random.randint(1000, 9999)
    complaint_no = f"HNC-{time_prefix}-{rand_code}"

    # Prepare Admin Email recipients
    recipients = get_admin_notification_emails()

    # Formatted submission time string
    submission_time_str = current_time.strftime('%d-%m-%Y %I:%M %p')

    # Dispatch Email to Admin (NO DB save - pure secure email dispatch)
    email_subject = f"[{subject_type}] ট্র্যাকিং নং #{complaint_no} - হেল্পলাইন হ্যালো নওগাঁ"
    email_details = [
        {'label': 'ট্র্যাকিং নং', 'value': complaint_no},
        {'label': 'তথ্যের ধরন / বিষয়', 'value': subject_type},
        {'label': 'প্রেরণকারীর নাম', 'value': name},
        {'label': 'মোবাইল নম্বর', 'value': phone},
        {'label': 'ঠিকানা', 'value': address if address else 'উল্লেখ করা হয়নি'},
        {'label': 'দাখিলের তারিখ ও সময়', 'value': submission_time_str},
        {'label': 'বিস্তারিত বিবরণ / আবেদন', 'value': details},
    ]

    try:
        send_system_email(
            subject=email_subject,
            recipient_list=recipients,
            headline=f"নতুন বার্তা: {subject_type}",
            greeting="শ্রদ্ধেয় অ্যাডমিন,",
            message_paragraphs=[
                f"ওয়েবসাইটে একজন নাগরিক একটি নতুন তথ্য/আবেদন দাখিল করেছেন। ট্র্যাকিং আইডি: #{complaint_no}।",
                "তথ্যের সর্বোচ্চ নিরাপত্তা নিশ্চিত করতে এই তথ্যটি ডাটাবেজে সংরক্ষণ করা হয়নি, সরাসরি আপনার অফিসিয়াল ইমেইলে প্রেরণ করা হলো।"
            ],
            details=email_details,
            footer_note="সতর্কতা: আবেদনকারী/তথ্য প্রদানকারীর পরিচয় ও তথ্যের পূর্ণ গোপনীয়তা বজায় রাখুন।",
            fail_silently=True,
            request=request,
        )
    except Exception:
        pass

    # Dispatch SMS to Complainant
    sms_text = f"[Helpline Hello Naogaon] আপনার তথ্য/আবেদন সফলভাবে গৃহীত হয়েছে। ট্র্যাকিং নং: {complaint_no}। তথ্যের গোপনীয়তা রক্ষা করা হবে। প্রয়োজনে: 01916314315"
    try:
        send_sms(phone, sms_text)
    except Exception:
        pass

    # Dispatch Notification SMS to Admin SIM
    admin_phone = getattr(settings, 'SMS_ADMIN_ALERT_PHONE', '01916314315')
    if admin_phone:
        try:
            admin_sms = f"[Helpline Hello Naogaon] নতুন নাগরিক বার্তা! বিষয়: {subject_type}। ট্র্যাকিং: {complaint_no}। প্রেরক: {phone}। ইমেইল চেক করুন।"
            send_sms(admin_phone, admin_sms, is_alert=True)
        except Exception:
            pass

    success_msg = f"আপনার তথ্য/আবেদন সফলভাবে দাখিল করা হয়েছে! আপনার ট্র্যাকিং নম্বর: {complaint_no}। আপনার ফোনে নিশ্চিতকরণ বার্তা পাঠানো হয়েছে।"
    if is_ajax:
        return JsonResponse({
            'success': True,
            'complaint_no': complaint_no,
            'message': success_msg,
            'phone': phone,
        })

    messages.success(request, success_msg)
    return redirect('core:home')


def terms_view(request):
    """Terms & Conditions compliance page"""
    site_setting = SiteSetting.objects.first()
    return render(request, 'core/terms.html', {'site_setting': site_setting})


def privacy_policy_view(request):
    """Privacy Policy compliance page"""
    site_setting = SiteSetting.objects.first()
    return render(request, 'core/privacy_policy.html', {'site_setting': site_setting})


def refund_policy_view(request):
    """Return & Refund Policy compliance page"""
    site_setting = SiteSetting.objects.first()
    return render(request, 'core/refund_policy.html', {'site_setting': site_setting})


def delivery_policy_view(request):
    """Delivery & Service Fulfillment Policy compliance page"""
    site_setting = SiteSetting.objects.first()
    return render(request, 'core/delivery_policy.html', {'site_setting': site_setting})

