import os
import logging
import requests
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)

# ==========================================
# PAYSTATION GATEWAY (100% Direct OTP / PIN)
# ==========================================

def get_paystation_config():
    """
    Retrieves PayStation Payment Gateway configuration.
    Defaults to sandbox test credentials provided by PayStation.
    """
    merchant_id = getattr(settings, 'PAYSTATION_MERCHANT_ID', os.getenv('PAYSTATION_MERCHANT_ID', '104-1653730183')).strip()
    password = getattr(settings, 'PAYSTATION_PASSWORD', os.getenv('PAYSTATION_PASSWORD', 'gamecoderstorepass')).strip()
    is_sandbox = getattr(settings, 'PAYSTATION_IS_SANDBOX', os.getenv('PAYSTATION_IS_SANDBOX', 'True') == 'True')

    base_url = 'https://sandbox.paystation.com.bd' if is_sandbox else 'https://api.paystation.com.bd'

    return {
        'merchant_id': merchant_id,
        'password': password,
        'is_sandbox': is_sandbox,
        'base_url': base_url
    }

def initiate_paystation_session(request, donation):
    """
    Initiates an official direct hosted checkout session with PayStation.
    Includes direct bKash (OTP+PIN), Nagad (OTP+PIN), Rocket, Upay, Cards (Visa/Mastercard), and all Banks.
    """
    config = get_paystation_config()
    url = f"{config['base_url']}/initiate-payment"

    domain = request.build_absolute_uri('/')[:-1]
    callback_url = f"{domain}{reverse('donations:payment_success')}"

    payload = {
        'merchantId': config['merchant_id'],
        'password': config['password'],
        'invoice_number': donation.tran_id,
        'currency': 'BDT',
        'payment_amount': f"{donation.amount:.2f}",
        'pay_with_charge': '0',
        'reference': f"Helpline Hello Naogaon {donation.donation_type}",
        'cust_name': donation.donor_name or 'Donor',
        'cust_phone': donation.donor_phone or '01700000000',
        'cust_email': donation.donor_email or 'info@helplinehellonaogaon.com',
        'cust_address': 'Naogaon, Bangladesh',
        'callback_url': callback_url,
        'opt_a': str(donation.id),
        'opt_b': donation.membership_id or '',
        'opt_c': donation.donation_type,
    }

    try:
        response = requests.post(url, headers={'Accept': 'application/json'}, data=payload, timeout=15)
        res_data = response.json()
        logger.info(f"PayStation Initiate Response [{response.status_code}]: {res_data}")

        if str(res_data.get('status_code')) == '200' and res_data.get('payment_url'):
            return {
                'success': True,
                'payment_url': res_data['payment_url'],
                'invoice_number': res_data.get('invoice_number', donation.tran_id)
            }
        else:
            error_msg = res_data.get('message', 'Failed to create payment link')
            logger.error(f"PayStation Error: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    except Exception as e:
        logger.error(f"PayStation Connection Error: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def verify_paystation_payment(invoice_number):
    """
    Queries PayStation Transaction Status v1 API using unique invoice_number.
    """
    if not invoice_number:
        return {'status_code': '400', 'status': 'failed', 'message': 'No invoice_number provided'}

    config = get_paystation_config()
    url = f"{config['base_url']}/transaction-status"

    headers = {
        'merchantId': config['merchant_id']
    }
    payload = {
        'invoice_number': invoice_number
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        res_data = response.json()
        logger.info(f"PayStation Status Response [{response.status_code}] for {invoice_number}: {res_data}")
        return res_data
    except Exception as e:
        logger.error(f"PayStation Status API Error: {e}")
        return {'status_code': '500', 'status': 'failed', 'message': str(e)}


# ==========================================
# PAYMENTLY / UDDOKTAPAY GATEWAY
# ==========================================

def get_paymently_config():
    """
    Retrieves the active UddoktaPay / Paymently gateway configuration.
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

    if not api_key:
        api_key = 'METB4CSw9c4KcIB7P5HejGqbCE8lNSYsAfmJWzTp'
    if not api_url:
        api_url = 'https://helplinehellonaogaon.paymently.io/api'

    return {
        'api_key': api_key,
        'api_url': api_url.rstrip('/'),
    }

def initiate_paymently_session(request, donation):
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


# ==========================================
# ACTIVE GATEWAY UNIFIED DISPATCHER
# ==========================================

def initiate_active_gateway_session(request, donation):
    """
    Intelligently routes to the configured active payment gateway:
    Priority: PayStation (Direct OTP/PIN) -> Fallback: Paymently.
    """
    active_gateway = getattr(settings, 'ACTIVE_PAYMENT_GATEWAY', 'paystation').lower()
    if active_gateway == 'paystation':
        res = initiate_paystation_session(request, donation)
        if res.get('success'):
            return res
        logger.warning(f"PayStation session initiation failed, falling back to Paymently: {res.get('error')}")

    return initiate_paymently_session(request, donation)


# Backward compatibility wrappers
def get_gateway_config():
    return get_paystation_config()

def initiate_payment_gateway_session(request, donation):
    res = initiate_active_gateway_session(request, donation)
    if res.get('success'):
        return {
            'success': True,
            'gateway_url': res.get('payment_url'),
            'sessionkey': donation.tran_id
        }
    return res

def validate_gateway_payment(val_id):
    active_gateway = getattr(settings, 'ACTIVE_PAYMENT_GATEWAY', 'paystation').lower()
    if active_gateway == 'paystation':
        return verify_paystation_payment(val_id)
    return verify_paymently_payment(val_id)
