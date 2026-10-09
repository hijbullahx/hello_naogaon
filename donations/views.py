import random
import logging
from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse

from .models import (
    DonationPageContent,
    Campaign,
    DonationImpact,
    EmergencyAppeal,
    DonationMethod,
    Bank,
    QRCode,
    FAQ,
    DonationStatistic,
    ProgramDonation,
    FinancialTransaction,
    PaymentGatewaySetting
)
from programs.models import Program
from volunteers.models import Volunteer, TeamMember
from django.conf import settings
from core.email_utils import send_system_email, get_admin_notification_emails
from core.sms_utils import send_sms
from .gateway import (
    initiate_active_gateway_session,
    initiate_paystation_session,
    verify_paystation_payment,
    initiate_paymently_session,
    verify_paymently_payment,
    get_paymently_config,
    get_paystation_config,
    get_paystation_dashboard_data,
    initiate_payment_gateway_session,
    validate_gateway_payment
)

logger = logging.getLogger(__name__)

def donation_page_view(request):
    """
    Dedicated donation page was deprecated/removed per user request:
    All donation actions now happen seamlessly inside the interactive popup modal (#directDonateModal).
    Redirects cleanly to home with modal opener (?donate=1 and any member_id query params preserved).
    """
    params = request.GET.copy()
    if 'donate' not in params:
        params['donate'] = '1'
    return redirect(f"/?{params.urlencode()}")


def member_pledge_lookup(request):
    """API endpoint to look up registered member (Volunteer or Team Member) info and financial pledge by member_id"""
    member_id = request.GET.get('member_id', '').strip()
    if not member_id:
        return JsonResponse({'found': False})
    
    vol = Volunteer.objects.filter(member_id__iexact=member_id, status='approved').first()
    if vol:
        sub = vol.subscription_summary
        has_cyclic_chada = vol.has_cyclic_chada
        is_reg_due = vol.is_registration_fee_due
        reg_fee = float(vol.registration_fee or 100.0)
        return JsonResponse({
            'found': True,
            'is_team_member': False,
            'is_volunteer': True,
            'member_id': vol.member_id,
            'full_name': vol.full_name,
            'role': 'স্বেচ্ছাসেবক সদস্য',
            'phone': vol.phone,
            'email': vol.email or '',
            'has_pledge': has_cyclic_chada,
            'has_cyclic_chada': has_cyclic_chada,
            'is_reg_fee_due': is_reg_due,
            'registration_fee': reg_fee,
            'frequency': 'monthly' if has_cyclic_chada else (vol.contribution_frequency or 'none'),
            'frequency_display': 'মাসিক চাঁদা' if has_cyclic_chada else ('নিবন্ধন ফি' if is_reg_due else 'ইচ্ছানুযায়ী'),
            'amount': sub['suggested_amount'],
            'monthly_fee': sub['monthly_fee'] if has_cyclic_chada else 0.0,
            'due_amount': sub['due_amount'],
            'advance_amount': sub['advance_amount'] if has_cyclic_chada else 0.0,
            'total_paid': sub['total_paid'],
            'total_billed': sub['total_billed'] if has_cyclic_chada else 0.0,
            'months_billed': sub['months_billed'] if has_cyclic_chada else 0,
            'join_date_formatted': sub['join_date_formatted'],
            'billing_day': sub['billing_day'],
            'status_label': sub['status_label'],
            'next_billing_date': sub['next_billing_date_formatted'],
        })
    
    tm = TeamMember.objects.filter(member_id__iexact=member_id).first()
    if tm:
        from volunteers.subscription_services import get_member_subscription_summary
        sub = get_member_subscription_summary(tm)
        return JsonResponse({
            'found': True,
            'is_team_member': True,
            'is_volunteer': False,
            'member_id': tm.member_id,
            'full_name': tm.name,
            'role': tm.effective_role,
            'phone': tm.phone or '',
            'email': tm.email or '',
            'has_pledge': True,
            'has_cyclic_chada': True,
            'is_reg_fee_due': False,
            'registration_fee': 0.0,
            'frequency': 'monthly',
            'frequency_display': 'মাসিক চাঁদা',
            'amount': sub['suggested_amount'],
            'monthly_fee': sub['monthly_fee'],
            'due_amount': sub['due_amount'],
            'advance_amount': sub['advance_amount'],
            'total_paid': sub['total_paid'],
            'total_billed': sub['total_billed'],
            'months_billed': sub['months_billed'],
            'join_date_formatted': sub['join_date_formatted'],
            'billing_day': sub['billing_day'],
            'status_label': sub['status_label'],
            'next_billing_date': sub['next_billing_date_formatted'],
        })

    return JsonResponse({'found': False})


