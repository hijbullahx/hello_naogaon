import calendar
import logging
from datetime import date, datetime
from django.conf import settings
from django.db.models import Sum
from core.email_utils import send_system_email, get_base_url
from core.sms_utils import send_sms

logger = logging.getLogger(__name__)

def is_admin_member(member):
    """
    Checks if a member is an Admin (প্রধান অ্যাডমিন / Superuser / System Admin).
    """
    if member.user and member.user.is_superuser:
        return True
    
    role = (member.role or '').strip().lower()
    custom_role = (member.custom_role or '').strip().lower()
    
    admin_keywords = ['প্রধান অ্যাডমিন', 'অ্যাডমিন', 'admin', 'administrator', 'superadmin', 'এডমিন']
    for kw in admin_keywords:
        if kw in role or kw in custom_role:
            return True
    return False

def is_president_member(member):
    """
    Checks if a member is President (সভাপতি).
    Excludes সহ-সভাপতি (Vice President).
    """
    role = (member.role or '').strip()
    custom_role = (member.custom_role or '').strip()
    
    if member.role == 'সভাপতি' or member.custom_role == 'সভাপতি':
        return True
    if 'সভাপতি' in role and 'সহ' not in role:
        return True
    if 'সভাপতি' in custom_role and 'সহ' not in custom_role:
        return True
    role_lower = role.lower()
    custom_role_lower = custom_role.lower()
    if ('president' in role_lower and 'vice' not in role_lower) or ('president' in custom_role_lower and 'vice' not in custom_role_lower):
        return True
    return False

def is_secretary_member(member):
    """
    Checks if a member is General Secretary (সাধারণ সম্পাদক).
    Excludes যুগ্ম / সহ / সাংগঠনিক / দপ্তর সম্পাদক.
    """
    role = (member.role or '').strip()
    custom_role = (member.custom_role or '').strip()
    
    if member.role == 'সাধারণ সম্পাদক' or member.custom_role == 'সাধারণ সম্পাদক':
        return True
    if 'সাধারণ সম্পাদক' in role or 'সাধারণ সম্পাদক' in custom_role:
        return True
    role_lower = role.lower()
    custom_role_lower = custom_role.lower()
    if ('general secretary' in role_lower or 'general secretary' in custom_role_lower):
        return True
    return False

def get_member_monthly_fee(member):
    """
    Determines fixed monthly fee:
    - শুধুমাত্র সভাপতি, সাধারণ সম্পাদক এবং অ্যাডমিন: 500 BDT
    - কোষাধ্যক্ষ সহ অন্যান্য সকল কার্যকরী ও সাধারণ পরিষদ সদস্যবৃন্দ: 100 BDT
    """
    if is_admin_member(member) or is_president_member(member) or is_secretary_member(member):
        return 500.0
    return 100.0

def calculate_billing_cycles(join_date, today=None):
    """
    Calculates number of monthly billing cycles elapsed from join_date up to today.
    Cycle 1 commences on the day of registration (join_date).
    Subsequent cycles commence on the monthly anniversary (billing day) of each month.
    """
    if not join_date:
        return 1
    if today is None:
        today = date.today()
    if today < join_date:
        return 1
    
    months_diff = (today.year - join_date.year) * 12 + (today.month - join_date.month)
    max_days_this_month = calendar.monthrange(today.year, today.month)[1]
    target_day = min(join_date.day, max_days_this_month)
    
    if today.day >= target_day:
        cycles = months_diff + 1
    else:
        cycles = max(1, months_diff)
    return cycles

