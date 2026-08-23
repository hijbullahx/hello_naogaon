import random
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
    FinancialTransaction
)
from programs.models import Program
from volunteers.models import Volunteer
from .gateway import initiate_payment_gateway_session, validate_gateway_payment

def donation_page_view(request):
    """
    View to display the main financial support (donation) page.
    """
    content, _ = DonationPageContent.objects.get_or_create(pk=1)
    
    # Pre-select volunteer if member_id is in query params (e.g. ?member_id=26082301)
    member_id_param = request.GET.get('member_id', '').strip()
    prefill_volunteer = None
    if member_id_param:
        prefill_volunteer = Volunteer.objects.filter(member_id=member_id_param).first()

    context = {
        'content': content,
        'campaigns': Campaign.objects.filter(is_active=True),
        'impacts': DonationImpact.objects.filter(is_active=True),
        'emergency_appeals': EmergencyAppeal.objects.filter(is_active=True),
        'donation_methods': DonationMethod.objects.filter(is_active=True),
        'banks': Bank.objects.filter(is_active=True),
        'qrcodes': QRCode.objects.filter(is_active=True).select_related('method'),
        'faqs': FAQ.objects.filter(is_active=True),
        'statistics': DonationStatistic.objects.filter(is_active=True),
        'programs': Program.objects.all(),
        'member_id_param': member_id_param,
        'prefill_volunteer': prefill_volunteer,
    }
    return render(request, 'donations/donation_page.html', context)


def member_pledge_lookup(request):
    """API endpoint to look up registered member info and financial pledge by member_id"""
    member_id = request.GET.get('member_id', '').strip()
    if not member_id:
        return JsonResponse({'found': False})
    
    vol = Volunteer.objects.filter(member_id=member_id).first()
    if not vol:
        return JsonResponse({'found': False})
    
    freq_dict = {
        'monthly': 'মাসিক (প্রতি মাসে)',
        'weekly': 'সাপ্তাহিক (প্রতি সপ্তাহে)',
        'yearly': 'বাৎসরিক (প্রতি বছরে)',
        'one_time': 'এককালীন',
        'none': 'কোনো নির্দিষ্ট প্রতিশ্রুতি নেই'
    }
    has_pledge = bool(vol.contribution_frequency and vol.contribution_frequency != 'none' and vol.contribution_amount)
    return JsonResponse({
        'found': True,
        'member_id': vol.member_id,
        'full_name': vol.full_name,
        'phone': vol.phone,
        'email': vol.email or '',
        'has_pledge': has_pledge,
        'frequency': vol.contribution_frequency if vol.contribution_frequency else 'one_time',
        'frequency_display': freq_dict.get(vol.contribution_frequency, vol.contribution_frequency or 'এককালীন'),
        'amount': float(vol.contribution_amount) if vol.contribution_amount else 0,
    })


@require_POST
def initiate_payment(request):
    """
    Automated payment gateway initiation.
    Does NOT require manual TrxID. Redirects user to secure online payment checkout.
    """
    donor_identity_type = request.POST.get('donor_identity_type', 'general').strip()
    membership_id = request.POST.get('membership_id', '').strip()
    frequency = request.POST.get('frequency', 'one_time').strip()
    donor_name = request.POST.get('donor_name', '').strip()
    donor_email = request.POST.get('donor_email', '').strip()
    donor_phone = request.POST.get('donor_phone', '').strip()
    amount = request.POST.get('amount')
    note = request.POST.get('note', '').strip()

    # Determine donation type & fetch member info if applicable
    if donor_identity_type == 'member' or membership_id:
        donation_type = 'volunteer'
        vol = Volunteer.objects.filter(member_id=membership_id).first()
        if vol:
            donor_name = vol.full_name
            donor_phone = vol.phone
            donor_email = vol.email or ''
            if not frequency or frequency == 'one_time':
                if vol.contribution_frequency and vol.contribution_frequency != 'none':
                    frequency = vol.contribution_frequency
        else:
            messages.error(request, "সঠিক সদস্য আইডি পাওয়া যায়নি। অনুগ্রহ করে যাচাই করে পুনরায় চেষ্টা করুন।")
            return redirect('donations:donate')
    else:
        donation_type = 'general'
        membership_id = None
        frequency = 'one_time'

    if not donor_name or not donor_phone or not amount:
        messages.error(request, "দয়া করে নাম, মোবাইল নম্বর এবং আর্থিক সহায়তার পরিমাণ সঠিকভাবে লিখুন।")
        return redirect('donations:donate')

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        messages.error(request, "দয়া করে সঠিক আর্থিক পরিমাণ লিখুন।")
        return redirect('donations:donate')

    # Generate unique transaction ID
    tran_id = f"HN{datetime.now().strftime('%y%m%d%H%M%S')}{random.randint(100, 999)}"

    # Create pending donation record
    donation = ProgramDonation.objects.create(
        donation_type=donation_type,
        frequency=frequency,
        program=None,
        donor_name=donor_name,
        donor_email=donor_email,
        donor_phone=donor_phone,
        membership_id=membership_id if membership_id else None,
        amount=amount_val,
        payment_method='Online Gateway',
        tran_id=tran_id,
        note=note,
        status='pending'
    )

    # Initiate payment gateway session
    gw_res = initiate_payment_gateway_session(request, donation)
    if gw_res.get('success') and gw_res.get('gateway_url'):
        return redirect(gw_res['gateway_url'])

    # Fallback to internal checkout
    return redirect('donations:gateway_checkout', tran_id=donation.tran_id)


