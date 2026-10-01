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
    except Exception:
        global_programs = []
        global_banks = []
        global_donation_methods = []
        global_qrcodes = []
        global_team_members = []
        global_volunteers = []

    return {
        'site_setting': setting,
        'global_programs': global_programs,
        'global_banks': global_banks,
        'global_donation_methods': global_donation_methods,
        'global_qrcodes': global_qrcodes,
        'global_team_members': global_team_members,
        'global_volunteers': global_volunteers,
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
