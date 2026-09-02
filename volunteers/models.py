from django.db import models
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

class Volunteer(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    )

    BLOOD_GROUPS = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    )

    CONTRIBUTION_FREQUENCIES = (
        ('none', 'কোনো নির্দিষ্ট প্রতিশ্রুতি নেই / ইচ্ছানুযায়ী'),
        ('monthly', 'মাসিক (প্রতি মাসে)'),
        ('weekly', 'সাপ্তাহিক (প্রতি সপ্তাহে)'),
        ('yearly', 'বাৎসরিক (প্রতি বছরে)'),
        ('one_time', 'এককালীন'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='volunteer_profile', null=True, blank=True)
    member_id = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="সদস্য আইডি")
    full_name = models.CharField(max_length=200, verbose_name="পূর্ণ নাম")
    email = models.EmailField(blank=True, null=True, verbose_name="ইমেইল")
    phone = models.CharField(max_length=20, verbose_name="মোবাইল নম্বর")
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True, null=True, verbose_name="রক্তের গ্রুপ")
    division = models.CharField(max_length=100, default="রাজশাহী", blank=True, verbose_name="বিভাগ")
    district = models.CharField(max_length=100, default="নওগাঁ", blank=True, verbose_name="জেলা")
    upazila = models.CharField(max_length=100, blank=True, null=True, verbose_name="উপজেলা / থানা")
    address = models.TextField(blank=True, null=True, verbose_name="ঠিকানা / স্থানীয় ঠিকানা")
    image = models.ImageField(upload_to='volunteers/', blank=True, null=True, verbose_name="ছবি")
    occupation = models.CharField(max_length=100, blank=True, null=True, verbose_name="পেশা")
    last_donated = models.DateField(blank=True, null=True, verbose_name="সর্বশেষ রক্তদানের তারিখ")
    contribution_frequency = models.CharField(max_length=20, choices=CONTRIBUTION_FREQUENCIES, default='none', blank=True, verbose_name="আর্থিক সহায়তার প্রতিশ্রুতি")
    contribution_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, verbose_name="প্রতিশ্রুত আর্থিক পরিমাণ (টাকা)")
    is_public_details = models.BooleanField(default=True, verbose_name="মোবাইল নম্বর ও বিস্তারিত তথ্য সকলের জন্য প্রদর্শন করতে চান?")
    application_date = models.DateTimeField(auto_now_add=True, verbose_name="নিবন্ধনের তারিখ")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')

    class Meta:
        ordering = ['-application_date']
        verbose_name = "Volunteer Member"
        verbose_name_plural = "Volunteer Members"

    def __str__(self):
        return f"{self.full_name} ({self.member_id or 'No ID'})"

    @property
    def full_address(self):
        if self.address and self.upazila and self.upazila in self.address:
            return self.address
        parts = [p for p in [self.address, self.upazila, self.district] if p]
        return ", ".join(parts) if parts else (self.address or "নওগাঁ")

    @property
    def is_eligible_to_donate(self):
        if not self.last_donated:
            return True
        diff = (date.today() - self.last_donated).days
        return diff >= 90

    @property
    def days_until_eligible(self):
        if not self.last_donated:
            return 0
        diff = (date.today() - self.last_donated).days
        return max(0, 90 - diff)

    def save(self, *args, **kwargs):
        if not self.member_id:
            today = date.today()
            prefix = today.strftime("%y%m%d")  # e.g. 260823 for 23 Aug 2026 (YYMMDD)
            todays_volunteers = Volunteer.objects.filter(member_id__startswith=prefix).values_list('member_id', flat=True)
            max_seq = 0
            for mid in todays_volunteers:
                if mid and len(mid) == 8 and mid[6:].isdigit():
                    seq = int(mid[6:])
                    if seq > max_seq:
                        max_seq = seq
            next_seq = max_seq + 1
            if next_seq > 99:
                raise ValueError("আজকের দিনের জন্য সর্বোচ্চ ৯৯ জন সদস্য নিবন্ধনের কোটা পূর্ণ হয়েছে। অনুগ্রহ করে আগামীকাল পুনরায় চেষ্টা করুন।")
            self.member_id = f"{prefix}{next_seq:02d}"
        super().save(*args, **kwargs)

        # Auto sync to BloodDonor database if blood_group is provided
        if self.blood_group:
            BloodDonor.objects.update_or_create(
                phone=self.phone,
                defaults={
                    'full_name': self.full_name,
                    'blood_group': self.blood_group,
                    'division': self.division or 'রাজশাহী',
                    'district': self.district or 'নওগাঁ',
                    'upazila': self.upazila,
                    'location': self.address or self.upazila or 'নওগাঁ',
                    'last_donated': self.last_donated,
                    'member_id': self.member_id,
                    'is_public_details': self.is_public_details,
                    'is_available': True,
                }
            )

