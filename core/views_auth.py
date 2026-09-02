import random
import secrets
import logging
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse
from core.models import PasswordResetOTP
from core.email_utils import send_system_email, get_base_url

logger = logging.getLogger(__name__)
User = get_user_model()


def mask_email(email):
    """Masks email address for secure UI display (e.g. h****5@gmail.com)"""
    if not email or '@' not in email:
        return email or ''
    user_part, domain_part = email.split('@', 1)
    if len(user_part) <= 2:
        masked_user = user_part[0] + '*'
    else:
        masked_user = user_part[0] + '*' * (len(user_part) - 2) + user_part[-1]
    return f"{masked_user}@{domain_part}"


def generate_secure_otp():
    """Generates a 6-digit numeric OTP"""
    return f"{secrets.randbelow(900000) + 100000}"


@require_POST
def validate_otp_code_api(request):
    """
    Ajax endpoint to validate 6-digit OTP code before enabling new password inputs.
    """
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return JsonResponse({'valid': False, 'message': 'সেশন পাওয়া যায়নি। অনুগ্রহ করে শুরু থেকে চেষ্টা করুন।'})

    user = User.objects.filter(pk=user_id, is_active=True).first()
    if not user:
        return JsonResponse({'valid': False, 'message': 'ব্যবহারকারী অ্যাকাউন্ট খুঁজে পাওয়া যায়নি।'})

    otp_input = request.POST.get('otp_code', '').strip().replace(' ', '')
    if not otp_input or len(otp_input) != 6:
        return JsonResponse({'valid': False, 'message': 'অনুগ্রহ করে সঠিক ৬ ডিজিটের ওটিপি কোডটি লিখুন।'})

    otp_record = PasswordResetOTP.objects.filter(user=user, is_used=False).order_by('-created_at').first()
    if not otp_record:
        return JsonResponse({'valid': False, 'message': 'কোনো সক্রিয় ওটিপি পাওয়া যায়নি। নতুন ওটিপি চেয়ে চেষ্টা করুন।'})

    if timezone.now() > otp_record.expires_at:
        otp_record.is_used = True
        otp_record.save()
        return JsonResponse({'valid': False, 'message': 'ওটিপির মেয়াদ (১০ মিনিট) শেষ হয়ে গেছে। দয়া করে পুনরায় ওটিপি চান।'})

    if otp_record.attempts >= 5:
        otp_record.is_used = True
        otp_record.save()
        return JsonResponse({'valid': False, 'message': 'সর্বোচ্চ ৫ বার ভুল ওটিপি দেওয়ায় কোডটি বাতিল হয়েছে। নতুন ওটিপি চান।'})

    if otp_record.otp_code != otp_input:
        otp_record.attempts += 1
        otp_record.save()
        remaining = 5 - otp_record.attempts
        return JsonResponse({'valid': False, 'message': f'ভুল ওটিপি কোড! অনুগ্রহ করে ইমেইল চেক করে সঠিক কোড দিন। (অবশিষ্ট সুযোগ: {remaining} বার)'})

    # Store verified flag in session
    request.session['otp_verified_token'] = otp_record.otp_code

    return JsonResponse({
        'valid': True,
        'message': '✅ ওটিপি সফলভাবে যাচাই হয়েছে! এবার নিচে আপনার নতুন পাসওয়ার্ড নির্ধারণ করুন।'
    })


