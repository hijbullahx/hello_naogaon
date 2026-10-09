from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from core.email_utils import send_system_email, get_admin_notification_emails
from core.sms_utils import send_sms, get_admin_phone
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
        sms_contrib = f" | চাঁদা: ৳{volunteer.contribution_amount:,.0f}"

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

    admin_phone = get_admin_phone()
    if volunteer.phone:
        # Compact 2-segment SMS template (<= 134 chars UCS-2)
        sms_text = f"[Hello Naogaon] {volunteer.full_name}, সদস্য নিবন্ধন সম্পন্ন। আইডি: {volunteer.member_id}{sms_contrib}। হটলাইন: {admin_phone}"
        try:
            send_sms(volunteer.phone, sms_text)
        except Exception as e:
            print(f"[VOLUNTEER SMS ERROR] {e}")

    # Send Notification to Admin (Email & SMS)
    try:
        admin_emails = get_admin_notification_emails()
        if admin_emails:
            admin_subject = f"👤 নতুন সদস্য নিবন্ধন — {volunteer.full_name} ({volunteer.member_id})"
            send_system_email(
                subject=admin_subject,
                recipient_list=admin_emails,
                headline="নতুন সদস্য ও রক্তদাতা নিবন্ধন",
                greeting="শ্রদ্ধেয় অ্যাডমিন,",
                message_paragraphs=[
                    f"ওয়েবসাইটে একজন নতুন সদস্য সফলভাবে নিবন্ধন সম্পন্ন করেছেন। সদস্য আইডি: #{volunteer.member_id}।"
                ],
                volunteer=volunteer,
                footer_note="সদস্যের তথ্যাদি এডমিন ড্যাশবোর্ড থেকে পরিচালনা করতে পারবেন।",
                fail_silently=True,
            )
    except Exception as e:
        print(f"[ADMIN VOLUNTEER EMAIL NOTIFY ERROR] {e}")

    # Compact 1-segment Admin SIM alert (<= 70 chars UCS-2)
    if admin_phone:
        try:
            admin_sms = f"[Hello Naogaon] নতুন সদস্য: {volunteer.full_name} (আইডি: {volunteer.member_id})।"
            send_sms(admin_phone, admin_sms, is_alert=True)
        except Exception:
            pass


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

        # 500 KB Max Image Limit Validation & PIL Integrity Check
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

            try:
                from PIL import Image
                image.seek(0)
                with Image.open(image) as img:
                    img.verify()
                image.seek(0)
            except Exception:
                try:
                    image.seek(0)
                except Exception:
                    pass
                messages.error(request, 'ছবির ফাইলটি সঠিক ফরম্যাটে নেই বা ক্ষতিগ্রস্ত। অনুগ্রহ করে একটি বৈধ JPG, PNG বা WebP ছবি দিন।')
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

        payment_mode = request.POST.get('payment_mode', 'gateway').strip()
        manual_channel = request.POST.get('manual_channel', 'bKash').strip()
        sender_account = request.POST.get('sender_account', '').strip()
        trx_id = request.POST.get('trx_id', '').strip()

        if payment_mode == 'manual' and not sender_account:
            messages.error(request, 'ম্যানুয়াল পেমেন্টের ক্ষেত্রে প্রেরকের মোবাইল নম্বর / অ্যাকাউন্ট নম্বর প্রদান করা আবশ্যক।')
            return redirect(next_url if next_url else 'volunteers:apply')

        if full_name and phone:
            import random
            from datetime import timedelta
            from django.utils import timezone
            from django.db import transaction
            from core.sms_utils import clean_bd_phone_number
            from donations.models import ProgramDonation
            from donations.gateway import initiate_active_gateway_session

            clean_phone = clean_bd_phone_number(phone)
            if not clean_phone or len(clean_phone) != 11 or not clean_phone.startswith('01'):
                messages.error(request, 'সঠিক ১১ ডিজিটের বাংলাদেশি মোবাইল নম্বর প্রদান করুন।')
                return redirect(next_url if next_url else 'volunteers:apply')

            # Duplicate / rapid double-click race condition protection (within 60 seconds)
            # 1. Atomic cache lock to prevent concurrent multi-worker race conditions
            from django.core.cache import cache
            lock_key = f"lock_apply_vol_{clean_phone}"
            if not cache.add(lock_key, '1', timeout=60):
                messages.info(request, f'ধন্যবাদ {full_name}! আপনার আবেদনটি ইতিমধ্যে সিস্টেমে জমা হচ্ছে। অনুগ্রহ করে অপেক্ষা করুন।')
                return redirect(next_url if next_url else 'volunteers:apply')

            # 2. Database debounce check for recent submission
            recent_cutoff = timezone.now() - timedelta(seconds=60)
            recent_vol = Volunteer.objects.filter(phone=clean_phone, application_date__gte=recent_cutoff).first()
            if recent_vol:
                messages.info(request, f'ধন্যবাদ {full_name}! আপনার আবেদনটি ইতিমধ্যে সিস্টেমে জমা হয়েছে। অনুগ্রহ করে অপেক্ষা করুন।')
                return redirect(next_url if next_url else 'volunteers:apply')

            existing_approved = Volunteer.objects.filter(phone=clean_phone, status='approved').first()
            if existing_approved:
                messages.warning(request, f'এই মোবাইল নম্বরটি দিয়ে ইতিমধ্যে সদস্য নিবন্ধন রয়েছে (আইডি: {existing_approved.member_id})।')
                return redirect(next_url if next_url else 'volunteers:apply')

            if payment_mode == 'manual':
                try:
                    with transaction.atomic():
                        vol = Volunteer.objects.create(
                            full_name=full_name,
                            email=email if email else None,
                            phone=clean_phone,
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
                            registration_fee=100.00,
                            payment_status='pending',
                            payment_method=f"Manual ({manual_channel})",
                            sender_account=sender_account,
                            trx_id=trx_id,
                            status='pending'
                        )

                        # Create corresponding ProgramDonation record for tracking in financial ledger
                        ProgramDonation.objects.create(
                            donation_type='volunteer_registration',
                            donor_name=full_name,
                            donor_phone=clean_phone,
                            donor_email=email or '',
                            amount=100.00,
                            payment_method=f"Manual ({manual_channel})",
                            sender_account=sender_account,
                            trx_id=trx_id,
                            status='pending',
                            membership_id=f"NEW_VOL_{vol.id}",
                            note=f"নতুন সদস্য নিবন্ধন ফি (ম্যানুয়াল যাচাই বাকি) - {full_name} ({clean_phone})"
                        )
                except Exception as e:
                    cache.delete(lock_key)
                    messages.error(request, f'আবেদন সংরক্ষণ করতে সমস্যা হয়েছে: {str(e)}')
                    return redirect(next_url if next_url else 'volunteers:apply')

                # Send Alert to Admin for Manual Verification (compact 1-segment template <= 70 chars)
                admin_phone = get_admin_phone()
                if admin_phone:
                    try:
                        admin_sms = f"[Hello Naogaon] নতুন সদস্য আবেদন: {full_name} ({manual_channel})। যাচাইয়ের জন্য এডমিন প্যানেল দেখুন।"
                        send_sms(admin_phone, admin_sms, is_alert=True)
                    except Exception:
                        pass

                messages.success(
                    request, 
                    f'ধন্যবাদ {full_name}! আপনার সদস্য রেজিস্ট্রেশন আবেদন ও ১০০ টাকা ম্যানুয়াল পেমেন্ট তথ্য সফলভাবে জমা হয়েছে। অ্যাডমিন প্যানেল থেকে তথ্য যাচাই ও অনুমোদনের পর আপনার সদস্য আইডি প্রস্তুত হবে এবং আপনার মোবাইল ও ইমেইলে বার্তা পাঠানো হবে।'
                )
                return redirect(next_url if next_url else 'volunteers:apply')

            else:
                # Gateway / Automated Payment
                gen_tran_id = f"REG_{int(datetime.now().timestamp())}_{random.randint(1000, 9999)}"
                try:
                    with transaction.atomic():
                        vol = Volunteer.objects.create(
                            full_name=full_name,
                            email=email if email else None,
                            phone=clean_phone,
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
                            registration_fee=100.00,
                            payment_status='unpaid',
                            payment_method='Online Gateway',
                            tran_id=gen_tran_id,
                            status='pending'
                        )

                        # Create initiated ProgramDonation for gateway checkout
                        donation = ProgramDonation.objects.create(
                            donation_type='volunteer_registration',
                            donor_name=full_name,
                            donor_phone=clean_phone,
                            donor_email=email or '',
                            amount=100.00,
                            payment_method='Online Gateway',
                            tran_id=gen_tran_id,
                            status='initiated',
                            membership_id=f"NEW_VOL_{vol.id}",
                            note=f"নতুন সদস্য নিবন্ধন ফি (অনলাইন গেটওয়ে) - {full_name} ({clean_phone})"
                        )
                except Exception as e:
                    cache.delete(lock_key)
                    messages.error(request, f'আবেদন সংরক্ষণ করতে সমস্যা হয়েছে: {str(e)}')
                    return redirect(next_url if next_url else 'volunteers:apply')

                session_res = initiate_active_gateway_session(request, donation)
                if session_res.get('success') and session_res.get('payment_url'):
                    return redirect(session_res['payment_url'])
                else:
                    return redirect('donations:gateway_checkout', tran_id=donation.tran_id)
        else:
            messages.error(request, 'দয়া করে আপনার নাম এবং মোবাইল নম্বর সঠিকভাবে লিখুন।')

    search_query = request.GET.get('q', '').strip()
    raw_group = request.GET.get('group', '').strip()
    blood_group_filter = normalize_blood_group(raw_group) if raw_group else ''
    selected_division = request.GET.get('division', '').strip()
    selected_district = request.GET.get('district', '').strip()
    selected_upazila = request.GET.get('upazila', '').strip()

    volunteers_list = Volunteer.objects.filter(status='approved').order_by('-id')

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


