import logging
import os
import requests
import threading
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Official Automas API Status Codes Mapping
AUTOMAS_STATUS_CODES = {
    0: "Success (সফলভাবে প্রেরিত)",
    101: "Invalid Message Length (বার্তার দৈর্ঘ্য সঠিক নয়)",
    102: "Sender Not Valid (অনুমোদিত প্রেরক আইডি নয়)",
    103: "Authentication Failed (ইউজার অথেন্টিকেশন ব্যর্থ)",
    104: "Invalid User (ব্যবহারকারী অ্যাকাউন্ট খুঁজে পাওয়া যায়নি)",
    105: "Invalid MSISDN (প্রাপকের মোবাইল নম্বর সঠিক নয়)",
    106: "Incorrect API Key (ভুল বা অবৈধ এপিআই কি)",
    107: "User Account Suspended (অ্যাকাউন্ট সাময়িক স্থগিত)",
    108: "IP Address Not Allowed (আইপি অনুমোদন নেই)",
    109: "API Access Not Allowed (এপিআই সেবা অ্যাক্টিভ নয়)",
    110: "Do Not Disturb (DND সক্রিয় থাকায় মেসেজ যায়নি)",
    111: "Spam Word Detected in Message (স্প্যাম শব্দ শনাক্ত হয়েছে)",
    1000: "Insufficient Balance (পর্যাপ্ত এসএমএস ব্যালেন্স নেই)",
    2300: "Destination Route Issue (অপারেটর রুট সমস্যা)",
    2400: "API Access Not Allowed",
    3300: "System Error (সিস্টেম ত্রুটি)",
}

def clean_bd_phone_number(phone_number, with_country_code=False):
    """
    Cleans and standardizes Bangladesh phone numbers.
    Input can be '+88017XXXXXXXX', '88017XXXXXXXX', or '017XXXXXXXX'.
    Returns '017XXXXXXXX' or '88017XXXXXXXX' based on flag.
    """
    if not phone_number:
        return ""
    digits = "".join(ch for ch in str(phone_number) if ch.isdigit())
    
    # Strip leading 88 if present to get standard 11 digits
    if len(digits) == 13 and digits.startswith('8801'):
        digits = digits[2:]
    elif len(digits) == 10 and digits.startswith('1'):
        digits = '0' + digits

    if len(digits) == 11 and digits.startswith('01'):
        return ('88' + digits) if with_country_code else digits
    
    return digits

def get_admin_phone():
    """
    Returns the master admin/helpline phone number configured in SiteSetting.
    Falls back to settings.SMS_ADMIN_ALERT_PHONE or '01916314315'.
    """
    try:
        from core.models import SiteSetting
        setting = SiteSetting.objects.first()
        if setting:
            if setting.admin_phone and setting.admin_phone.strip():
                return clean_bd_phone_number(setting.admin_phone.strip())
            if setting.contact_phone and setting.contact_phone.strip():
                return clean_bd_phone_number(setting.contact_phone.strip())
    except Exception:
        pass
    fallback = getattr(settings, 'SMS_ADMIN_ALERT_PHONE', os.environ.get('SMS_ADMIN_ALERT_PHONE', '01916314315'))
    return clean_bd_phone_number(fallback) if fallback else '01916314315'


ALERT_TIERS = [10.0, 3.0]