@require_http_methods(["GET", "POST"])
def forgot_password_view(request):
    """
    Step 1: User submits their registered Email or Username.
    Validates user, generates 6-digit OTP, sends it via email, and redirects to OTP verification.
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        identifier = request.POST.get('email_or_username', '').strip()
        if not identifier:
            messages.error(request, "অনুগ্রহ করে আপনার নিবন্ধিত ইমেইল বা ইউজারনেম লিখুন।")
            return render(request, 'registration/password_reset_form.html')

        # Find active user by email or username
        user = User.objects.filter(is_active=True).filter(
            models_Q_lookup(identifier)
        ).first()

        if not user or not user.email:
            messages.error(request, "দুঃখিত! এই তথ্যের সাথে মেলে এমন কোনো নিবন্ধিত সক্রিয় ব্যবহারকারী একাউন্ট পাওয়া যায়নি।")
            return render(request, 'registration/password_reset_form.html', {'identifier': identifier})

        # Invalidate existing unused OTPs
        PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)

        # Generate new 6-digit OTP
        otp_code = generate_secure_otp()
        expires_at = timezone.now() + timedelta(minutes=10)

        otp_obj = PasswordResetOTP.objects.create(
            user=user,
            email=user.email,
            otp_code=otp_code,
            expires_at=expires_at
        )

        # Send OTP email
        base_url = get_base_url(request)
        subject = f"🔐 হেল্পলাইন হ্যালো নওগাঁ — পাসওয়ার্ড রিসেট ওটিপি কোড: {otp_code}"
        greeting = "সম্মানিত সদস্য / ব্যবহারকারী"
        headline = "পাসওয়ার্ড রিসেটের ওটিপি (OTP) ভেরিফিকেশন কোড"

        message_paragraphs = [
            "আপনার হেল্পলাইন হ্যালো নওগাঁ অ্যাকাউন্টের পাসওয়ার্ড রিসেট করার জন্য একটি ওটিপি কোড অনুরোধ করা হয়েছে।",
            f"নিচের ৬ ডিজিটের ওটিপি (OTP) কোডটি ব্যবহার করে আগামী ১০ মিনিটের মধ্যে পাসওয়ার্ড পরিবর্তন সম্পন্ন করুন:"
        ]

        details = [
            {'label': '🔑 ওটিপি কোড (OTP)', 'value': f"👉 {otp_code} 👈"},
            {'label': 'ইউজারনেম', 'value': user.username},
            {'label': 'মেয়াদ', 'value': '১০ মিনিট (10 Minutes)'},
            {'label': 'অনুরোধের সময়', 'value': datetime.now().strftime('%d %B, %Y %I:%M %p')},
        ]

        footer_note = "নিরাপত্তার স্বার্থে এই ওটিপি কোডটি কারো সাথে শেয়ার করবেন না। আপনি যদি এই অনুরোধ না করে থাকেন, তবে এই ইমেইলটি উপেক্ষা করুন।"

        send_system_email(
            subject=subject,
            recipient_list=[user.email],
            recipient_name=user.get_full_name() or user.username,
            greeting=greeting,
            headline=headline,
            message_paragraphs=message_paragraphs,
            details=details,
            footer_note=footer_note,
            fail_silently=True
        )

        # Save session context
        request.session['reset_user_id'] = user.id
        request.session['reset_email'] = user.email
        request.session['otp_sent_at'] = timezone.now().timestamp()

        messages.success(request, f"আপনার নিবন্ধিত ইমেইলে ({mask_email(user.email)}) ৬ ডিজিটের একটি ওটিপি পাঠানো হয়েছে।")
        return redirect('core:verify_password_reset_otp')

    return render(request, 'registration/password_reset_form.html')


def models_Q_lookup(identifier):
    from django.db.models import Q
    return Q(email__iexact=identifier) | Q(username__iexact=identifier)


@require_http_methods(["GET", "POST"])
def verify_otp_and_reset_password_view(request):
    """
    Step 2: User enters 6-digit OTP and their new password.
    Validates OTP, sets new password, and redirects to login with success message.
    """
    user_id = request.session.get('reset_user_id')
    user_email = request.session.get('reset_email')

    if not user_id:
        messages.warning(request, "অনুগ্রহ করে প্রথমে আপনার ইমেইল বা ইউজারনেম দিয়ে ওটিপির জন্য অনুরোধ করুন।")
        return redirect('core:password_reset_request')

    user = User.objects.filter(pk=user_id, is_active=True).first()
    if not user:
        messages.error(request, "ব্যবহারকারী খুঁজে পাওয়া যায়নি। পুনরায় চেষ্টা করুন।")
        return redirect('core:password_reset_request')

    masked = mask_email(user_email or user.email)

    if request.method == 'POST':
        otp_input = request.POST.get('otp_code', '').strip().replace(' ', '')
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not otp_input:
            messages.error(request, "অনুগ্রহ করে ৬ ডিজিটের ওটিপি কোডটি লিখুন।")
            return render(request, 'registration/password_reset_confirm.html', {'masked_email': masked})

        if not new_password or not confirm_password:
            messages.error(request, "অনুগ্রহ করে নতুন পাসওয়ার্ড এবং নিশ্চিতকরণ পাসওয়ার্ড লিখুন।")
            return render(request, 'registration/password_reset_confirm.html', {'masked_email': masked, 'otp_code': otp_input})

        if new_password != confirm_password:
            messages.error(request, "নতুন পাসওয়ার্ড এবং নিশ্চিতকরণ পাসওয়ার্ড মেলেনি!")
            return render(request, 'registration/password_reset_confirm.html', {'masked_email': masked, 'otp_code': otp_input})

        if len(new_password) < 6:
            messages.error(request, "পাসওয়ার্ডের দৈর্ঘ্য ন্যূনতম ৬ অক্ষরের হতে হবে।")
            return render(request, 'registration/password_reset_confirm.html', {'masked_email': masked, 'otp_code': otp_input})

        # Fetch latest active OTP
        otp_record = PasswordResetOTP.objects.filter(user=user, is_used=False).order_by('-created_at').first()

        if not otp_record:
            messages.error(request, "কোনো সক্রিয় ওটিপি পাওয়া যায়নি। অনুগ্রহ করে নতুন ওটিপি অনুরোধ করুন।")
            return redirect('core:password_reset_request')

        # Check expiration
        if timezone.now() > otp_record.expires_at:
            otp_record.is_used = True
            otp_record.save()
            messages.error(request, "ওটিপির মেয়াদ (১০ মিনিট) শেষ হয়ে গেছে। অনুগ্রহ করে নতুন ওটিপি চেয়ে চেষ্টা করুন।")
            return render(request, 'registration/password_reset_confirm.html', {'masked_email': masked})

        # Check attempts limit
        if otp_record.attempts >= 5:
            otp_record.is_used = True
            otp_record.save()
            messages.error(request, "সর্বোচ্চ ৫ বার ভুল ওটিপি দেওয়ার কারণে কোডটি বাতিল করা হয়েছে। নতুন ওটিপি চান।")
            return redirect('core:password_reset_request')

        # Validate OTP
        if otp_record.otp_code != otp_input:
            otp_record.attempts += 1
            otp_record.save()
            remaining = 5 - otp_record.attempts
            messages.error(request, f"ভুল ওটিপি কোড! অনুগ্রহ করে ইমেইল চেক করে সঠিক ৬ ডিজিটের কোড দিন। (আর {remaining} বার চেষ্টা করতে পারবেন)")
            return render(request, 'registration/password_reset_confirm.html', {'masked_email': masked, 'otp_code': otp_input})

        # OTP is VALID -> Set new password
        user.set_password(new_password)
        user.save()

        # Mark OTP as used
        otp_record.is_used = True
        otp_record.save()

        # Clear session
        request.session.pop('reset_user_id', None)
        request.session.pop('reset_email', None)
        request.session.pop('otp_sent_at', None)

        # Send password changed confirmation email
        base_url = get_base_url(request)
        confirm_subject = "✅ হেল্পলাইন হ্যালো নওগাঁ — আপনার পাসওয়ার্ড সফলভাবে পরিবর্তিত হয়েছে"
        confirm_body = [
            "আপনার হেল্পলাইন হ্যালো নওগাঁ অ্যাকাউন্টের পাসওয়ার্ড সফলভাবে পরিবর্তন করা হয়েছে।",
            "আপনি এখন থেকে আপনার নতুন পাসওয়ার্ড দিয়ে অ্যাকাউন্টে লগইন করতে পারবেন।"
        ]
        confirm_details = [
            {'label': 'ইউজারনেম', 'value': user.username},
            {'label': 'পরিবর্তনের সময়', 'value': datetime.now().strftime('%d %B, %Y %I:%M %p')},
        ]
        action_buttons = [
            {'label': 'লগইন করুন', 'url': f"{base_url}/accounts/login/"},
        ]
        send_system_email(
            subject=confirm_subject,
            recipient_list=[user.email],
            recipient_name=user.get_full_name() or user.username,
            greeting="সম্মানিত ব্যবহারকারী",
            headline="পাসওয়ার্ড পরিবর্তন সফল হয়েছে!",
            message_paragraphs=confirm_body,
            details=confirm_details,
            action_buttons=action_buttons,
            footer_note="আপনি যদি নিজে এই পাসওয়ার্ড পরিবর্তন না করে থাকেন, তবে অবিলম্বে এডমিন টিমের সাথে যোগাযোগ করুন।",
            fail_silently=True
        )

        messages.success(request, "🎉 আপনার পাসওয়ার্ড সফলভাবে পরিবর্তন করা হয়েছে! অনুগ্রহ করে নতুন পাসওয়ার্ড দিয়ে লগইন করুন।")
        return redirect('login')

    return render(request, 'registration/password_reset_confirm.html', {'masked_email': masked})


@require_POST
def resend_otp_view(request):
    """
    Resends a fresh OTP to the user's email with throttling.
    """
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, "সেশন পাওয়া যায়নি। পুনরায় শুরু করুন।")
        return redirect('core:password_reset_request')

    user = User.objects.filter(pk=user_id, is_active=True).first()
    if not user or not user.email:
        messages.error(request, "ব্যবহারকারী খুঁজে পাওয়া যায়নি।")
        return redirect('core:password_reset_request')

    # Throttling check (at least 30 seconds)
    last_sent = request.session.get('otp_sent_at', 0)
    if timezone.now().timestamp() - last_sent < 30:
        remaining = int(30 - (timezone.now().timestamp() - last_sent))
        messages.warning(request, f"অনুগ্রহ করে আরও {remaining} সেকেন্ড অপেক্ষা করে পুনরায় ওটিপির অনুরোধ করুন।")
        return redirect('core:verify_password_reset_otp')

    # Invalidate previous OTPs
    PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)

    # Generate new OTP
    otp_code = generate_secure_otp()
    expires_at = timezone.now() + timedelta(minutes=10)

    PasswordResetOTP.objects.create(
        user=user,
        email=user.email,
        otp_code=otp_code,
        expires_at=expires_at
    )

    # Send Email
    subject = f"🔐 হেল্পলাইন হ্যালো নওগাঁ — নতুন পাসওয়ার্ড রিসেট ওটিপি: {otp_code}"
    message_paragraphs = [
        "আপনার অনুরোধে একটি নতুন ওটিপি (OTP) ভেরিফিকেশন কোড প্রদান করা হলো।",
        "নিচের ৬ ডিজিটের ওটিপি ব্যবহার করে পাসওয়ার্ড পরিবর্তন সম্পন্ন করুন:"
    ]
    details = [
        {'label': '🔑 নতুন ওটিপি (OTP)', 'value': f"👉 {otp_code} 👈"},
        {'label': 'ইউজারনেম', 'value': user.username},
        {'label': 'মেয়াদ', 'value': '১০ মিনিট'},
    ]

    send_system_email(
        subject=subject,
        recipient_list=[user.email],
        recipient_name=user.get_full_name() or user.username,
        greeting="সম্মানিত ব্যবহারকারী",
        headline="নতুন পাসওয়ার্ড রিসেট ওটিপি",
        message_paragraphs=message_paragraphs,
        details=details,
        footer_note="নিরাপত্তার স্বার্থে এই কোডটি গোপন রাখুন।",
        fail_silently=True
    )

    request.session['otp_sent_at'] = timezone.now().timestamp()
    messages.success(request, f"নতুন ওটিপি কোড আপনার ইমেইলে ({mask_email(user.email)}) পাঠানো হয়েছে।")
    return redirect('core:verify_password_reset_otp')
