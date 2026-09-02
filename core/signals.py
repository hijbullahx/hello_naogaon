import logging
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from core.email_utils import send_system_email, get_base_url

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def notify_superuser_creation(sender, instance, created, **kwargs):
    """
    Automatically sends an official email notification when a Superadmin account is created.
    """
    if created and instance.is_superuser and instance.email:
        try:
            base_url = get_base_url()
            current_time = datetime.now().strftime('%d %B, %Y %I:%M %p')
            
            subject = "🎉 হেল্পলাইন হ্যালো নওগাঁ — প্রধান অ্যাডমিন (Superadmin) অ্যাকাউন্ট প্রস্তুত!"
            greeting = "সম্মানিত প্রধান অ্যাডমিন"
            headline = "অভিনন্দন! আপনার সুপার অ্যাডমিন অ্যাকাউন্ট সক্রিয় হয়েছে"
            
            message_paragraphs = [
                "হেল্পলাইন হ্যালো নওগাঁ প্ল্যাটফর্মের সর্বোচ্চ প্রশাসনিক (Superadmin / মূল অ্যাডমিন) দায়িত্ব পালনের জন্য আপনার অ্যাকাউন্টটি সফলভাবে সক্রিয় করা হয়েছে।",
                "আপনি এখন থেকে হেল্পলাইন হ্যালো নওগাঁর প্রধান এডমিন ড্যাশবোর্ড, ওয়েবসাইট কন্টেন্ট (CMS), আর্থিক হিসাব-নিকাশ এবং কেন্দ্রীয় ডাটাবেসের পূর্ণ নিয়ন্ত্রণ ও ব্যবস্থাপনা পরিচালনা করতে পারবেন।"
            ]
            
            details = [
                {'label': 'ইউজারনেম (Username)', 'value': instance.username},
                {'label': 'ইমেইল এড্রেস (Email)', 'value': instance.email},
                {'label': 'অ্যাডমিন পদমর্যাদা', 'value': 'প্রধান অ্যাডমিন (Super Administrator)'},
                {'label': 'অ্যাক্সেস পারমিশন', 'value': 'ফুল সিস্টেম, CMS ও ফিন্যান্সিয়াল কন্ট্রোল'},
                {'label': 'অ্যাকাউন্ট তৈরির সময়', 'value': current_time},
            ]
            
            action_buttons = [
                {'label': 'অ্যাডমিন ড্যাশবোর্ডে প্রবেশ করুন', 'url': f"{base_url}/dashboard/"},
                {'label': 'মূল ওয়েবসাইট দেখুন', 'url': f"{base_url}/"},
            ]
            
            footer_note = "নিরাপত্তার স্বার্থে আপনার পাসওয়ার্ড ও লগইন সংক্রান্ত গোপনীয় তথ্য কারো সাথে শেয়ার করবেন না।"
            
            sent = send_system_email(
                subject=subject,
                recipient_list=[instance.email],
                recipient_name=instance.get_full_name() or instance.username,
                greeting=greeting,
                headline=headline,
                message_paragraphs=message_paragraphs,
                details=details,
                action_buttons=action_buttons,
                footer_note=footer_note,
                fail_silently=True
            )
            if sent:
                logger.info("Superuser creation notification email sent successfully to %s", instance.email)
            else:
                logger.warning("Superuser creation email could not be sent to %s", instance.email)
        except Exception as e:
            logger.error("Error sending superuser notification email: %s", e)


@receiver(post_save, sender=User)
def sync_superuser_to_team_member(sender, instance, created, **kwargs):
    """
    Ensure every superuser/main admin automatically has a corresponding TeamMember entry
    with role 'প্রধান অ্যাডমিন', so they appear in public leadership list.
    """
    if instance.is_superuser:
        try:
            from volunteers.models import TeamMember, generate_next_member_id
            tm = getattr(instance, 'team_profile', None)
            if not tm:
                tm = TeamMember.objects.filter(user=instance).first()
            if not tm and instance.email:
                tm = TeamMember.objects.filter(email__iexact=instance.email).first()
                if tm and not tm.user:
                    tm.user = instance
                    tm.save()
            if not tm:
                name = instance.get_full_name() or instance.username
                TeamMember.objects.create(
                    user=instance,
                    member_id=generate_next_member_id(),
                    name=name,
                    role='অন্যান্য',
                    custom_role='প্রধান অ্যাডমিন',
                    email=instance.email or '',
                    division='রাজশাহী',
                    district='নওগাঁ',
                    order=0,
                )
        except Exception as e:
            logger.error("Error auto-syncing superuser to TeamMember: %s", e)
