import logging
from datetime import datetime
from django.conf import settings
from core.email_utils import send_system_email, get_base_url, get_admin_notification_emails
from core.sms_utils import send_sms
from core.models import SiteSetting

logger = logging.getLogger(__name__)

def get_admin_contact_info():
    """Returns primary helpline phone and email from SiteSetting or fallback"""
    phone = '01748470965'
    email = 'helplinehellonaogaon@gmail.com'
    try:
        setting = SiteSetting.objects.first()
        if setting:
            if setting.contact_phone:
                phone = setting.contact_phone
            if setting.contact_email:
                email = setting.contact_email
    except Exception:
        pass
    return phone, email


def notify_admin_new_manual_donation(donation, request=None):
    """
    Dispatches instant SMS and Email notifications to Admin(s)
    whenever a user/member submits a manual donation (bKash/Nagad/Rocket/Bank) for approval.
    """
    admin_phone = getattr(settings, 'SMS_ADMIN_ALERT_PHONE', None) or '01748470965'
    base_url = get_base_url(request)
    contact_phone, _ = get_admin_contact_info()

    # 1. Admin SMS
    if admin_phone:
        try:
            sms_text = (
                f"[Helpline Hello Naogaon] নতুন ম্যানুয়াল পেমেন্ট জমা! "
                f"দাতা: {donation.donor_name}, পরিমাণ: ৳{donation.amount:,.0f}, "
                f"মাধ্যম: {donation.payment_method}, প্রেরক: {donation.sender_account or 'N/A'}, "
                f"TrxID: {donation.trx_id or 'N/A'}। অনুমোদনের অপেক্ষায়।"
            )
            send_sms(admin_phone, sms_text)
        except Exception as e:
            logger.error(f"[ADMIN MANUAL DONATION SMS ERROR] {e}")

    # 2. Admin Email
    try:
        admin_emails = get_admin_notification_emails()
        if admin_emails:
            admin_url = f"{base_url}/admin/donations/programdonation/{donation.id}/change/"
            dashboard_url = f"{base_url}/dashboard/?tab=finance-section"

            paragraphs = [
                "ওয়েবসাইটে একজন দাতা/সদস্য ম্যানুয়াল সেন্ড মানি বা ব্যাংক ডিপোজিটের মাধ্যমে পেমেন্ট করে ট্রানজেকশন তথ্য জমা দিয়েছেন।",
                "অনুগ্রহ করে আপনার মোবাইল ব্যাংকিং বা ব্যাংক স্টেটমেন্টের সাথে প্রদত্ত ট্রানজেকশন আইডি (TrxID) ও প্রেরক নম্বর মিলিয়ে দেখে এটি অনুমোদন (Approve) বা বাতিল (Reject) করুন।"
            ]

            details = [
                {'label': 'দাতা / সদস্যের নাম', 'value': donation.donor_name},
                {'label': 'মোবাইল নম্বর', 'value': donation.donor_phone},
            ]
            if donation.membership_id:
                details.append({'label': 'মেম্বারশিপ আইডি', 'value': donation.membership_id})
            if donation.donor_email:
                details.append({'label': 'দাতার ইমেইল', 'value': donation.donor_email})

            details.extend([
                {'label': 'অনুদানের পরিমাণ', 'value': f"৳ {donation.amount:,.2f}"},
                {'label': 'পেমেন্ট মাধ্যম', 'value': donation.payment_method},
                {'label': 'প্রেরকের নম্বর / অ্যাকাউন্ট', 'value': donation.sender_account or 'উল্লেখ নেই'},
                {'label': 'ট্রানজেকশন আইডি (TrxID)', 'value': donation.trx_id or 'উল্লেখ নেই'},
                {'label': 'ইনভয়েস ট্র্যাকিং নং', 'value': donation.tran_id or str(donation.id)},
                {'label': 'খাত / কার্যক্রম', 'value': donation.program.title if donation.program else ('সদস্য চাঁদা' if donation.membership_id else 'সাধারণ অনুদান')},
            ])
            if donation.note:
                details.append({'label': 'দাতার মন্তব্য / নোট', 'value': donation.note})

            action_buttons = [
                {'label': '✅ অ্যাডমিন প্যানেল থেকে অনুমোদন করুন', 'url': admin_url, 'style': 'success'},
                {'label': '📊 ড্যাশবোর্ড ফাইন্যান্স লেজার', 'url': dashboard_url, 'style': 'primary'},
            ]

            send_system_email(
                subject=f"🔔 নতুন ম্যানুয়াল অনুদান/চাঁদা অনুমোদনের অপেক্ষায় (৳{donation.amount:,.0f} - {donation.donor_name})",
                recipient_list=admin_emails,
                recipient_name="শ্রদ্ধেয় অ্যাডমিন",
                greeting="আসসালামু আলাইকুম",
                headline="নতুন ম্যানুয়াল পেমেন্ট অনুমোদনের অপেক্ষায়",
                message_paragraphs=paragraphs,
                details=details,
                action_buttons=action_buttons,
                footer_note="যেকোনো তথ্যের প্রয়োজনে যোগাযোগ: " + contact_phone,
                fail_silently=True,
                request=request
            )
    except Exception as e:
        logger.error(f"[ADMIN MANUAL DONATION EMAIL ERROR] {e}")


