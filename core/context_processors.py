from core.models import SiteSetting
from volunteers.models import BloodDonor, Volunteer, TeamMember
from programs.models import Program
from news.models import Article
from gallery.models import Photo
from donations.models import Bank, DonationMethod, QRCode

def site_settings_context(request):
    """
    Global context processor to ensure a single source of truth for organization contact info.
    Synchronizes Phone, Email, Address, Google Map, Social links across the entire project.
    Also provides global programs, donation methods, and members for the donate modal.
    """
    try:
        setting = SiteSetting.objects.first()
        if not setting:
            setting, _ = SiteSetting.objects.get_or_create(pk=1)
    except Exception:
        setting = None

    try:
        global_programs = Program.objects.filter(target_amount__gt=0).exclude(status='completed').order_by('order', '-id')
        global_banks = Bank.objects.filter(is_active=True)
        global_donation_methods = DonationMethod.objects.filter(is_active=True)
        global_qrcodes = QRCode.objects.filter(is_active=True).select_related('method')
        global_team_members = TeamMember.objects.all().order_by('order', 'name')
        global_volunteers = Volunteer.objects.filter(status='approved').order_by('full_name')
        featured_board_program = Program.objects.filter(status='ongoing', is_featured_board=True).first()
    except Exception:
        global_programs = []
        global_banks = []
        global_donation_methods = []
        global_qrcodes = []
        global_team_members = []
        global_volunteers = []
        featured_board_program = None

    logged_in_member = None
    logged_in_donations = []
    logged_in_total_donated = 0
    if request.user.is_authenticated:
        try:
            logged_in_member = getattr(request.user, 'team_profile', None) or getattr(request.user, 'volunteer_profile', None)
            if logged_in_member:
                from donations.models import ProgramDonation
                from django.db.models import Q, Sum
                q_f = Q()
                m_id = getattr(logged_in_member, 'member_id', None)
                m_ph = getattr(logged_in_member, 'phone', None)
                m_em = getattr(logged_in_member, 'email', None)
                if m_id:
                    q_f |= Q(membership_id__iexact=m_id)
                if m_ph:
                    q_f |= Q(donor_phone__iexact=m_ph)
                if m_em:
                    q_f |= Q(donor_email__iexact=m_em)
                if q_f:
                    logged_in_donations = ProgramDonation.objects.filter(q_f).order_by('-created_at')
                    logged_in_total_donated = logged_in_donations.filter(status='approved').aggregate(Sum('amount'))['amount__sum'] or 0
        except Exception:
            pass

    manual_bkash = None
    manual_nagad = None
    manual_rocket = None
    manual_upay = None
    manual_bank = None
    manual_qrcode = None
    try:
        manual_bkash = DonationMethod.objects.filter(name__iexact='bKash').first()
        manual_nagad = DonationMethod.objects.filter(name__iexact='Nagad').first()
        manual_rocket = DonationMethod.objects.filter(name__iexact='Rocket').first()
        manual_upay = DonationMethod.objects.filter(name__iexact='Upay').first()
        manual_bank = Bank.objects.first()
        manual_qrcode = QRCode.objects.first()
    except Exception:
        pass

    return {
        'site_setting': setting,
        'global_programs': global_programs,
        'global_banks': global_banks,
        'global_donation_methods': global_donation_methods,
        'global_qrcodes': global_qrcodes,
        'manual_bkash': manual_bkash,
        'manual_nagad': manual_nagad,
        'manual_rocket': manual_rocket,
        'manual_upay': manual_upay,
        'manual_bank': manual_bank,
        'manual_qrcode': manual_qrcode,
        'global_team_members': global_team_members,
        'global_volunteers': global_volunteers,
        'featured_board_program': featured_board_program,
        'logged_in_member': logged_in_member,
        'logged_in_member_name': getattr(logged_in_member, 'name', '') if logged_in_member else '',
        'logged_in_donations': logged_in_donations,
        'logged_in_total_donated': logged_in_total_donated,
    }

def admin_dashboard_stats(request):
    """
    Context processor providing summary counts for the Cardly Admin Dashboard.
    """
    try:
        total_donors = BloodDonor.objects.count()
        total_volunteers = Volunteer.objects.count()
        ongoing_programs = Program.objects.filter(status='ongoing').count()
        total_articles = Article.objects.filter(is_published=True).count()
        total_photos = Photo.objects.count()
        total_banks = Bank.objects.count()
    except Exception:
        total_donors = 0
        total_volunteers = 0
        ongoing_programs = 0
        total_articles = 0
        total_photos = 0
        total_banks = 0

    return {
        'dashboard_stats': {
            'total_donors': total_donors,
            'total_volunteers': total_volunteers,
            'ongoing_programs': ongoing_programs,
            'total_articles': total_articles,
            'total_photos': total_photos,
            'total_banks': total_banks,
        }
    }
