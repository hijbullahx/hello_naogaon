from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from core.models import SiteSetting


def get_base_url(request=None):
    """Returns absolute base URL without trailing slash"""
    if request:
        try:
            return request.build_absolute_uri('/')[:-1]
        except Exception:
            pass
    return getattr(settings, 'SITE_URL', 'https://helplinehellonaogaon.com').rstrip('/')


def send_system_email(
    subject,
    recipient_list=None,
    recipient_name=None,
    greeting=None,
    headline=None,
    message_paragraphs=None,
    details=None,
    action_buttons=None,
    login_info=None,
    volunteer=None,
    team_member=None,
    footer_note=None,
    from_email=None,
    request=None,
    fail_silently=True,
):
    """
    Unified high-quality Email sender for Helpline Hello Naogaon.
    Renders responsive branded HTML email template and Plaintext fallback.
    """
    try:
        site_setting = SiteSetting.objects.first()
    except Exception:
        site_setting = None

    site_title = site_setting.title if site_setting and site_setting.title else "Helpline Hello Naogaon"
    site_tagline = site_setting.tagline if site_setting and site_setting.tagline else "সবসময় আপনার পাশে - একটি মানবিক ও স্বেচ্ছাসেবী সংগঠন"
    contact_email = site_setting.contact_email if site_setting and site_setting.contact_email else "info@helplinehellonaogaon.com"
    contact_phone = site_setting.contact_phone if site_setting and site_setting.contact_phone else ""
    contact_address = site_setting.contact_address if site_setting and site_setting.contact_address else ""

    base_url = get_base_url(request)
    current_year = datetime.now().year

    # Normalize recipient list
    if isinstance(recipient_list, str):
        recipient_list = [recipient_list]
    elif recipient_list is None:
        recipient_list = []

    if message_paragraphs is None:
        message_paragraphs = []
    elif isinstance(message_paragraphs, str):
        message_paragraphs = [message_paragraphs]

    formatted_details = []
    if details:
        if isinstance(details, dict):
            for k, v in details.items():
                if v:
                    formatted_details.append({'label': str(k), 'value': str(v)})
        elif isinstance(details, list):
            for item in details:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    formatted_details.append({'label': str(item[0]), 'value': str(item[1])})
                elif isinstance(item, dict) and 'label' in item and 'value' in item:
                    formatted_details.append(item)

    final_buttons = list(action_buttons) if action_buttons else []

    # 1. Automatic context enrichment for Volunteer / Blood Donor
    if volunteer:
        if not recipient_list and volunteer.email:
            recipient_list = [volunteer.email]
        if not recipient_name:
            recipient_name = volunteer.full_name
        if not headline:
            headline = "সদস্য নিবন্ধন সফল হয়েছে!"

        # Auto details for volunteer
        vol_details = [
            {'label': 'সদস্য আইডি (Member ID)', 'value': volunteer.member_id or 'N/A'},
            {'label': 'পূর্ণ নাম', 'value': volunteer.full_name},
            {'label': 'মোবাইল নম্বর', 'value': volunteer.phone},
            {'label': 'রক্তের গ্রুপ', 'value': volunteer.blood_group or 'N/A'},
            {'label': 'পেশা', 'value': volunteer.occupation or 'N/A'},
            {'label': 'ঠিকানা', 'value': volunteer.full_address},
        ]

        # Financial Pledge detail if present
        if volunteer.contribution_frequency and volunteer.contribution_frequency != 'none' and volunteer.contribution_amount and volunteer.contribution_amount > 0:
            freq_dict = {
                'monthly': 'মাসিক (প্রতি মাসে)',
                'weekly': 'সাপ্তাহিক (প্রতি সপ্তাহে)',
                'yearly': 'বাৎসরিক (প্রতি বছরে)',
                'one_time': 'এককালীন',
            }
            freq_text = freq_dict.get(volunteer.contribution_frequency, volunteer.contribution_frequency)
            vol_details.append({
                'label': 'আর্থিক সহায়তার প্রতিশ্রুতি',
                'value': f"{freq_text} - ৳{volunteer.contribution_amount:,.2f}"
            })

        # Prepend to details if not already present
        existing_labels = {d['label'] for d in formatted_details}
        for vd in vol_details:
            if vd['label'] not in existing_labels:
                formatted_details.append(vd)

        # Auto Action Buttons for Volunteer:
        if volunteer.member_id:
            profile_url = f"{base_url}/volunteers/blood-donors/?q={volunteer.member_id}"
            donate_url = f"{base_url}/donations/donate/?member_id={volunteer.member_id}"
            
            if not any(b.get('url') == profile_url for b in final_buttons):
                final_buttons.append({
                    'label': '🔎 আপনার প্রোফাইল দেখুন',
                    'url': profile_url,
                    'style': 'primary'
                })
            
            if not any(b.get('url') == donate_url for b in final_buttons):
                final_buttons.append({
                    'label': '❤️ আর্থিক সহায়তা প্রদান',
                    'url': donate_url,
                    'style': 'warning'
                })

    # 2. Automatic context enrichment for Team Member (সভাপতি, সাধারণ সম্পাদক, কোষাধ্যক্ষ, পরিষদ সদস্য, ইত্যাদি)
    if team_member:
        if not recipient_list and team_member.email:
            recipient_list = [team_member.email]
        if not recipient_name:
            recipient_name = team_member.name
        if not headline:
            headline = f"টিম সদস্য ({team_member.effective_role}) বিবরণ"

        tm_details = [
            {'label': 'মেম্বার আইডি', 'value': team_member.member_id or 'N/A'},
            {'label': 'পদবী / ভূমিকা', 'value': team_member.effective_role},
            {'label': 'মোবাইল নম্বর', 'value': team_member.phone or 'N/A'},
            {'label': 'ইমেইল এড্রেস', 'value': team_member.email or 'N/A'},
        ]
        if team_member.address:
            tm_details.append({'label': 'ঠিকানা', 'value': team_member.address})

        existing_labels = {d['label'] for d in formatted_details}
        for td in tm_details:
            if td['label'] not in existing_labels:
                formatted_details.append(td)

        login_url = f"{base_url}/accounts/login/"
        if login_info or team_member.user:
            if not any(b.get('url') == login_url for b in final_buttons):
                final_buttons.insert(0, {
                    'label': '🔐 অ্যাকাউন্টে লগইন করুন',
                    'url': login_url,
                    'style': 'primary'
                })

        about_url = f"{base_url}/about/"
        if not any(b.get('url') == about_url for b in final_buttons):
            final_buttons.append({
                'label': '👥 পরিচালনা পর্ষদ তালিকা',
                'url': about_url,
                'style': 'info'
            })

    # Always ensure a website home button exists if less than 3 buttons
    if len(final_buttons) < 3:
        home_url = f"{base_url}/"
        if not any(b.get('url') == home_url for b in final_buttons):
            final_buttons.append({
                'label': '🌐 ওয়েবসাইট ভিজিট',
                'url': home_url,
                'style': 'secondary'
            })

    # Filter recipients
    valid_recipients = [r.strip() for r in recipient_list if r and isinstance(r, str) and '@' in r]
    if not valid_recipients:
        return False

    context = {
        'subject': subject,
        'site_title': site_title,
        'site_tagline': site_tagline,
        'site_url': base_url,
        'site_domain': 'helplinehellonaogaon.com',
        'contact_email': contact_email,
        'contact_phone': contact_phone,
        'contact_address': contact_address,
        'current_year': current_year,
        'recipient_name': recipient_name,
        'greeting': greeting,
        'headline': headline,
        'message_paragraphs': message_paragraphs,
        'details': formatted_details,
        'login_info': login_info,
        'action_buttons': final_buttons,
        'footer_note': footer_note,
    }

    # Render HTML template
    html_content = render_to_string('emails/system_email.html', context)

    # Build plain text fallback
    plain_text_lines = [
        f"{site_title} - {site_tagline}",
        "=" * 50,
        f"{subject}",
        "=" * 50,
        "",
        f"{greeting or 'আসসালামু আলাইকুম'}{', ' + recipient_name if recipient_name else ''}",
        "",
    ]
    for p in message_paragraphs:
        plain_text_lines.append(p)
        plain_text_lines.append("")

    if formatted_details:
        plain_text_lines.append("📋 বিবরণ ও তথ্যাবলী:")
        plain_text_lines.append("-" * 30)
        for item in formatted_details:
            plain_text_lines.append(f"{item['label']}: {item['value']}")
        plain_text_lines.append("")

    if login_info:
        plain_text_lines.append("🔐 একাউন্ট লগইন তথ্য:")
        plain_text_lines.append("-" * 30)
        if login_info.get('username'):
            plain_text_lines.append(f"ইউজারনেম / আইডি: {login_info['username']}")
        if login_info.get('password'):
            plain_text_lines.append(f"পাসওয়ার্ড: {login_info['password']}")
        if login_info.get('role'):
            plain_text_lines.append(f"পদবী: {login_info['role']}")
        plain_text_lines.append(f"লগইন লিংক: {base_url}/accounts/login/")
        plain_text_lines.append("")

    if final_buttons:
        plain_text_lines.append("প্রয়োজনীয় লিংক:")
        plain_text_lines.append("-" * 30)
        for btn in final_buttons:
            plain_text_lines.append(f"{btn['label']}: {btn['url']}")
        plain_text_lines.append("")

    if footer_note:
        plain_text_lines.append(f"নোট: {footer_note}")
        plain_text_lines.append("")

    plain_text_lines.extend([
        "ধন্যবাদান্তে,",
        f"{site_title} টিম",
        f"ওয়েবসাইট: {base_url}",
        f"যোগাযোগ: {contact_phone} | {contact_email}",
        "",
        f"© {current_year} {site_title} — All Rights Reserved | Developed by Md. Taher Bin Omar Hijbullah (https://hijbullah.me/)",
    ])

    text_content = "\n".join(plain_text_lines)

    # Determine sender email with display name
    raw_from = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@helplinehellonaogaon.com') or 'info@helplinehellonaogaon.com'
    if '<' not in raw_from:
        formatted_from = f"{site_title} <{raw_from}>"
    else:
        formatted_from = raw_from

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=formatted_from,
            to=valid_recipients,
            reply_to=[contact_email] if contact_email else None,
        )
        msg.attach_alternative(html_content, "text/html")
        sent_count = msg.send(fail_silently=fail_silently)
        return bool(sent_count)
    except Exception as e:
        if not fail_silently:
            raise
        return False