def notify_donor_manual_submission(donation, request=None):
    """
    Sends acknowledgment SMS & Email to donor that manual submission was received and is pending verification.
    """
    contact_phone, contact_email = get_admin_contact_info()

    # 1. Donor SMS
    if donation.donor_phone:
        try:
            donor_sms = (
                f"[Helpline Hello Naogaon] শ্রদ্ধেয় {donation.donor_name}, "
                f"আপনার ৳{donation.amount:,.0f} ম্যানুয়াল অনুদান/চাঁদার তথ্য সফলভাবে গৃহীত হয়েছে (যাচাই চলছে)। "
                f"অ্যাডমিন অনুমোদন শেষে নিশ্চিতকরণ বার্তা পাবেন। প্রয়োজনে: {contact_phone}"
            )
            send_sms(donation.donor_phone, donor_sms)
        except Exception as e:
            logger.error(f"[DONOR MANUAL SUBMIT SMS ERROR] {e}")

    # 2. Donor Email
    if donation.donor_email:
        try:
            paragraphs = [
                f"হেল্পলাইন হ্যালো নওগাঁর তহবিলে আপনার ৳{donation.amount:,.2f} ম্যানুয়াল সহায়তার তথ্য সফলভাবে জমা হয়েছে।",
                "আমাদের প্রশাসনিক দল আপনার প্রেরিত ট্রানজেকশন তথ্যটি স্টেটমেন্টের সাথে মিলিয়ে দেখে অতিসত্বর অনুমোদন করবে। অনুমোদন সম্পন্ন হওয়ার সাথে সাথে আপনি স্বয়ংক্রিয় রসিদ ও নিশ্চিতকরণ বার্তা পাবেন।"
            ]

            details = [
                {'label': 'দাতার নাম', 'value': donation.donor_name},
                {'label': 'সহায়তার পরিমাণ', 'value': f"৳ {donation.amount:,.2f}"},
                {'label': 'পেমেন্ট মাধ্যম', 'value': donation.payment_method},
                {'label': 'প্রেরকের নম্বর / অ্যাকাউন্ট', 'value': donation.sender_account or 'উল্লেখ নেই'},
                {'label': 'ট্রানজেকশন আইডি (TrxID)', 'value': donation.trx_id or 'উল্লেখ নেই'},
                {'label': 'ইনভয়েস ট্র্যাকিং নং', 'value': donation.tran_id or str(donation.id)},
                {'label': 'বর্তমান অবস্থা', 'value': 'অপেক্ষমাণ (Pending Verification)'},
            ]

            send_system_email(
                subject=f"⏳ আপনার অনুদান/চাঁদা তথ্য জমা হয়েছে — হেল্পলাইন হ্যালো নওগাঁ (৳{donation.amount:,.0f})",
                recipient_list=[donation.donor_email],
                recipient_name=donation.donor_name,
                greeting="শ্রদ্ধেয় দাতা,",
                headline="পেমেন্ট তথ্য সফলভাবে জমা হয়েছে",
                message_paragraphs=paragraphs,
                details=details,
                footer_note=f"যেকোনো প্রয়োজনে যোগাযোগ: {contact_phone} | {contact_email}",
                fail_silently=True,
                request=request
            )
        except Exception as e:
            logger.error(f"[DONOR MANUAL SUBMIT EMAIL ERROR] {e}")


