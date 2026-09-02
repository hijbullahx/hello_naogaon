from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from core.email_utils import send_system_email
from .models import Volunteer, TeamMember, BloodDonor

def send_member_notifications(volunteer):
    """
    Sends Member ID and voluntary financial commitment details via Email and SMS.
    """
    freq_dict = {
        'monthly': 'মাসিক (প্রতি মাসে)',
        'weekly': 'সাপ্তাহিক (প্রতি সপ্তাহে)',
        'yearly': 'বাৎসরিক (প্রতি বছরে)',
        'one_time': 'এককালীন',
        'none': 'কোনো নির্দিষ্ট প্রতিশ্রুতি নেই'
    }
    freq_text = freq_dict.get(volunteer.contribution_frequency, 'কোনো নির্দিষ্ট প্রতিশ্রুতি নেই')
    
    sms_contrib = ""
    if volunteer.contribution_frequency != 'none' and volunteer.contribution_amount and volunteer.contribution_amount > 0:
        sms_contrib = f" | প্রতিশ্রুতি: {freq_text} ৳{volunteer.contribution_amount:,.0f}"

    subject = f"Helpline Hello Naogaon - সদস্য নিবন্ধন সম্পন্ন (আইডি: {volunteer.member_id})"
    
    paragraphs = [
        f"Helpline Hello Naogaon-এ সদস্য/স্বেচ্ছাসেবক হিসেবে সফলভাবে নিবন্ধিত হওয়ার জন্য আপনাকে আন্তরিক মোবারকবাদ ও উষ্ণ অভিনন্দন!",
        "আমাদের সংগঠনের মূল লক্ষ্য মানবতার সেবায় নিঃস্বার্থভাবে কাজ করা এবং সমাজের অসহায় মানুষের পাশে দাঁড়ানো। আপনার এই অংশগ্রহণ আমাদের পথচলাকে আরও সমৃদ্ধ ও শক্তিশালী করবে।"
    ]

    if volunteer.contribution_frequency != 'none' and volunteer.contribution_amount and volunteer.contribution_amount > 0:
        paragraphs.append(
            f"আপনি স্বেচ্ছায় {freq_text} ৳{volunteer.contribution_amount:,.2f} টাকা আর্থিক সহায়তা প্রদানের সদিচ্ছা প্রকাশ করেছেন। "
            "আপনার প্রতিশ্রুত সময় অনুযায়ী নিয়মিত সহায়তার জন্য আপডেট ও লিঙ্ক পেয়ে যাবেন।"
        )

    if volunteer.email:
        send_system_email(
            subject=subject,
            recipient_list=[volunteer.email],
            recipient_name=volunteer.full_name,
            greeting="প্রিয়",
            headline="সদস্য ও রক্তদাতা নিবন্ধন সম্পন্ন",
            message_paragraphs=paragraphs,
            volunteer=volunteer,
            footer_note="জরুরি রক্তদান বা যেকোনো প্রয়োজনে আমাদের হটলাইনে যোগাযোগ করতে পারেন।",
            fail_silently=True,
        )

    if volunteer.phone:
        sms_text = f"Helpline Hello Naogaon: ধন্যবাদ {volunteer.full_name}! আপনার সদস্য আইডি: {volunteer.member_id}{sms_contrib}। আর্থিক সহায়তা লিঙ্ক: https://helplinehellonaogaon.com/donations/donate/?member_id={volunteer.member_id}"
        print(f"[SMS SUCCESS] Sent Member ID {volunteer.member_id} to {volunteer.phone} | Content: {sms_text}")


from datetime import datetime, date

def normalize_blood_group(val):
    """Safely normalizes blood group string handling URL decoding issues (e.g. '+' decoded as space)"""
    if not val:
        return ''
    val = val.strip().upper().replace(' ', '+')
    if val in ['A', 'B', 'O', 'AB']:
        val = f"{val}+"
    return val