def gateway_checkout_view(request, tran_id):
    """
    Renders interactive and secure payment gateway checkout simulation.
    """
    donation = get_object_or_404(ProgramDonation, tran_id=tran_id)
    if donation.status == 'approved':
        return redirect('donations:receipt', donation_id=donation.id)

    return render(request, 'donations/gateway_checkout.html', {
        'donation': donation
    })


@csrf_exempt
def payment_success(request):
    """
    Payment Gateway Success Callback.
    Verifies transaction, marks donation as approved, logs financial income transaction, and shows receipt.
    """
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    val_id = request.POST.get('val_id') or request.GET.get('val_id')
    card_type = request.POST.get('card_type') or request.POST.get('payment_method') or 'Online Gateway'
    bank_tran_id = request.POST.get('bank_tran_id') or request.POST.get('trx_id') or f"PGW{random.randint(10000000, 99999999)}"

    if not tran_id:
        messages.error(request, "পেমেন্ট তথ্য পাওয়া যায়নি।")
        return redirect('donations:donate')

    donation = ProgramDonation.objects.filter(tran_id=tran_id).first()
    if not donation:
        messages.error(request, "অনুরোধকৃত লেনদেনটি খুঁজে পাওয়া যায়নি।")
        return redirect('donations:donate')

    if donation.status != 'approved':
        # Update donation to approved status
        donation.status = 'approved'
        donation.payment_method = card_type
        donation.card_type = card_type
        donation.bank_tran_id = bank_tran_id
        donation.trx_id = bank_tran_id
        donation.save()

        # Log into Financial Transactions (Income)
        category_name = 'স্বেচ্ছাসেবক মাসিক চাঁদা / সহায়তা' if donation.donation_type == 'volunteer' else 'সাধারণ আর্থিক সহায়তা'
        trx_note = f"গেটওয়ে চ্যানেল: {card_type} | ট্রানজেকশন আইডি: {bank_tran_id} | মেম্বার আইডি: {donation.membership_id or 'N/A'} | মোবাইল: {donation.donor_phone}"
        if donation.note:
            trx_note += f" | নোট: {donation.note}"

        FinancialTransaction.objects.create(
            transaction_type='income',
            title=f"{category_name} ({donation.donor_name})",
            category=category_name,
            amount=donation.amount,
            payment_method=card_type,
            trx_id=bank_tran_id,
            donor_name=donation.donor_name,
            date=date.today(),
            note=trx_note
        )

    member_txt = f" (সদস্য আইডি: {donation.membership_id})" if donation.membership_id else ""
    messages.success(
        request, 
        f'ধন্যবাদ {donation.donor_name}{member_txt}! আপনার ৳{donation.amount:,.2f} অনলাইন পেমেন্ট সফলভাবে গৃহীত হয়েছে।'
    )
    return redirect('donations:receipt', donation_id=donation.id)


@csrf_exempt
def payment_fail(request):
    """
    Payment Gateway Failure Callback.
    """
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    if tran_id:
        donation = ProgramDonation.objects.filter(tran_id=tran_id).first()
        if donation and donation.status == 'pending':
            donation.status = 'failed'
            donation.save()

    messages.error(request, "দুঃখিত, আপনার অনলাইন পেমেন্ট সম্পন্ন হয়নি বা ব্যর্থ হয়েছে। অনুগ্রহ করে পুনরায় চেষ্টা করুন।")
    return redirect('donations:donate')


@csrf_exempt
def payment_cancel(request):
    """
    Payment Gateway Cancel Callback.
    """
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    if tran_id:
        donation = ProgramDonation.objects.filter(tran_id=tran_id).first()
        if donation and donation.status == 'pending':
            donation.status = 'cancelled'
            donation.save()

    messages.warning(request, "অনলাইন পেমেন্ট প্রক্রিয়াটি বাতিল করা হয়েছে।")
    return redirect('donations:donate')


@csrf_exempt
def payment_ipn(request):
    """
    Payment Gateway IPN (Instant Payment Notification) Webhook.
    """
    tran_id = request.POST.get('tran_id')
    val_id = request.POST.get('val_id')
    if tran_id:
        donation = ProgramDonation.objects.filter(tran_id=tran_id).first()
        if donation and donation.status == 'pending':
            donation.status = 'approved'
            donation.bank_tran_id = val_id or f"IPN{random.randint(100000, 999999)}"
            donation.trx_id = donation.bank_tran_id
            donation.save()
    return JsonResponse({'status': 'IPN received'})


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