def api_members_search(request):
    """API endpoint to search and retrieve registered members (Team Members and Volunteers)"""
    from django.db.models import Q
    from volunteers.subscription_services import get_member_subscription_summary
    q = request.GET.get('q', '').strip()
    members = []

    # 1. Team Members (Core Leadership & Council Members)
    tm_qs = TeamMember.objects.all().order_by('order', 'name')
    if q:
        tm_qs = tm_qs.filter(Q(name__icontains=q) | Q(member_id__icontains=q) | Q(phone__icontains=q))
    
    for tm in tm_qs:
        sub = get_member_subscription_summary(tm)
        members.append({
            'member_id': tm.member_id or '',
            'name': tm.name,
            'role': tm.effective_role or 'পরিচালনা পরিষদ',
            'phone': tm.phone or '',
            'email': tm.email or '',
            'photo_url': tm.image.url if tm.image else '',
            'is_team': True,
            'frequency': 'monthly',
            'frequency_display': 'মাসিক চাঁদা',
            'pledge_amount': sub['suggested_amount'],
            'monthly_fee': sub['monthly_fee'],
            'due_amount': sub['due_amount'],
            'advance_amount': sub['advance_amount'],
            'total_paid': sub['total_paid'],
            'months_billed': sub['months_billed'],
            'join_date_formatted': sub['join_date_formatted'],
            'status_label': sub['status_label'],
        })

    # 2. Approved Volunteers
    vol_qs = Volunteer.objects.filter(status='approved').order_by('full_name')
    if q:
        vol_qs = vol_qs.filter(Q(full_name__icontains=q) | Q(member_id__icontains=q) | Q(phone__icontains=q))

    for vol in vol_qs:
        sub = vol.subscription_summary
        has_cyclic_chada = vol.has_cyclic_chada
        is_reg_due = vol.is_registration_fee_due
        reg_fee = float(vol.registration_fee or 100.0)
        members.append({
            'member_id': vol.member_id or '',
            'name': vol.full_name,
            'role': 'স্বেচ্ছাসেবক সদস্য',
            'phone': vol.phone or '',
            'email': vol.email or '',
            'photo_url': vol.image.url if vol.image else '',
            'is_team': False,
            'is_volunteer': True,
            'has_cyclic_chada': has_cyclic_chada,
            'is_reg_fee_due': is_reg_due,
            'registration_fee': reg_fee,
            'frequency': 'monthly' if has_cyclic_chada else 'none',
            'frequency_display': 'মাসিক চাঁদা' if has_cyclic_chada else ('নিবন্ধন ফি' if is_reg_due else 'ইচ্ছানুযায়ী'),
            'pledge_amount': sub['suggested_amount'],
            'monthly_fee': sub['monthly_fee'] if has_cyclic_chada else 0.0,
            'due_amount': sub['due_amount'],
            'advance_amount': sub['advance_amount'] if has_cyclic_chada else 0.0,
            'total_paid': sub['total_paid'],
            'months_billed': sub['months_billed'] if has_cyclic_chada else 0,
            'join_date_formatted': sub['join_date_formatted'],
            'status_label': sub['status_label'],
        })

    return JsonResponse({'members': members, 'count': len(members)})