def notify_donor_donation_approved(donation, request=None):
    """
    Sends official receipt and congratulatory confirmation SMS & Email when admin approves a donation.
    If the donor is a registered member, calculates and displays their remaining due or advance balance.
    """
    contact_phone, contact_email = get_admin_contact_info()
    base_url = get_base_url(request)

    # Calculate member subscription balance if donation is linked to a membership
    member_sub = None
    balance_sms_text = ""
    balance_email_text = ""
    if donation.membership_id:
        try:
            from volunteers.models import TeamMember
            from volunteers.subscription_services import get_member_subscription_summary
            tm = TeamMember.objects.filter(member_id__iexact=donation.membership_id).first()
            if tm:
                member_sub = get_member_subscription_summary(tm)
                due_amt = member_sub.get('due_amount', 0)
                adv_amt = member_sub.get('advance_amount', 0)
                if due_amt > 0:
                    balance_sms_text = f"বর্তমান বকেয়া চাঁদা: ৳{due_amt:,.0f}"
                    balance_email_text = f"আপনার বর্তমান বকেয়া চাঁদার পরিমাণ ৳{due_amt:,.2f}।"
                elif adv_amt > 0:
                    balance_sms_text = f"বর্তমান অগ্রিম জমা: ৳{adv_amt:,.0f}"
                    balance_email_text = f"আপনার বর্তমানে ৳{adv_amt:,.2f} অগ্রিম চাঁদা জমা রয়েছে।"
                else:
                    balance_sms_text = "চলতি চাঁদা সম্পূর্ণ পরিশোধিত"
                    balance_email_text = "আপনার চলতি মাসের চাঁদা সম্পূর্ণ পরিশোধিত রয়েছে।"
        except Exception as ex:
            logger.warning(f"Error calculating member subscription in approval notification: {ex}")

    # 1. Donor SMS
    if donation.donor_phone:
        try:
            if member_sub:
                donor_sms = (
                    f"[Helpline Hello Naogaon] শ্রদ্ধেয় {donation.donor_name}, "
                    f"আপনার ৳{donation.amount:,.0f} চাঁদা অনুমোদিত হয়েছে। "
                    f"{balance_sms_text}। "
                    f"TrxID: {donation.trx_id or donation.tran_id}। ধন্যবাদ। প্রয়োজনে: {contact_phone}"
                )
            else:
                donor_sms = (
                    f"[Helpline Hello Naogaon] শ্রদ্ধেয় {donation.donor_name}, "
                    f"আপনার ৳{donation.amount:,.0f} অনুদান সফলভাবে অনুমোদিত হয়েছে। "
                    f"TrxID: {donation.trx_id or donation.tran_id}। সংগঠনের পক্ষ থেকে ধন্যবাদ। প্রয়োজনে: {contact_phone}"
                )
            send_sms(donation.donor_phone, donor_sms)
        except Exception as e:
            logger.error(f"[DONOR APPROVAL SMS ERROR] {e}")

    # 2. Donor Email
    if donation.donor_email:
        try:
            paragraphs = [
                f"হেল্পলাইন হ্যালো নওগাঁর মাধ্যমে মানবতার সেবায় আপনার ৳{donation.amount:,.2f} অনুদান/চাঁদাটি সফলভাবে যাচাই ও অনুমোদিত হয়েছে।",
            ]
            if balance_email_text:
                paragraphs.append(balance_email_text)
            paragraphs.append("আপনার এই মহতী অবদান অসহায় ও সুবিধাবঞ্চিত মানুষের পাশে দাঁড়াতে আমাদের প্রেরণা যোগাবে। সংগঠনের পক্ষ থেকে আপনার প্রতি আন্তরিক ধন্যবাদ ও কৃতজ্ঞতা প্রকাশ করছি।")

            receipt_url = f"{base_url}/donations/receipt/{donation.id}/"

            details = [
                {'label': 'দাতা / সদস্যের নাম', 'value': donation.donor_name},
            ]
            if donation.membership_id:
                details.append({'label': 'মেম্বারশিপ আইডি', 'value': donation.membership_id})
            details.extend([
                {'label': 'অনুমোদিত অনুদানের পরিমাণ', 'value': f"৳ {donation.amount:,.2f}"},
                {'label': 'পেমেন্ট মাধ্যম', 'value': donation.payment_method},
            ])

            if member_sub:
                details.append({'label': 'নির্ধারিত মাসিক চাঁদা', 'value': f"৳ {member_sub.get('monthly_fee', 0):,.2f}"})
                details.append({'label': 'সর্বমোট পরিশোধিত চাঁদা', 'value': f"৳ {member_sub.get('total_paid', 0):,.2f}"})
                if member_sub.get('due_amount', 0) > 0:
                    details.append({'label': 'বর্তমান বকেয়া চাঁদা', 'value': f"৳ {member_sub.get('due_amount', 0):,.2f}"})
                elif member_sub.get('advance_amount', 0) > 0:
                    details.append({'label': 'অগ্রিম জমার পরিমাণ', 'value': f"৳ {member_sub.get('advance_amount', 0):,.2f}"})
                else:
                    details.append({'label': 'চাঁদার অবস্থা', 'value': 'সম্পূর্ণ পরিশোধিত (Paid in Full)'})

            details.extend([
                {'label': 'ট্রানজেকশন আইডি (TrxID)', 'value': donation.trx_id or donation.tran_id},
                {'label': 'ইনভয়েস ট্র্যাকিং নং', 'value': donation.tran_id or str(donation.id)},
                {'label': 'অনুমোদনের তারিখ', 'value': datetime.now().strftime('%d %B, %Y %I:%M %p')},
                {'label': 'কার্যক্রম / খাত', 'value': donation.program.title if donation.program else ('সদস্য চাঁদা' if donation.membership_id else 'সাধারণ তহবিল')},
                {'label': 'বর্তমান অবস্থা', 'value': 'অনুমোদিত (Approved)'},
            ])

            action_buttons = [
                {'label': '🧾 মানি রসিদ দেখুন / ডাউনলোড করুন', 'url': receipt_url, 'style': 'success'},
            ]

            send_system_email(
                subject=f"✅ অনুদান প্রাপ্তি নিশ্চিতকরণ — হেল্পলাইন হ্যালো নওগাঁ (৳{donation.amount:,.0f})",
                recipient_list=[donation.donor_email],
                recipient_name=donation.donor_name,
                greeting="শ্রদ্ধেয় দাতা,",
                headline="আপনার অনুদান/চাঁদা সফলভাবে অনুমোদিত হয়েছে",
                message_paragraphs=paragraphs,
                details=details,
                action_buttons=action_buttons,
                footer_note=f"যেকোনো তথ্যের প্রয়োজনে যোগাযোগ: {contact_phone} | {contact_email}",
                fail_silently=True,
                request=request
            )
        except Exception as e:
            logger.error(f"[DONOR APPROVAL EMAIL ERROR] {e}")


