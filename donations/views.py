from django.shortcuts import render
from .models import (
    DonationPageContent,
    Campaign,
    DonationImpact,
    EmergencyAppeal,
    DonationMethod,
    Bank,
    QRCode,
    FAQ,
    DonationStatistic
)

def donation_page_view(request):
    """
    View to display the main donation page with all its components.
    """
    # Use .first() assuming there's only one, or create one if it doesn't exist
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
