from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from .models import Volunteer, TeamMember, BloodDonor

def send_member_notifications(volunteer):
    """
    Sends Member ID via Email (from info@helplinehellonaogaon.com) and SMS.
    If both email and phone are provided, sends both.
    """
    subject = f"Helpline Hello Naogaon - সদস্য নিবন্ধন সম্পন্ন (আইডি: {volunteer.member_id})"
    message_body = (
        f"প্রিয় {volunteer.full_name},\n\n"
        f"Helpline Hello Naogaon-এ সদস্য/স্বেচ্ছাসেবক হিসেবে সফলভাবে নিবন্ধিত হওয়ার জন্য ধন্যবাদ!\n\n"
        f"আপনার সদস্য বিবরণ:\n"
        f"----------------------\n"
        f"সদস্য আইডি (Member ID): {volunteer.member_id}\n"
        f"নাম: {volunteer.full_name}\n"
        f"মোবাইল নম্বর: {volunteer.phone}\n"
        f"রক্তের গ্রুপ: {volunteer.blood_group or 'N/A'}\n"
        f"পেশা: {volunteer.occupation or 'N/A'}\n\n"
        f"ধন্যবাদ,\nHelpline Hello Naogaon টিম"
    )

    if volunteer.email:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@helplinehellonaogaon.com') or 'info@helplinehellonaogaon.com'
        try:
            send_mail(
                subject,
                message_body,
                from_email,
                [volunteer.email],
                fail_silently=True,
            )
            print(f"[EMAIL SUCCESS] Sent Member ID {volunteer.member_id} to {volunteer.email} from {from_email}")
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")

    if volunteer.phone:
        sms_text = f"Helpline Hello Naogaon: ধন্যবাদ {volunteer.full_name}! আপনার সদস্য আইডি: {volunteer.member_id}"
        print(f"[SMS SUCCESS] Sent Member ID {volunteer.member_id} to {volunteer.phone} | Content: {sms_text}")


from datetime import datetime, date

def blood_donors_list(request):
    blood_group = request.GET.get('group', '').strip()
    search_query = request.GET.get('q', '').strip()
    
    donors = BloodDonor.objects.filter(is_available=True)
    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    if search_query:
        donors = donors.filter(
            Q(full_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(member_id__icontains=search_query) |
            Q(blood_group__icontains=search_query)
        )

    context = {
        'donors': donors,
        'selected_group': blood_group,
        'search_query': search_query,
        'groups': ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    }
    return render(request, 'volunteers/blood_donors.html', context)


def register_blood_donor(request):
    """Register directly as a Blood Donor with optional existing Member ID"""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        blood_group = request.POST.get('blood_group', '').strip()
        phone = request.POST.get('phone', '').strip()
        location = request.POST.get('location', '').strip()
        last_donated_str = request.POST.get('last_donated', '').strip()
        member_id = request.POST.get('member_id', '').strip()
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

        # If existing member_id provided, check if volunteer exists and link
        if member_id:
            vol = Volunteer.objects.filter(member_id=member_id).first()
            if vol:
                if not vol.blood_group:
                    vol.blood_group = blood_group
                if last_donated_val:
                    vol.last_donated = last_donated_val
                vol.save()

        donor, created = BloodDonor.objects.update_or_create(
            phone=phone,
            defaults={
                'full_name': full_name,
                'blood_group': blood_group,
                'location': location or 'নওগাঁ',
                'last_donated': last_donated_val,
                'member_id': member_id if member_id else None,
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
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        blood_group = request.POST.get('blood_group', '').strip()
        occupation = request.POST.get('occupation', '').strip()
        address = request.POST.get('address', '').strip()
        last_donated_str = request.POST.get('last_donated', '').strip()
        is_public_details = request.POST.get('is_public_details') == 'on'
        image = request.FILES.get('image')

        # 100 KB Max Image Limit Validation
        if image:
            max_size_bytes = 100 * 1024  # 100 KB
            if image.size > max_size_bytes:
                size_kb = image.size / 1024
                messages.error(
                    request,
                    f'ছবির সাইজ সর্বোচ্চ 100 KB হতে পারবে (আপনার ছবির সাইজ: {size_kb:.1f} KB)। '
                    f'অনুগ্রহ করে resizepixel.com থেকে ছবির সাইজ কমিয়ে আপলোড করুন।'
                )
                return redirect('volunteers:apply')

        last_donated_val = None
        if last_donated_str:
            try:
                last_donated_val = datetime.strptime(last_donated_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        if full_name and phone:
            try:
                vol = Volunteer.objects.create(
                    full_name=full_name,
                    email=email if email else None,
                    phone=phone,
                    blood_group=blood_group if blood_group else None,
                    occupation=occupation if occupation else None,
                    address=address if address else None,
                    last_donated=last_donated_val,
                    is_public_details=is_public_details,
                    image=image,
                    status='approved'
                )
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('volunteers:apply')

            # Auto-sync to Blood Donor Database if blood group is selected
            if blood_group:
                BloodDonor.objects.update_or_create(
                    phone=phone,
                    defaults={
                        'full_name': full_name,
                        'blood_group': blood_group,
                        'location': address if address else 'নওগাঁ',
                        'last_donated': last_donated_val,
                        'member_id': vol.member_id,
                        'is_public_details': is_public_details,
                        'is_available': True,
                    }
                )
            
            send_member_notifications(vol)

            messages.success(
                request, 
                f'অভিনন্দন {full_name}! আপনার সদস্য নিবন্ধন সফলভাবে সম্পন্ন হয়েছে। আপনার সদস্য আইডি (Member ID): {vol.member_id}'
            )
            return redirect('volunteers:apply')
        else:
            messages.error(request, 'দয়া করে আপনার নাম এবং মোবাইল নম্বর সঠিকভাবে লিখুন।')

    search_query = request.GET.get('q', '').strip()
    blood_group_filter = request.GET.get('group', '').strip()

    volunteers_list = Volunteer.objects.all().order_by('-id')

    if search_query:
        volunteers_list = volunteers_list.filter(
            Q(member_id__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(blood_group__icontains=search_query)
        )

    if blood_group_filter:
        volunteers_list = volunteers_list.filter(blood_group=blood_group_filter)

    team_members = TeamMember.objects.all()

    context = {
        'team_members': team_members,
        'volunteers_list': volunteers_list,
        'search_query': search_query,
        'blood_group_filter': blood_group_filter,
        'groups': ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    }
    return render(request, 'volunteers/volunteer_form.html', context)