def notify_donor_donation_rejected(donation, reason='', request=None):
    """
    Sends polite notification SMS & Email to donor if payment could not be verified or was rejected,
    instructing them to contact admin immediately if they already paid or need clarification.
    """
    contact_phone, contact_email = get_admin_contact_info()

    # 1. Donor SMS
    if donation.donor_phone:
        try:
            donor_sms = (
                f"[Helpline Hello Naogaon] শ্রদ্ধেয় {donation.donor_name}, "
                f"আপনার জমাকৃত ৳{donation.amount:,.0f} পেমেন্ট তথ্যের সাথে আমাদের হিসাব মেলেনি বা তা যাচাই করা সম্ভব হয়নি। "
                f"কোনো সমস্যা বা ভুল হয়ে থাকলে অবিলম্বে যোগাযোগ করুন: {contact_phone}"
            )
            send_sms(donation.donor_phone, donor_sms)
        except Exception as e:
            logger.error(f"[DONOR REJECTION SMS ERROR] {e}")

    # 2. Donor Email
    if donation.donor_email:
        try:
            paragraphs = [
                f"শ্রদ্ধেয় {donation.donor_name}, হেল্পলাইন হ্যালো নওগাঁর তহবিলে আপনার জমাকৃত ৳{donation.amount:,.2f} টাকার পেমেন্ট তথ্যের সাথে আমাদের ব্যাংক বা মোবাইল ব্যাংকিং স্টেটমেন্ট মেলানো সম্ভব হয়নি অথবা তথ্যটি সঠিক পাওয়া যায়নি।",
                "যদি আপনার অ্যাকাউন্ট থেকে টাকা কেটে নেওয়া হয়ে থাকে অথবা ট্রানজেকশন তথ্য প্রদানে কোনো ভুল হয়ে থাকে, তবে কোনো চিন্তা করবেন না। অনুগ্রহ করে অবিলম্বে আমাদের প্রশাসনিক দলের সাথে যোগাযোগ করুন।"
            ]
            if reason:
                paragraphs.append(f"অ্যাডমিন মন্তব্য: {reason}")

            details = [
                {'label': 'দাতার নাম', 'value': donation.donor_name},
                {'label': 'সহায়তার পরিমাণ', 'value': f"৳ {donation.amount:,.2f}"},
                {'label': 'পেমেন্ট মাধ্যম', 'value': donation.payment_method},
                {'label': 'প্রেরকের নম্বর / অ্যাকাউন্ট', 'value': donation.sender_account or 'উল্লেখ নেই'},
                {'label': 'প্রদত্ত TrxID', 'value': donation.trx_id or 'উল্লেখ নেই'},
                {'label': 'ইনভয়েস ট্র্যাকিং নং', 'value': donation.tran_id or str(donation.id)},
                {'label': 'বর্তমান অবস্থা', 'value': 'যাচাই ব্যর্থ / বাতিল (Rejected)'},
                {'label': 'সহায়তা হেল্পলাইন', 'value': contact_phone},
                {'label': 'অফিসিয়াল ইমেইল', 'value': contact_email},
            ]

            send_system_email(
                subject=f"⚠️ অনুদান/চাঁদা তথ্য যাচাই সংক্রান্ত — হেল্পলাইন হ্যালো নওগাঁ",
                recipient_list=[donation.donor_email],
                recipient_name=donation.donor_name,
                greeting="শ্রদ্ধেয় দাতা,",
                headline="পেমেন্ট তথ্য যাচাই সংক্রান্ত নোটিফিকেশন",
                message_paragraphs=paragraphs,
                details=details,
                footer_note=f"আপনার সহযোগিতা আমাদের কাম্য। সরাসরি কথা বলতে কল করুন: {contact_phone}",
                fail_silently=True,
                request=request
            )
        except Exception as e:
            logger.error(f"[DONOR REJECTION EMAIL ERROR] {e}")
