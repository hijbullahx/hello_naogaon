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

def donation_page_view(request):
    """
    View to display the main donation page with all its components.
    """
    content, _ = DonationPageContent.objects.get_or_create(pk=1)
    
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
    }
    return render(request, 'donations/donation_page.html', context)

@require_POST
def submit_program_donation(request):
    """
    Handles financial contributions submitted for specific programs ("আমাদের কার্যক্রম").
    Creates a ProgramDonation record and automatically logs an Income FinancialTransaction.
    """
    program_id = request.POST.get('program_id')
    donor_name = request.POST.get('donor_name', '').strip()
    donor_email = request.POST.get('donor_email', '').strip()
    donor_phone = request.POST.get('donor_phone', '').strip()
    membership_id = request.POST.get('membership_id', '').strip()
    amount = request.POST.get('amount')
    payment_method = request.POST.get('payment_method', 'bKash')
    trx_id = request.POST.get('trx_id', '').strip()
    note = request.POST.get('note', '').strip()

    if not donor_name or not donor_phone or not amount:
        messages.error(request, "দয়া করে নাম, মোবাইল নম্বর এবং সহায়তার পরিমাণ পূরণ করুন।")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        messages.error(request, "দয়া করে সঠিক আর্থিক পরিমাণ লিখুন।")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    program = None
    if program_id and str(program_id).isdigit():
        program = Program.objects.filter(pk=program_id).first()

    # 1. Save ProgramDonation Record
    donation = ProgramDonation.objects.create(
        program=program,
        donor_name=donor_name,
        donor_email=donor_email,
        donor_phone=donor_phone,
        membership_id=membership_id,
        amount=amount_val,
        payment_method=payment_method,
        trx_id=trx_id,
        note=note,
        status='approved'
    )

    # 2. Automatically record in Financial Management as Income
    prog_title = program.title if program else "সাধারণ কার্যক্রম"
    trx_note = f"Program: {prog_title} | Member ID: {membership_id or 'N/A'} | Email: {donor_email} | Phone: {donor_phone}"
    if note:
        trx_note += f" | Note: {note}"

    FinancialTransaction.objects.create(
        transaction_type='income',
        title=f"কার্যক্রম সহায়তা: {prog_title} ({donor_name})",
        category=f"কার্যক্রম সহায়তা - {prog_title}",
        amount=amount_val,
        payment_method=payment_method,
        trx_id=trx_id,
        donor_name=donor_name,
        date=date.today(),
        note=trx_note
    )

    messages.success(request, f'ধন্যবাদ {donor_name}! "{prog_title}" কার্যক্রমে আপনার ৳{amount_val:,.2f} আর্থিক সহায়তা সফলভাবে গৃহীত হয়েছে।')
    return redirect(request.META.get('HTTP_REFERER', '/'))
