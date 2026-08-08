from volunteers.models import BloodDonor, Volunteer
from programs.models import Program
from news.models import Article
from core.models import ContactMessage
from gallery.models import Photo
from donations.models import Bank

def admin_dashboard_stats(request):
    """
    Context processor providing summary counts for the Cardly Admin Dashboard.
    """
    try:
        total_donors = BloodDonor.objects.count()
        total_volunteers = Volunteer.objects.count()
        ongoing_programs = Program.objects.filter(status='ongoing').count()
        total_articles = Article.objects.filter(is_published=True).count()
        unread_messages = ContactMessage.objects.filter(is_read=False).count()
        total_photos = Photo.objects.count()
        total_banks = Bank.objects.count()
    except Exception:
        total_donors = 0
        total_volunteers = 0
        ongoing_programs = 0
        total_articles = 0
        unread_messages = 0
        total_photos = 0
        total_banks = 0

    return {
        'dashboard_stats': {
            'total_donors': total_donors,
            'total_volunteers': total_volunteers,
            'ongoing_programs': ongoing_programs,
            'total_articles': total_articles,
            'unread_messages': unread_messages,
            'total_photos': total_photos,
            'total_banks': total_banks,
        }
    }
