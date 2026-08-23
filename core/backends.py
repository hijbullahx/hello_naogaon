from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class MultiIdentifierAuthBackend(ModelBackend):
    """
    Allows authentication using:
    1. Username
    2. Email address
    3. Member ID (from linked TeamMember or Volunteer profile)
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        identifier = username.strip()
        user = None

        # 1. Check exact username
        user = User.objects.filter(username__iexact=identifier).first()

        # 2. Check exact email
        if not user:
            user = User.objects.filter(email__iexact=identifier).first()

        # 3. Check TeamMember member_id
        if not user:
            try:
                from volunteers.models import TeamMember
                tm = TeamMember.objects.filter(member_id__iexact=identifier, user__isnull=False).select_related('user').first()
                if tm and tm.user:
                    user = tm.user
            except Exception:
                pass

        # 4. Check Volunteer member_id
        if not user:
            try:
                from volunteers.models import Volunteer
                vol = Volunteer.objects.filter(member_id__iexact=identifier, user__isnull=False).select_related('user').first()
                if vol and vol.user:
                    user = vol.user
            except Exception:
                pass

        # Validate password
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
