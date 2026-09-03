from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from core.email_utils import send_system_email
from core.models import SiteSetting, StatCounter, AboutImage
from programs.models import Program, Event, SuccessStory
from news.models import Article, Category
from volunteers.models import BloodDonor, Volunteer, TeamMember
from gallery.models import Photo, Album
from donations.models import (
    Bank, QRCode, DonationMethod, FinancialTransaction,
    DonationPageContent, Campaign, ProgramDonation, EmergencyAppeal, DonationImpact, FAQ
)
from django.db.models import Q, Sum

User = get_user_model()

def get_user_dashboard_role(user):
    """
    Returns a comprehensive dictionary of role properties and permissions.
    """
    if not user or not user.is_authenticated:
        return {
            'role_name': 'ভিজিটর',
            'role_type': 'visitor',
            'can_manage_cms': False,
            'can_manage_team': False,
            'can_manage_volunteers': False,
            'can_edit_finance': False,
            'is_leader': False,
            'team_member': None,
            'badge_color': 'secondary',
            'icon': 'fas fa-user',
            'welcome_title': 'স্বাগতম',
        }

    if user.is_superuser or (user.is_staff and not getattr(user, 'team_profile', None)):
        return {
            'role_name': 'প্রধান অ্যাডমিন (Super Admin)' if user.is_superuser else 'অ্যাডমিন (Admin)',
            'role_type': 'superuser' if user.is_superuser else 'staff_admin',
            'can_manage_cms': True,
            'can_manage_team': True,
            'can_manage_volunteers': True,
            'can_edit_finance': True,
            'is_leader': False,
            'team_member': getattr(user, 'team_profile', None),
            'badge_color': 'danger',
            'icon': 'fas fa-user-shield',
            'welcome_title': 'প্রধান অ্যাডমিন কন্ট্রোল প্যানেল' if user.is_superuser else 'অ্যাডমিন কন্ট্রোল প্যানেল',
        }

    tm = getattr(user, 'team_profile', None)
    if tm:
        role = tm.role
        eff_role = tm.effective_role or role
        if role == 'সভাপতি':
            return {
                'role_name': f'সভাপতি ({tm.name})',
                'role_type': 'president',
                'can_manage_cms': False,
                'can_manage_team': False,
                'can_manage_volunteers': False,
                'can_edit_finance': False,
                'is_leader': True,
                'team_member': tm,
                'badge_color': 'warning',
                'icon': 'fas fa-crown',
                'welcome_title': f'সম্মানিত সভাপতি, {tm.name}',
            }
        elif role == 'সাধারণ সম্পাদক':
            return {
                'role_name': f'সাধারণ সম্পাদক ({tm.name})',
                'role_type': 'secretary',
                'can_manage_cms': False,
                'can_manage_team': False,
                'can_manage_volunteers': False,
                'can_edit_finance': False,
                'is_leader': True,
                'team_member': tm,
                'badge_color': 'primary',
                'icon': 'fas fa-feather-alt',
                'welcome_title': f'সম্মানিত সাধারণ সম্পাদক, {tm.name}',
            }
        elif role == 'কোষাধ্যক্ষ':
            return {
                'role_name': f'কোষাধ্যক্ষ ({tm.name})',
                'role_type': 'treasurer',
                'can_manage_cms': False,
                'can_manage_team': False,
                'can_manage_volunteers': False,
                'can_edit_finance': True,
                'is_leader': True,
                'team_member': tm,
                'badge_color': 'success',
                'icon': 'fas fa-wallet',
                'welcome_title': f'সম্মানিত কোষাধ্যক্ষ, {tm.name}',
            }
        elif role == 'সাধারণ পরিষদ সদস্য':
            return {
                'role_name': f'সাধারণ পরিষদ সদস্য ({tm.name})',
                'role_type': 'council',
                'can_manage_cms': False,
                'can_manage_team': False,
                'can_manage_volunteers': False,
                'can_edit_finance': False,
                'is_leader': True,
                'team_member': tm,
                'badge_color': 'info',
                'icon': 'fas fa-users',
                'welcome_title': f'সম্মানিত পরিষদ সদস্য, {tm.name}',
            }
        else:
            return {
                'role_name': f'{eff_role} ({tm.name})',
                'role_type': 'other_leader',
                'can_manage_cms': False,
                'can_manage_team': False,
                'can_manage_volunteers': False,
                'can_edit_finance': False,
                'is_leader': True,
                'team_member': tm,
                'badge_color': 'secondary',
                'icon': 'fas fa-user-tie',
                'welcome_title': f'সম্মানিত টিম মেম্বার, {tm.name}',
            }

    return {
        'role_name': user.get_full_name() or user.username or 'স্টাফ ইউজার',
        'role_type': 'staff',
        'can_manage_cms': False,
        'can_manage_team': False,
        'can_manage_volunteers': False,
        'can_edit_finance': False,
        'is_leader': False,
        'team_member': None,
        'badge_color': 'secondary',
        'icon': 'fas fa-user-tag',
        'welcome_title': f'স্বাগতম, {user.get_full_name() or user.username}',
    }