def evaluate_low_balance_alert(balance_val):
    """
    Checks if balance has dropped below warning tiers (10 BDT, 3 BDT).
    Sends a concise 1-segment alert SMS and free email alert to admin without repeated spam.
    """
    try:
        current_bal = float(balance_val)
    except (TypeError, ValueError):
        return

    admin_phone = get_admin_phone()

    # If recharged above 10 BDT, reset the tracker
    if current_bal > 10.0:
        cache.delete('sms_last_alerted_tier')
        return

    # Find the current matching tier (e.g. if 7.50, tier is 10.0; if 2.50, tier is 3.0)
    current_tier = None
    for tier in ALERT_TIERS:
        if current_bal <= tier:
            current_tier = tier

    if current_tier is None:
        return

    last_alerted_tier = cache.get('sms_last_alerted_tier')
    # If we have already alerted for this tier or a lower tier, skip to avoid spam
    if last_alerted_tier is not None and last_alerted_tier <= current_tier:
        return

    # 1. Send free Email Alert to admin
    try:
        from core.email_utils import send_system_email, get_admin_notification_emails
        admin_emails = get_admin_notification_emails()
        if admin_emails:
            send_system_email(
                subject=f"⚠️ জরুরি সতর্কতা: এসএমএস ব্যালেন্স কমে ৳{current_bal:.2f} হয়েছে",
                recipient_list=admin_emails,
                headline="এসএমএস গেটওয়ে ব্যালেন্স সতর্কবার্তা",
                greeting="শ্রদ্ধেয় অ্যাডমিন,",
                message_paragraphs=[
                    f"আমাদের অটোগেটওয়ে এসএমএস ব্যালেন্স কমে ৳{current_bal:.2f} টাকায় নেমে এসেছে।",
                    "নাগরিক সেবা ও সদস্য নিশ্চিতকরণ এসএমএস নিরবচ্ছিন্ন রাখতে অনতিবিলম্বে অটমাস পোর্টালে ব্যালেন্স রিচার্জ করুন।"
                ],
                details=[
                    {'label': 'বর্তমান ব্যালেন্স', 'value': f"৳ {current_bal:.2f}"},
                    {'label': 'সতর্কবার্তা টিয়ার', 'value': f"৳ {current_tier:.0f} বা তার নিচে"},
                    {'label': 'রিচার্জ পোর্টাল', 'value': 'https://asms.automas.com.bd/recharge_balance'},
                ],
                footer_note="ব্যালেন্স নিঃশেষ হয়ে গেলে সদস্য নিবন্ধন ও অনুদান নোটিফিকেশন সাময়িকভাবে ব্যাহত হতে পারে।",
                fail_silently=True
            )
    except Exception as em_err:
        logger.warning(f"Failed to dispatch low SMS balance email: {em_err}")

    # 2. Send ultra-compact 1-segment alert SMS to admin SIM (<= 70 chars UCS-2)
    if admin_phone:
        recharge_url = "asms.automas.com.bd"
        msg = f"[Hello Naogaon] এসএমএস ব্যালেন্স ৳{current_bal:.2f}। রিচার্জ: {recharge_url}"

        logger.warning(f"[SMS LOW BALANCE ALERT] Triggering alert for tier {current_tier} (Bal: {current_bal}) to {admin_phone}")
        success = send_sms(admin_phone, msg, is_alert=True)
        if success:
            cache.set('sms_last_alerted_tier', current_tier, 86400 * 3)


