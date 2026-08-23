import os
import logging
import requests
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)

def get_gateway_config():
    """
    Retrieves the active payment gateway configuration from database (PaymentGatewaySetting)
    or falls back to environment variables and settings.
    """
    try:
        from .models import PaymentGatewaySetting
        config = PaymentGatewaySetting.objects.filter(is_active=True).first()
        if config and config.store_id and config.store_password:
            return {
                'provider': config.provider,
                'store_id': config.store_id.strip(),
                'store_passwd': config.store_password.strip(),
                'is_sandbox': config.is_sandbox,
            }
    except Exception as e:
        logger.warning(f"Could not load PaymentGatewaySetting from DB: {e}")

    # Fallback to settings / env variables
    store_id = getattr(settings, 'SSLCOMMERZ_STORE_ID', os.getenv('SSLCOMMERZ_STORE_ID', 'testbox')).strip()
    store_passwd = getattr(settings, 'SSLCOMMERZ_STORE_PASS', os.getenv('SSLCOMMERZ_STORE_PASS', 'qwerty')).strip()
    is_sandbox = getattr(settings, 'SSLCOMMERZ_IS_SANDBOX', os.getenv('SSLCOMMERZ_IS_SANDBOX', 'True') == 'True')

    return {
        'provider': 'sslcommerz',
        'store_id': store_id or 'testbox',
        'store_passwd': store_passwd or 'qwerty',
        'is_sandbox': is_sandbox,
    }

def get_sslcommerz_api_urls(is_sandbox=True):
    if is_sandbox:
        return {
            'session': 'https://sandbox.sslcommerz.com/gwprocess/v4/api.php',
            'validate': 'https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php',
        }
    return {
        'session': 'https://securepay.sslcommerz.com/gwprocess/v4/api.php',
        'validate': 'https://securepay.sslcommerz.com/validator/api/validationserverAPI.php',
    }

def initiate_payment_gateway_session(request, donation):
    """
    Directly initiates an official payment gateway session with SSLCommerz API.
    Returns the official GatewayPageURL to redirect the user to the gateway checkout.
    """
    config = get_gateway_config()
    urls = get_sslcommerz_api_urls(config['is_sandbox'])

    domain = request.build_absolute_uri('/')[:-1]
    success_url = f"{domain}{reverse('donations:payment_success')}"
    fail_url = f"{domain}{reverse('donations:payment_fail')}"
    cancel_url = f"{domain}{reverse('donations:payment_cancel')}"
    ipn_url = f"{domain}{reverse('donations:payment_ipn')}"

    post_data = {
        'store_id': config['store_id'],
        'store_passwd': config['store_passwd'],
        'total_amount': f"{donation.amount:.2f}",
        'currency': 'BDT',
        'tran_id': donation.tran_id,
        'success_url': success_url,
        'fail_url': fail_url,
        'cancel_url': cancel_url,
        'ipn_url': ipn_url,
        'cus_name': donation.donor_name or 'Donor',
        'cus_email': donation.donor_email or 'info@helplinehellonaogaon.com',
        'cus_phone': donation.donor_phone or '01700000000',
        'cus_add1': 'Naogaon, Bangladesh',
        'cus_city': 'Naogaon',
        'cus_country': 'Bangladesh',
        'shipping_method': 'NO',
        'product_name': 'Helpline Hello Naogaon Financial Contribution',
        'product_category': 'Charity Donation',
        'product_profile': 'non-physical-goods',
        'value_a': str(donation.id),
        'value_b': donation.membership_id or '',
        'value_c': donation.donation_type,
    }

    try:
        response = requests.post(urls['session'], data=post_data, timeout=12)
        res_data = response.json()
        if res_data.get('status') == 'SUCCESS' and res_data.get('GatewayPageURL'):
            logger.info(f"SSLCommerz Session created successfully for {donation.tran_id}: {res_data.get('sessionkey')}")
            return {
                'success': True,
                'gateway_url': res_data['GatewayPageURL'],
                'sessionkey': res_data.get('sessionkey')
            }
        else:
            error_reason = res_data.get('failedreason', 'Unknown Gateway Error')
            logger.error(f"SSLCommerz Session Error: {error_reason}")
            return {
                'success': False,
                'error': error_reason
            }
    except Exception as e:
        logger.error(f"Failed to connect to SSLCommerz API: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def validate_gateway_payment(val_id):
    """
    Validates a transaction directly with SSLCommerz Validation Server.
    """
    if not val_id:
        return {'status': 'INVALID', 'error': 'No val_id provided'}

    config = get_gateway_config()
    urls = get_sslcommerz_api_urls(config['is_sandbox'])

    params = {
        'val_id': val_id,
        'store_id': config['store_id'],
        'store_passwd': config['store_passwd'],
        'format': 'json'
    }

    try:
        response = requests.get(urls['validate'], params=params, timeout=12)
        res_data = response.json()
        logger.info(f"SSLCommerz Validation Response: {res_data.get('status')} for val_id: {val_id}")
        return res_data
    except Exception as e:
        logger.error(f"SSLCommerz Validation API error: {e}")
        return {'status': 'ERROR', 'error': str(e)}