def get_member_subscription_summary(member, today=None):
    """
    Calculates the complete subscription & fee summary for a TeamMember:
    - monthly_fee (500 or 100)
    - join_date & billing_day
    - months_billed (billing cycles passed)
    - total_billed
    - total_paid (completed donations)
    - due_amount (বকেয়া)
    - advance_amount (অগ্রিম)
    - suggested_amount
    """
    if today is None:
        today = date.today()

    monthly_fee = get_member_monthly_fee(member)
    
    if member.created_at:
        join_date = member.created_at.date()
    else:
        join_date = today

    billing_day = join_date.day
    cycles = calculate_billing_cycles(join_date, today)
    total_billed = cycles * monthly_fee

    # Calculate all successful payments made under this member_id
    from donations.models import ProgramDonation
    paid_qs = ProgramDonation.objects.filter(
        membership_id=member.member_id,
        status__in=['approved', 'completed']
    )
    total_paid = float(paid_qs.aggregate(total=Sum('amount'))['total'] or 0.0)

    balance = total_paid - total_billed
    if balance < 0:
        due_amount = abs(balance)
        advance_amount = 0.0
        status_label = 'বকেয়া'
        suggested_amount = due_amount
    elif balance > 0:
        due_amount = 0.0
        advance_amount = balance
        status_label = 'অগ্রিম জমা'
        suggested_amount = monthly_fee
    else:
        due_amount = 0.0
        advance_amount = 0.0
        status_label = 'পরিশোধিত'
        suggested_amount = monthly_fee

    # Next billing date
    max_days_this_month = calendar.monthrange(today.year, today.month)[1]
    this_month_target_day = min(join_date.day, max_days_this_month)
    if today.day < this_month_target_day:
        next_billing_date = date(today.year, today.month, this_month_target_day)
    else:
        # Next month
        next_month = today.month + 1 if today.month < 12 else 1
        next_year = today.year if today.month < 12 else today.year + 1
        max_days_next = calendar.monthrange(next_year, next_month)[1]
        next_billing_date = date(next_year, next_month, min(join_date.day, max_days_next))

    return {
        'member_id': member.member_id or '',
        'name': member.name,
        'role': member.effective_role,
        'phone': member.phone or '',
        'email': member.email or '',
        'monthly_fee': monthly_fee,
        'join_date': join_date,
        'join_date_formatted': join_date.strftime('%d-%m-%Y'),
        'billing_day': billing_day,
        'months_billed': cycles,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'due_amount': due_amount,
        'advance_amount': advance_amount,
        'balance': balance,
        'status_label': status_label,
        'suggested_amount': suggested_amount,
        'next_billing_date': next_billing_date,
        'next_billing_date_formatted': next_billing_date.strftime('%d-%m-%Y'),
    }

def send_member_registration_notification(member):
    """
    Sends Welcome & First Month Fee notification upon Member Registration.
    """
    summary = get_member_subscription_summary(member)
    base_url = get_base_url()
    payment_url = f"{base_url}/donations/?member_id={member.member_id}"

    # 1. SMS Notification
    if member.phone:
        sms_msg = (
            f"[Helpline Hello Naogaon] {member.name}, পরিচালনা পর্ষদে আপনাকে স্বাগতম! "
            f"সদস্য আইডি: {member.member_id}। আপনার পদবীতে মাসিক নির্ধারিত চাঁদা ৳{summary['monthly_fee']:,.0f}। "
            f"সহজে চাঁদা পরিশোধ করুন: {payment_url}"
        )
        try:
            send_sms(member.phone, sms_msg)
            logger.info("Sent registration subscription SMS to %s", member.phone)
        except Exception as e:
            logger.error("Error sending registration subscription SMS to %s: %s", member.phone, e)

    # 2. Email Notification
    if member.email:
        subject = f"Hello Naogaon - সদস্য নিবন্ধন ও মাসিক চাঁদা বিবরণী (আইডি: {member.member_id})"
        paragraphs = [
            f"আসসালামু আলাইকুম {member.name},",
            f"হেল্পলাইন হ্যালো নওগাঁ (Helpline Hello Naogaon)-এর পরিচালনা পর্ষদে {member.effective_role} হিসেবে অন্তর্ভুক্ত হওয়ায় আপনাকে উষ্ণ অভিনন্দন!",
            f"সংগঠনের নীতিমালা অনুযায়ী আপনার পদের জন্য নির্ধারিত মাসিক চাঁদার পরিমাণ ৳{summary['monthly_fee']:,.2f} টাকা। "
            f"প্রতি মাসের {summary['billing_day']} তারিখে আপনার মাসিক চাঁদা ধার্য হবে এবং পূর্বের বকেয়া (যদি থাকে) সহ নিয়মিত আপডেট বার্তা পাবেন।",
            "আপনার প্রথম মাসের চাঁদা নিচের বোতামে চাপ দিয়ে সরাসরি বিকাশ, নগদ বা ব্যাংক কার্ডের মাধ্যমে অনলাইনে পরিশোধ করতে পারবেন।"
        ]

        details = [
            {'label': 'সদস্যের নাম', 'value': member.name},
            {'label': 'সদস্য পদবী', 'value': member.effective_role},
            {'label': 'সদস্য আইডি (Member ID)', 'value': member.member_id},
            {'label': 'নির্ধারিত মাসিক চাঁদা', 'value': f"৳{summary['monthly_fee']:,.2f} / মাস"},
            {'label': 'মাসিক বিলিং তারিখ', 'value': f"প্রতি মাসের {summary['billing_day']} তারিখ"},
            {'label': 'চলতি মাসের প্রদেয় চাঁদা', 'value': f"৳{summary['monthly_fee']:,.2f}"},
        ]

        action_buttons = [
            {'label': 'অনলাইনে চাঁদা পরিশোধ করুন', 'url': payment_url},
            {'label': 'আমাদের ওয়েবসাইট দেখুন', 'url': base_url},
        ]

        send_system_email(
            subject=subject,
            recipient_list=[member.email],
            recipient_name=member.name,
            greeting="শ্রদ্ধেয় সদস্য",
            headline="সদস্য নিবন্ধন ও নির্ধারিত মাসিক চাঁদা",
            message_paragraphs=paragraphs,
            details=details,
            action_buttons=action_buttons,
            footer_note="আপনার নিয়মিত সহযোগিতা সমাজের অসহায় মানুষের পাশে দাঁড়াতে আমাদের শক্তি জোগাবে।",
            fail_silently=True
        )

