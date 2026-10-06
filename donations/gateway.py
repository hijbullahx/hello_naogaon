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
    Priority: PaymentGatewaySetting (DB) -> settings / .env.
    Defaults to live production credentials.
    """
    merchant_id = getattr(settings, 'PAYSTATION_MERCHANT_ID', os.getenv('PAYSTATION_MERCHANT_ID', '')).strip()
    password = getattr(settings, 'PAYSTATION_PASSWORD', os.getenv('PAYSTATION_PASSWORD', '')).strip()
    is_sandbox = getattr(settings, 'PAYSTATION_IS_SANDBOX', os.getenv('PAYSTATION_IS_SANDBOX', 'False') == 'True')

    try:
        from .models import PaymentGatewaySetting
        db_setting = PaymentGatewaySetting.objects.filter(is_active=True).first()
        if db_setting and db_setting.store_id:
            merchant_id = db_setting.store_id.strip()
            if db_setting.store_password:
                password = db_setting.store_password.strip()
            is_sandbox = db_setting.is_sandbox
    except Exception as e:
        logger.warning(f"Could not load PaymentGatewaySetting from DB: {e}")

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

    # Format payment amount cleanly (integer if whole, float otherwise)
    try:
        amt_float = float(donation.amount)
        if amt_float.is_integer():
            amount_str = str(int(amt_float))
        else:
            amount_str = f"{amt_float:.2f}"
    except Exception:
        amount_str = str(donation.amount)

    payload = {
        'merchantId': config['merchant_id'],
        'password': config['password'],
        'invoice_number': donation.tran_id,
        'currency': 'BDT',
        'payment_amount': amount_str,
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

def get_paystation_dashboard_data():
    """
    Computes and aggregates PayStation Payment Gateway metrics matching
    the merchant dashboard (merchant.paystation.com.bd).
    Returns summary stats, method breakdowns, and recent transactions.
    """
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Q, Sum
    from .models import ProgramDonation

    config = get_paystation_config()
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate last month boundaries
    first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_of_last_month = first_of_this_month - timedelta(seconds=1)
    first_of_last_month = last_day_of_last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Query approved gateway transactions (excluding manual bKash/Nagad send-money)
    gateway_qs = ProgramDonation.objects.filter(
        status='approved'
    ).filter(
        Q(tran_id__isnull=False) & ~Q(tran_id='')
    ).exclude(
        payment_method__icontains='Manual'
    ).exclude(
        payment_method__icontains='ম্যানুয়াল'
    ).order_by('-created_at')

    # Aggregations
    total_col = float(gateway_qs.aggregate(total=Sum('amount'))['total'] or 0.0)
    today_col = float(gateway_qs.filter(created_at__gte=today_start).aggregate(total=Sum('amount'))['total'] or 0.0)
    last_month_col = float(gateway_qs.filter(
        created_at__gte=first_of_last_month,
        created_at__lte=last_day_of_last_month
    ).aggregate(total=Sum('amount'))['total'] or 0.0)

    # In PayStation, recent collections are unsettled until payout cycle
    unsettled_amt = total_col

    # Percentages
    today_pct = 100.0 if today_col > 0 else 0.0
    total_pct = 0.0
    last_month_pct = 0.0
    unsettled_pct = 0.0

    # Payment Methods breakdown
    methods_dict = {
        'bkash': {'name': 'BKash', 'amount': 0.0, 'count': 0, 'color': '#e2136e', 'icon': 'fas fa-mobile-alt'},
        'nagad': {'name': 'Nagad', 'amount': 0.0, 'count': 0, 'color': '#f7941d', 'icon': 'fas fa-wallet'},
        'rocket': {'name': 'Rocket', 'amount': 0.0, 'count': 0, 'color': '#8c3494', 'icon': 'fas fa-money-bill-wave'},
        'card': {'name': 'Cards/Other', 'amount': 0.0, 'count': 0, 'color': '#0d6efd', 'icon': 'fas fa-credit-card'},
    }

    for item in gateway_qs:
        m = (item.card_type or item.payment_method or '').lower()
        amt = float(item.amount)
        if 'bkash' in m:
            methods_dict['bkash']['amount'] += amt
            methods_dict['bkash']['count'] += 1
        elif 'nagad' in m:
            methods_dict['nagad']['amount'] += amt
            methods_dict['nagad']['count'] += 1
        elif 'rocket' in m:
            methods_dict['rocket']['amount'] += amt
            methods_dict['rocket']['count'] += 1
        else:
            methods_dict['card']['amount'] += amt
            methods_dict['card']['count'] += 1

    for k, v in methods_dict.items():
        v['percentage'] = round((v['amount'] / total_col * 100.0), 1) if total_col > 0 else 0.0

    # Determine most used
    most_used = max(methods_dict.values(), key=lambda x: x['amount'])
    most_used_str = f"{most_used['name']}-{most_used['percentage']}%" if total_col > 0 else "BKash-100.0%"

    # Recent transactions list
    recent_transactions = []
    for idx, d in enumerate(gateway_qs[:30], 1):
        trx_id_display = f"#{d.trx_id}" if d.trx_id else (f"#{d.bank_tran_id}" if d.bank_tran_id else "#N/A")
        raw_m = (d.card_type or d.payment_method or 'BKash').strip()
        pm_clean = 'BKash' if 'bkash' in raw_m.lower() else ('Nagad' if 'nagad' in raw_m.lower() else ('Rocket' if 'rocket' in raw_m.lower() else raw_m))
        amt_float = float(d.amount)
        amt_display = f"৳ {int(amt_float) if amt_float.is_integer() else f'{amt_float:.2f}'}"

        recent_transactions.append({
            'index': idx,
            'id': d.id,
            'customer_name': d.donor_name or 'Anonymous Donor',
            'customer_email': d.donor_email or 'info@helplinehellonaogaon.com',
            'customer_phone': d.donor_phone or '',
            'amount': amt_float,
            'amount_display': amt_display,
            'payment_method': pm_clean,
            'settlement_status': 'Not settled',
            'trx_id': trx_id_display,
            'raw_trx_id': d.trx_id or d.bank_tran_id or '',
            'invoice_number': d.tran_id or '',
            'date_time': d.created_at.strftime('%Y-%m-%d %H:%M') if d.created_at else '',
            'date_display': d.created_at.strftime('%d %b, %Y %I:%M %p') if d.created_at else '',
        })

    def _fmt(val):
        return str(int(val)) if float(val).is_integer() else f"{val:.2f}"

    return {
        'merchant_id': config['merchant_id'],
        'is_sandbox': config['is_sandbox'],
        'base_url': config['base_url'],
        'portal_url': 'https://merchant.paystation.com.bd',
        'history_url': 'https://merchant.paystation.com.bd/transaction-history',
        'unsettled_amount': _fmt(unsettled_amt),
        'unsettled_amount_val': unsettled_amt,
        'unsettled_change': f"{unsettled_pct:.1f}%Last month",
        'last_month_net_collection': _fmt(last_month_col),
        'last_month_net_collection_val': last_month_col,
        'last_month_change': f"{last_month_pct:.1f}%Last month",
        'total_collection': _fmt(total_col),
        'total_collection_val': total_col,
        'total_collection_change': f"{total_pct:.1f}%Last month",
        'today_collection': _fmt(today_col),
        'today_collection_val': today_col,
        'today_change': f"{today_pct:.1f}%Last day",
        'payment_methods': methods_dict,
        'most_used_method': most_used_str,
        'recent_transactions': recent_transactions,
        'count': len(recent_transactions),
    }



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