class TeamMember(models.Model):
    ROLE_CHOICES = (
        ('সভাপতি', 'সভাপতি (President)'),
        ('সাধারণ সম্পাদক', 'সাধারণ সম্পাদক (General Secretary)'),
        ('কোষাধ্যক্ষ', 'কোষাধ্যক্ষ (Treasurer)'),
        ('সাধারণ পরিষদ সদস্য', 'সাধারণ পরিষদ সদস্য (General Council Member)'),
        ('অন্যান্য', 'অন্যান্য (Other)'),
    )

    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='team_profile', null=True, blank=True, verbose_name="ইউজার অ্যাকাউন্ট")
    member_id = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="সদস্য আইডি")
    name = models.CharField(max_length=200, verbose_name="পূর্ণ নাম")
    role = models.CharField(max_length=100, verbose_name="পদবী / ভূমিকা")
    custom_role = models.CharField(max_length=100, blank=True, null=True, verbose_name="কাস্টম পদবী (যদি অন্যান্য হয়)")
    email = models.EmailField(blank=True, null=True, verbose_name="ইমেইল এড্রেস")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="ফোন নম্বর")
    division = models.CharField(max_length=100, default="রাজশাহী", blank=True, null=True, verbose_name="বিভাগ")
    district = models.CharField(max_length=100, default="নওগাঁ", blank=True, null=True, verbose_name="জেলা")
    upazila = models.CharField(max_length=100, blank=True, null=True, verbose_name="উপজেলা / থানা")
    address = models.TextField(blank=True, null=True, verbose_name="ঠিকানা")
    image = models.ImageField(upload_to='team/', blank=True, null=True, verbose_name="ছবি")
    bio = models.TextField(blank=True, verbose_name="সংক্ষিপ্ত বিবরণ")
    order = models.IntegerField(default=0, help_text='Order to display on the team page', verbose_name="প্রদর্শনের ক্রম")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="যোগদানের তারিখ")

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.name} ({self.effective_role}) - {self.member_id or 'No ID'}"

    @property
    def full_address(self):
        parts = [p for p in [self.address, self.upazila, self.district, self.division] if p]
        return ", ".join(parts) if parts else (self.address or "")

    @property
    def effective_role(self):
        if self.role == 'অন্যান্য' and self.custom_role:
            return self.custom_role
        return self.role or ''

    def clean(self):
        from django.core.exceptions import ValidationError
        # Role quota limits
        single_roles = ['সভাপতি', 'সাধারণ সম্পাদক', 'কোষাধ্যক্ষ']
        if self.role in single_roles:
            qs = TeamMember.objects.filter(role=self.role)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(f'দুঃখিত! "{self.role}" পদবীতে ইতিমধ্যে ১ জন সদস্য নিযুক্ত রয়েছেন। একক পদে একাধিক সদস্য থাকতে পারবেন না।')
        elif self.role == 'সাধারণ পরিষদ সদস্য':
            qs = TeamMember.objects.filter(role='সাধারণ পরিষদ সদস্য')
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.count() >= 4:
                raise ValidationError('দুঃখিত! "সাধারণ পরিষদ সদস্য" পদে সর্বোচ্চ ৪ জন সদস্যের কোটা পূর্ণ রয়েছে।')

    def save(self, *args, **kwargs):
        self.clean()
        if not self.member_id:
            today = date.today()
            prefix = f"HHN{today.strftime('%y%m%d')}"
            count = TeamMember.objects.filter(member_id__startswith=prefix).count()
            self.member_id = f"{prefix}{count + 1:02d}"
        try:
            self.order = int(self.order or 0)
        except (ValueError, TypeError):
            self.order = 0
        super().save(*args, **kwargs)

class BloodDonor(models.Model):
    BLOOD_GROUPS = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    )
    member_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="সদস্য আইডি (যদি থাকে)")
    full_name = models.CharField(max_length=200, verbose_name="পূর্ণ নাম")
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, verbose_name="রক্তের গ্রুপ")
    phone = models.CharField(max_length=20, verbose_name="মোবাইল নম্বর")
    division = models.CharField(max_length=100, default="রাজশাহী", blank=True, verbose_name="বিভাগ")
    district = models.CharField(max_length=100, default="নওগাঁ", blank=True, verbose_name="জেলা")
    upazila = models.CharField(max_length=100, blank=True, null=True, verbose_name="উপজেলা / থানা")
    location = models.CharField(max_length=255, help_text="Area / Address", verbose_name="ঠিকানা / এলাকা")
    last_donated = models.DateField(blank=True, null=True, verbose_name="সর্বশেষ রক্তদানের তারিখ")
    is_available = models.BooleanField(default=True, verbose_name="রক্তদানে সক্রিয়")
    is_public_details = models.BooleanField(default=True, verbose_name="তথ্য সকলের জন্য প্রদর্শন করতে চান?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="তালিকাভুক্তির তারিখ")

    class Meta:
        ordering = ['blood_group', 'full_name']
        verbose_name = "Blood Donor"
        verbose_name_plural = "Blood Donors"

    def __str__(self):
        return f"{self.full_name} ({self.blood_group}) - {self.phone}"

    @property
    def full_address(self):
        if self.location and self.upazila and self.upazila in self.location:
            return self.location
        parts = [p for p in [self.location, self.upazila, self.district] if p]
        return ", ".join(parts) if parts else (self.location or "নওগাঁ")

    @property
    def is_eligible_to_donate(self):
        if not self.is_available:
            return False
        if not self.last_donated:
            return True
        diff = (date.today() - self.last_donated).days
        return diff >= 90

    @property
    def days_until_eligible(self):
        if not self.last_donated:
            return 0
        diff = (date.today() - self.last_donated).days
        return max(0, 90 - diff)