@require_POST
def initiate_payment(request):
    """
    Automated official payment gateway initiation.
    Redirects user directly to the official Payment Gateway (PayStation / Paymently) hosted page.
    """
    donor_identity_type = request.POST.get('donor_identity_type', 'general').strip()
    prog_donor_kind = request.POST.get('prog_donor_kind', '').strip()
    membership_id = request.POST.get('membership_id', '').strip()
    frequency = request.POST.get('frequency', 'one_time').strip()
    donor_name = request.POST.get('donor_name', '').strip()
    donor_email = request.POST.get('donor_email', '').strip()
    donor_phone = request.POST.get('donor_phone', '').strip()
    amount = request.POST.get('amount')
    note = request.POST.get('note', '').strip()
    program_id = request.POST.get('program_id')

    prog = None
    if program_id:
        prog = Program.objects.filter(pk=program_id).first()

    # Determine donation type & fetch member info if applicable
    if prog or donor_identity_type == 'program':
        if not prog:
            messages.error(request, "অনুগ্রহ করে একটি বৈধ কার্যক্রম নির্বাচন করুন।")
            return redirect(request.META.get('HTTP_REFERER') or '/?donate=1')
        if prog.status == 'completed':
            messages.error(request, "নির্বাচিত কার্যক্রমটি ইতিমধ্যে সম্পন্ন হয়েছে।")
            return redirect(request.META.get('HTTP_REFERER') or '/?donate=1')
            
        donation_type = 'program'
        frequency = 'one_time'

        is_member_mode = (donor_identity_type == 'member' or prog_donor_kind == 'member' or bool(membership_id))
        if is_member_mode and not membership_id and request.user.is_authenticated:
            user_m = getattr(request.user, 'team_profile', None) or getattr(request.user, 'volunteer_profile', None)
            if user_m and user_m.member_id:
                membership_id = user_m.member_id

        if is_member_mode:
            if not membership_id:
                messages.error(request, "সংস্থার সদস্য হিসেবে অনুদান প্রদান করতে আপনার সদস্য আইডি লিখুন।")
                return redirect(request.META.get('HTTP_REFERER') or '/?donate=1')

            vol = Volunteer.objects.filter(member_id__iexact=membership_id).first()
            tm = TeamMember.objects.filter(member_id__iexact=membership_id).first() if not vol else None
            if vol:
                if not donor_name: donor_name = vol.full_name
                if not donor_phone: donor_phone = vol.phone
                if not donor_email: donor_email = vol.email or donor_email
            elif tm:
                if not donor_name: donor_name = tm.name
                if not donor_phone: donor_phone = tm.phone or donor_phone
                if not donor_email: donor_email = tm.email or donor_email
            else:
                messages.error(request, f"সদস্য আইডি '{membership_id}' পাওয়া যায়নি। অনুগ্রহ করে যাচাই করে পুনরায় চেষ্টা করুন।")
                return redirect(request.META.get('HTTP_REFERER') or '/?donate=1')
        else:
            membership_id = None

    elif donor_identity_type == 'member':
        if not membership_id and request.user.is_authenticated:
            user_m = getattr(request.user, 'team_profile', None) or getattr(request.user, 'volunteer_profile', None)
            if user_m and user_m.member_id:
                membership_id = user_m.member_id

        vol = Volunteer.objects.filter(member_id__iexact=membership_id).first() if membership_id else None
        if vol:
            is_reg_payment = (request.POST.get('is_reg_payment') == 'true') or (
                vol.is_registration_fee_due and not vol.has_cyclic_chada
            )
            if is_reg_payment:
                donation_type = 'volunteer_registration'
                frequency = 'one_time'
                donor_name = vol.full_name
                donor_phone = vol.phone
                donor_email = vol.email or ''
                if not note:
                    note = f"সদস্য নিবন্ধন ফি পরিশোধ - {vol.full_name} ({vol.member_id})"
            else:
                donation_type = 'volunteer'
                donor_name = vol.full_name
                donor_phone = vol.phone
                donor_email = vol.email or ''
                if not frequency or frequency == 'one_time':
                    if vol.contribution_frequency and vol.contribution_frequency != 'none':
                        frequency = vol.contribution_frequency
        else:
            tm = TeamMember.objects.filter(member_id__iexact=membership_id).first() if membership_id else None
            if tm:
                donation_type = 'leadership'
                donor_name = tm.name
                donor_phone = tm.phone or donor_phone
                donor_email = tm.email or donor_email
            else:
                messages.error(request, "সঠিক সদস্য আইডি পাওয়া যায়নি। অনুগ্রহ করে যাচাই করে পুনরায় চেষ্টা করুন।")
                return redirect(request.META.get('HTTP_REFERER') or '/?donate=1')
    else:
        donation_type = 'general'
        frequency = 'one_time'
        if membership_id:
            vol = Volunteer.objects.filter(member_id__iexact=membership_id).first()
            if vol:
                if not donor_name: donor_name = vol.full_name
                if not donor_phone: donor_phone = vol.phone
                if not donor_email: donor_email = vol.email or donor_email
            else:
                tm = TeamMember.objects.filter(member_id__iexact=membership_id).first()
                if tm:
                    if not donor_name: donor_name = tm.name
                    if not donor_phone: donor_phone = tm.phone or donor_phone
                    if not donor_email: donor_email = tm.email or donor_email

    if not donor_name or not donor_phone or not amount:
        messages.error(request, "দয়া করে নাম, মোবাইল নম্বর এবং আর্থিক সহায়তার পরিমাণ সঠিকভাবে লিখুন।")
        return redirect(request.META.get('HTTP_REFERER') or '/?donate=1')

    from decimal import Decimal, InvalidOperation
    from datetime import timedelta
    from django.utils import timezone

    try:
        amount_val = Decimal(str(amount).strip())
        if amount_val <= 0:
            raise ValueError()
    except (ValueError, TypeError, InvalidOperation):
        messages.error(request, "দয়া করে সঠিক আর্থিক পরিমাণ লিখুন।")
        return redirect(request.META.get('HTTP_REFERER') or '/?donate=1')

    # Generate unique transaction ID
    tran_id = f"HN{datetime.now().strftime('%y%m%d%H%M%S')}{random.randint(100, 999)}"

    payment_mode = request.POST.get('payment_mode', 'gateway').strip().lower()
    manual_channel = request.POST.get('manual_channel', 'bKash').strip()
    sender_account = request.POST.get('sender_account', '').strip()
    trx_id = request.POST.get('trx_id', '').strip()

    # Manual Send-Money / Bank Deposit workflow
    if payment_mode == 'manual':
        if not sender_account:
            messages.error(request, "ম্যানুয়াল পেমেন্ট সম্পন্ন করতে আপনার প্রেরক অ্যাকাউন্ট বা মোবাইল নম্বর প্রদান করুন।")
            return redirect(request.META.get('HTTP_REFERER') or '/?donate=1')

        # Debounce rapid duplicate manual donation submission (within 60s) using atomic cache lock
        from django.core.cache import cache
        from django.db import transaction
        lock_key = f"lock_manual_don_{donor_phone}_{amount_val}"
        if not cache.add(lock_key, '1', timeout=60):
            messages.info(request, f"ধন্যবাদ {donor_name}! আপনার সহায়তার তথ্যটি ইতিমধ্যে সিস্টেমে জমা হচ্ছে। অনুগ্রহ করে অপেক্ষা করুন।")
            return redirect(request.META.get('HTTP_REFERER') or '/?donate=1')

        recent_cutoff = timezone.now() - timedelta(seconds=60)
        recent_dup = ProgramDonation.objects.filter(
            donor_phone=donor_phone,
            amount=amount_val,
            status='pending',
            created_at__gte=recent_cutoff
        ).first()
        if recent_dup:
            messages.info(request, f"ধন্যবাদ {donor_name}! আপনার সহায়তার তথ্যটি ইতিমধ্যে সিস্টেমে জমা হয়েছে। অনুগ্রহ করে যাচাইয়ের জন্য অপেক্ষা করুন।")
            return redirect(request.META.get('HTTP_REFERER') or '/?donate=1')

        try:
            with transaction.atomic():
                donation = ProgramDonation.objects.create(
                    donation_type=donation_type,
                    frequency=frequency,
                    program=prog,
                    donor_name=donor_name,
                    donor_email=donor_email,
                    donor_phone=donor_phone,
                    membership_id=membership_id if membership_id else None,
                    amount=amount_val,
                    payment_method=f"Manual ({manual_channel})",
                    sender_account=sender_account,
                    card_type=manual_channel,
                    trx_id=trx_id,
                    tran_id=tran_id,
                    note=note,
                    status='pending'
                )
        except Exception as e:
            cache.delete(lock_key)
            messages.error(request, "অনুদান তথ্য সংরক্ষণ করতে সমস্যা হয়েছে। অনুগ্রহ করে পুনরায় চেষ্টা করুন।")
            return redirect(request.META.get('HTTP_REFERER') or '/?donate=1')

        from .donation_notifications import notify_admin_new_manual_donation, notify_donor_manual_submission
        notify_admin_new_manual_donation(donation, request=request)
        notify_donor_manual_submission(donation, request=request)

        member_txt = f" (সদস্য আইডি: {donation.membership_id})" if donation.membership_id else ""
        messages.success(
            request, 
            f"ধন্যবাদ {donation.donor_name}{member_txt}! আপনার ৳{amount_val:,.0f} ম্যানুয়াল পেমেন্টের তথ্য সফলভাবে জমা হয়েছে। অ্যাডমিন প্যানেল থেকে স্টেটমেন্ট যাচাই শেষে এটি অনুমোদিত হবে এবং আপনার কাছে নিশ্চিতকরণ এসএমএস ও ইমেইল পাঠানো হবে।"
        )
        return redirect(request.META.get('HTTP_REFERER') or '/')

    # Automated Online Gateway workflow
    donation = ProgramDonation.objects.create(
        donation_type=donation_type,
        frequency=frequency,
        program=prog,
        donor_name=donor_name,
        donor_email=donor_email,
        donor_phone=donor_phone,
        membership_id=membership_id if membership_id else None,
        amount=amount_val,
        payment_method='Online Gateway',
        tran_id=tran_id,
        note=note,
        status='initiated'
    )

    # Save donation reference to session for reliable callback fallback
    request.session['last_donation_tran_id'] = donation.tran_id
    request.session['last_donation_id'] = donation.id

    # Initiate automated checkout session (PayStation Direct OTP/PIN or Paymently)
    session_res = initiate_active_gateway_session(request, donation)
    if session_res.get('success') and session_res.get('payment_url'):
        return redirect(session_res['payment_url'])
    else:
        logger.warning(f"Payment gateway initiation fallback for {donation.tran_id}: {session_res.get('error')}")
        messages.info(request, "অনলাইন পেমেন্ট গেটওয়েতে সংযোগ করা যাচ্ছে না। আপনি নিচের তথ্য ব্যবহার করে সহায়তা পাঠাতে পারেন।")
        return redirect('donations:gateway_checkout', tran_id=donation.tran_id)


