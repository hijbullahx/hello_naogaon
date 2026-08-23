from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from core.models import SiteSetting, StatCounter, AboutImage
from programs.models import Program, Event, SuccessStory
from news.models import Article, Category
from volunteers.models import BloodDonor, Volunteer, TeamMember
from gallery.models import Photo, Album
from donations.models import (
    Bank, QRCode, DonationMethod, FinancialTransaction,
    DonationPageContent, Campaign, ProgramDonation, EmergencyAppeal, DonationImpact, FAQ
)
from django.db.models import Sum
from datetime import date

def validate_image_100kb(request, image_file, field_name="ছবি"):
    """Validates that uploaded image/file is <= 100 KB"""
    if image_file and image_file.size > 100 * 1024:
        size_kb = image_file.size / 1024
        messages.error(
            request,
            f'{field_name}-র সাইজ সর্বোচ্চ 100 KB হতে পারবে (আপনার ফাইলের সাইজ: {size_kb:.1f} KB)। '
            f'অনুগ্রহ করে resizepixel.com থেকে ছবির সাইজ কমিয়ে পুনরায় আপলোড করুন।'
        )
        return False
    return True

@staff_member_required
def dashboard_home(request):
    """
    Main Custom Cardly Front-End Admin Control Panel.
    Provides section-by-section edit cards for Hero, About, Programs, Blood Donors, Volunteers, Financial Management, News, Gallery, Donations & Footer.
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
    }
    return render(request, 'dashboard/index.html', context)

@staff_member_required
def update_hero_section(request):
    """Update Site Title, Taglines, Contact Info & Hero/Logo Images"""
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
            if not validate_image_100kb(request, request.FILES['logo'], 'লোগো ছবি'):
                return redirect('/dashboard/?tab=home-section')
            setting.logo = request.FILES['logo']

        if 'hero_image' in request.FILES:
            if not validate_image_100kb(request, request.FILES['hero_image'], 'হিরো ছবি'):
                return redirect('/dashboard/?tab=home-section')
            setting.hero_image = request.FILES['hero_image']

        setting.save()
        messages.success(request, 'হেডার, হিরো ও যোগাযোগের তথ্য সফলভাবে আপডেট হয়েছে!')
    return redirect('/dashboard/?tab=home-section')

@staff_member_required
def update_about_section(request):
    """Update About Us Text & Upload Featured/Grid Images"""
    if request.method == 'POST':
        setting, _ = SiteSetting.objects.get_or_create(pk=1)
        setting.about_text = request.POST.get('about_text', setting.about_text)
        setting.about_video_url = request.POST.get('about_video_url', setting.about_video_url)
        setting.save()

        # Handle Featured Main Image
        if 'featured_image' in request.FILES:
            if not validate_image_100kb(request, request.FILES['featured_image'], 'ফিচারড ছবি'):
                return redirect('/dashboard/?tab=home-section')
            AboutImage.objects.filter(is_featured=True).delete()
            AboutImage.objects.create(image=request.FILES['featured_image'], is_featured=True)

        # Handle Grid Image Upload
        if 'grid_image' in request.FILES:
            if not validate_image_100kb(request, request.FILES['grid_image'], 'গ্রিড ছবি'):
                return redirect('/dashboard/?tab=home-section')
            AboutImage.objects.create(image=request.FILES['grid_image'], is_featured=False)

        messages.success(request, 'আমাদের সম্পর্কে সেকশনের তথ্য আপডেট হয়েছে!')
    return redirect('/dashboard/?tab=home-section')

@staff_member_required
def delete_about_image(request, pk):
    """Delete an About section grid image"""
    img = get_object_or_404(AboutImage, pk=pk)
    img.delete()
    messages.success(request, 'ছবিটি সফলভাবে মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=home-section')

@staff_member_required
def update_stat_counters(request):
    """Update 4 Stat Counters"""
    if request.method == 'POST':
        for i in range(1, 5):
            title = request.POST.get(f'stat_title_{i}')
            value = request.POST.get(f'stat_value_{i}')
            icon = request.POST.get(f'stat_icon_{i}')
            if title and value:
                counter, _ = StatCounter.objects.get_or_create(order=i)
                counter.title = title
                counter.value = value
                counter.icon = icon or counter.icon
                counter.save()
        messages.success(request, 'পরিসংখ্যান কাউন্টার আপডেট হয়েছে!')
    return redirect('/dashboard/?tab=home-section')

@staff_member_required
def save_program(request):
    """Create or update a Program"""
    if request.method == 'POST':
        prog_id = request.POST.get('program_id')
        title = request.POST.get('title')
        short_description = request.POST.get('short_description', '')
        description = request.POST.get('description', '')
        status = request.POST.get('status', 'ongoing')
        badge_color = request.POST.get('badge_color', 'bg-success')

        image_file = request.FILES.get('image')
        if image_file and not validate_image_100kb(request, image_file, 'কার্যক্রমের ছবি'):
            return redirect('/dashboard/?tab=programs-section')

        if prog_id:
            prog = get_object_or_404(Program, pk=prog_id)
            prog.title = title
            prog.short_description = short_description
            prog.description = description
            prog.status = status
            prog.badge_color = badge_color
            if image_file:
                prog.image = image_file
            prog.save()
            messages.success(request, f'কার্যক্রম "{title}" আপডেট হয়েছে!')
        else:
            prog = Program.objects.create(
                title=title,
                short_description=short_description,
                description=description,
                status=status,
                badge_color=badge_color,
                image=image_file
            )
            messages.success(request, f'নতুন কার্যক্রম "{title}" যোগ করা হয়েছে!')
    return redirect('/dashboard/?tab=programs-section')

@staff_member_required
def delete_program(request, pk):
    """Delete a Program"""
    prog = get_object_or_404(Program, pk=pk)
    title = prog.title
    prog.delete()
    messages.success(request, f'কার্যক্রম "{title}" মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=programs-section')

@staff_member_required
def save_news(request):
    """Create or update a News Article"""
    if request.method == 'POST':
        art_id = request.POST.get('article_id')
        title = request.POST.get('title')
        content = request.POST.get('content', '')
        category_name = request.POST.get('category', 'সাধারণ')

        image_file = request.FILES.get('image')
        if image_file and not validate_image_100kb(request, image_file, 'সংবাদের ছবি'):
            return redirect('/dashboard/?tab=news-section')

        category, _ = Category.objects.get_or_create(name=category_name)

        if art_id:
            art = get_object_or_404(Article, pk=art_id)
            art.title = title
            art.content = content
            art.category = category
            if image_file:
                art.image = image_file
            art.save()
            messages.success(request, f'সংবাদ "{title}" আপডেট হয়েছে!')
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
    """Delete a News Article"""
    art = get_object_or_404(Article, pk=pk)
    title = art.title
    art.delete()
    messages.success(request, f'সংবাদ "{title}" মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=news-section')

@staff_member_required
def update_bank_and_donation(request):
    """Update Bank Account details & bKash QR code image"""
    if request.method == 'POST':
        b_id = request.POST.get('bank_id')
        bank_name = request.POST.get('bank_name')
        account_name = request.POST.get('account_name')
        account_number = request.POST.get('account_number')
        branch = request.POST.get('branch', '')
        swift_code = request.POST.get('swift_code', '')

        if bank_name and account_number:
            if b_id:
                bank = get_object_or_404(Bank, pk=b_id)
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
            if not validate_image_100kb(request, qr_file, 'QR কোড ছবি'):
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
    if request.method == 'POST':
        content, _ = DonationPageContent.objects.get_or_create(pk=1)
        content.hero_title = request.POST.get('hero_title', content.hero_title)
        content.hero_subtitle = request.POST.get('hero_subtitle', content.hero_subtitle)
        content.why_donate_title = request.POST.get('why_donate_title', content.why_donate_title)
        content.why_donate_text = request.POST.get('why_donate_text', content.why_donate_text)
        content.transparency_title = request.POST.get('transparency_title', content.transparency_title)
        content.transparency_text = request.POST.get('transparency_text', content.transparency_text)

        if 'hero_image' in request.FILES:
            if not validate_image_100kb(request, request.FILES['hero_image'], 'দানের পেজ হিরো ছবি'):
                return redirect('/dashboard/?tab=bank-section')
            content.hero_image = request.FILES['hero_image']

        content.save()
        messages.success(request, 'দানের পেজের তথ্য সফলভাবে আপডেট করা হয়েছে!')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def save_campaign(request):
    """Create or update a Campaign"""
    if request.method == 'POST':
        c_id = request.POST.get('campaign_id')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        goal_amount = request.POST.get('goal_amount', 0)
        raised_amount = request.POST.get('raised_amount', 0)
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        image_file = request.FILES.get('image')
        if image_file and not validate_image_100kb(request, image_file, 'ক্যাম্পেইন ছবি'):
            return redirect('/dashboard/?tab=bank-section')

        if c_id:
            camp = get_object_or_404(Campaign, pk=c_id)
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
    """Delete a Campaign"""
    camp = get_object_or_404(Campaign, pk=pk)
    title = camp.title
    camp.delete()
    messages.success(request, f'ক্যাম্পেইন "{title}" মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def save_emergency_appeal(request):
    """Create or update an Emergency Appeal"""
    if request.method == 'POST':
        appeal_id = request.POST.get('appeal_id')
        title = request.POST.get('title')
        description = request.POST.get('description', '')

        image_file = request.FILES.get('image')
        if image_file and not validate_image_100kb(request, image_file, 'জরুরি আপিল ছবি'):
            return redirect('/dashboard/?tab=bank-section')

        if appeal_id:
            app = get_object_or_404(EmergencyAppeal, pk=appeal_id)
            app.title = title
            app.description = description
            if image_file:
                app.image = image_file
            app.save()
            messages.success(request, f'জরুরি আবেদন "{title}" আপডেট করা হয়েছে!')
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
    """Delete an Emergency Appeal"""
    app = get_object_or_404(EmergencyAppeal, pk=pk)
    title = app.title
    app.delete()
    messages.success(request, f'জরুরি আবেদন "{title}" মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def save_donation_impact(request):
    """Create or update a Donation Impact item"""
    if request.method == 'POST':
        imp_id = request.POST.get('impact_id')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        icon_class = request.POST.get('icon_class', 'fas fa-heart')

        if imp_id:
            imp = get_object_or_404(DonationImpact, pk=imp_id)
            imp.amount = amount
            imp.description = description
            imp.icon_class = icon_class
            imp.save()
            messages.success(request, f'দান প্রভাব (৳{amount}) আপডেট করা হয়েছে!')
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
    """Delete a Donation Impact item"""
    imp = get_object_or_404(DonationImpact, pk=pk)
    imp.delete()
    messages.success(request, 'দান প্রভাব উপাদান মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def save_faq(request):
    """Create or update a Donation FAQ"""
    if request.method == 'POST':
        faq_id = request.POST.get('faq_id')
        question = request.POST.get('question')
        answer = request.POST.get('answer')

        if faq_id:
            faq = get_object_or_404(FAQ, pk=faq_id)
            faq.question = question
            faq.answer = answer
            faq.save()
            messages.success(request, 'জিজ্ঞাসাবাদ (FAQ) আপডেট করা হয়েছে!')
        else:
            FAQ.objects.create(
                question=question,
                answer=answer
            )
            messages.success(request, 'নতুন জিজ্ঞাসাবাদ (FAQ) তৈরি করা হয়েছে!')
    return redirect('/dashboard/?tab=bank-section')

@staff_member_required
def delete_faq(request, pk):
    """Delete a Donation FAQ"""
    faq = get_object_or_404(FAQ, pk=pk)
    faq.delete()
    messages.success(request, 'জিজ্ঞাসাবাদ (FAQ) মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=bank-section')


@staff_member_required
def save_donor(request):
    """Create or update a Blood Donor"""
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
            donor = get_object_or_404(BloodDonor, pk=donor_id)
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
    """Delete a Blood Donor"""
    donor = get_object_or_404(BloodDonor, pk=pk)
    name = donor.full_name
    donor.delete()
    messages.success(request, f'রক্তদাতা "{name}" মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=donors-section')

@staff_member_required
def save_volunteer(request):
    """Create or update a Volunteer"""
    if request.method == 'POST':
        vol_id = request.POST.get('volunteer_id')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone')
        blood_group = request.POST.get('blood_group', '').strip()
        occupation = request.POST.get('occupation', '').strip()
        division = request.POST.get('division', 'রাজশাহী').strip()
        district = request.POST.get('district', 'নওগাঁ').strip()
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
            vol = get_object_or_404(Volunteer, pk=vol_id)
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

        if blood_group:
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
    """Delete a Volunteer"""
    vol = get_object_or_404(Volunteer, pk=pk)
    name = vol.full_name
    vol.delete()
    messages.success(request, f'স্বেচ্ছাসেবক "{name}" মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=volunteers-section')

@staff_member_required
def save_team_member(request):
    """Create or update a Leadership Team Member"""
    if request.method == 'POST':
        tm_id = request.POST.get('member_id')
        name = request.POST.get('name')
        role = request.POST.get('role')
        bio = request.POST.get('bio', '')
        order = request.POST.get('order', 0)

        image_file = request.FILES.get('image')
        if image_file and not validate_image_100kb(request, image_file, 'টিম সদস্যের ছবি'):
            return redirect('/dashboard/?tab=volunteers-section')

        if tm_id:
            tm = get_object_or_404(TeamMember, pk=tm_id)
            tm.name = name
            tm.role = role
            tm.bio = bio
            tm.order = order
            if image_file:
                tm.image = image_file
            tm.save()
            messages.success(request, f'টিম সদস্য "{name}" তথ্য আপডেট হয়েছে!')
        else:
            TeamMember.objects.create(
                name=name,
                role=role,
                bio=bio,
                order=order,
                image=image_file
            )
            messages.success(request, f'নতুন টিম সদস্য "{name}" যোগ করা হয়েছে!')
    return redirect('/dashboard/?tab=volunteers-section')

@staff_member_required
def delete_team_member(request, pk):
    """Delete a Team Member"""
    tm = get_object_or_404(TeamMember, pk=pk)
    name = tm.name
    tm.delete()
    messages.success(request, f'টিম সদস্য "{name}" মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=volunteers-section')

@staff_member_required
def save_financial_transaction(request):
    """Create or update a Financial Transaction"""
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

        receipt_file = request.FILES.get('receipt')
        if receipt_file and not validate_image_100kb(request, receipt_file, 'রশিদ/ভাউচার ফাইল'):
            return redirect('/dashboard/?tab=finance-section')

        if trx_id_db:
            trx = get_object_or_404(FinancialTransaction, pk=trx_id_db)
            trx.transaction_type = t_type
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
            FinancialTransaction.objects.create(
                transaction_type=t_type,
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
    """Delete a Financial Transaction"""
    trx = get_object_or_404(FinancialTransaction, pk=pk)
    trx.delete()
    messages.success(request, 'আর্থিক লেনদেন মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=finance-section')

@staff_member_required
def save_gallery_photo(request):
    """Upload new gallery photo"""
    if request.method == 'POST':
        caption = request.POST.get('caption', '')
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            if not validate_image_100kb(request, image_file, 'গ্যালারির ছবি'):
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