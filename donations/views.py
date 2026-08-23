from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from datetime import date
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

def donation_page_view(request):
    """
    View to display the main financial support (donation) page with all components.
    """
    content, _ = DonationPageContent.objects.get_or_create(pk=1)
    
    # Pre-select volunteer if member_id is in query params (e.g. from SMS/Email reminder ?member_id=26082301)
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

@require_POST
def submit_donation(request):
    """
    Handles general, volunteer fee, emergency relief, and program financial contributions.
    """
    donation_type = request.POST.get('donation_type', 'general').strip()
    frequency = request.POST.get('frequency', 'one_time').strip()
    program_id = request.POST.get('program_id')
    donor_name = request.POST.get('donor_name', '').strip()
    donor_email = request.POST.get('donor_email', '').strip()
    donor_phone = request.POST.get('donor_phone', '').strip()
    membership_id = request.POST.get('membership_id', '').strip()
    amount = request.POST.get('amount')
    payment_method = request.POST.get('payment_method', 'bKash').strip()
    trx_id = request.POST.get('trx_id', '').strip()
    note = request.POST.get('note', '').strip()

    # If membership_id is provided, check if volunteer exists to supplement name/phone if blank
    if membership_id:
        vol = Volunteer.objects.filter(member_id=membership_id).first()
        if vol:
            if not donor_name:
                donor_name = vol.full_name
            if not donor_phone:
                donor_phone = vol.phone
            if not donor_email and vol.email:
                donor_email = vol.email

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

    program = None
    if program_id and str(program_id).isdigit():
        program = Program.objects.filter(pk=program_id).first()

    donation = ProgramDonation.objects.create(
        donation_type=donation_type,
        frequency=frequency,
        program=program,
        donor_name=donor_name,
        donor_email=donor_email,
        donor_phone=donor_phone,
        membership_id=membership_id if membership_id else None,
        amount=amount_val,
        payment_method=payment_method,
        trx_id=trx_id,
        note=note,
        status='approved'
    )

    # Automatically record in Financial Transactions (Income)
    type_labels = {
        'volunteer': 'স্বেচ্ছাসেবক অনুদান / মাসিক চাঁদা',
        'general': 'সাধারণ আর্থিক সহায়তা',
        'program': f"কার্যক্রম সহায়তা - {program.title if program else 'সাধারণ'}",
        'emergency': 'জরুরি ত্রাণ ও চিকিৎসা তহবিল',
    }
    category_name = type_labels.get(donation_type, 'আর্থিক সহায়তা')
    trx_note = f"সহায়তার ধরন: {category_name} | ফ্রিকোয়েন্সি: {frequency} | মেম্বার আইডি: {membership_id or 'N/A'} | মোবাইল: {donor_phone}"
    if note:
        trx_note += f" | নোট: {note}"

    FinancialTransaction.objects.create(
        transaction_type='income',
        title=f"{category_name} ({donor_name})",
        category=category_name,
        amount=amount_val,
        payment_method=payment_method,
        trx_id=trx_id,
        donor_name=donor_name,
        date=date.today(),
        note=trx_note
    )

    member_txt = f" (সদস্য আইডি: {membership_id})" if membership_id else ""
    messages.success(
        request, 
        f'ধন্যবাদ {donor_name}{member_txt}! {category_name}-এ আপনার ৳{amount_val:,.2f} আর্থিক সহায়তা সফলভাবে গৃহীত হয়েছে। আপনার অনুদান মানুষের কল্যাণে ভূমিকা রাখবে।'
    )
    return redirect('donations:donate')


@require_POST
def submit_program_donation(request):
    """
    Handles financial contributions submitted for specific programs ("আমাদের কার্যক্রম").
    """
    return submit_donation(request)