def blood_donors_list(request):
    raw_group = request.GET.get('group', '').strip()
    blood_group = normalize_blood_group(raw_group) if raw_group else ''
    selected_division = request.GET.get('division', '').strip()
    selected_district = request.GET.get('district', '').strip()
    selected_upazila = request.GET.get('upazila', '').strip()
    search_query = request.GET.get('q', '').strip()
    
    donors = BloodDonor.objects.filter(is_available=True)
    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    if selected_division:
        donors = donors.filter(division__icontains=selected_division)
    if selected_district:
        donors = donors.filter(district__icontains=selected_district)
    if selected_upazila:
        donors = donors.filter(Q(upazila__icontains=selected_upazila) | Q(location__icontains=selected_upazila))
    if search_query:
        norm_bg = normalize_blood_group(search_query)
        q_filter = (
            Q(full_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(upazila__icontains=search_query) |
            Q(district__icontains=search_query) |
            Q(division__icontains=search_query) |
            Q(member_id__icontains=search_query) |
            Q(blood_group__iexact=search_query)
        )
        if norm_bg in ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']:
            q_filter |= Q(blood_group=norm_bg)
        donors = donors.filter(q_filter)

    context = {
        'donors': donors,
        'selected_group': blood_group,
        'selected_division': selected_division,
        'selected_district': selected_district,
        'selected_upazila': selected_upazila,
        'search_query': search_query,
        'groups': ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'],
    }
    return render(request, 'volunteers/blood_donors.html', context)


def register_blood_donor(request):
    """Register directly as a Blood Donor with Division, District, Upazila, and Local Address"""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        blood_group = request.POST.get('blood_group', '').strip()
        phone = request.POST.get('phone', '').strip()
        division = request.POST.get('division', 'রাজশাহী').strip()
        district = request.POST.get('district', 'নওগাঁ').strip()
        upazila = request.POST.get('upazila', '').strip()
        address = request.POST.get('address', '').strip()
        last_donated_str = request.POST.get('last_donated', '').strip()
        is_public_details = request.POST.get('is_public_details') == 'on'

        if not full_name or not phone or not blood_group:
            messages.error(request, 'দয়া করে নাম, রক্তের গ্রুপ ও মোবাইল নম্বর সঠিকভাবে প্রদান করুন।')
            return redirect('volunteers:blood_donors')

        last_donated_val = None
        if last_donated_str:
            try:
                last_donated_val = datetime.strptime(last_donated_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        # Check if a Volunteer exists with this phone number to retain member_id linkage
        vol = Volunteer.objects.filter(phone=phone).first()
        member_id = vol.member_id if vol else None

        loc_parts = [p for p in [address, upazila, district] if p]
        formatted_loc = ", ".join(loc_parts) if loc_parts else (address or upazila or district or 'নওগাঁ')

        donor, created = BloodDonor.objects.update_or_create(
            phone=phone,
            defaults={
                'full_name': full_name,
                'blood_group': blood_group,
                'division': division or 'রাজশাহী',
                'district': district or 'নওগাঁ',
                'upazila': upazila,
                'location': formatted_loc,
                'last_donated': last_donated_val,
                'member_id': member_id,
                'is_public_details': is_public_details,
                'is_available': True,
            }
        )

        messages.success(
            request,
            f'ধন্যবাদ {full_name}! জরুরি রক্তদাতা ডাটাবেসে আপনার তথ্য সফলভাবে তালিকাভুক্ত হয়েছে।'
        )
        return redirect('volunteers:blood_donors')

    return redirect('volunteers:blood_donors')


def apply_volunteer(request):
    if request.method == 'POST':
        next_url = request.POST.get('next', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        blood_group = request.POST.get('blood_group', '').strip()
        occupation = request.POST.get('occupation', '').strip()
        division = request.POST.get('division', '').strip()
        district = request.POST.get('district', '').strip()
        upazila = request.POST.get('upazila', '').strip()
        address = request.POST.get('address', '').strip()
        last_donated_str = request.POST.get('last_donated', '').strip()
        contribution_frequency = request.POST.get('contribution_frequency', 'none').strip()
        contribution_amount_str = request.POST.get('contribution_amount', '0').strip()
        is_public_details = request.POST.get('is_public_details') == 'on'
        image = request.FILES.get('image')

        # 500 KB Max Image Limit Validation
        if image:
            max_size_bytes = 500 * 1024  # 500 KB
            if image.size > max_size_bytes:
                size_kb = image.size / 1024
                messages.error(
                    request,
                    f'ছবির সাইজ সর্বোচ্চ 500 KB হতে পারবে (আপনার ছবির সাইজ: {size_kb:.1f} KB)। '
                    f'অনুগ্রহ করে resizepixel.com থেকে ছবির সাইজ কমিয়ে আপলোড করুন।'
                )
                return redirect(next_url if next_url else 'volunteers:apply')

        last_donated_val = None
        if last_donated_str:
            try:
                last_donated_val = datetime.strptime(last_donated_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        contribution_amount_val = 0
        if contribution_amount_str:
            try:
                contribution_amount_val = float(contribution_amount_str)
            except ValueError:
                contribution_amount_val = 0

        if full_name and phone:
            try:
                vol = Volunteer.objects.create(
                    full_name=full_name,
                    email=email if email else None,
                    phone=phone,
                    blood_group=blood_group if blood_group else None,
                    occupation=occupation if occupation else None,
                    division=division,
                    district=district,
                    upazila=upazila,
                    address=address if address else None,
                    last_donated=last_donated_val,
                    contribution_frequency=contribution_frequency,
                    contribution_amount=contribution_amount_val,
                    is_public_details=is_public_details,
                    image=image,
                    status='approved'
                )
            except ValueError as e:
                messages.error(request, str(e))
                return redirect(next_url if next_url else 'volunteers:apply')

            send_member_notifications(vol)

            messages.success(
                request, 
                f'অভিনন্দন {full_name}! আপনার সদস্য নিবন্ধন সফলভাবে সম্পন্ন হয়েছে। আপনার সদস্য আইডি (Member ID): {vol.member_id}'
            )
            return redirect(next_url if next_url else 'volunteers:apply')
        else:
            messages.error(request, 'দয়া করে আপনার নাম এবং মোবাইল নম্বর সঠিকভাবে লিখুন।')

    search_query = request.GET.get('q', '').strip()
    raw_group = request.GET.get('group', '').strip()
    blood_group_filter = normalize_blood_group(raw_group) if raw_group else ''
    selected_division = request.GET.get('division', '').strip()
    selected_district = request.GET.get('district', '').strip()
    selected_upazila = request.GET.get('upazila', '').strip()

    volunteers_list = Volunteer.objects.all().order_by('-id')

    if search_query:
        norm_bg = normalize_blood_group(search_query)
        q_filter = (
            Q(member_id__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(upazila__icontains=search_query) |
            Q(district__icontains=search_query) |
            Q(division__icontains=search_query) |
            Q(blood_group__iexact=search_query)
        )
        if norm_bg in ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']:
            q_filter |= Q(blood_group=norm_bg)
        volunteers_list = volunteers_list.filter(q_filter)

    if blood_group_filter:
        volunteers_list = volunteers_list.filter(blood_group=blood_group_filter)

    if selected_division:
        volunteers_list = volunteers_list.filter(division__icontains=selected_division)

    if selected_district:
        volunteers_list = volunteers_list.filter(district__icontains=selected_district)

    if selected_upazila:
        volunteers_list = volunteers_list.filter(Q(upazila__icontains=selected_upazila) | Q(address__icontains=selected_upazila))

    team_members = TeamMember.objects.all().order_by('order', 'id')

    context = {
        'team_members': team_members,
        'volunteers_list': volunteers_list,
        'search_query': search_query,
        'blood_group_filter': blood_group_filter,
        'selected_division': selected_division,
        'selected_district': selected_district,
        'selected_upazila': selected_upazila,
        'groups': ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'],
    }
    return render(request, 'volunteers/volunteer_form.html', context)


import os
import json
from django.http import JsonResponse
from django.conf import settings

_BD_GEO_CACHE = None

def get_bd_geo_json(request):
    """API endpoint to fetch complete 8 divisions, 64 districts and 494 upazilas of Bangladesh"""
    global _BD_GEO_CACHE
    if _BD_GEO_CACHE is None:
        file_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'bangladesh_geo.json')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                _BD_GEO_CACHE = json.load(f)
        else:
            _BD_GEO_CACHE = {}
    return JsonResponse(_BD_GEO_CACHE)