def start_checkout_payment(request, tran_id):
    """
    Direct endpoint from checkout preview page to initiate or re-launch active payment session.
    """
    donation = get_object_or_404(ProgramDonation, tran_id=tran_id)
    if donation.status == 'approved':
        messages.info(request, "এই অনুদানটি ইতিমধ্যে সফলভাবে পরিশোধ করা হয়েছে।")
        return redirect('donations:receipt', donation_id=donation.id)

    request.session['last_donation_tran_id'] = donation.tran_id
    request.session['last_donation_id'] = donation.id

    session_res = initiate_active_gateway_session(request, donation)
    if session_res.get('success') and session_res.get('payment_url'):
        return redirect(session_res['payment_url'])
    else:
        messages.error(request, f"পেমেন্ট গেটওয়েতে সংযোগ করতে সমস্যা হয়েছে: {session_res.get('error')}")
        return redirect('donations:gateway_checkout', tran_id=donation.tran_id)


def gateway_checkout_view(request, tran_id):
    """
    Renders the official gateway checkout page with automated payment button and manual send-money fallback.
    """
    donation = get_object_or_404(ProgramDonation, tran_id=tran_id)
    donation_methods = DonationMethod.objects.filter(is_active=True)
    banks = Bank.objects.filter(is_active=True)
    qrcodes = QRCode.objects.filter(is_active=True).select_related('method')
    return render(request, 'donations/gateway_checkout.html', {
        'donation': donation,
        'donation_methods': donation_methods,
        'banks': banks,
        'qrcodes': qrcodes,
    })


@require_POST
def confirm_checkout_payment(request, tran_id):
    """
    Saves user's manual payment submission (Payment method, Sender Account & Trx ID) as pending verification.
    """
    donation = get_object_or_404(ProgramDonation, tran_id=tran_id)
    payment_channel = request.POST.get('payment_channel') or 'bKash'
    sender_account = request.POST.get('sender_account', '').strip()
    trx_id = request.POST.get('trx_id', '').strip()

    donation.payment_method = f"Manual ({payment_channel})"
    donation.card_type = payment_channel
    if sender_account:
        donation.sender_account = sender_account
    donation.trx_id = trx_id
    donation.status = 'pending'
    donation.save()

    from .donation_notifications import notify_admin_new_manual_donation, notify_donor_manual_submission
    notify_admin_new_manual_donation(donation, request=request)
    notify_donor_manual_submission(donation, request=request)

    member_txt = f" (সদস্য আইডি: {donation.membership_id})" if donation.membership_id else ""
    messages.success(
        request, 
        f'ধন্যবাদ {donation.donor_name}{member_txt}! আপনার ৳{donation.amount:,.2f} সহায়তার তথ্য ও ট্রানজেকশন আইডি সফলভাবে জমা হয়েছে। অ্যাডমিন প্যানেল থেকে যাচাই শেষে এটি অনুমোদিত হবে এবং আপনার কাছে নোটিফিকেশন পাঠানো হবে।'
    )
    return redirect(request.META.get('HTTP_REFERER') or '/')