def can_user_edit_finance(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    tm = getattr(user, 'team_profile', None)
    if tm and tm.role in ['কোষাধ্যক্ষ', 'সভাপতি', 'সাধারণ সম্পাদক']:
        return True
    return False

def can_user_edit_general(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return False

def validate_image_size(request, image_file, max_kb=1024, field_name="ছবি"):
    """
    Validates uploaded image file size dynamically within 100KB to 1MB range.
    """
    if image_file and image_file.size > max_kb * 1024:
        size_kb = image_file.size / 1024
        limit_str = f"{max_kb / 1024:.0f} MB" if max_kb >= 1024 else f"{max_kb} KB"
        size_str = f"{size_kb / 1024:.2f} MB" if size_kb >= 1024 else f"{size_kb:.1f} KB"
        messages.error(
            request,
            f'{field_name}-র সাইজ সর্বোচ্চ {limit_str} হতে পারবে (আপনার ফাইলের সাইজ: {size_str})। '
            f'অনুগ্রহ করে resizepixel.com থেকে ছবির সাইজ কিছুটা কমিয়ে পুনরায় আপলোড করুন।'
        )
        return False
    return True

@staff_member_required
def dashboard_home(request):
    """
    Main Custom Front-End Control Panel with Role-Based Separation:
    - Superuser: Full CMS, Teams, Volunteers, News, Gallery, Finance & Bank management.
    - President / Secretary / Council: Customized animated welcome, view-only for Team Members, Volunteers/Donors, Finance, and personal donation tab.
    - Treasurer: Full Finance & Accounting control, view-only for Team & Volunteers, and personal donation tab.
    """
    site_setting, _ = SiteSetting.objects.get_or_create(pk=1)
    stat_counters = StatCounter.objects.all().order_by('order')
    about_featured_image = AboutImage.objects.filter(is_featured=True).first()
    about_grid_images = AboutImage.objects.filter(is_featured=False).order_by('order')
    
    programs = Program.objects.all().order_by('order', '-id')
    articles = Article.objects.all().order_by('-publish_date')
    donors = BloodDonor.objects.all().order_by('-id')
    volunteers = Volunteer.objects.all().order_by('-id')
    team_members = TeamMember.objects.all().order_by('order')
    photos = Photo.objects.all().order_by('-id')
    banks = Bank.objects.all()
    qrcodes = QRCode.objects.all()

    # Donation Page Models
    donation_content, _ = DonationPageContent.objects.get_or_create(pk=1)
    campaigns = Campaign.objects.all().order_by('-id')
    emergency_appeals = EmergencyAppeal.objects.all().order_by('-created_at')
    impacts = DonationImpact.objects.all().order_by('amount')
    faqs = FAQ.objects.all()

    # Financial Management Calculations & Date Range Filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    transactions = FinancialTransaction.objects.all().order_by('-date', '-id')
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    net_balance = total_income - total_expense

    # Role and access permissions
    user_role_info = get_user_dashboard_role(request.user)
    user_role_name = user_role_info['role_name']
    can_edit_all = user_role_info['can_manage_cms']
    can_edit_finance = user_role_info['can_edit_finance']

    # Leadership Role Quotas
    president_count = TeamMember.objects.filter(role='সভাপতি').count()
    secretary_count = TeamMember.objects.filter(role='সাধারণ সম্পাদক').count()
    treasurer_count = TeamMember.objects.filter(role='কোষাধ্যক্ষ').count()
    council_count = TeamMember.objects.filter(role='সাধারণ পরিষদ সদস্য').count()

    # Personal Donation history for logged-in Team Member
    my_tm = user_role_info.get('team_member')
    my_donations = []
    my_total_donated = 0
    my_donation_count = 0
    if my_tm:
        q_filter = Q()
        if my_tm.member_id:
            q_filter |= Q(membership_id=my_tm.member_id)
        if my_tm.email:
            q_filter |= Q(donor_email__iexact=my_tm.email)
        if my_tm.phone:
            q_filter |= Q(donor_phone__iexact=my_tm.phone)
        if q_filter:
            my_donations = ProgramDonation.objects.filter(q_filter).order_by('-created_at')
            my_total_donated = my_donations.filter(status='approved').aggregate(Sum('amount'))['amount__sum'] or 0
            my_donation_count = my_donations.filter(status='approved').count()

    context = {
        'site_setting': site_setting,
        'stat_counters': stat_counters,
        'about_featured_image': about_featured_image,
        'about_grid_images': about_grid_images,
        'programs': programs,
        'articles': articles,
        'donors': donors,
        'volunteers': volunteers,
        'team_members': team_members,
        'photos': photos,
        'banks': banks,
        'qrcodes': qrcodes,
        'donation_content': donation_content,
        'campaigns': campaigns,
        'emergency_appeals': emergency_appeals,
        'impacts': impacts,
        'faqs': faqs,
        'transactions': transactions,
        'program_donations': ProgramDonation.objects.all().order_by('-created_at'),
        'total_program_donations': ProgramDonation.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'user_role_info': user_role_info,
        'user_role_name': user_role_name,
        'can_edit_all': can_edit_all,
        'can_edit_finance': can_edit_finance,
        'team_role_choices': TeamMember.ROLE_CHOICES,
        'president_count': president_count,
        'secretary_count': secretary_count,
        'treasurer_count': treasurer_count,
        'council_count': council_count,
        'my_tm': my_tm,
        'my_donations': my_donations,
        'my_total_donated': my_total_donated,
        'my_donation_count': my_donation_count,
    }
    return render(request, 'dashboard/index.html', context)

@staff_member_required
def update_hero_section(request):
    """Update Site Title, Taglines, Contact Info & Hero/Logo Images"""
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    if request.method == 'POST':
        setting, _ = SiteSetting.objects.get_or_create(pk=1)
        setting.hero_badge = request.POST.get('hero_badge', setting.hero_badge)
        setting.hero_title = request.POST.get('hero_title', setting.hero_title)
        setting.hero_subtitle = request.POST.get('hero_subtitle', setting.hero_subtitle)
        setting.title = request.POST.get('title', setting.title)
        setting.tagline = request.POST.get('tagline', setting.tagline)
        setting.contact_phone = request.POST.get('contact_phone', setting.contact_phone)
        setting.contact_email = request.POST.get('contact_email', setting.contact_email)
        setting.facebook_url = request.POST.get('facebook_url', setting.facebook_url)
        setting.youtube_url = request.POST.get('youtube_url', setting.youtube_url)
        setting.whatsapp_number = request.POST.get('whatsapp_number', setting.whatsapp_number)

        if 'logo' in request.FILES:
            if not validate_image_size(request, request.FILES['logo'], max_kb=300, field_name='লোগো ছবি'):
                return redirect('/dashboard/?tab=home-section')
            setting.logo = request.FILES['logo']

        if 'hero_image' in request.FILES:
            if not validate_image_size(request, request.FILES['hero_image'], max_kb=1024, field_name='হিরো ব্যানার ছবি'):
                return redirect('/dashboard/?tab=home-section')
            setting.hero_image = request.FILES['hero_image']

        setting.save()
        messages.success(request, 'হেডার, হিরো ও যোগাযোগের তথ্য সফলভাবে আপডেট হয়েছে!')
    return redirect('/dashboard/?tab=home-section')

@staff_member_required
def update_about_section(request):
    """Update About Us Text & Upload Featured/Grid Images"""
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    if request.method == 'POST':
        setting, _ = SiteSetting.objects.get_or_create(pk=1)
        setting.about_heading = request.POST.get('about_heading', setting.about_heading)
        setting.about_text = request.POST.get('about_text', setting.about_text)
        setting.save()

        # Handle Featured Main Image (1MB max)
        if 'featured_image' in request.FILES:
            if not validate_image_size(request, request.FILES['featured_image'], max_kb=1024, field_name='ফিচারড ছবি'):
                return redirect('/dashboard/?tab=home-section')
            AboutImage.objects.filter(is_featured=True).delete()
            AboutImage.objects.create(image=request.FILES['featured_image'], is_featured=True)

        # Handle Grid Image Upload (600KB max)
        if 'grid_image' in request.FILES:
            if not validate_image_size(request, request.FILES['grid_image'], max_kb=600, field_name='গ্রিড ছবি'):
                return redirect('/dashboard/?tab=home-section')
            AboutImage.objects.create(image=request.FILES['grid_image'], is_featured=False)

        messages.success(request, 'আমাদের সম্পর্কে সেকশনের তথ্য আপডেট হয়েছে!')
    return redirect('/dashboard/?tab=home-section')

@staff_member_required
def delete_about_image(request, pk):
    """Delete an About section grid image safely"""
    img = AboutImage.objects.filter(pk=pk).first()
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    if img:
        img.delete()
        messages.success(request, 'ছবিটি সফলভাবে মুছে ফেলা হয়েছে!')
    else:
        messages.warning(request, 'ছবিটি ইতিমধ্যে মুছে ফেলা হয়েছে বা খুঁজে পাওয়া যায়নি।')
    return redirect('/dashboard/?tab=home-section')

@staff_member_required
def save_stat_counter(request):
    """Create or update a single StatCounter via Pop-up Modal (fixed system icons & theme colors)"""
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    if request.method == 'POST':
        stat_id = request.POST.get('stat_id')
        title = request.POST.get('title', '').strip()
        value = request.POST.get('value', '').strip()

        # System design matching maps for icons & colors
        SYSTEM_SLOTS = {
            1: ('fas fa-tint', 'danger'),           # রক্তদান
            2: ('fas fa-users', 'success'),         # পরিবারকে সহায়তা
            3: ('fas fa-graduation-cap', 'warning'), # শিক্ষার্থী সহায়তা
            4: ('fas fa-hands-helping', 'primary'), # স্বেচ্ছাসেবক
            5: ('fas fa-seedling', 'info'),         # গাছ রোপণ
        }

        if stat_id:
            stat = StatCounter.objects.filter(pk=stat_id).first()
            if stat:
                stat.title = title
                stat.value = value
                default_icon, default_color = SYSTEM_SLOTS.get(stat.order, ('fas fa-heart', 'success'))
                stat.icon_class = stat.icon_class or default_icon
                stat.badge_color = stat.badge_color or default_color
                stat.save()
                messages.success(request, f'"{stat.title}" কাউন্টার কার্ডের মান ({stat.value}) সফলভাবে আপডেট করা হয়েছে!')
            else:
                messages.warning(request, 'কাউন্টার কার্ডটি খুঁজে পাওয়া যায়নি।')
        else:
            current_count = StatCounter.objects.count()
            order = current_count + 1
            default_icon, default_color = SYSTEM_SLOTS.get(order, ('fas fa-heart', 'success'))
            StatCounter.objects.create(
                title=title,
                value=value,
                icon_class=default_icon,
                badge_color=default_color,
                order=order,
                is_active=True
            )
            messages.success(request, f'নতুন কাউন্টার কার্ড "{title}" সফলভাবে তৈরি হয়েছে!')
    return redirect('/dashboard/?tab=home-section')

@staff_member_required
def delete_stat_counter(request, pk):
    """Delete a StatCounter safely"""
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    stat = StatCounter.objects.filter(pk=pk).first()
    if stat:
        title = stat.title
        stat.delete()
        messages.success(request, f'"{title}" কাউন্টার কার্ড সফলভাবে মুছে ফেলা হয়েছে!')
    else:
        messages.warning(request, 'কাউন্টার কার্ডটি ইতিমধ্যে মুছে ফেলা হয়েছে বা খুঁজে পাওয়া যায়নি।')
    return redirect('/dashboard/?tab=home-section')

@staff_member_required
def update_stat_counters(request):
    """Legacy wrapper redirecting to save_stat_counter"""
    return save_stat_counter(request)

def get_auto_program_theme(title):
    t = (title or "").lower()
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    if any(k in t for k in ["রক্ত", "চিকিৎসা", "মেডিকেল", "স্বাস্থ্য", "ব্লাড", "blood", "medical", "hospital", "রোগী", "অসুস্থ"]):
        return "fas fa-tint", "danger"
    elif any(k in t for k in ["শিক্ষা", "স্কুল", "বই", "খাতা", "মেধাবী", "student", "education", "school", "কলম", "বৃত্তি", "পাঠাগার"]):
        return "fas fa-graduation-cap", "warning"
    elif any(k in t for k in ["গাছ", "বৃক্ষ", "পরিবেশ", "সবুজ", "plant", "tree", "environment", "রোপণ", "বন"]):
        return "fas fa-seedling", "info"
    elif any(k in t for k in ["খাদ্য", "ত্রাণ", "বন্যা", "শীতবস্ত্র", "সাহায্য", "পুনর্বাসন", "ঈদ", "উপহার", "food", "relief", "কম্বল", "বস্ত্র"]):
        return "fas fa-hands-helping", "success"
    elif any(k in t for k in ["স্বেচ্ছাসেবক", "যুব", "কমিউনিটি", "টিম", "volunteer", "youth", "সংগঠন"]):
        return "fas fa-users", "primary"
    return "fas fa-hands-helping", "success"

def get_auto_impact_icon(description):
    d = (description or "").lower()
    if any(k in d for k in ["রক্ত", "চিকিৎসা", "মেডিকেল", "ঔষধ", "স্বাস্থ্য", "ব্লাড"]):
        return "fas fa-heartbeat"
    elif any(k in d for k in ["শিক্ষা", "বই", "খাতা", "শিক্ষার্থী", "স্কুল", "টিউশন", "কলম"]):
        return "fas fa-book-open"
    elif any(k in d for k in ["খাদ্য", "খাবার", "প্যাকেট", "মিল", "ত্রাণ", "রেশন"]):
        return "fas fa-utensils"
    elif any(k in d for k in ["গাছ", "বৃক্ষ", "চারা", "পরিবেশ"]):
        return "fas fa-seedling"
    elif any(k in d for k in ["পরিবার", "ঘর", "পুনর্বাসন", "বাসস্থান"]):
        return "fas fa-home"
    return "fas fa-heart"

@staff_member_required
def save_program(request):
    """Create or update a Program with automatic icon and badge color"""
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    if request.method == 'POST':
        prog_id = request.POST.get('program_id')
        title = request.POST.get('title')
        short_description = request.POST.get('short_description', '')
        description = request.POST.get('description', '')
        status = request.POST.get('status', 'ongoing')
        auto_icon, auto_badge = get_auto_program_theme(title)
        badge_color = request.POST.get('badge_color') or auto_badge
        icon_class = request.POST.get('icon_class') or auto_icon

        target_amount_str = request.POST.get('target_amount', '').strip()
        target_amount = None
        if target_amount_str:
            try:
                target_amount = float(target_amount_str)
                if target_amount <= 0:
                    target_amount = None
            except (ValueError, TypeError):
                target_amount = None

        image_file = request.FILES.get('image')
        if image_file and not validate_image_size(request, image_file, max_kb=800, field_name='কার্যক্রমের ছবি'):
            return redirect('/dashboard/?tab=programs-section')

        if prog_id:
            prog = Program.objects.filter(pk=prog_id).first()
            if prog:
                prog.title = title
                prog.short_description = short_description
                prog.description = description
                prog.status = status
                prog.icon_class = icon_class
                prog.badge_color = badge_color
                prog.target_amount = target_amount
                if image_file:
                    prog.image = image_file
                prog.save()
                messages.success(request, f'কার্যক্রম "{title}" আপডেট হয়েছে!')
            else:
                messages.warning(request, 'কার্যক্রমটি খুঁজে পাওয়া যায়নি।')
        else:
            prog = Program.objects.create(
                title=title,
                short_description=short_description,
                description=description,
                status=status,
                icon_class=icon_class,
                badge_color=badge_color,
                target_amount=target_amount,
                image=image_file
            )
            messages.success(request, f'নতুন কার্যক্রম "{title}" যোগ করা হয়েছে!')
    return redirect('/dashboard/?tab=programs-section')

@staff_member_required
def delete_program(request, pk):
    """Delete a Program safely without 404"""
    prog = Program.objects.filter(pk=pk).first()
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    if not prog:
        messages.warning(request, 'কার্যক্রমটি ইতিমধ্যে মুছে ফেলা হয়েছে বা খুঁজে পাওয়া যায়নি।')
        return redirect('/dashboard/?tab=programs-section')

    title = prog.title
    try:
        # Safely detach any foreign key references before deleting
        ProgramDonation.objects.filter(program=prog).update(program=None)
        FinancialTransaction.objects.filter(program=prog).update(program=None)
        prog.delete()
        messages.success(request, f'কার্যক্রম "{title}" সফলভাবে মুছে ফেলা হয়েছে!')
    except Exception as e:
        messages.error(request, f'কার্যক্রম মুছে ফেলতে সমস্যা হয়েছে: {e}')
    return redirect('/dashboard/?tab=programs-section')

@staff_member_required
def save_news(request):
    """Create or update a News Article safely"""
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    if request.method == 'POST':
        art_id = request.POST.get('article_id')
        title = request.POST.get('title')
        content = request.POST.get('content', '')
        category_name = request.POST.get('category', 'সাধারণ')

        image_file = request.FILES.get('image')
        if image_file and not validate_image_size(request, image_file, max_kb=1024, field_name='সংবাদের কভার ছবি'):
            return redirect('/dashboard/?tab=news-section')

        category, _ = Category.objects.get_or_create(name=category_name)

        if art_id:
            art = Article.objects.filter(pk=art_id).first()
            if art:
                art.title = title
                art.content = content
                art.category = category
                if image_file:
                    art.image = image_file
                art.save()
                messages.success(request, f'সংবাদ "{title}" আপডেট হয়েছে!')
            else:
                messages.warning(request, 'সংবাদটি খুঁজে পাওয়া যায়নি।')
        else:
            Article.objects.create(
                title=title,
                content=content,
                category=category,
                image=image_file,
                is_published=True
            )
            messages.success(request, f'নতুন সংবাদ "{title}" প্রকাশ করা হয়েছে!')
    return redirect('/dashboard/?tab=news-section')

@staff_member_required
def delete_news(request, pk):
    """Delete a News Article safely"""
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    art = Article.objects.filter(pk=pk).first()
    if art:
        title = art.title
        art.delete()
        messages.success(request, f'সংবাদ "{title}" মুছে ফেলা হয়েছে!')
    else:
        messages.warning(request, 'সংবাদটি ইতিমধ্যে মুছে ফেলা হয়েছে বা খুঁজে পাওয়া যায়নি।')
    return redirect('/dashboard/?tab=news-section')

@staff_member_required
def update_bank_and_donation(request):
    """Update Bank Account details & bKash QR code image"""
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    if request.method == 'POST':
        b_id = request.POST.get('bank_id')
        bank_name = request.POST.get('bank_name')
        account_name = request.POST.get('account_name')
        account_number = request.POST.get('account_number')
        branch = request.POST.get('branch', '')
        swift_code = request.POST.get('swift_code', '')

        if bank_name and account_number:
            if b_id:
                bank = Bank.objects.filter(pk=b_id).first()
                if bank:
                    bank.bank_name = bank_name
                    bank.account_name = account_name
                    bank.account_number = account_number
                    bank.branch = branch
                    bank.swift_code = swift_code
                    bank.save()
            else:
                Bank.objects.create(
                    bank_name=bank_name,
                    account_name=account_name,
                    account_number=account_number,
                    branch=branch,
                    swift_code=swift_code
                )

        if 'qr_image' in request.FILES:
            qr_file = request.FILES['qr_image']
            if not validate_image_size(request, qr_file, max_kb=300, field_name='QR কোড ছবি'):
                return redirect('/dashboard/?tab=bank-section')

            bkash_method, _ = DonationMethod.objects.get_or_create(name='bKash')
            qr = QRCode.objects.filter(method=bkash_method).first()
            if qr:
                qr.image = qr_file
                qr.save()
            else:
                QRCode.objects.create(method=bkash_method, image=qr_file)

        messages.success(request, 'ব্যাংক হিসাব ও পেমেন্ট তথ্য সফলভাবে সেভ করা হয়েছে!')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def update_donation_page_content(request):
    """Update Donation Page texts and Hero Image"""
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    if request.method == 'POST':
        content, _ = DonationPageContent.objects.get_or_create(pk=1)
        content.hero_title = request.POST.get('hero_title', content.hero_title)
        content.hero_subtitle = request.POST.get('hero_subtitle', content.hero_subtitle)
        content.why_donate_title = request.POST.get('why_donate_title', content.why_donate_title)
        content.why_donate_text = request.POST.get('why_donate_text', content.why_donate_text)
        content.transparency_title = request.POST.get('transparency_title', content.transparency_title)
        content.transparency_text = request.POST.get('transparency_text', content.transparency_text)

        if 'hero_image' in request.FILES:
            if not validate_image_size(request, request.FILES['hero_image'], max_kb=1024, field_name='দানের পেজ ব্যানার ছবি'):
                return redirect('/dashboard/?tab=bank-section')
            content.hero_image = request.FILES['hero_image']

        content.save()
        messages.success(request, 'দানের পেজের তথ্য সফলভাবে আপডেট করা হয়েছে!')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def save_campaign(request):
    """Create or update a Campaign"""
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    if request.method == 'POST':
        c_id = request.POST.get('campaign_id')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        goal_amount = request.POST.get('goal_amount', 0)
        raised_amount = request.POST.get('raised_amount', 0)
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        image_file = request.FILES.get('image')
        if image_file and not validate_image_size(request, image_file, max_kb=800, field_name='ক্যাম্পেইন কভার ছবি'):
            return redirect('/dashboard/?tab=bank-section')

        if c_id:
            camp = Campaign.objects.filter(pk=c_id).first()
            if camp:
                camp.title = title
                camp.description = description
                camp.goal_amount = goal_amount
                camp.raised_amount = raised_amount
                if start_date:
                    camp.start_date = start_date
                if end_date:
                    camp.end_date = end_date
                if image_file:
                    camp.image = image_file
                camp.save()
                messages.success(request, f'ক্যাম্পেইন "{title}" আপডেট করা হয়েছে!')
            else:
                messages.warning(request, 'ক্যাম্পেইনটি খুঁজে পাওয়া যায়নি।')
        else:
            camp = Campaign.objects.create(
                title=title,
                description=description,
                goal_amount=goal_amount,
                raised_amount=raised_amount,
                start_date=start_date or date.today(),
                end_date=end_date or None,
                image=image_file
            )
            messages.success(request, f'নতুন ক্যাম্পেইন "{title}" তৈরি করা হয়েছে!')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def delete_campaign(request, pk):
    """Delete a Campaign safely"""
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    camp = Campaign.objects.filter(pk=pk).first()
    if camp:
        title = camp.title
        camp.delete()
        messages.success(request, f'ক্যাম্পেইন "{title}" মুছে ফেলা হয়েছে!')
    else:
        messages.warning(request, 'ক্যাম্পেইনটি ইতিমধ্যে মুছে ফেলা হয়েছে বা খুঁজে পাওয়া যায়নি।')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def save_emergency_appeal(request):
    """Create or update an Emergency Appeal safely"""
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    if request.method == 'POST':
        appeal_id = request.POST.get('appeal_id')
        title = request.POST.get('title')
        description = request.POST.get('description', '')

        image_file = request.FILES.get('image')
        if image_file and not validate_image_size(request, image_file, max_kb=800, field_name='জরুরি আপিল ছবি'):
            return redirect('/dashboard/?tab=bank-section')

        if appeal_id:
            app = EmergencyAppeal.objects.filter(pk=appeal_id).first()
            if app:
                app.title = title
                app.description = description
                if image_file:
                    app.image = image_file
                app.save()
                messages.success(request, f'জরুরি আবেদন "{title}" আপডেট করা হয়েছে!')
            else:
                messages.warning(request, 'আবেদনটি খুঁজে পাওয়া যায়নি।')
        else:
            EmergencyAppeal.objects.create(
                title=title,
                description=description,
                image=image_file
            )
            messages.success(request, f'নতুন জরুরি আবেদন "{title}" তৈরি করা হয়েছে!')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def delete_emergency_appeal(request, pk):
    """Delete an Emergency Appeal safely"""
    app = EmergencyAppeal.objects.filter(pk=pk).first()
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    if app:
        title = app.title
        app.delete()
        messages.success(request, f'জরুরি আবেদন "{title}" মুছে ফেলা হয়েছে!')
    else:
        messages.warning(request, 'আবেদনটি ইতিমধ্যে মুছে ফেলা হয়েছে বা খুঁজে পাওয়া যায়নি।')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def save_donation_impact(request):
    """Create or update a Donation Impact item with automatic icon selection safely"""
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    if request.method == 'POST':
        imp_id = request.POST.get('impact_id')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        auto_icon = get_auto_impact_icon(description)
        icon_class = request.POST.get('icon_class') or auto_icon

        if imp_id:
            imp = DonationImpact.objects.filter(pk=imp_id).first()
            if imp:
                imp.amount = amount
                imp.description = description
                imp.icon_class = icon_class
                imp.save()
                messages.success(request, f'দান প্রভাব (৳{amount}) আপডেট করা হয়েছে!')
            else:
                messages.warning(request, 'আইটেমটি খুঁজে পাওয়া যায়নি।')
        else:
            DonationImpact.objects.create(
                amount=amount,
                description=description,
                icon_class=icon_class
            )
            messages.success(request, f'নতুন দান প্রভাব (৳{amount}) তৈরি করা হয়েছে!')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def delete_donation_impact(request, pk):
    """Delete a Donation Impact item safely"""
    imp = DonationImpact.objects.filter(pk=pk).first()
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    if imp:
        imp.delete()
        messages.success(request, 'দান প্রভাব উপাদান মুছে ফেলা হয়েছে!')
    else:
        messages.warning(request, 'আইটেমটি ইতিমধ্যে মুছে ফেলা হয়েছে বা খুঁজে পাওয়া যায়নি।')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def save_faq(request):
    """Create or update a Donation FAQ safely"""
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    if request.method == 'POST':
        faq_id = request.POST.get('faq_id')
        question = request.POST.get('question')
        answer = request.POST.get('answer')

        if faq_id:
            faq = FAQ.objects.filter(pk=faq_id).first()
            if faq:
                faq.question = question
                faq.answer = answer
                faq.save()
                messages.success(request, 'জিজ্ঞাসাবাদ (FAQ) আপডেট করা হয়েছে!')
            else:
                messages.warning(request, 'FAQ টি খুঁজে পাওয়া যায়নি।')
        else:
            FAQ.objects.create(
                question=question,
                answer=answer
            )
            messages.success(request, 'নতুন জিজ্ঞাসাবাদ (FAQ) তৈরি করা হয়েছে!')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def delete_faq(request, pk):
    """Delete a Donation FAQ safely"""
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    faq = FAQ.objects.filter(pk=pk).first()
    if faq:
        faq.delete()
        messages.success(request, 'জিজ্ঞাসাবাদ (FAQ) মুছে ফেলা হয়েছে!')
    else:
        messages.warning(request, 'FAQ টি ইতিমধ্যে মুছে ফেলা হয়েছে বা খুঁজে পাওয়া যায়নি।')
    return redirect('/dashboard/?tab=bank-section')


@staff_member_required
def save_donor(request):
    """Create or update a Blood Donor safely"""
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    if request.method == 'POST':
        donor_id = request.POST.get('donor_id')
        name = request.POST.get('full_name')
        group = request.POST.get('blood_group')
        phone = request.POST.get('phone')
        location = request.POST.get('location')
        last_donated_str = request.POST.get('last_donated', '').strip()
        member_id = request.POST.get('member_id', '').strip()
        is_available = request.POST.get('is_available') == 'on'
        is_public_details = request.POST.get('is_public_details') != 'off'

        last_donated_val = None
        if last_donated_str:
            try:
                from datetime import datetime
                last_donated_val = datetime.strptime(last_donated_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        division = request.POST.get('division', 'রাজশাহী').strip()
        district = request.POST.get('district', 'নওগাঁ').strip()
        upazila = request.POST.get('upazila', '').strip()

        if donor_id:
            donor = BloodDonor.objects.filter(pk=donor_id).first()
            if donor:
                donor.full_name = name
                donor.blood_group = group
                donor.phone = phone
                donor.division = division or 'রাজশাহী'
                donor.district = district or 'নওগাঁ'
                donor.upazila = upazila
                donor.location = location
                donor.last_donated = last_donated_val
                donor.member_id = member_id if member_id else None
                donor.is_available = is_available
                donor.is_public_details = is_public_details
                donor.save()
                messages.success(request, f'রক্তদাতা "{name}" তথ্য আপডেট করা হয়েছে!')
            else:
                messages.warning(request, 'রক্তদাতার তথ্য খুঁজে পাওয়া যায়নি।')
        else:
            BloodDonor.objects.create(
                full_name=name,
                blood_group=group,
                phone=phone,
                division=division or 'রাজশাহী',
                district=district or 'নওগাঁ',
                upazila=upazila,
                location=location,
                last_donated=last_donated_val,
                member_id=member_id if member_id else None,
                is_available=is_available,
                is_public_details=is_public_details
            )
            messages.success(request, f'নতুন রক্তদাতা "{name}" তালিকাভুক্ত করা হয়েছে!')
    return redirect('/dashboard/?tab=donors-section')

@staff_member_required
def delete_donor(request, pk):
    """Delete a Blood Donor safely"""
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    donor = BloodDonor.objects.filter(pk=pk).first()
    if donor:
        name = donor.full_name
        donor.delete()
        messages.success(request, f'রক্তদাতা "{name}" মুছে ফেলা হয়েছে!')
    else:
        messages.warning(request, 'রক্তদাতার তথ্য ইতিমধ্যে মুছে ফেলা হয়েছে বা খুঁজে পাওয়া যায়নি।')
    return redirect('/dashboard/?tab=donors-section')

@staff_member_required
def save_volunteer(request):
    """Create or update a Volunteer safely"""
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    if request.method == 'POST':
        vol_id = request.POST.get('volunteer_id')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone')
        blood_group = request.POST.get('blood_group', '').strip()
        occupation = request.POST.get('occupation', '').strip()
        division = request.POST.get('division', '').strip()
        district = request.POST.get('district', '').strip()
        upazila = request.POST.get('upazila', '').strip()
        address = request.POST.get('address', '')
        last_donated_str = request.POST.get('last_donated', '').strip()
        status = request.POST.get('status', 'approved')

        last_donated_val = None
        if last_donated_str:
            try:
                from datetime import datetime
                last_donated_val = datetime.strptime(last_donated_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        if vol_id:
            vol = Volunteer.objects.filter(pk=vol_id).first()
            if vol:
                vol.full_name = full_name
                vol.email = email
                vol.phone = phone
                vol.blood_group = blood_group if blood_group else None
                vol.occupation = occupation if occupation else None
                vol.division = division or 'রাজশাহী'
                vol.district = district or 'নওগাঁ'
                vol.upazila = upazila
                vol.address = address
                vol.last_donated = last_donated_val
                vol.status = status
                vol.save()
                messages.success(request, f'স্বেচ্ছাসেবক "{full_name}" তথ্য আপডেট করা হয়েছে!')
            else:
                messages.warning(request, 'স্বেচ্ছাসেবকের তথ্য খুঁজে পাওয়া যায়নি।')
        else:
            vol = Volunteer.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                blood_group=blood_group if blood_group else None,
                occupation=occupation if occupation else None,
                division=division or 'রাজশাহী',
                district=district or 'নওগাঁ',
                upazila=upazila,
                address=address,
                last_donated=last_donated_val,
                status=status
            )
            messages.success(request, f'নতুন স্বেচ্ছাসেবক "{full_name}" তালিকাভুক্ত করা হয়েছে!')

        if blood_group and vol:
            BloodDonor.objects.update_or_create(
                phone=phone,
                defaults={
                    'full_name': full_name,
                    'blood_group': blood_group,
                    'division': division or 'রাজশাহী',
                    'district': district or 'নওগাঁ',
                    'upazila': upazila,
                    'location': address or upazila or 'নওগাঁ',
                    'last_donated': last_donated_val,
                    'member_id': vol.member_id,
                    'is_available': True,
                }
            )
    return redirect('/dashboard/?tab=volunteers-section')

@staff_member_required
def delete_volunteer(request, pk):
    """Delete a Volunteer safely"""
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    vol = Volunteer.objects.filter(pk=pk).first()
    if vol:
        name = vol.full_name
        vol.delete()
        messages.success(request, f'স্বেচ্ছাসেবক "{name}" মুছে ফেলা হয়েছে!')
    else:
        messages.warning(request, 'স্বেচ্ছাসেবকের তথ্য ইতিমধ্যে মুছে ফেলা হয়েছে বা খুঁজে পাওয়া যায়নি।')
    return redirect('/dashboard/?tab=volunteers-section')

@staff_member_required
def save_team_member(request):
    """Create or update a Leadership Team Member safely with role validation, user account creation, and email notifications"""
    if not request.user.is_superuser:
        messages.warning(request, 'টিম মেম্বার তৈরি বা পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।')
        return redirect('/dashboard/?tab=volunteers-section')

    if request.method == 'POST':
        tm_id = request.POST.get('member_pk')
        name = request.POST.get('name', '').strip()
        role = request.POST.get('role', 'অন্যান্য').strip()
        custom_role = request.POST.get('custom_role', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        division = request.POST.get('division', '').strip()
        district = request.POST.get('district', '').strip()
        upazila = request.POST.get('upazila', '').strip()
        address = request.POST.get('address', '').strip()
        bio = request.POST.get('bio', '').strip()
        try:
            order_val = request.POST.get('order', '0')
            order = int(order_val) if order_val and str(order_val).strip() else 0
        except (ValueError, TypeError):
            order = 0

        blood_group = request.POST.get('blood_group', '').strip()
        last_donated_str = request.POST.get('last_donated', '').strip()
        last_donated = None
        if last_donated_str:
            try:
                from datetime import datetime
                last_donated = datetime.strptime(last_donated_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                last_donated = None
        is_public_details = bool(request.POST.get('is_public_details'))
        custom_member_id = request.POST.get('custom_member_id', '').strip()

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        image_file = request.FILES.get('image')
        if image_file and not validate_image_size(request, image_file, max_kb=500, field_name='টিম সদস্যের ছবি'):
            return redirect('/dashboard/?tab=volunteers-section')

        # 1. Role Quota Validation
        SINGLE_SEAT_ROLES = ['সভাপতি', 'সাধারণ সম্পাদক', 'কোষাধ্যক্ষ']
        if role in SINGLE_SEAT_ROLES:
            existing_query = TeamMember.objects.filter(role=role)
            if tm_id:
                existing_query = existing_query.exclude(pk=tm_id)
            existing_member = existing_query.first()
            if existing_member:
                messages.error(
                    request,
                    f'দুঃখিত! "{role}" পদবীতে ইতিমধ্যে একজন সদস্য ({existing_member.name}) নিযুক্ত রয়েছেন। একক পদে সর্বোচ্চ ১ জন সদস্য থাকতে পারবেন।'
                )
                return redirect('/dashboard/?tab=volunteers-section')
        elif role == 'সাধারণ পরিষদ সদস্য':
            council_query = TeamMember.objects.filter(role='সাধারণ পরিষদ সদস্য')
            if tm_id:
                council_query = council_query.exclude(pk=tm_id)
            if council_query.count() >= 4:
                messages.error(
                    request,
                    'দুঃখিত! "সাধারণ পরিষদ সদস্য" পদে সর্বোচ্চ ৪ জন সদস্যের কোটা পূর্ণ রয়েছে। নতুন সাধারণ পরিষদ সদস্য যুক্ত করা যাবে না।'
                )
                return redirect('/dashboard/?tab=volunteers-section')

        # 2. Find or Initialize TeamMember instance
        tm = None
        if tm_id:
            tm = TeamMember.objects.filter(pk=tm_id).first()
            if not tm:
                messages.warning(request, 'টিম সদস্যের তথ্য খুঁজে পাওয়া যায়নি।')
                return redirect('/dashboard/?tab=volunteers-section')
        elif custom_member_id:
            # If custom_member_id is provided, check if a TeamMember already has this ID
            tm = TeamMember.objects.filter(member_id__iexact=custom_member_id).first()

        # Check if an existing Volunteer matches custom_member_id or phone to link their account
        vol = None
        if custom_member_id:
            vol = Volunteer.objects.filter(member_id__iexact=custom_member_id).first()
        if not vol and phone:
            vol = Volunteer.objects.filter(phone=phone).first()

        # 3. User account creation / linking
        is_new_member = (tm is None)
        if is_new_member and role == 'অন্যান্য':
            auth_user = None
            user_created_or_updated = False
        else:
            auth_user = tm.user if (tm and tm.user) else None
            user_created_or_updated = False
            if username:
                existing_user_query = User.objects.filter(username__iexact=username)
                if auth_user:
                    existing_user_query = existing_user_query.exclude(pk=auth_user.pk)
                if existing_user_query.exists():
                    messages.error(request, f'"{username}" ইউজারনেমটি ইতিমধ্যে ব্যবহৃত হয়েছে। অনুগ্রহ করে অন্য ইউজারনেম দিন।')
                    return redirect('/dashboard/?tab=volunteers-section')

                if auth_user:
                    auth_user.username = username
                    if email:
                        auth_user.email = email
                    auth_user.first_name = name
                    if password:
                        auth_user.set_password(password)
                    auth_user.is_staff = True
                    auth_user.save()
                    user_created_or_updated = True
                else:
                    auth_user = User.objects.create_user(
                        username=username,
                        email=email or '',
                        password=password if password else 'Pass1234@',
                        first_name=name
                    )
                    auth_user.is_staff = True
                    auth_user.save()
                    user_created_or_updated = True
            elif auth_user and password:
                auth_user.set_password(password)
                auth_user.save()
                user_created_or_updated = True

        # 4. Save Team Member
        if tm:
            tm.name = name
            tm.role = role
            tm.custom_role = custom_role if role == 'অন্যান্য' else ''
            tm.email = email
            tm.phone = phone
            tm.blood_group = blood_group
            tm.last_donated = last_donated
            tm.is_public_details = is_public_details
            tm.division = division
            tm.district = district
            tm.upazila = upazila
            tm.address = address
            tm.bio = bio
            tm.order = order
            if custom_member_id:
                tm.member_id = custom_member_id
            if auth_user:
                tm.user = auth_user
            if image_file:
                tm.image = image_file
            tm.save()
            messages.success(request, f'সদস্য আইডি "{tm.member_id}" অনুযায়ী টিম সদস্য "{name}"-এর তথ্য সফলভাবে আপডেট হয়েছে!')
        else:
            tm = TeamMember(
                name=name,
                role=role,
                custom_role=custom_role if role == 'অন্যান্য' else '',
                email=email,
                phone=phone,
                blood_group=blood_group,
                last_donated=last_donated,
                is_public_details=is_public_details,
                division=division,
                district=district,
                upazila=upazila,
                address=address,
                bio=bio,
                order=order,
                user=auth_user,
                image=image_file
            )
            if custom_member_id:
                tm.member_id = custom_member_id
            tm.save()
            messages.success(request, f'সদস্য আইডি "{tm.member_id}" দিয়ে টিম সদস্য "{name}" সফলভাবে যুক্ত হয়েছে!')

        # 5. Email Notification to Member (fail-silently)
        if email:
            try:
                subject = f"Hello Naogaon - পরিচালনা পর্ষদ / টিম মেম্বার হিসেবে আপনাকে স্বাগতম!"
                paragraphs = [
                    f"হ্যালো নওগাঁ (Hello Naogaon)-এর পরিচালনা পর্ষদ / টিম মেম্বার ({tm.effective_role}) হিসেবে যুক্ত হওয়ায় আপনাকে আন্তরিক মোবারকবাদ ও শুভেচ্ছা!",
                    "সংগঠনকে সামনের দিকে এগিয়ে নিতে এবং মানবতার সেবায় কার্যকর ভূমিকা পালনে আপনার সক্রিয় ভূমিকা আমাদের জন্য অত্যন্ত গর্বের ও অনুপ্রেরণার।"
                ]
                
                login_info_data = None
                if username or (auth_user and user_created_or_updated):
                    login_id = username or (auth_user.username if auth_user else tm.member_id)
                    login_info_data = {
                        'username': login_id,
                        'password': password if password else '(নির্ধারিত পাসওয়ার্ড)',
                        'role': tm.effective_role,
                    }

                send_system_email(
                    subject=subject,
                    recipient_list=[email],
                    recipient_name=name,
                    greeting="আসসালামু আলাইকুম",
                    headline="পরিচালনা পর্ষদ ও টিম সদস্য নিবন্ধন",
                    message_paragraphs=paragraphs,
                    team_member=tm,
                    login_info=login_info_data,
                    request=request,
                    footer_note="আপনার অ্যাকাউন্টের নিরাপত্তা রক্ষার্থে প্রথমবার লগইন করার পর পাসওয়ার্ড পরিবর্তন করে নিন।",
                    fail_silently=True,
                )
            except Exception as e:
                print(f"[TEAM MEMBER EMAIL ERROR] {e}")

    return redirect('/dashboard/?tab=volunteers-section')

@staff_member_required
def delete_team_member(request, pk):
    """Delete a Team Member safely"""
    if not request.user.is_superuser:
        messages.warning(request, 'টিম সদস্য মুছে ফেলার অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।')
        return redirect('/dashboard/?tab=volunteers-section')

    tm = TeamMember.objects.filter(pk=pk).first()
    if tm:
        name = tm.name
        if tm.user:
            tm.user.delete()
        tm.delete()
        messages.success(request, f'টিম সদস্য "{name}" মুছে ফেলা হয়েছে!')
    else:
        messages.warning(request, 'টিম সদস্যের তথ্য ইতিমধ্যে মুছে ফেলা হয়েছে বা খুঁজে পাওয়া যায়নি।')
    return redirect('/dashboard/?tab=volunteers-section')

@staff_member_required
def save_financial_transaction(request):
    """Create or update a Financial Transaction safely"""
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    if request.method == 'POST':
        trx_id_db = request.POST.get('transaction_id')
        t_type = request.POST.get('transaction_type', 'income')
        title = request.POST.get('title')
        category = request.POST.get('category', 'সাধারণ')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method', 'bKash')
        trx_id = request.POST.get('trx_id', '')
        donor_name = request.POST.get('donor_name', '')
        date_val = request.POST.get('date') or date.today()
        note = request.POST.get('note', '')

        program_id = request.POST.get('program_id')
        prog = Program.objects.filter(pk=program_id).first() if program_id else None

        receipt_file = request.FILES.get('receipt')
        if receipt_file and not validate_image_size(request, receipt_file, max_kb=800, field_name='রশিদ/ভাউচার ফাইল'):
            return redirect('/dashboard/?tab=finance-section')

        if trx_id_db:
            trx = FinancialTransaction.objects.filter(pk=trx_id_db).first()
            if trx:
                trx.transaction_type = t_type
                trx.program = prog
                trx.title = title
                trx.category = category
                trx.amount = amount
                trx.payment_method = payment_method
                trx.trx_id = trx_id
                trx.donor_name = donor_name
                trx.date = date_val
                trx.note = note
                if receipt_file:
                    trx.receipt = receipt_file
                trx.save()
                messages.success(request, 'আর্থিক লেনদেন আপডেট করা হয়েছে!')
            else:
                messages.warning(request, 'লেনদেনটি খুঁজে পাওয়া যায়নি।')
        else:
            FinancialTransaction.objects.create(
                transaction_type=t_type,
                program=prog,
                title=title,
                category=category,
                amount=amount,
                payment_method=payment_method,
                trx_id=trx_id,
                donor_name=donor_name,
                date=date_val,
                note=note,
                receipt=receipt_file
            )
            messages.success(request, 'নতুন আর্থিক লেনদেন অন্তর্ভুক্ত করা হয়েছে!')
    return redirect('/dashboard/?tab=finance-section')

@staff_member_required
def delete_financial_transaction(request, pk):
    """Delete a Financial Transaction safely"""
    trx = FinancialTransaction.objects.filter(pk=pk).first()
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    if trx:
        trx.delete()
        messages.success(request, 'আর্থিক লেনদেন মুছে ফেলা হয়েছে!')
    else:
        messages.warning(request, 'লেনদেনটি ইতিমধ্যে মুছে ফেলা হয়েছে বা খুঁজে পাওয়া যায়নি।')
    return redirect('/dashboard/?tab=finance-section')

@staff_member_required
def save_gallery_photo(request):
    """Upload new gallery photo"""
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    if request.method == 'POST':
        caption = request.POST.get('caption', '')
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            if not validate_image_size(request, image_file, max_kb=1024, field_name='গ্যালারির ছবি'):
                return redirect('/dashboard/?tab=gallery-section')

            album, _ = Album.objects.get_or_create(title='Main Gallery')
            Photo.objects.create(
                album=album,
                image=image_file,
                caption=caption
            )
            messages.success(request, 'গ্যালারিতে নতুন ছবি আপলোড করা হয়েছে!')
        else:
            messages.error(request, 'দয়া করে একটি ছবি নির্বাচন করুন')
    return redirect('/dashboard/?tab=gallery-section')

@staff_member_required
def update_footer_section(request):
    """Update footer text, address, phone, email & map embed"""
    if not can_user_edit_general(request.user):
        messages.warning(request, "এই তথ্য পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।")
        return redirect("/dashboard/")

    if request.method == 'POST':
        setting, _ = SiteSetting.objects.get_or_create(pk=1)
        setting.footer_about = request.POST.get('footer_about', setting.footer_about)
        setting.contact_address = request.POST.get('contact_address', setting.contact_address)
        setting.contact_phone = request.POST.get('contact_phone', setting.contact_phone)
        setting.contact_email = request.POST.get('contact_email', setting.contact_email)
        setting.google_map_embed_url = request.POST.get('google_map_embed_url', setting.google_map_embed_url)
        setting.save()
        messages.success(request, 'ফুটার ও যোগাযোগের তথ্য আপডেট হয়েছে!')
    return redirect('/dashboard/?tab=home-section')
import openpyxl
from django.http import HttpResponse

@staff_member_required
def export_financial_excel(request):
    """Export Financial Transactions to Excel"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    transactions = FinancialTransaction.objects.all().order_by('-date', '-id')
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Financial Statement"

    headers = ['তারিখ', 'ধরণ', 'শিরোনাম/বিবরণ', 'ক্যাটাগরি', 'দাতা/গ্রহীতা', 'পেমেন্ট মেথড', 'Trx ID', 'পরিমাণ (BDT)', 'নোট']
    ws.append(headers)

    for trx in transactions:
        t_type = "আয় (Income)" if trx.transaction_type == 'income' else "ব্যয় (Expense)"
        ws.append([
            str(trx.date),
            t_type,
            trx.title,
            trx.category,
            trx.donor_name or "-",
            trx.payment_method,
            trx.trx_id or "-",
            float(trx.amount),
            trx.note or "-"
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Financial_Statement.xlsx'
    wb.save(response)
    return response

@staff_member_required
def print_financial_statement(request):
    """Print Statement View"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    transactions = FinancialTransaction.objects.all().order_by('-date', '-id')
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    net_balance = total_income - total_expense

    site_setting, _ = SiteSetting.objects.get_or_create(pk=1)

    context = {
        'site_setting': site_setting,
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'start_date': start_date,
        'end_date': end_date,
        'today': date.today()
    }
    return render(request, 'dashboard/print_financial_statement.html', context)

@staff_member_required
def approve_program_donation(request, pk):
    """Approve a pending program/general donation, update raised amount and record in FinancialTransaction safely"""
    donation = ProgramDonation.objects.filter(pk=pk).first()
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    if not donation:
        messages.warning(request, 'অনুদানের তথ্যটি ইতিমধ্যে অনুমোদিত বা মুছে ফেলা হয়েছে।')
        return redirect('/dashboard/?tab=finance-section')

    if donation.status != 'approved':
        donation.status = 'approved'
        donation.save()

        # Update program raised_amount if linked
        if donation.program:
            prog = donation.program
            prog.raised_amount = (prog.raised_amount or 0) + donation.amount
            prog.save()
            category_name = f"কার্যক্রম: {prog.title}"
            title_name = f"কার্যক্রম অনুদান - {prog.title} ({donation.donor_name})"
        elif donation.donation_type == 'volunteer':
            category_name = "স্বেচ্ছাসেবক মাসিক চাঁদা / সহায়তা"
            title_name = f"স্বেচ্ছাসেবক চাঁদা ({donation.donor_name})"
        else:
            category_name = "সাধারণ আর্থিক সহায়তা"
            title_name = f"সাধারণ আর্থিক সহায়তা ({donation.donor_name})"

        trx_note = f"পেমেন্ট মাধ্যম: {donation.payment_method} | Trx ID: {donation.trx_id or 'N/A'} | মেম্বার আইডি: {donation.membership_id or 'N/A'} | ফোন: {donation.donor_phone}"
        if donation.program:
            trx_note += f" | কার্যক্রম: {donation.program.title}"
        if donation.note:
            trx_note += f" | নোট: {donation.note}"

        FinancialTransaction.objects.create(
            transaction_type='income',
            program=donation.program,
            title=title_name,
            category=category_name,
            amount=donation.amount,
            payment_method=donation.payment_method or 'bKash',
            trx_id=donation.trx_id or f"HN{donation.id}",
            donor_name=donation.donor_name,
            date=date.today(),
            note=trx_note
        )
        messages.success(request, f'অনুদান (৳{donation.amount}) সফলভাবে অনুমোদিত হয়েছে এবং ফাইন্যান্স লেজারে যুক্ত হয়েছে!')
    return redirect('/dashboard/?tab=finance-section')

@staff_member_required
def delete_program_donation(request, pk):
    """Delete a donation entry safely"""
    donation = ProgramDonation.objects.filter(pk=pk).first()
    if not can_user_edit_finance(request.user):
        messages.warning(request, "আর্থিক হিসাব পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিন ও কোষাধ্যক্ষের রয়েছে।")
        return redirect("/dashboard/?tab=finance-section")

    if donation:
        donation.delete()
        messages.success(request, 'অনুদানের তথ্য মুছে ফেলা হয়েছে!')
    else:
        messages.warning(request, 'অনুদানের তথ্য ইতিমধ্যে মুছে ফেলা হয়েছে বা খুঁজে পাওয়া যায়নি।')
    return redirect('/dashboard/?tab=finance-section')


@login_required
def update_profile(request):
    """Allow any logged-in user (admin, team member, volunteer) to update their own profile."""
    redirect_target = request.META.get('HTTP_REFERER') or '/dashboard/'
    if request.method != 'POST':
        return redirect(redirect_target)

    user = request.user
    new_name = request.POST.get('profile_name', '').strip()
    new_email = request.POST.get('profile_email', '').strip()
    new_phone = request.POST.get('profile_phone', '').strip()
    new_division = request.POST.get('profile_division', '').strip()
    new_district = request.POST.get('profile_district', '').strip()
    new_upazila = request.POST.get('profile_upazila', '').strip()
    new_address = request.POST.get('profile_address', '').strip()
    new_bio = request.POST.get('profile_bio', '').strip()
    profile_blood_group = request.POST.get('profile_blood_group', '').strip()
    profile_last_donated_str = request.POST.get('profile_last_donated', '').strip()
    profile_last_donated = None
    if profile_last_donated_str:
        try:
            from datetime import datetime
            profile_last_donated = datetime.strptime(profile_last_donated_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            profile_last_donated = None
    profile_is_public_details = bool(request.POST.get('profile_is_public_details'))
    new_password = request.POST.get('profile_password', '').strip()
    confirm_password = request.POST.get('profile_confirm_password', '').strip()

    changes = []

    # Update User model
    if new_name and new_name != user.get_full_name():
        parts = new_name.split(' ')
        user.first_name = parts[0]
        user.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
        changes.append(f'নাম: {new_name}')

    if new_email and new_email != user.email:
        if User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
            messages.error(request, 'এই ইমেইলটি অন্য কোনো অ্যাকাউন্টে ইতিমধ্যে ব্যবহৃত হয়েছে।')
            return redirect(redirect_target)
        user.email = new_email
        changes.append(f'ইমেইল: {new_email}')

    if new_password:
        if new_password != confirm_password:
            messages.error(request, 'নতুন পাসওয়ার্ড এবং নিশ্চিতকরণ পাসওয়ার্ড মেলেনি।')
            return redirect(redirect_target)
        if len(new_password) < 6:
            messages.error(request, 'পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে।')
            return redirect(redirect_target)
        user.set_password(new_password)
        changes.append('পাসওয়ার্ড পরিবর্তিত হয়েছে')

    user.save()

    # Update TeamMember profile if exists or link/create for staff/superuser
    tm = getattr(user, 'team_profile', None)
    if not tm and (user.is_staff or user.is_superuser):
        tm = TeamMember.objects.filter(user=user).first()
        if not tm and user.email:
            tm = TeamMember.objects.filter(email__iexact=user.email).first()
            if tm and not tm.user:
                tm.user = user
                tm.save()
        if not tm and (new_phone or new_address or new_division or new_district or new_upazila or 'profile_photo' in request.FILES):
            from volunteers.models import generate_next_member_id
            role_title = 'প্রধান অ্যাডমিন' if user.is_superuser else 'স্টাফ অ্যাডমিন'
            tm = TeamMember.objects.create(
                user=user,
                name=new_name or user.get_full_name() or user.username,
                role='অন্যান্য',
                custom_role=role_title,
                email=user.email,
                member_id=generate_next_member_id(),
                phone=new_phone,
                division=new_division or 'রাজশাহী',
                district=new_district or 'নওগাঁ',
                upazila=new_upazila,
                address=new_address
            )
            changes.append('টিম প্রোফাইল সংযুক্ত হয়েছে')

    if tm:
        if new_name:
            tm.name = new_name
        if new_email:
            tm.email = new_email
        if new_phone and new_phone != tm.phone:
            tm.phone = new_phone
            changes.append(f'ফোন: {new_phone}')
        if new_division and new_division != tm.division:
            tm.division = new_division
            changes.append(f'বিভাগ: {new_division}')
        if new_district and new_district != tm.district:
            tm.district = new_district
            changes.append(f'জেলা: {new_district}')
        if new_upazila and new_upazila != tm.upazila:
            tm.upazila = new_upazila
            changes.append(f'উপজেলা: {new_upazila}')
        if new_address and new_address != tm.address:
            tm.address = new_address
            changes.append(f'ঠিকানা: {new_address}')
        if new_bio and new_bio != tm.bio:
            tm.bio = new_bio
            changes.append('সংক্ষিপ্ত পরিচিতি (Bio) আপডেট হয়েছে')
        if profile_blood_group:
            tm.blood_group = profile_blood_group
            changes.append(f'রক্তের গ্রুপ: {profile_blood_group}')
        if profile_last_donated:
            tm.last_donated = profile_last_donated
            changes.append(f'সর্বশেষ রক্তদান: {profile_last_donated}')
        tm.is_public_details = profile_is_public_details

        # Photo update
        if 'profile_photo' in request.FILES:
            photo_file = request.FILES['profile_photo']
            if not validate_image_size(request, photo_file, max_kb=500, field_name='প্রোফাইল ছবি'):
                return redirect(redirect_target)
            tm.image = photo_file
            changes.append('প্রোফাইল ছবি আপডেট হয়েছে')

        tm.save()

    # Update Volunteer profile if exists
    vp = getattr(user, 'volunteer_profile', None)
    if vp:
        if new_name:
            vp.full_name = new_name
        if new_email:
            vp.email = new_email
        if new_phone and new_phone != vp.phone:
            vp.phone = new_phone
            changes.append(f'ফোন: {new_phone}')
        if profile_blood_group:
            vp.blood_group = profile_blood_group
        if profile_last_donated:
            vp.last_donated = profile_last_donated
        vp.is_public_details = profile_is_public_details
        if new_division and new_division != vp.division:
            vp.division = new_division
            changes.append(f'বিভাগ: {new_division}')
        if new_district and new_district != vp.district:
            vp.district = new_district
            changes.append(f'জেলা: {new_district}')
        if new_upazila and new_upazila != vp.upazila:
            vp.upazila = new_upazila
            changes.append(f'উপজেলা: {new_upazila}')
        if new_address and new_address != vp.address:
            vp.address = new_address
            changes.append(f'ঠিকানা: {new_address}')
        vp.save()

    # Send notification email if changes made
    if changes and (new_email or user.email):
        recipient = new_email or user.email
        display_name = new_name or user.get_full_name() or user.username
        try:
            send_system_email(
                subject='আপনার প্রোফাইল তথ্য সফলভাবে আপডেট হয়েছে — Helpline Hello Naogaon',
                recipient_list=[recipient],
                recipient_name=display_name,
                greeting=f'প্রিয় {display_name},',
                headline='প্রোফাইল সফলভাবে আপডেট হয়েছে',
                message_paragraphs=[
                    'আপনার Helpline Hello Naogaon ড্যাশবোর্ড প্রোফাইল তথ্য সফলভাবে পরিবর্তন করা হয়েছে।',
                    'পরিবর্তনসমূহ: ' + ', '.join(changes),
                    'আপনি যদি নিজে এই পরিবর্তন না করে থাকেন, তবে অবিলম্বে প্রধান এডমিনের সাথে যোগাযোগ করুন।',
                ],
                request=request,
                fail_silently=True,
            )
        except Exception:
            pass

    if changes:
        messages.success(request, f'প্রোফাইল তথ্য সফলভাবে আপডেট হয়েছে! ({", ".join(changes)})')
    else:
        messages.info(request, 'কোনো পরিবর্তন করা হয়নি।')

    if new_password:
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)

    return redirect(redirect_target)


@staff_member_required
def delete_gallery_photo(request, pk):
    """Delete a single gallery photo safely."""
    if not can_user_edit_general(request.user):
        messages.warning(request, 'গ্যালারি পরিবর্তনের অনুমতি শুধুমাত্র প্রধান এডমিনের রয়েছে।')
        return redirect('/dashboard/?tab=gallery-section')
    from gallery.models import Photo
    photo = Photo.objects.filter(pk=pk).first()
    if photo:
        photo.delete()
        messages.success(request, 'ছবিটি সফলভাবে মুছে ফেলা হয়েছে!')
    else:
        messages.warning(request, 'ছবিটি খুঁজে পাওয়া যায়নি।')
    return redirect('/dashboard/?tab=gallery-section')