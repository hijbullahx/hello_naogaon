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
        has_pledge = (vol.contribution_frequency == 'monthly' and vol.contribution_amount and float(vol.contribution_amount) > 0)
        return JsonResponse({
            'found': True,
            'is_team_member': False,
            'member_id': vol.member_id,
            'full_name': vol.full_name,
            'role': 'স্বেচ্ছাসেবক সদস্য',
            'phone': vol.phone,
            'email': vol.email or '',
            'has_pledge': has_pledge,
            'frequency': 'monthly' if has_pledge else (vol.contribution_frequency or 'none'),
            'frequency_display': 'মাসিক চাঁদা' if has_pledge else 'ইচ্ছানুযায়ী',
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
    
    tm = TeamMember.objects.filter(member_id__iexact=member_id).first()
    if tm:
        from volunteers.subscription_services import get_member_subscription_summary
        sub = get_member_subscription_summary(tm)
        return JsonResponse({
            'found': True,
            'is_team_member': True,
            'member_id': tm.member_id,
            'full_name': tm.name,
            'role': tm.effective_role,
            'phone': tm.phone or '',
            'email': tm.email or '',
            'has_pledge': True,
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
        has_pledge = (vol.contribution_frequency == 'monthly' and vol.contribution_amount and float(vol.contribution_amount) > 0)
        members.append({
            'member_id': vol.member_id or '',
            'name': vol.full_name,
            'role': 'স্বেচ্ছাসেবক সদস্য',
            'phone': vol.phone or '',
            'email': vol.email or '',
            'photo_url': vol.image.url if vol.image else '',
            'is_team': False,
            'frequency': 'monthly' if has_pledge else 'none',
            'frequency_display': 'মাসিক চাঁদা' if has_pledge else 'ইচ্ছানুযায়ী',
            'pledge_amount': sub['suggested_amount'],
            'monthly_fee': sub['monthly_fee'],
            'due_amount': sub['due_amount'],
            'advance_amount': sub['advance_amount'],
            'total_paid': sub['total_paid'],
            'months_billed': sub['months_billed'],
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
    if donor_identity_type == 'general':
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
    elif donor_identity_type == 'program':
        if not prog or not prog.needs_funding:
            messages.error(request, "নির্বাচিত কার্যক্রমে বর্তমানে কোনো আর্থিক সহায়তার প্রয়োজন নেই।")
            return redirect(request.META.get('HTTP_REFERER') or '/?donate=1')
        donation_type = 'program'
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
    elif prog and prog.needs_funding:
        donation_type = 'program'
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
    elif donor_identity_type == 'member':
        vol = Volunteer.objects.filter(member_id__iexact=membership_id).first() if membership_id else None
        if vol:
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
        membership_id = None
        frequency = 'one_time'

    if not donor_name or not donor_phone or not amount:
        messages.error(request, "দয়া করে নাম, মোবাইল নম্বর এবং আর্থিক সহায়তার পরিমাণ সঠিকভাবে লিখুন।")
        return redirect(request.META.get('HTTP_REFERER') or '/?donate=1')

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            raise ValueError()
    except (ValueError, TypeError):
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
    Idempotent processor for verified completed donations:
    1. Updates donation status to 'approved'
    2. Updates program raised amount
    3. Records FinancialTransaction
    4. Dispatches SMS & Email receipts to donor
    5. Dispatches Admin alert SMS & Email
    """
    if donation.status == 'approved':
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

    donation.status = 'approved'
    donation.payment_method = payment_method
    donation.card_type = payment_method
    donation.bank_tran_id = invoice_id
    donation.trx_id = trx_id
    donation.save()

    # 1. Update Program raised_amount
    if donation.program:
        prog = donation.program
        prog.raised_amount = (prog.raised_amount or 0) + donation.amount
        prog.save()
        category_name = f"কার্যক্রম: {prog.title}"
        title_name = f"কার্যক্রম অনুদান - {prog.title} ({donation.donor_name})"
    elif donation.donation_type == 'volunteer_registration' or (donation.membership_id and str(donation.membership_id).startswith('NEW_VOL_')):
        category_name = 'সদস্য নিবন্ধন ফি'
        title_name = f"সদস্য নিবন্ধন ফি ({donation.donor_name})"
    elif donation.donation_type == 'volunteer':
        category_name = 'স্বেচ্ছাসেবক মাসিক চাঁদা / সহায়তা'
        title_name = f"স্বেচ্ছাসেবক চাঁদা ({donation.donor_name})"
    else:
        category_name = 'সাধারণ আর্থিক সহায়তা'
        title_name = f"সাধারণ আর্থিক সহায়তা ({donation.donor_name})"

    # Handle Volunteer registration approval & notification if applicable
    is_vol_reg = donation.donation_type == 'volunteer_registration' or (donation.membership_id and str(donation.membership_id).startswith('NEW_VOL_'))
    vol_obj = None
    if is_vol_reg:
        from volunteers.models import Volunteer, generate_unique_member_id
        from volunteers.views import send_member_notifications
        
        if donation.membership_id and str(donation.membership_id).startswith('NEW_VOL_'):
            try:
                vid = int(str(donation.membership_id).replace('NEW_VOL_', ''))
                vol_obj = Volunteer.objects.filter(pk=vid).first()
            except (ValueError, TypeError):
                pass
        if not vol_obj and donation.tran_id:
            vol_obj = Volunteer.objects.filter(tran_id=donation.tran_id).first()
        if not vol_obj and donation.donor_phone:
            vol_obj = Volunteer.objects.filter(phone=donation.donor_phone, status='pending').first()

        if vol_obj:
            vol_obj.status = 'approved'
            vol_obj.payment_status = 'paid'
            vol_obj.payment_method = payment_method
            vol_obj.trx_id = trx_id
            if not vol_obj.member_id:
                vol_obj.member_id = generate_unique_member_id(prefix_str="")
            vol_obj.save()
            donation.membership_id = vol_obj.member_id
            donation.save(update_fields=['membership_id'])
            try:
                send_member_notifications(vol_obj)
            except Exception as ex:
                logger.error(f"[VOL NOTIFY ERROR ON PAYMENT PROCESS] {ex}")

    trx_note = f"পেমেন্ট মাধ্যম: {payment_method} | TrxID: {trx_id} | ইনভয়েস: {invoice_id} | মোবাইল: {donation.donor_phone}"
    if donation.membership_id:
        trx_note += f" | মেম্বার আইডি: {donation.membership_id}"
    if donation.program:
        trx_note += f" | কার্যক্রম: {donation.program.title}"
    if donation.note:
        trx_note += f" | নোট: {donation.note}"

    # 2. Record FinancialTransaction (income) if not already created
    if not FinancialTransaction.objects.filter(trx_id=trx_id, transaction_type='income').exists():
        FinancialTransaction.objects.create(
            transaction_type='income',
            program=donation.program,
            title=title_name,
            category=category_name,
            amount=donation.amount,
            payment_method=payment_method,
            trx_id=trx_id,
            donor_name=donation.donor_name,
            date=date.today(),
            note=trx_note
        )

    # 3. Dispatch Notifications to Donor & Admin
    if not vol_obj:
        from donations.donation_notifications import notify_donor_donation_approved
        try:
            notify_donor_donation_approved(donation, request=request)
        except Exception as ex:
            logger.error(f"[DONATION APPROVAL NOTIFICATIONS ERROR] {ex}")

    return donation


@csrf_exempt
def payment_success(request):
    """
    Official Payment Gateway Success Callback.
    Verifies transaction with PayStation or Paymently Verify API, updates donation,
    logs financial transaction, dispatches notifications, and shows official receipt.
    """
    invoice_number = request.GET.get('invoice_number') or request.POST.get('invoice_number')
    invoice_id = request.GET.get('invoice_id') or request.POST.get('invoice_id')
    tran_id = request.GET.get('tran_id') or request.POST.get('tran_id') or invoice_number

    # 1. PayStation Verification
    target_invoice = invoice_number or tran_id
    if target_invoice:
        ps_res = verify_paystation_payment(target_invoice)
        if str(ps_res.get('status_code')) == '200' and ps_res.get('data'):
            ps_data = ps_res['data']
            if str(ps_data.get('trx_status', '')).lower() == 'success':
                donation = ProgramDonation.objects.filter(tran_id=target_invoice).first()
                if donation:
                    payment_data = {
                        'payment_method': ps_data.get('payment_method') or 'PayStation',
                        'transaction_id': ps_data.get('trx_id') or target_invoice,
                        'invoice_id': target_invoice,
                        'amount': ps_data.get('payment_amount') or donation.amount
                    }
                    process_successful_payment(donation, payment_data, request=request)
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

    invoice_number = payload.get('invoice_number')
    trx_status = str(payload.get('trx_status', '')).lower()

    # 1. PayStation IPN handler
    if invoice_number and trx_status == 'success':
        donation = ProgramDonation.objects.filter(tran_id=invoice_number).first()
        if donation:
            payment_data = {
                'payment_method': payload.get('payment_method') or 'PayStation',
                'transaction_id': payload.get('trx_id') or invoice_number,
                'invoice_id': invoice_number,
                'amount': payload.get('trx_amount') or donation.amount
            }
            process_successful_payment(donation, payment_data, request=request)
            return JsonResponse({'status': 'success'})

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
                process_successful_payment(donation, verification_res, request=request)
                return JsonResponse({'status': 'SUCCESS', 'message': 'Payment approved'})

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
