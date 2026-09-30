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

ALERT_TIERS = [10.0, 8.0, 5.0, 4.0, 3.0, 2.0, 1.0]

def evaluate_low_balance_alert(balance_val):
    """
    Checks if balance has dropped below warning tiers (10, 8, 5, 4, 3, etc.).
    Sends an alert SMS to admin phone (01916314315) without spamming repeatedly
    for the same tier.
    """
    try:
        current_bal = float(balance_val)
    except (TypeError, ValueError):
        return

    admin_phone = getattr(settings, 'SMS_ADMIN_ALERT_PHONE', os.environ.get('SMS_ADMIN_ALERT_PHONE', '01916314315'))
    if not admin_phone:
        return

    # If recharged above 10 BDT, reset the tracker
    if current_bal > 10.0:
        cache.delete('sms_last_alerted_tier')
        return

    # Find the current matching tier (e.g. if 7.50, tier is 8.0)
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

    # Send alert SMS
    recharge_url = "asms.automas.com.bd/recharge_balance"
    msg = f"[Helpline Hello Naogaon] জরুরি সতর্কবার্তা: আপনার এসএমএস ব্যালেন্স কমে {current_bal:.2f} টাকা হয়েছে। নিরবচ্ছিন্ন সেবার জন্য এখনই রিচার্জ করুন: {recharge_url}"

    logger.warning(f"[SMS LOW BALANCE ALERT] Triggering alert for tier {current_tier} (Bal: {current_bal}) to {admin_phone}")
    success = send_sms(admin_phone, msg, is_alert=True)
    if success:
        cache.set('sms_last_alerted_tier', current_tier, 86400 * 7)


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
