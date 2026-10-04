import logging
import threading
from django.conf import settings
from core.email_utils import send_system_email, get_base_url
from core.sms_utils import send_sms, clean_bd_phone_number
from volunteers.models import Volunteer, TeamMember
from volunteers.subscription_services import is_admin_member

logger = logging.getLogger(__name__)

def _send_notifications_worker(program, base_url):
    """
    Background worker to dispatch SMS and Email to:
    - All approved Volunteers
    - All Team Members except Admin
    Deduplicating by phone and email.
    """
    try:
        target_val = float(program.target_amount or 0) if program.target_amount else 0
        prog_url = f"{base_url}/programs/{program.id}/"

        if target_val > 0:
            target_str = f"৳{int(target_val):,}"
            # Compact SMS message to minimize character count and SMS cost
            sms_msg = f"[Hello Naogaon] নতুন প্রকল্প: {program.title[:20]}। বাজেট {target_str}। তথ্য ও অংশ নিতে: {prog_url}"

            # Email content
            email_subject = f"Hello Naogaon - নতুন তহবিল ও কার্যক্রম উদ্যোগ: {program.title}"
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
            # Compact SMS message without budget
            sms_msg = f"[Hello Naogaon] নতুন {status_text} উদ্যোগ: {program.title[:22]}। বিস্তারিত ও অংশ নিতে: {prog_url}"

            # Email content
            email_subject = f"Hello Naogaon - নতুন {status_text} উদ্যোগ: {program.title}"
            email_paragraphs = [
                f"হেল্পলাইন হ্যালো নওগাঁর একটি নতুন মানবিক উদ্যোগ হিসেবে '{program.title}' পরিচালিত হচ্ছে।",
                "নিচের লিংকে গিয়ে আপনারা এই কার্যক্রমের বিস্তারিত তথ্য ও পরিকল্পনা দেখতে পারবেন।",
                "সংগঠনের এই মহতী কার্যক্রমে আপনার সক্রিয় অংশগ্রহণ ও আন্তরিক সহযোগিতা কামনা করছি।"
            ]
            email_details = [
                {'label': 'কার্যক্রমের নাম', 'value': program.title},
                {'label': 'কার্যক্রমের অবস্থা', 'value': 'চলমান কার্যক্রম' if program.status == 'ongoing' else 'আসন্ন কার্যক্রম'},
            ]

        email_action_buttons = [
            {'label': 'কার্যক্রমের বিস্তারিত দেখুন', 'url': prog_url},
            {'label': 'আমাদের ওয়েবসাইট দেখুন', 'url': base_url},
        ]

        seen_phones = set()
        seen_emails = set()
        sms_sent_count = 0
        email_sent_count = 0

        # 1. Team Members (Exclude Admin)
        team_members = TeamMember.objects.all().order_by('order', 'name')
        for tm in team_members:
            if is_admin_member(tm):
                continue
            phone = clean_bd_phone_number(tm.phone)
            email = (tm.email or '').strip().lower()

            if phone and phone not in seen_phones:
                seen_phones.add(phone)
                try:
                    send_sms(phone, sms_msg)
                    sms_sent_count += 1
                except Exception as e:
                    logger.error("Error sending program fund SMS to %s (%s): %s", tm.name, phone, e)

            if email and email not in seen_emails:
                seen_emails.add(email)
                try:
                    send_system_email(
                        subject=email_subject,
                        recipient_list=[email],
                        recipient_name=tm.name,
                        greeting="শ্রদ্ধেয় সদস্য",
                        headline="নতুন কার্যক্রম ও অনুদান উদ্যোগ",
                        message_paragraphs=[f"আসসালামু আলাইকুম {tm.name},"] + email_paragraphs,
                        details=email_details,
                        action_buttons=email_action_buttons,
                        footer_note="আপনার সক্রিয় অংশগ্রহণ আমাদের মানবিক উদ্যোগগুলোকে সফল করে তোলে।",
                        fail_silently=True
                    )
                    email_sent_count += 1
                except Exception as e:
                    logger.error("Error sending program fund email to %s (%s): %s", tm.name, email, e)

        # 2. Approved Volunteers
        volunteers = Volunteer.objects.filter(status='approved').order_by('full_name')
        for vol in volunteers:
            phone = clean_bd_phone_number(vol.phone)
            email = (vol.email or '').strip().lower()

            if phone and phone not in seen_phones:
                seen_phones.add(phone)
                try:
                    send_sms(phone, sms_msg)
                    sms_sent_count += 1
                except Exception as e:
                    logger.error("Error sending program fund SMS to %s (%s): %s", vol.full_name, phone, e)

            if email and email not in seen_emails:
                seen_emails.add(email)
                try:
                    send_system_email(
                        subject=email_subject,
                        recipient_list=[email],
                        recipient_name=vol.full_name,
                        greeting="প্রিয় স্বেচ্ছাসেবী",
                        headline="নতুন কার্যক্রম ও অনুদান উদ্যোগ",
                        message_paragraphs=[f"আসসালামু আলাইকুম {vol.full_name},"] + email_paragraphs,
                        details=email_details,
                        action_buttons=email_action_buttons,
                        footer_note="সমাজের অসহায় মানুষের পাশে দাঁড়াতে আমাদের এই উদ্যোগকে এগিয়ে নিন।",
                        fail_silently=True
                    )
                    email_sent_count += 1
                except Exception as e:
                    logger.error("Error sending program fund email to %s (%s): %s", vol.full_name, email, e)

        logger.info(
            "Dispatched program fund notifications for '%s': SMS sent: %d, Email sent: %d",
            program.title, sms_sent_count, email_sent_count
        )
    except Exception as ex:
        logger.error("Unexpected error in _send_notifications_worker for program %s: %s", getattr(program, 'id', 'unknown'), ex)

def notify_members_volunteers_program_fund(program, request=None, async_mode=True):
    """
    Triggers SMS and Email notifications to all approved volunteers and non-admin team members
    when a program's funding budget/target_amount is set.
    """
    if not program:
        return False

    base_url = get_base_url(request) if request else "https://hellonaogaon.org"

    if async_mode:
        worker = threading.Thread(
            target=_send_notifications_worker,
            args=(program, base_url),
            daemon=True
        )
        worker.start()
        return True
    else:
        _send_notifications_worker(program, base_url)
        return True