def team_invite_register(request, token):
    """
    Public registration page accessed via a single-use secret token.
    Pre-fills and locks the designation (effective_role).
    Upon successful registration, saves the TeamMember (without auth user account),
    sends welcome SMS & email, and marks the invitation token as used so it cannot be used again.
    """
    from .models import TeamInvitation, TeamMember
    from django.utils import timezone

    invitation = TeamInvitation.objects.filter(token=token).first()
    if not invitation:
        return render(request, 'volunteers/team_invite_status.html', {
            'status': 'invalid',
            'title': 'অবৈধ বা অকার্যকর লিংক',
            'message': 'দুঃখিত! এই আমন্ত্রণ লিংকটি খুঁজে পাওয়া যায়নি বা এটি ভুল। সঠিক লিংকের জন্য অনুগ্রহ করে প্রধান অ্যাডমিনের সাথে যোগাযোগ করুন।'
        }, status=404)

    if invitation.is_used:
        registered_name = invitation.registered_member.name if invitation.registered_member else 'একজন সদস্য'
        return render(request, 'volunteers/team_invite_status.html', {
            'status': 'used',
            'title': 'লিংকটি ইতিমধ্যে ব্যবহৃত হয়ে গেছে',
            'message': f'এই ওয়ান-টাইম আমন্ত্রণ লিংকটি ব্যবহার করে ইতিমধ্যে {registered_name} টিম মেম্বার হিসেবে নিবন্ধন সম্পন্ন করেছেন। একটি লিংক শুধুমাত্র একবারই ব্যবহারযোগ্য।',
            'invitation': invitation
        })

    if request.method == 'POST':
        # Re-check in case of duplicate rapid submission
        invitation.refresh_from_db()
        if invitation.is_used:
            messages.error(request, 'দুঃখিত! এই লিংকটি ইতিমধ্যে অন্য একজন ব্যবহার করে ফেলেছেন।')
            return redirect('volunteers:team_invite_register', token=token)

        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        blood_group = request.POST.get('blood_group', '').strip()
        last_donated_str = request.POST.get('last_donated', '').strip()
        division = request.POST.get('division', 'রাজশাহী').strip()
        district = request.POST.get('district', 'নওগাঁ').strip()
        upazila = request.POST.get('upazila', '').strip()
        address = request.POST.get('address', '').strip()
        bio = request.POST.get('bio', '').strip()
        is_public_details = request.POST.get('is_public_details') == 'on'
        image_file = request.FILES.get('image')

        if not name or not phone:
            messages.error(request, 'অনুগ্রহ করে আপনার পূর্ণ নাম এবং মোবাইল নম্বর সঠিকভাবে প্রদান করুন।')
            return render(request, 'volunteers/team_invite_register.html', {
                'invitation': invitation,
                'role': invitation.effective_role
            })

        # Image validation (max 500 KB)
        if image_file and image_file.size > 500 * 1024:
            size_kb = image_file.size / 1024
            messages.error(request, f'ছবির সাইজ সর্বোচ্চ 500 KB হতে পারবে (আপনার ছবির সাইজ: {size_kb:.1f} KB)। অনুগ্রহ করে সাইজ কমিয়ে আপলোড করুন।')
            return render(request, 'volunteers/team_invite_register.html', {
                'invitation': invitation,
                'role': invitation.effective_role
            })

        last_donated = None
        if last_donated_str:
            try:
                from datetime import datetime
                last_donated = datetime.strptime(last_donated_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                last_donated = None

        try:
            tm = TeamMember(
                name=name,
                role=invitation.role,
                custom_role=invitation.custom_role,
                phone=phone,
                email=email or None,
                blood_group=blood_group or None,
                last_donated=last_donated,
                is_public_details=is_public_details,
                division=division or 'রাজশাহী',
                district=district or 'নওগাঁ',
                upazila=upazila,
                address=address,
                bio=bio,
                user=None  # Explicitly no login user account needed
            )
            if image_file:
                tm.image = image_file
            tm.save()

            # Mark invitation as permanently used
            invitation.is_used = True
            invitation.used_at = timezone.now()
            invitation.registered_member = tm
            invitation.save()

            # 1. Send SMS to newly registered Team Member (compact 2-segment template)
            if tm.phone:
                sms_text = f"[Hello Naogaon] {tm.name}, টিম সদস্য নিবন্ধন সম্পন্ন। পদবি: {tm.effective_role}, আইডি: {tm.member_id}। ধন্যবাদ।"
                try:
                    send_sms(tm.phone, sms_text)
                except Exception as ex:
                    print(f"[TEAM MEMBER SMS ERROR] {ex}")

            # 2. Send Email to Member (if provided)
            if tm.email:
                try:
                    send_system_email(
                        subject=f"Helpline Hello Naogaon - টিম মেম্বার নিবন্ধন সম্পন্ন (আইডি: {tm.member_id})",
                        recipient_list=[tm.email],
                        recipient_name=tm.name,
                        greeting="শ্রদ্ধেয়",
                        headline="টিম মেম্বার হিসেবে স্বাগতম",
                        message_paragraphs=[
                            f"হেল্পলাইন হ্যালো নওগাঁর পরিচালনা পর্ষদ ও কার্যকরী টিমে '{tm.effective_role}' হিসেবে সফলভাবে নিবন্ধিত হওয়ায় আপনাকে আন্তরিক মোবারকবাদ ও উষ্ণ অভিনন্দন!",
                            "মানবতার সেবায় আপনার আন্তরিক অংশগ্রহণ ও মূল্যবান পরামর্শ আমাদের সমাজসেবামূলক পথচলাকে আরও সমৃদ্ধ ও বেগবান করবে।"
                        ],
                        details=[
                            {'label': 'সদস্যের নাম', 'value': tm.name},
                            {'label': 'নির্ধারিত পদবি', 'value': tm.effective_role},
                            {'label': 'সদস্য আইডি', 'value': tm.member_id},
                            {'label': 'মোবাইল নম্বর', 'value': tm.phone},
                        ],
                        footer_note="সংগঠনের ওয়েবসাইট ও টিম তালিকায় আপনার পরিচিতি প্রদর্শিত হবে।",
                        fail_silently=True
                    )
                except Exception as ex:
                    print(f"[TEAM MEMBER EMAIL ERROR] {ex}")

            return render(request, 'volunteers/team_invite_success.html', {
                'member': tm,
                'role': tm.effective_role,
            })

        except Exception as e:
            messages.error(request, f'নিবন্ধন সংরক্ষণে ত্রুটি দেখা দিয়েছে: {str(e)}')
            return render(request, 'volunteers/team_invite_register.html', {
                'invitation': invitation,
                'role': invitation.effective_role
            })

    return render(request, 'volunteers/team_invite_register.html', {
        'invitation': invitation,
        'role': invitation.effective_role
    })