from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from core.models import SiteSetting, StatCounter, AboutImage, ContactMessage
from programs.models import Program, Event, SuccessStory
from news.models import Article, Category
from volunteers.models import BloodDonor, Volunteer, TeamMember
from gallery.models import Photo, Album
from donations.models import Bank, QRCode, DonationMethod

@staff_member_required
def dashboard_home(request):
    """
    Main Custom Cardly Front-End Admin Control Panel.
    Provides section-by-section edit cards for Hero, About, Programs, Blood Donors, Volunteers, News, Gallery, Donations & Footer.
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
    messages_list = ContactMessage.objects.all().order_by('-created_at')

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
        'messages_list': messages_list,
    }
    return render(request, 'dashboard/index.html', context)

@staff_member_required
def save_volunteer(request):
    """Create or update a Volunteer"""
    if request.method == 'POST':
        vol_id = request.POST.get('volunteer_id')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone')
        address = request.POST.get('address', '')
        status = request.POST.get('status', 'approved')

        if vol_id:
            vol = get_object_or_404(Volunteer, pk=vol_id)
            vol.full_name = full_name
            vol.email = email
            vol.phone = phone
            vol.address = address
            vol.status = status
            vol.save()
            messages.success(request, f'স্বেচ্ছাসেবক "{full_name}" তথ্য আপডেট করা হয়েছে!')
        else:
            Volunteer.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                status=status
            )
            messages.success(request, f'নতুন স্বেচ্ছাসেবক "{full_name}" সফলভাবে যুক্ত করা হয়েছে!')
    return redirect('/dashboard/?tab=volunteers-section')

@staff_member_required
def delete_volunteer(request, pk):
    """Delete a Volunteer"""
    vol = get_object_or_404(Volunteer, pk=pk)
    name = vol.full_name
    vol.delete()
    messages.success(request, f'স্বেচ্ছাসেবক "{name}" তথ্য মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=volunteers-section')

@staff_member_required
def save_team_member(request):
    """Create or update a Team Member"""
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        name = request.POST.get('name')
        role = request.POST.get('role')
        bio = request.POST.get('bio', '')
        order = request.POST.get('order', 0)

        if member_id:
            mem = get_object_or_404(TeamMember, pk=member_id)
            mem.name = name
            mem.role = role
            mem.bio = bio
            mem.order = order
            if 'image' in request.FILES:
                mem.image = request.FILES['image']
            mem.save()
            messages.success(request, f'টিম মেম্বার "{name}" তথ্য আপডেট করা হয়েছে!')
        else:
            TeamMember.objects.create(
                name=name,
                role=role,
                bio=bio,
                order=order,
                image=request.FILES.get('image')
            )
            messages.success(request, f'নতুন টিম মেম্বার "{name}" যুক্ত করা হয়েছে!')
    return redirect('/dashboard/?tab=volunteers-section')

@staff_member_required
def delete_team_member(request, pk):
    """Delete a Team Member"""
    mem = get_object_or_404(TeamMember, pk=pk)
    name = mem.name
    mem.delete()
    messages.success(request, f'টিম মেম্বার "{name}" মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=volunteers-section')


@staff_member_required
def update_hero_section(request):
    """Handle POST request for editing Top bar & Hero Section"""
    if request.method == 'POST':
        setting, _ = SiteSetting.objects.get_or_create(pk=1)
        setting.hero_badge = request.POST.get('hero_badge', setting.hero_badge)
        setting.hero_title = request.POST.get('hero_title', setting.hero_title)
        setting.hero_subtitle = request.POST.get('hero_subtitle', setting.hero_subtitle)
        setting.contact_phone = request.POST.get('contact_phone', setting.contact_phone)
        setting.contact_email = request.POST.get('contact_email', setting.contact_email)
        setting.facebook_url = request.POST.get('facebook_url', setting.facebook_url)
        setting.youtube_url = request.POST.get('youtube_url', setting.youtube_url)
        setting.whatsapp_number = request.POST.get('whatsapp_number', setting.whatsapp_number)

        if 'logo' in request.FILES:
            setting.logo = request.FILES['logo']
        if 'hero_image' in request.FILES:
            setting.hero_image = request.FILES['hero_image']

        setting.save()
        messages.success(request, 'হেডার ও হিরো সেকশন সফলভাবে আপডেট করা হয়েছে!')
    return redirect('/dashboard/?tab=home-section')

@staff_member_required
def update_about_section(request):
    """Handle POST request for editing 'আমাদের সম্পর্কে' Section"""
    if request.method == 'POST':
        setting, _ = SiteSetting.objects.get_or_create(pk=1)
        setting.about_heading = request.POST.get('about_heading', setting.about_heading)
        setting.about_text = request.POST.get('about_text', setting.about_text)
        setting.save()

        # Handle Featured Main Image
        if 'featured_image' in request.FILES:
            AboutImage.objects.filter(is_featured=True).delete()
            AboutImage.objects.create(
                image=request.FILES['featured_image'],
                caption='Featured Main Image',
                is_featured=True
            )

        # Handle Multiple Sub Image Grid Uploads
        sub_images = request.FILES.getlist('sub_images')
        for img in sub_images:
            AboutImage.objects.create(
                image=img,
                caption='Sub Grid Image',
                is_featured=False
            )

        messages.success(request, 'আমাদের সম্পর্কে সেকশন সফলভাবে আপডেট করা হয়েছে!')
    return redirect('/dashboard/?tab=home-section')

@staff_member_required
def delete_about_image(request, pk):
    """Delete a specific sub-image from the About Grid"""
    img = get_object_or_404(AboutImage, pk=pk)
    img.delete()
    messages.success(request, 'ছবিটি সফলভাবে মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=home-section')


@staff_member_required
def update_stat_counters(request):
    """Handle POST request for updating 5 Stat Counters"""
    if request.method == 'POST':
        stat_ids = request.POST.getlist('stat_id')
        for sid in stat_ids:
            try:
                stat = StatCounter.objects.get(pk=sid)
                stat.title = request.POST.get(f'title_{sid}', stat.title)
                stat.value = request.POST.get(f'value_{sid}', stat.value)
                stat.icon_class = request.POST.get(f'icon_{sid}', stat.icon_class)
                stat.badge_color = request.POST.get(f'color_{sid}', stat.badge_color)
                stat.save()
            except StatCounter.DoesNotExist:
                pass
        messages.success(request, 'হোমপেজ কাউন্টার কার্ডসমূহ আপডেট করা হয়েছে!')
    return redirect('/dashboard/?tab=home-section')

@staff_member_required
def save_program(request):
    """Create or update a Program"""
    if request.method == 'POST':
        program_id = request.POST.get('program_id')
        title = request.POST.get('title')
        short_desc = request.POST.get('short_description', '')
        desc = request.POST.get('description', '')
        icon = request.POST.get('icon_class', 'fas fa-heart')
        color = request.POST.get('badge_color', 'success')
        status = request.POST.get('status', 'ongoing')

        if program_id:
            prog = get_object_or_404(Program, pk=program_id)
            prog.title = title
            prog.short_description = short_desc
            prog.description = desc
            prog.icon_class = icon
            prog.badge_color = color
            prog.status = status
            if 'image' in request.FILES:
                prog.image = request.FILES['image']
            prog.save()
            messages.success(request, f'প্রোগ্রাম "{title}" আপডেট করা হয়েছে!')
        else:
            prog = Program.objects.create(
                title=title,
                short_description=short_desc,
                description=desc,
                icon_class=icon,
                badge_color=color,
                status=status,
                image=request.FILES.get('image')
            )
            messages.success(request, f'নতুন প্রোগ্রাম "{title}" তৈরি করা হয়েছে!')
    return redirect('/dashboard/?tab=programs-section')

@staff_member_required
def delete_program(request, pk):
    """Delete a Program"""
    prog = get_object_or_404(Program, pk=pk)
    title = prog.title
    prog.delete()
    messages.success(request, f'প্রোগ্রাম "{title}" মুছে ফেলা হয়েছে!')
    return redirect('/dashboard/?tab=programs-section')

@staff_member_required
def save_news(request):
    """Create or update a News Article"""
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        title = request.POST.get('title')
        content = request.POST.get('content')

        if article_id:
            art = get_object_or_404(Article, pk=article_id)
            art.title = title
            art.content = content
            if 'image' in request.FILES:
                art.image = request.FILES['image']
            art.save()
            messages.success(request, f'সংবাদ "{title}" আপডেট করা হয়েছে!')
        else:
            Article.objects.create(
                title=title,
                content=content,
                image=request.FILES.get('image'),
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
    """Update Bank Account details and QR Code"""
    if request.method == 'POST':
        bank_name = request.POST.get('bank_name')
        account_name = request.POST.get('account_name')
        account_number = request.POST.get('account_number')
        swift_code = request.POST.get('swift_code')

        bank, _ = Bank.objects.get_or_create(pk=1)
        bank.bank_name = bank_name
        bank.account_name = account_name
        bank.account_number = account_number
        bank.swift_code = swift_code
        bank.save()

        if 'qr_image' in request.FILES:
            method, _ = DonationMethod.objects.get_or_create(name='bKash')
            QRCode.objects.all().delete()
            QRCode.objects.create(
                method=method,
                image=request.FILES['qr_image'],
                details='bKash Merchant / Personal'
            )

        messages.success(request, 'ব্যাংক একাউন্ট ও অনুদান তথ্য আপডেট করা হয়েছে!')
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

        if donor_id:
            donor = get_object_or_404(BloodDonor, pk=donor_id)
            donor.full_name = name
            donor.blood_group = group
            donor.phone = phone
            donor.location = location
            donor.save()
            messages.success(request, f'রক্তদাতা "{name}" তথ্য আপডেট করা হয়েছে!')
        else:
            BloodDonor.objects.create(
                full_name=name,
                blood_group=group,
                phone=phone,
                location=location,
                is_available=True
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
def save_gallery_photo(request):
    """Upload new gallery photo"""
    if request.method == 'POST':
        caption = request.POST.get('caption', '')
        if 'image' in request.FILES:
            album, _ = Album.objects.get_or_create(title='Main Gallery')
            Photo.objects.create(
                album=album,
                image=request.FILES['image'],
                caption=caption
            )
            messages.success(request, 'গ্যালারিতে নতুন ছবি আপলোড করা হয়েছে!')
        else:
            messages.error(request, 'দয়া করে ছবি নির্বাচন করুন।')
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
        messages.success(request, 'ফুটার ও যোগাযোগ তথ্য আপডেট করা হয়েছে!')
    return redirect('/dashboard/?tab=home-section')