def process_successful_payment(donation, payment_data, request=None):
    """
    Idempotent, concurrency-safe processor for verified completed donations:
    1. Uses select_for_update() inside transaction.atomic() to prevent race conditions.
    2. Updates donation status to 'approved'
    3. Updates program raised amount
    4. Records FinancialTransaction
    5. Dispatches SMS & Email receipts only AFTER transaction commits
    """
    from django.db import transaction
    from decimal import Decimal, InvalidOperation

    if donation.status == 'approved':
        return donation

    # Verify payment amount according to gateway contract
    raw_amount = payment_data.get('amount') or payment_data.get('payment_amount') or payment_data.get('trx_amount') or payment_data.get('paid_amount')
    try:
        paid_amount = Decimal(str(raw_amount).strip()) if raw_amount is not None else None
    except (InvalidOperation, TypeError, ValueError):
        paid_amount = None

    if paid_amount is None or paid_amount < donation.amount:
        logger.error(
            f"[PAYMENT REJECTED] Amount validation failed for donation {donation.id}: "
            f"expected {donation.amount}, received {paid_amount}"
        )
        return donation

    raw_method = payment_data.get('payment_method') or 'Online Gateway'
    # Format payment method nicely
    m_lower = str(raw_method).lower()
    if 'bkash' in m_lower:
        payment_method = 'bKash'
    elif 'nagad' in m_lower:
        payment_method = 'Nagad'
    elif 'rocket' in m_lower:
        payment_method = 'Rocket'
    elif 'upay' in m_lower:
        payment_method = 'Upay'
    else:
        payment_method = str(raw_method)

    trx_id = payment_data.get('transaction_id') or payment_data.get('trx_id') or donation.tran_id
    invoice_id = str(payment_data.get('invoice_id') or donation.bank_tran_id or '')

    notifications_to_send = []

    with transaction.atomic():
        locked_donation = ProgramDonation.objects.select_for_update().filter(pk=donation.pk).first()
        if not locked_donation or locked_donation.status == 'approved':
            return locked_donation or donation

        locked_donation.status = 'approved'
        locked_donation.payment_method = payment_method
        locked_donation.card_type = payment_method
        locked_donation.bank_tran_id = invoice_id
        locked_donation.trx_id = trx_id
        locked_donation.save()

        # 1. Update Program raised_amount
        if locked_donation.program:
            prog = locked_donation.program
            prog.raised_amount = (prog.raised_amount or 0) + locked_donation.amount
            prog.save()
            category_name = f"কার্যক্রম: {prog.title}"
            title_name = f"কার্যক্রম অনুদান - {prog.title} ({locked_donation.donor_name})"
        elif locked_donation.donation_type == 'volunteer_registration' or (locked_donation.membership_id and str(locked_donation.membership_id).startswith('NEW_VOL_')):
            category_name = 'সদস্য নিবন্ধন ফি'
            title_name = f"সদস্য নিবন্ধন ফি ({locked_donation.donor_name})"
        elif locked_donation.donation_type in ['volunteer', 'leadership']:
            category_name = 'সদস্য মাসিক চাঁদা'
            title_name = f"সদস্য মাসিক চাঁদা ({locked_donation.donor_name})"
        elif locked_donation.donation_type == 'emergency':
            category_name = 'জরুরি ত্রাণ ও চিকিৎসা তহবিল'
            title_name = f"জরুরি তহবিল অনুদান ({locked_donation.donor_name})"
        else:
            category_name = 'সাধারণ আর্থিক সহায়তা'
            title_name = f"সাধারণ আর্থিক সহায়তা ({locked_donation.donor_name})"

        # Handle Volunteer registration approval & notification if applicable
        is_vol_reg = locked_donation.donation_type == 'volunteer_registration' or (locked_donation.membership_id and str(locked_donation.membership_id).startswith('NEW_VOL_'))
        vol_obj = None
        if is_vol_reg:
            from volunteers.models import Volunteer, generate_unique_member_id

            if locked_donation.membership_id and str(locked_donation.membership_id).startswith('NEW_VOL_'):
                try:
                    vid = int(str(locked_donation.membership_id).replace('NEW_VOL_', ''))
                    vol_obj = Volunteer.objects.filter(pk=vid).first()
                except (ValueError, TypeError):
                    pass
            elif locked_donation.membership_id:
                vol_obj = Volunteer.objects.filter(member_id__iexact=locked_donation.membership_id).first()

            if not vol_obj and locked_donation.tran_id:
                vol_obj = Volunteer.objects.filter(tran_id=locked_donation.tran_id).first()
            if not vol_obj and locked_donation.donor_phone:
                vol_obj = Volunteer.objects.filter(phone=locked_donation.donor_phone).first()

            if vol_obj:
                if vol_obj.status != 'approved':
                    vol_obj.status = 'approved'
                vol_obj.payment_status = 'paid'
                vol_obj.payment_method = payment_method
                vol_obj.trx_id = trx_id
                if not vol_obj.member_id:
                    vol_obj.member_id = generate_unique_member_id(prefix_str="")
                vol_obj.save()
                locked_donation.membership_id = vol_obj.member_id
                locked_donation.save(update_fields=['membership_id'])
                notifications_to_send.append(('vol', vol_obj))

        trx_note = f"পেমেন্ট মাধ্যম: {payment_method} | TrxID: {trx_id} | ইনভয়েস: {invoice_id} | মোবাইল: {locked_donation.donor_phone}"
        if locked_donation.membership_id:
            trx_note += f" | মেম্বার আইডি: {locked_donation.membership_id}"
        if locked_donation.program:
            trx_note += f" | কার্যক্রম: {locked_donation.program.title}"
        if locked_donation.note:
            trx_note += f" | নোট: {locked_donation.note}"

        # 2. Record FinancialTransaction (income) if not already created
        if not FinancialTransaction.objects.filter(trx_id=trx_id, transaction_type='income').exists():
            FinancialTransaction.objects.create(
                donation=locked_donation,
                transaction_type='income',
                program=locked_donation.program,
                title=title_name,
                category=category_name,
                amount=locked_donation.amount,
                payment_method=payment_method,
                trx_id=trx_id,
                donor_name=locked_donation.donor_name,
                date=date.today(),
                note=trx_note,
                is_manual_entry=False
            )

        if locked_donation.program:
            try:
                from core.views_dashboard import sync_program_raised_amount
                sync_program_raised_amount(locked_donation.program)
            except Exception:
                pass

        if not vol_obj:
            notifications_to_send.append(('donor', locked_donation))

        # 3. Dispatch Notifications only AFTER database transaction is safely committed
        def _dispatch_payment_notifications():
            for n_type, n_target in notifications_to_send:
                if n_type == 'vol':
                    try:
                        from volunteers.views import send_member_notifications
                        send_member_notifications(n_target)
                    except Exception as ex:
                        logger.error(f"[VOL NOTIFY ERROR ON PAYMENT PROCESS] {ex}")
                elif n_type == 'donor':
                    try:
                        from donations.donation_notifications import notify_donor_donation_approved
                        notify_donor_donation_approved(n_target, request=request)
                    except Exception as ex:
                        logger.error(f"[DONATION APPROVAL NOTIFICATIONS ERROR] {ex}")

        transaction.on_commit(_dispatch_payment_notifications)

    return locked_donation