def send_member_monthly_reminder(member, today=None):
    """
    Sends recurring monthly fee reminder on the member's monthly billing anniversary.
    Includes current month's fee + any previous dues.
    """
    summary = get_member_subscription_summary(member, today=today)
    base_url = get_base_url()
    payment_url = f"{base_url}/donations/?member_id={member.member_id}"

    due_str = f"৳{summary['due_amount']:,.0f}" if summary['due_amount'] > 0 else "০"
    
    # 1. SMS Reminder
    if member.phone:
        if summary['due_amount'] > 0:
            sms_msg = (
                f"[Helpline Hello Naogaon] {member.name}, মাসিক চাঁদা রিমাইন্ডার (আইডি: {member.member_id})। "
                f"মাসিক চাঁদা: ৳{summary['monthly_fee']:,.0f}। মোট বকেয়া: {due_str} টাকা। "
                f"অনলাইনে পরিশোধ করুন: {payment_url}"
            )
        else:
            sms_msg = (
                f"[Helpline Hello Naogaon] {member.name}, আইডি: {member.member_id}। "
                f"চলতি মাসের নির্ধারিত চাঁদা ৳{summary['monthly_fee']:,.0f} টাকা প্রস্তুত রয়েছে। "
                f"পরিশোধ করতে ভিজিট করুন: {payment_url}"
            )
        try:
            send_sms(member.phone, sms_msg)
            logger.info("Sent monthly subscription reminder SMS to %s", member.phone)
        except Exception as e:
            logger.error("Error sending monthly reminder SMS to %s: %s", member.phone, e)

    # 2. Email Reminder
    if member.email:
        subject = f"Hello Naogaon - মাসিক চাঁদা রিমাইন্ডার ও হিসাব বিবরণী (আইডি: {member.member_id})"
        paragraphs = [
            f"সম্মানিত {member.name},",
            f"হেল্পলাইন হ্যালো নওগাঁর নিয়মিত কার্যক্রম ও মানবিক সেবাসমূহ অব্যাহত রাখতে পরিচালনা পর্ষদের নির্ধারিত মাসিক চাঁদা অত্যন্ত গুরুত্বপূর্ণ।",
            f"আপনার সদস্য আইডি: #{member.member_id} ({member.effective_role})। প্রতি মাসের {summary['billing_day']} তারিখে আপনার নিয়মিত মাসিক চাঁদা ধার্য করা হয়।"
        ]

        if summary['due_amount'] > 0:
            paragraphs.append(
                f"হিসাব অনুযায়ী আপনার বর্তমান মোট প্রদেয় / বকেয়ার পরিমাণ {due_str} টাকা। "
                "সংগঠনের কার্যক্রম সুন্দরভাবে পরিচালনার স্বার্থে দ্রুত বকেয়া পরিশোধ করার জন্য বিনীত অনুরোধ জানানো হচ্ছে।"
            )
        elif summary['advance_amount'] > 0:
            paragraphs.append(
                f"আপনার অ্যাকাউন্টে ইতিমধ্যে ৳{summary['advance_amount']:,.2f} টাকা অগ্রিম জমা রয়েছে। আপনার আন্তরিক সহযোগিতার জন্য ধন্যবাদ!"
            )
        else:
            paragraphs.append(
                "আপনার পূর্বের সকল মাসের চাঁদা পরিশোধিত রয়েছে। চলতি মাসের চাঁদা পরিশোধের জন্য নিচের বাটনে ক্লিক করুন।"
            )

        details = [
            {'label': 'সদস্য আইডি (Member ID)', 'value': member.member_id},
            {'label': 'নির্ধারিত মাসিক চাঁদা', 'value': f"৳{summary['monthly_fee']:,.2f}"},
            {'label': 'সদস্য শুরুর তারিখ', 'value': summary['join_date_formatted']},
            {'label': 'মোট প্রযোজ্য বিলিং মাস', 'value': f"{summary['months_billed']} মাস"},
            {'label': 'মোট ধার্যকৃত চাঁদা', 'value': f"৳{summary['total_billed']:,.2f}"},
            {'label': 'এ যাবৎ মোট পরিশোধিত', 'value': f"৳{summary['total_paid']:,.2f}"},
            {'label': 'বর্তমান বকেয়া / প্রদেয়', 'value': f"৳{summary['due_amount']:,.2f}"},
        ]
        if summary['advance_amount'] > 0:
            details.append({'label': 'অগ্রিম জমা', 'value': f"৳{summary['advance_amount']:,.2f}"})

        action_buttons = [
            {'label': 'অনলাইনে চাঁদা পরিশোধ করুন', 'url': payment_url},
            {'label': 'হিসাব ও অনুদান পেজ দেখুন', 'url': f"{base_url}/donations/"},
        ]

        send_system_email(
            subject=subject,
            recipient_list=[member.email],
            recipient_name=member.name,
            greeting="আসসালামু আলাইকুম",
            headline="মাসিক চাঁদা ও হিসাব হালনাগাদ",
            message_paragraphs=paragraphs,
            details=details,
            action_buttons=action_buttons,
            footer_note="আপনার নিয়মিত আর্থিক সহায়তা সমাজ পরিবর্তনে আমাদের মূল চালিকাশক্তি।",
            fail_silently=True
        )

