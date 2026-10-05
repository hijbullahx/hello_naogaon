import logging
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from core.sms_utils import send_sms, clean_bd_phone_number, get_admin_phone
from core.email_utils import send_system_email, get_admin_notification_emails

logger = logging.getLogger(__name__)


@csrf_exempt
def inbound_sms_webhook(request):
    """
    Handles incoming/reply SMS from Automas or other SMS gateway webhooks.
    Bypasses and forwards the incoming message directly to Admin SIM (+8801916314315)
    and sends an email alert to the admin notification emails.
    """
    if request.method not in ['POST', 'GET']:
        return HttpResponse("Method not allowed", status=405)

    data = request.POST if request.method == 'POST' else request.GET

    # Extract sender from various possible field names used by aggregators
    sender = (
        data.get('from') or data.get('sender') or data.get('msisdn') or 
        data.get('mobile') or data.get('phone') or data.get('contacts') or ''
    ).strip()

    # Extract message text from various possible field names
    message = (
        data.get('message') or data.get('text') or data.get('msg') or 
        data.get('smstext') or data.get('body') or ''
    ).strip()

    # If payload is in JSON body
    if not message and request.body:
        try:
            body_json = json.loads(request.body.decode('utf-8'))
            if isinstance(body_json, dict):
                sender = sender or (body_json.get('from') or body_json.get('sender') or body_json.get('msisdn') or '')
                message = message or (body_json.get('message') or body_json.get('text') or body_json.get('msg') or '')
        except Exception:
            pass

    sender = sender or 'Unknown'
    clean_sender = clean_bd_phone_number(sender) or sender
    admin_phone = get_admin_phone()

    logger.info(f"[INBOUND SMS RECEIVED] From: {clean_sender} | Content: {message}")

    # 1. Forward SMS directly to Admin Phone (+8801916314315)
    forward_sms_sent = False
    if admin_phone and message:
        # Keep within single part length
        short_msg = (message[:100] + '...') if len(message) > 100 else message
        forward_text = f"[Helpline Hello Naogaon] ফিরতি বার্তা এসেছে! প্রেরক: {clean_sender}। বার্তা: {short_msg}"
        try:
            forward_sms_sent = send_sms(admin_phone, forward_text, is_alert=True)
            logger.info(f"[INBOUND SMS FORWARDED] Forwarded to admin {admin_phone}: {forward_sms_sent}")
        except Exception as e:
            logger.error(f"[INBOUND SMS FORWARD ERROR] {e}")

    # 2. Forward full Email alert to Admin
    try:
        admin_emails = get_admin_notification_emails()
        if admin_emails and message:
            send_system_email(
                subject=f"📩 নতুন ফিরতি এসএমএস এসেছে — {clean_sender}",
                recipient_list=admin_emails,
                headline="এসএমএস গেটওয়ে থেকে নতুন ফিরতি বার্তা",
                greeting="শ্রদ্ধেয় অ্যাডমিন,",
                message_paragraphs=[
                    f"আমাদের এসএমএস নম্বরে ({getattr(settings, 'AUTOMAS_SENDER_ID', '8809617642529')}) একজন নাগরিক/সদস্য ফিরতি বার্তা পাঠিয়েছেন।",
                    "বার্তাটি স্বয়ংক্রিয়ভাবে বাইপাস করে আপনার ফোনে ও এই ইমেইলে প্রেরণ করা হয়েছে।"
                ],
                details=[
                    {'label': 'প্রেরকের মোবাইল নম্বর', 'value': clean_sender},
                    {'label': 'বার্তা / মেসেজ', 'value': message},
                ],
                footer_note="আপনি সরাসরি প্রেরকের নম্বরে কল অথবা এসএমএস করে যোগাযোগ করতে পারেন।",
                fail_silently=True,
                request=request
            )
    except Exception as e:
        logger.error(f"[INBOUND EMAIL FORWARD ERROR] {e}")

    return JsonResponse({
        'status': 'success',
        'forwarded_to': admin_phone,
        'sms_forwarded': forward_sms_sent,
        'sender': clean_sender
    })