@csrf_exempt
def payment_success(request):
    """
    Official Payment Gateway Success Callback.
    Verifies transaction with PayStation or Paymently Verify API, updates donation,
    logs financial transaction, dispatches notifications, and shows official receipt.
    """
    invoice_number = request.GET.get('invoice_number') or request.POST.get('invoice_number') or request.GET.get('invoice') or request.POST.get('invoice') or request.GET.get('trxId') or request.POST.get('trxId')
    invoice_id = request.GET.get('invoice_id') or request.POST.get('invoice_id')
    tran_id = request.GET.get('tran_id') or request.POST.get('tran_id') or invoice_number or request.session.get('last_donation_tran_id')
    opt_a = request.GET.get('opt_a') or request.POST.get('opt_a') or request.session.get('last_donation_id')

    if opt_a and not tran_id:
        try:
            d_by_id = ProgramDonation.objects.filter(pk=int(opt_a)).first()
            if d_by_id:
                tran_id = d_by_id.tran_id
        except Exception:
            pass

    # Fallback to session tran_id if not explicitly provided
    if not tran_id and not invoice_number:
        tran_id = request.session.get('last_donation_tran_id')

    # 1. PayStation Verification
    target_invoice = invoice_number or tran_id
    if target_invoice:
        ps_res = verify_paystation_payment(target_invoice)
        if str(ps_res.get('status_code')) == '200' and ps_res.get('data'):
            ps_data = ps_res['data']
            trx_st = str(ps_data.get('trx_status', '')).lower()
            if 'success' in trx_st:
                donation = ProgramDonation.objects.filter(tran_id=target_invoice).first()
                if not donation and ps_data.get('opt_a'):
                    try:
                        donation = ProgramDonation.objects.filter(pk=int(ps_data['opt_a'])).first()
                    except Exception:
                        pass
                if donation:
                    # Validate paid amount from PayStation response before proceeding
                    paid_raw = ps_data.get('payment_amount') or ps_data.get('trx_amount')
                    from decimal import Decimal, InvalidOperation
                    try:
                        paid_amount = Decimal(str(paid_raw).strip()) if paid_raw is not None else None
                    except (InvalidOperation, TypeError, ValueError):
                        paid_amount = None

                    if paid_amount is None or paid_amount < donation.amount:
                        logger.error(f"[PAYMENT REJECTED] PayStation amount mismatch for donation {donation.id}: expected {donation.amount}, received {paid_amount}")
                        messages.error(request, "পেমেন্টের পরিমাণ সঠিক নয় বা অসম্পূর্ণ।")
                        return redirect('core:home')

                    payment_data = {
                        'payment_method': ps_data.get('payment_method') or donation.payment_method or 'PayStation',
                        'transaction_id': ps_data.get('trx_id') or target_invoice,
                        'invoice_id': target_invoice,
                        'amount': paid_amount
                    }
                    process_successful_payment(donation, payment_data, request=request)
                    request.session.pop('last_donation_tran_id', None)
                    request.session.pop('last_donation_id', None)
                    if donation.donation_type == 'volunteer_registration':
                        messages.success(
                            request,
                            f'অভিনন্দন {donation.donor_name}! আপনার ১০০ টাকা সদস্য নিবন্ধন ফি সফলভাবে পরিশোধ হয়েছে এবং সদস্য আইডি: {donation.membership_id} ইস্যু করা হয়েছে। আপনার মোবাইল ও ইমেইলে বার্তা পাঠানো হয়েছে।'
                        )
                    else:
                        member_txt = f" (সদস্য আইডি: {donation.membership_id})" if donation.membership_id else ""
                        messages.success(
                            request, 
                            f'ধন্যবাদ {donation.donor_name}{member_txt}! আপনার ৳{donation.amount:,.2f} অনলাইন অনুদান সফলভাবে গৃহীত হয়েছে।'
                        )
                    return redirect('donations:receipt', donation_id=donation.id)
            elif trx_st in ['failed', 'fail', 'cancelled', 'cancel']:
                donation = ProgramDonation.objects.filter(tran_id=target_invoice).first()
                if donation and donation.status in ['initiated', 'pending']:
                    donation.status = 'failed' if 'fail' in trx_st else 'cancelled'
                    donation.save(update_fields=['status'])
                messages.warning(request, f"অনলাইন পেমেন্ট সম্পন্ন হয়নি (স্ট্যাটাস: {ps_data.get('trx_status')})। আপনি পুনরায় চেষ্টা করতে পারেন।")
                return redirect('donations:gateway_checkout', tran_id=target_invoice)

    # 2. Paymently Verification
    if invoice_id:
        verification_res = verify_paymently_payment(invoice_id)
        status = str(verification_res.get('status', '')).upper()
        if status == 'COMPLETED':
            meta = verification_res.get('metadata') or {}
            target_tran_id = meta.get('tran_id') or tran_id
            donation = None
            if target_tran_id:
                donation = ProgramDonation.objects.filter(tran_id=target_tran_id).first()
            if not donation and meta.get('donation_id'):
                donation = ProgramDonation.objects.filter(pk=meta.get('donation_id')).first()
            if not donation and invoice_id:
                donation = ProgramDonation.objects.filter(bank_tran_id=invoice_id).first()

            if donation:
                # Validate paid amount from Paymently response before proceeding
                paid_raw = verification_res.get('amount')
                from decimal import Decimal, InvalidOperation
                try:
                    paid_amount = Decimal(str(paid_raw).strip()) if paid_raw is not None else None
                except (InvalidOperation, TypeError, ValueError):
                    paid_amount = None

                if paid_amount is None or paid_amount < donation.amount:
                    logger.error(f"[PAYMENT REJECTED] Paymently amount mismatch for donation {donation.id}: expected {donation.amount}, received {paid_amount}")
                    messages.error(request, "পেমেন্টের পরিমাণ সঠিক নয় বা অসম্পূর্ণ।")
                    return redirect('core:home')

                process_successful_payment(donation, verification_res, request=request)
                if donation.donation_type == 'volunteer_registration':
                    messages.success(
                        request,
                        f'অভিনন্দন {donation.donor_name}! আপনার ১০০ টাকা সদস্য নিবন্ধন ফি সফলভাবে পরিশোধ হয়েছে এবং সদস্য আইডি: {donation.membership_id} ইস্যু করা হয়েছে। আপনার মোবাইল ও ইমেইলে বার্তা পাঠানো হয়েছে।'
                    )
                else:
                    member_txt = f" (সদস্য আইডি: {donation.membership_id})" if donation.membership_id else ""
                    messages.success(
                        request, 
                        f'ধন্যবাদ {donation.donor_name}{member_txt}! আপনার ৳{donation.amount:,.2f} অনলাইন অনুদান সফলভাবে গৃহীত হয়েছে।'
                    )
                return redirect('donations:receipt', donation_id=donation.id)
            else:
                logger.error(f"Donation record not found for verified invoice {invoice_id}")
                messages.success(request, "আপনার অনুদান সফলভাবে গৃহীত হয়েছে। তথ্য যাচাই শেষে আপডেট করা হবে।")
                return redirect('core:home')
        else:
            status_desc = verification_res.get('status', 'PENDING')
            messages.warning(request, f"পেমেন্ট স্ট্যাটাস: {status_desc}। পেমেন্ট সম্পূর্ণ হয়নি বা অপেক্ষমাণ রয়েছে।")
            return redirect('core:home')

    # Fallback to tran_id check
    if tran_id:
        donation = ProgramDonation.objects.filter(tran_id=tran_id).first()
        if donation and donation.status == 'approved':
            return redirect('donations:receipt', donation_id=donation.id)

    messages.error(request, "পেমেন্ট সংক্রান্ত তথ্য পাওয়া যায়নি বা পেমেন্ট সম্পন্ন হয়নি।")
    return redirect('core:home')


