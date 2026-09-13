import logging
import os
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def send_sms(phone_number, message):
    """
    Sends an SMS to the given phone number.
    Supports environment-configured bulk SMS gateways (e.g., Greenweb, BulkSMSBD)
    and falls back to standard console logging.
    """
    if not phone_number:
        return False

    # Clean phone number (remove spaces, hyphens)
    cleaned_phone = "".join(ch for ch in str(phone_number) if ch.isdigit() or ch == '+')

    # Ensure Bangladesh country code if local 11-digit number
    if len(cleaned_phone) == 11 and cleaned_phone.startswith('01'):
        formatted_phone = '88' + cleaned_phone
    elif cleaned_phone.startswith('+880'):
        formatted_phone = cleaned_phone.replace('+', '')
    else:
        formatted_phone = cleaned_phone

    sms_api_url = getattr(settings, 'SMS_API_URL', os.environ.get('SMS_API_URL', ''))
    sms_api_token = getattr(settings, 'SMS_API_TOKEN', os.environ.get('SMS_API_TOKEN', ''))

    sent = False

    if sms_api_url and sms_api_token:
        try:
            payload = {
                'token': sms_api_token,
                'to': formatted_phone,
                'message': message,
            }
            res = requests.post(sms_api_url, data=payload, timeout=5)
            if res.status_code == 200:
                sent = True
                logger.info(f"[SMS GATEWAY SUCCESS] Sent to {formatted_phone}: {res.text}")
            else:
                logger.warning(f"[SMS GATEWAY ERROR] Status {res.status_code} for {formatted_phone}")
        except Exception as e:
            logger.error(f"[SMS GATEWAY EXCEPTION] Failed to send to {formatted_phone}: {e}")

    # Standard console log for monitoring
    print(f"[SMS DISPATCH] To: {formatted_phone} | Message: {message}")
    return True