def send_sms(phone_number, message, is_alert=False):
    """
    Sends an SMS via Automas Bulk SMS API.
    Supports both English (ASCII) and Bengali (Unicode) messages automatically.
    Falls back gracefully to console logging if credentials are not configured in .env.
    """
    if not phone_number or not message:
        logger.warning("[SMS] Empty phone number or message.")
        return False

    cleaned_phone = clean_bd_phone_number(phone_number)
    if not cleaned_phone:
        logger.warning(f"[SMS] Invalid phone number provided: {phone_number}")
        return False

    api_key = getattr(settings, 'AUTOMAS_API_KEY', os.environ.get('AUTOMAS_API_KEY', '')).strip()
    sender_id = getattr(settings, 'AUTOMAS_SENDER_ID', os.environ.get('AUTOMAS_SENDER_ID', '')).strip()
    api_url = getattr(settings, 'AUTOMAS_API_URL', os.environ.get('AUTOMAS_API_URL', 'https://api.automas.com.bd/smsapiv3')).strip()

    # Detect Unicode (Bangla / non-ASCII)
    is_unicode = any(ord(char) > 127 for char in message)

    # If API Key is not yet configured, log to console safely (e.g. during local testing)
    if not api_key:
        safe_msg = message.encode('ascii', 'backslashreplace').decode('ascii')
        logger.info(f"[SMS SIMULATION - NO API KEY] To: {cleaned_phone} | Unicode: {is_unicode} | Msg: {safe_msg}")
        return True

    # Prepare Automas Gateway Payload
    payload = {
        'api_key': api_key,
        'apikey': api_key,
        'senderid': sender_id,
        'sender': sender_id,
        'contacts': cleaned_phone,
        'msisdn': cleaned_phone,
        'to': cleaned_phone,
        'msg': message,
        'smstext': message,
        'type': 'unicode' if is_unicode else 'text',
    }

    if is_unicode:
        payload['smsformat'] = '8'

    try:
        response = requests.post(api_url, data=payload, timeout=10)
        
        if response.status_code == 200:
            try:
                res_data = response.json()
            except Exception:
                res_data = None

            # Parse Automas standard response: {"response":[{"status":0,"id":296334,"msisdn":"018..."}]}
            if isinstance(res_data, dict) and 'response' in res_data:
                first_item = res_data['response'][0] if isinstance(res_data['response'], list) and res_data['response'] else {}
                status_code = first_item.get('status', -1)
                sms_id = first_item.get('id', 'N/A')
                status_desc = AUTOMAS_STATUS_CODES.get(status_code, f"Status code {status_code}")
                
                if status_code == 0:
                    logger.info(f"[AUTOMAS SMS SUCCESS] Sent to {cleaned_phone} | ID: {sms_id}")
                    print(f"[AUTOMAS SMS SUCCESS] To: {cleaned_phone} | ID: {sms_id}")

                    # Trigger non-blocking low balance check after successful send
                    if not is_alert:
                        try:
                            threading.Thread(target=check_sms_balance, kwargs={'trigger_low_balance_alert': True}, daemon=True).start()
                        except Exception as th_err:
                            logger.warning(f"Failed to start async balance check: {th_err}")

                    return True
                else:
                    logger.error(f"[AUTOMAS SMS FAILED] Code: {status_code} ({status_desc}) | To: {cleaned_phone}")
                    print(f"[AUTOMAS SMS ERROR] Code {status_code}: {status_desc} for {cleaned_phone}")
                    return False
            
            # Simple fallback check
            logger.info(f"[AUTOMAS SMS RESPONSE] {response.text}")
            return True
        else:
            logger.error(f"[AUTOMAS HTTP ERROR] HTTP {response.status_code}: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"[AUTOMAS CONNECTION EXCEPTION] {e}")
        print(f"[AUTOMAS CONNECTION EXCEPTION] {e}")
        return False


def check_sms_balance(trigger_low_balance_alert=True):
    """
    Checks remaining balance from Automas SMS API.
    Returns balance string (e.g., '100.0') or None on error.
    Updates cache and optionally evaluates low balance alerts to admin.
    """
    api_key = getattr(settings, 'AUTOMAS_API_KEY', os.environ.get('AUTOMAS_API_KEY', '')).strip()
    if not api_key:
        return None

    balance_url = 'https://api.automas.com.bd/getbalancev3'
    try:
        res = requests.get(balance_url, params={'apikey': api_key}, timeout=5)
        if res.status_code == 200:
            data = res.json()
            balance_val = None
            if isinstance(data, dict) and 'response' in data:
                balance_val = data.get('response')
            else:
                balance_val = res.text.strip()

            if balance_val is not None:
                # Update cache so dashboard stays auto-synced
                try:
                    cache.set('automas_sms_balance', float(balance_val), 300)
                except Exception:
                    pass

                if trigger_low_balance_alert:
                    evaluate_low_balance_alert(balance_val)

            return balance_val
    except Exception as e:
        logger.error(f"[AUTOMAS BALANCE CHECK ERROR] {e}")
    return None
