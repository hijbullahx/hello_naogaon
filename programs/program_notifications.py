import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings
from core.email_utils import send_system_email, get_base_url
from core.sms_utils import send_sms, clean_bd_phone_number
from volunteers.models import Volunteer, TeamMember

logger = logging.getLogger(__name__)


def get_program_notification_recipients():
    """
    Returns deduplicated recipient lists:
    - sms_recipients: list of tuples (name, phone)
    - email_recipients: list of tuples (name, email)
    
    Includes:
    1. All Team Members (Leadership, Committee, Coordinators, Admin members)
    2. All active Volunteers (Approved and active registered volunteers)
    """
    seen_phones = set()
    seen_emails = set()
    sms_recipients = []
    email_recipients = []

    # 1. Team Members (include ALL team members without excluding anyone)
    team_members = TeamMember.objects.all().order_by('order', 'name')
    for tm in team_members:
        phone = clean_bd_phone_number(tm.phone)
        email = (tm.email or '').strip().lower()

        if phone and phone not in seen_phones:
            seen_phones.add(phone)
            sms_recipients.append((tm.name, phone))

        if email and email not in seen_emails:
            seen_emails.add(email)
            email_recipients.append((tm.name, email))

    # 2. Volunteers (All active roster volunteers, excluding only abandoned unpaid gateway attempts)
    volunteers = Volunteer.objects.exclude(
        payment_status='unpaid', payment_method='Online Gateway'
    ).order_by('full_name')
    for vol in volunteers:
        phone = clean_bd_phone_number(vol.phone)
        email = (vol.email or '').strip().lower()

        if phone and phone not in seen_phones:
            seen_phones.add(phone)
            sms_recipients.append((vol.full_name, phone))

        if email and email not in seen_emails:
            seen_emails.add(email)
            email_recipients.append((vol.full_name, email))

    return sms_recipients, email_recipients


def _send_single_sms(name, phone, message):
    try:
        ok = send_sms(phone, message)
        if ok:
            return True, phone, None
        return False, phone, "SMS gateway returned failure"
    except Exception as e:
        logger.error("Error sending program fund SMS to %s (%s): %s", name, phone, e)
        return False, phone, str(e)


def _send_emails_worker(email_recipients, subject, paragraphs, details, action_buttons):
    """Background worker to send system emails without delaying SMS or HTTP responses."""
    sent_count = 0
    for name, email in email_recipients:
        try:
            send_system_email(
                subject=subject,
                recipient_list=[email],
                recipient_name=name,
                greeting="শ্রদ্ধেয় সদস্য",
                headline="কার্যক্রম ও অনুদান উদ্যোগ",
                message_paragraphs=[f"আসসালামু আলাইকুম {name},"] + paragraphs,
                details=details,
                action_buttons=action_buttons,
                footer_note="আপনার আন্তরিক অংশগ্রহণ আমাদের মানবিক উদ্যোগগুলোকে সফল করে তোলে।",
                fail_silently=True
            )
            sent_count += 1
        except Exception as e:
            logger.error("Error sending program fund email to %s (%s): %s", name, email, e)
    logger.info("Background emails finished: %d sent successfully.", sent_count)