@csrf_exempt
def payment_fail(request):
    """
    Payment Gateway Failure Callback.
    """
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    invoice_id = request.POST.get('invoice_id') or request.GET.get('invoice_id') or request.GET.get('invoice_number')
    if tran_id:
        donation = ProgramDonation.objects.filter(tran_id=tran_id).first()
        if donation and donation.status == 'pending':
            donation.status = 'failed'
            donation.save()
    elif invoice_id:
        donation = ProgramDonation.objects.filter(bank_tran_id=invoice_id).first()
        if donation and donation.status == 'pending':
            donation.status = 'failed'
            donation.save()

    messages.error(request, "দুঃখিত, আপনার অনলাইন পেমেন্ট সম্পন্ন হয়নি বা ব্যর্থ হয়েছে। অনুগ্রহ করে পুনরায় চেষ্টা করুন।")
    return redirect('core:home')


@csrf_exempt
def payment_cancel(request):
    """
    Payment Gateway Cancel Callback.
    """
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    invoice_id = request.POST.get('invoice_id') or request.GET.get('invoice_id') or request.GET.get('invoice_number')
    if tran_id:
        donation = ProgramDonation.objects.filter(tran_id=tran_id).first()
        if donation and donation.status == 'pending':
            donation.status = 'cancelled'
            donation.save()
    elif invoice_id:
        donation = ProgramDonation.objects.filter(bank_tran_id=invoice_id).first()
        if donation and donation.status == 'pending':
            donation.status = 'cancelled'
            donation.save()

    messages.warning(request, "অনলাইন পেমেন্ট প্রক্রিয়াটি বাতিল করা হয়েছে।")
    return redirect('core:home')


