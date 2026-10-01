import os
import logging
import requests
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)

def get_paymently_config():
    """
    Retrieves the active UddoktaPay / Paymently gateway configuration.
    Priority:
    1. Active PaymentGatewaySetting in database (if provider is paymently or uddoktapay)
    2. Django settings (PAYMENTLY_API_KEY, PAYMENTLY_API_URL)
    3. Environment variables or fallback default
    """
    api_key = getattr(settings, 'PAYMENTLY_API_KEY', os.getenv('PAYMENTLY_API_KEY', '')).strip()
    api_url = getattr(settings, 'PAYMENTLY_API_URL', os.getenv('PAYMENTLY_API_URL', 'https://helplinehellonaogaon.paymently.io/api')).strip()

    try:
        from .models import PaymentGatewaySetting
        db_setting = PaymentGatewaySetting.objects.filter(is_active=True).first()
        if db_setting:
            if db_setting.store_password:
                api_key = db_setting.store_password.strip()
            if db_setting.store_id and ('http' in db_setting.store_id):
                api_url = db_setting.store_id.strip()
    except Exception as e:
        logger.warning(f"Could not load PaymentGatewaySetting from DB: {e}")

    # Fallback to confirmed live credentials if empty
    if not api_key:
        api_key = 'METB4CSw9c4KcIB7P5HejGqbCE8lNSYsAfmJWzTp'
    if not api_url:
        api_url = 'https://helplinehellonaogaon.paymently.io/api'

    return {
        'api_key': api_key,
        'api_url': api_url.rstrip('/'),
    }

def initiate_paymently_session(request, donation):
    """
    Directly initiates an automated hosted checkout session with UddoktaPay / Paymently.
    Returns:
        {
            'success': True,
            'payment_url': 'https://helplinehellonaogaon.paymently.io/checkout/...',
            'message': 'Success'
        }
        or
        {
            'success': False,
            'error': 'Error description'
        }
    """
    config = get_paymently_config()
    api_key = config['api_key']
    api_url = config['api_url']

    checkout_url = f"{api_url}/checkout-v2"

    domain = request.build_absolute_uri('/')[:-1]
    redirect_url = f"{domain}{reverse('donations:payment_success')}"
    cancel_url = f"{domain}{reverse('donations:payment_cancel')}"
    webhook_url = f"{domain}{reverse('donations:payment_ipn')}"

    headers = {
        'RT-UDDOKTAPAY-API-KEY': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    payload = {
        'full_name': donation.donor_name or 'Donor',
        'email': donation.donor_email or 'info@helplinehellonaogaon.com',
        'amount': f"{donation.amount:.2f}",
        'metadata': {
            'tran_id': donation.tran_id,
            'donation_id': str(donation.id),
            'donor_phone': donation.donor_phone or '',
            'membership_id': donation.membership_id or '',
            'donation_type': donation.donation_type,
        },
        'redirect_url': redirect_url,
        'cancel_url': cancel_url,
        'webhook_url': webhook_url,
    }

    try:
        response = requests.post(checkout_url, json=payload, headers=headers, timeout=15)
        res_data = response.json()
        logger.info(f"Paymently Checkout Response [{response.status_code}]: {res_data}")

        if response.status_code == 200 and res_data.get('payment_url'):
            return {
                'success': True,
                'payment_url': res_data['payment_url'],
                'message': res_data.get('message', 'Success'),
            }
        else:
            error_reason = res_data.get('message') or res_data.get('error') or f"HTTP {response.status_code}"
            logger.error(f"Paymently Session Error: {error_reason}")
            return {
                'success': False,
                'error': error_reason
            }
    except Exception as e:
        logger.error(f"Failed to connect to Paymently API: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def verify_paymently_payment(invoice_id):
    """
    Validates a transaction directly with Paymently / UddoktaPay Verify API.
    Returns:
        JSON response with payment details, status ('COMPLETED', 'PENDING', etc.),
        transaction_id (bKash/Nagad TrxID), amount, and metadata.
    """
    if not invoice_id:
        return {'status': 'INVALID', 'message': 'No invoice_id provided'}

    config = get_paymently_config()
    api_key = config['api_key']
    api_url = config['api_url']

    verify_url = f"{api_url}/verify-payment"

    headers = {
        'RT-UDDOKTAPAY-API-KEY': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    payload = {
        'invoice_id': invoice_id
    }

    try:
        response = requests.post(verify_url, json=payload, headers=headers, timeout=15)
        res_data = response.json()
        logger.info(f"Paymently Validation Response [{response.status_code}] for invoice {invoice_id}: {res_data.get('status')}")
        return res_data
    except Exception as e:
        logger.error(f"Paymently Validation API error: {e}")
        return {'status': 'ERROR', 'message': str(e)}

# Backward compatibility wrappers
def get_gateway_config():
    return get_paymently_config()

def initiate_payment_gateway_session(request, donation):
    res = initiate_paymently_session(request, donation)
    if res.get('success'):
        return {
            'success': True,
            'gateway_url': res.get('payment_url'),
            'sessionkey': donation.tran_id
        }
    return res

def validate_gateway_payment(val_id):
    return verify_paymently_payment(val_id)
