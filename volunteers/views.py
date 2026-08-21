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


def blood_donors_list(request):
    blood_group = request.GET.get('group', '')
    donors = BloodDonor.objects.filter(is_available=True)
    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    context = {
        'donors': donors,
        'selected_group': blood_group,
        'groups': ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    }
    return render(request, 'volunteers/blood_donors.html', context)


def apply_volunteer(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        blood_group = request.POST.get('blood_group', '').strip()
        occupation = request.POST.get('occupation', '').strip()
        address = request.POST.get('address', '').strip()
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

        if full_name and phone:
            vol = Volunteer.objects.create(
                full_name=full_name,
                email=email if email else None,
                phone=phone,
                blood_group=blood_group if blood_group else None,
                occupation=occupation if occupation else None,
                address=address if address else None,
                is_public_details=is_public_details,
                image=image,
                status='approved'
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