def send_all_existing_members_update():
    """
    Sends an updated status notification (SMS & Email) to ALL existing core TeamMembers right now.
    """
    from volunteers.models import TeamMember
    members = TeamMember.objects.all().order_by('order', 'name')
    sent_count = 0
    results = []

    for mem in members:
        summary = get_member_subscription_summary(mem)
        base_url = get_base_url()
        payment_url = f"{base_url}/donations/?member_id={mem.member_id}"

        # 1. SMS
        sms_sent = False
        if mem.phone:
            due_str = f"৳{summary['due_amount']:,.0f}" if summary['due_amount'] > 0 else "০"
            sms_msg = (
                f"[Helpline Hello Naogaon] {mem.name}, আপনার সদস্য আইডি: {mem.member_id} ({mem.effective_role})। "
                f"মাসিক চাঁদা: ৳{summary['monthly_fee']:,.0f}। বর্তমান বকেয়া: {due_str} টাকা। "
                f"বিস্তারিত ও পরিশোধ: {payment_url}"
            )
            try:
                sms_sent = send_sms(mem.phone, sms_msg)
            except Exception as e:
                logger.error("Error sending SMS update to %s: %s", mem.phone, e)

        # 2. Email
        email_sent = False
        if mem.email:
            subject = f"Hello Naogaon - পরিচালনা পর্ষদ সদস্য চাঁদা ও হিসাব বিবরণী হালনাগাদ (আইডি: {mem.member_id})"
            paragraphs = [
                f"আসসালামু আলাইকুম {mem.name},",
                "হেল্পলাইন হ্যালো নওগাঁ (Helpline Hello Naogaon)-এর সম্মানিত পরিচালনা পর্ষদ / টিম মেম্বারদের মাসিক চাঁদা ও আর্থিক হিসাব ব্যবস্থা অটোমেশন ও হালনাগাদ করা হয়েছে।",
                f"সংগঠনের নীতিমালা অনুযায়ী আপনার পদের ({mem.effective_role}) জন্য মাসিক নির্ধারিত চাঁদা ৳{summary['monthly_fee']:,.2f} টাকা। "
                f"আপনার সদস্য অন্তর্ভুক্তির তারিখ ({summary['join_date_formatted']}) হতে প্রতি মাসের {summary['billing_day']} তারিখে এই চাঁদা ধার্য হচ্ছে।",
                "আপনি ওয়েবসাইট থেকে যেকোনো সময় আপনার বকেয়া বা অগ্রিম জমা দেখতে পারবেন এবং অনলাইনে যেকোনো পরিমাণ টাকা সরাসরি বিকাশ, নগদ বা কার্ড দিয়ে সহজে পরিশোধ করতে পারবেন।"
            ]

            details = [
                {'label': 'সদস্যের নাম', 'value': mem.name},
                {'label': 'পদবী', 'value': mem.effective_role},
                {'label': 'সদস্য আইডি (Member ID)', 'value': mem.member_id},
                {'label': 'নির্ধারিত মাসিক চাঁদা', 'value': f"৳{summary['monthly_fee']:,.2f} / মাস"},
                {'label': 'অন্তর্ভুক্তির তারিখ', 'value': summary['join_date_formatted']},
                {'label': 'প্রযোজ্য মাস সংখ্যা', 'value': f"{summary['months_billed']} মাস"},
                {'label': 'মোট ধার্যকৃত চাঁদা', 'value': f"৳{summary['total_billed']:,.2f}"},
                {'label': 'এ যাবৎ মোট পরিশোধিত', 'value': f"৳{summary['total_paid']:,.2f}"},
                {'label': 'বর্তমান বকেয়া (Due)', 'value': f"৳{summary['due_amount']:,.2f}"},
            ]
            if summary['advance_amount'] > 0:
                details.append({'label': 'অগ্রিম জমা (Advance)', 'value': f"৳{summary['advance_amount']:,.2f}"})

            action_buttons = [
                {'label': 'অনলাইনে চাঁদা পরিশোধ করুন', 'url': payment_url},
                {'label': 'মূল ওয়েবসাইট দেখুন', 'url': base_url},
            ]

            try:
                email_sent = send_system_email(
                    subject=subject,
                    recipient_list=[mem.email],
                    recipient_name=mem.name,
                    greeting="শ্রদ্ধেয় সদস্য",
                    headline="মাসিক চাঁদা হিসাব ও পলিসি হালনাগাদ",
                    message_paragraphs=paragraphs,
                    details=details,
                    action_buttons=action_buttons,
                    footer_note="সংগঠনকে শক্তিশালী ও গতিশীল রাখতে আপনার নিয়মিত সক্রিয় অংশগ্রহণ আমাদের গর্ব।",
                    fail_silently=True
                )
            except Exception as e:
                logger.error("Error sending email update to %s: %s", mem.email, e)

        sent_count += 1
        results.append({
            'member_id': mem.member_id,
            'name': mem.name,
            'phone': mem.phone,
            'email': mem.email,
            'monthly_fee': summary['monthly_fee'],
            'due_amount': summary['due_amount'],
            'advance_amount': summary['advance_amount'],
            'sms_sent': sms_sent,
            'email_sent': email_sent,
        })

    return results