@csrf_exempt
def payment_ipn(request):
    """
    Payment Gateway IPN (Instant Payment Notification) Webhook.
    Receives automated webhook notifications from PayStation and Paymently.
    """
    try:
        import json
        if request.body:
            payload = json.loads(request.body.decode('utf-8'))
        else:
            payload = request.POST.dict()
    except Exception as e:
        logger.warning(f"Failed to parse IPN payload: {e}")
        payload = request.POST.dict()

    # 1. PayStation IPN handler (Requires trusted server-side status verification)
    ps_invoice = payload.get('invoice_number') or payload.get('invoice') or payload.get('tran_id')
    if ps_invoice and not payload.get('invoice_id'):
        ps_res = verify_paystation_payment(ps_invoice)
        if str(ps_res.get('status_code')) == '200' and ps_res.get('data'):
            ps_data = ps_res['data']
            ps_status = str(ps_data.get('trx_status', '')).lower()
            if 'success' in ps_status:
                donation = ProgramDonation.objects.filter(tran_id=ps_invoice).first()
                if not donation and ps_data.get('opt_a'):
                    try:
                        donation = ProgramDonation.objects.filter(pk=int(ps_data['opt_a'])).first()
                    except Exception:
                        pass

                if donation:
                    paid_raw = ps_data.get('payment_amount') or ps_data.get('trx_amount')
                    payment_data = {
                        'payment_method': ps_data.get('payment_method') or donation.payment_method or 'PayStation',
                        'transaction_id': ps_data.get('trx_id') or ps_invoice,
                        'invoice_id': ps_invoice,
                        'amount': paid_raw
                    }
                    res_donation = process_successful_payment(donation, payment_data, request=request)
                    if res_donation and res_donation.status == 'approved':
                        return JsonResponse({'status': 'success', 'message': 'PayStation payment approved'})
                    return JsonResponse({'status': 'rejected', 'error': 'Amount validation failed'}, status=400)
                else:
                    logger.error(f"[PAYSTATION IPN REJECTED] No donation found for verified invoice {ps_invoice}")
                    return JsonResponse({'status': 'rejected', 'error': 'Donation not found'}, status=404)
            else:
                logger.warning(f"[PAYSTATION IPN REJECTED] PayStation status not successful: {ps_status}")
                return JsonResponse({'status': 'rejected', 'error': f'Payment status {ps_status}'}, status=400)
        else:
            logger.error(f"[PAYSTATION IPN REJECTED] PayStation verification failed for invoice {ps_invoice}: {ps_res}")
            return JsonResponse({'status': 'rejected', 'error': 'PayStation verification failed'}, status=400)

    # 2. Paymently IPN handler
    invoice_id = payload.get('invoice_id')
    if invoice_id:
        verification_res = verify_paymently_payment(invoice_id)
        if str(verification_res.get('status', '')).upper() == 'COMPLETED':
            meta = verification_res.get('metadata') or {}
            target_tran_id = meta.get('tran_id')
            donation = None
            if target_tran_id:
                donation = ProgramDonation.objects.filter(tran_id=target_tran_id).first()
            if not donation and meta.get('donation_id'):
                donation = ProgramDonation.objects.filter(pk=meta.get('donation_id')).first()
            if not donation:
                donation = ProgramDonation.objects.filter(bank_tran_id=invoice_id).first()

            if donation:
                res_donation = process_successful_payment(donation, verification_res, request=request)
                if res_donation and res_donation.status == 'approved':
                    return JsonResponse({'status': 'SUCCESS', 'message': 'Payment approved'})
                return JsonResponse({'status': 'REJECTED', 'error': 'Amount validation failed'}, status=400)

    return JsonResponse({'status': 'RECEIVED'})


def donation_receipt_view(request, donation_id):
    """
    Displays the official printable money receipt for a completed donation.
    """
    donation = get_object_or_404(ProgramDonation, pk=donation_id)
    return render(request, 'donations/donation_receipt.html', {
        'donation': donation
    })


@require_POST
def submit_donation(request):
    """
    Legacy wrapper redirecting to initiate_payment.
    """
    return initiate_payment(request)


@require_POST
def submit_program_donation(request):
    """
    Handles financial contributions submitted for specific programs.
    """
    return initiate_payment(request)


def api_paystation_dashboard(request):
    """
    AJAX endpoint for PayStation Merchant Gateway dashboard popup.
    Provides live statistics, method breakdown, and recent transactions.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)

    try:
        data = get_paystation_dashboard_data()
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        logger.error(f"Error fetching PayStation dashboard data: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def api_paystation_verify_trx(request):
    """
    AJAX endpoint to live-query PayStation Transaction Status API for a single invoice.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)

    invoice_number = request.GET.get('invoice_number', '').strip()
    if not invoice_number:
        return JsonResponse({'success': False, 'error': 'No invoice number provided'}, status=400)

    try:
        result = verify_paystation_payment(invoice_number)
        return JsonResponse({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"PayStation live verification error for {invoice_number}: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