def notify_members_volunteers_program_fund(program, request=None, async_mode=False):
    """
    Dispatches SMS to ALL team members and volunteers using parallel fast HTTP workers,
    and dispatches Emails in a background thread.
    Returns a dictionary of execution stats:
      {'sms_sent_count': X, 'sms_failed_count': Y, 'total_recipients': Z}
    """
    if not program:
        return {'sms_sent_count': 0, 'sms_failed_count': 0, 'total_recipients': 0}

    base_url = get_base_url(request) if request else "https://helplinehellonaogaon.com"
    if not base_url or any(loc in base_url for loc in ['127.0.0.1', 'localhost', '0.0.0.0', 'testserver']):
        base_url = "https://helplinehellonaogaon.com"
    prog_url = f"{base_url}/programs/{program.id}/"
    target_val = float(program.target_amount or 0) if program.target_amount else 0

    # Build concise, high-impact SMS message
    if target_val > 0:
        target_str = f"৳{int(target_val):,}"
        sms_msg = f"[Hello Naogaon] কার্যক্রম: {program.title[:24]}। লক্ষ্যমাত্রা: {target_str}। বিস্তারিত ও অংশ নিতে: {prog_url}"
        email_paragraphs = [
            f"হেল্পলাইন হ্যালো নওগাঁর মানবিক উদ্যোগ হিসেবে '{program.title}' কার্যক্রমে {target_str} টাকার একটি বাজেট / আর্থিক লক্ষ্যমাত্রা নির্ধারণ করা হয়েছে।",
            "নিচের লিংকে গিয়ে আপনারা কার্যক্রমের বর্তমান সংগৃহীত অর্থ, প্রগ্রেস ও যাবতীয় আপডেট তথ্য জানতে পারবেন।",
            "সংগঠনের এই মহৎ কার্যক্রমে আপনিও সাধ্যমতো অনুদান প্রদান করে মানবিক সেবায় শামিল হোন এবং অন্যদেরও সহযোগিতার আহ্বান জানান।"
        ]
        email_details = [
            {'label': 'কার্যক্রমের নাম', 'value': program.title},
            {'label': 'নির্ধারিত লক্ষ্যমাত্রা / বাজেট', 'value': f"৳{target_val:,.2f}"},
            {'label': 'বর্তমান সংগৃহীত অনুদান', 'value': f"৳{float(program.raised_amount or 0):,.2f}"},
        ]
    else:
        status_text = "চলমান" if program.status == 'ongoing' else ("আসন্ন" if program.status == 'upcoming' else "মানবিক")
        sms_msg = f"[Hello Naogaon] {status_text} কার্যক্রম: {program.title[:26]}। বিস্তারিত তথ্য ও অংশ নিতে: {prog_url}"
        email_paragraphs = [
            f"হেল্পলাইন হ্যালো নওগাঁর একটি নতুন মানবিক উদ্যোগ হিসেবে '{program.title}' পরিচালিত হচ্ছে।",
            "নিচের লিংকে গিয়ে আপনারা এই কার্যক্রমের বিস্তারিত তথ্য ও পরিকল্পনা দেখতে পারবেন।",
            "সংগঠনের এই মহতী কার্যক্রমে আপনার সক্রিয় অংশগ্রহণ ও আন্তরিক সহযোগিতা কামনা করছি।"
        ]
        email_details = [
            {'label': 'কার্যক্রমের নাম', 'value': program.title},
            {'label': 'কার্যক্রমের অবস্থা', 'value': 'চলমান কার্যক্রম' if program.status == 'ongoing' else 'আসন্ন কার্যক্রম'},
        ]

    email_subject = f"Hello Naogaon - কার্যক্রম ও অনুদান উদ্যোগ: {program.title}"
    email_action_buttons = [
        {'label': 'কার্যক্রমের বিস্তারিত দেখুন', 'url': prog_url},
        {'label': 'আমাদের ওয়েবসাইট দেখুন', 'url': base_url},
    ]

    sms_recipients, email_recipients = get_program_notification_recipients()
    total_recipients = len(sms_recipients)

    logger.info(
        "Broadcasting program '%s' to %d unique phone numbers and %d unique email addresses.",
        program.title, total_recipients, len(email_recipients)
    )

    sms_sent_count = 0
    sms_failed_count = 0

    if sms_recipients:
        # Fast parallel execution: 5 workers to send all SMS rapidly without getting killed by Passenger
        max_workers = min(8, len(sms_recipients))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {
                executor.submit(_send_single_sms, name, phone, sms_msg): (name, phone)
                for name, phone in sms_recipients
            }
            for future in as_completed(future_to_item):
                ok, phone, err = future.result()
                if ok:
                    sms_sent_count += 1
                else:
                    sms_failed_count += 1

    # Dispatch emails asynchronously in background thread so user response is instant
    if email_recipients:
        threading.Thread(
            target=_send_emails_worker,
            args=(email_recipients, email_subject, email_paragraphs, email_details, email_action_buttons),
            daemon=True
        ).start()

    logger.info(
        "Broadcast completed for '%s': %d SMS sent, %d failed out of %d.",
        program.title, sms_sent_count, sms_failed_count, total_recipients
    )

    return {
        'sms_sent_count': sms_sent_count,
        'sms_failed_count': sms_failed_count,
        'total_recipients': total_recipients,
    }
