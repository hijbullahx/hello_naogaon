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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='volunteer_profile', null=True, blank=True)
    member_id = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="সদস্য আইডি")
    full_name = models.CharField(max_length=200, verbose_name="পূর্ণ নাম")
    email = models.EmailField(blank=True, null=True, verbose_name="ইমেইল")
    phone = models.CharField(max_length=20, verbose_name="মোবাইল নম্বর")
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True, null=True, verbose_name="রক্তের গ্রুপ")
    address = models.TextField(blank=True, null=True, verbose_name="ঠিকানা")
    image = models.ImageField(upload_to='volunteers/', blank=True, null=True, verbose_name="ছবি")
    occupation = models.CharField(max_length=100, blank=True, null=True, verbose_name="পেশা")
    is_public_details = models.BooleanField(default=True, verbose_name="মোবাইল নম্বর ও বিস্তারিত তথ্য সকলের জন্য প্রদর্শন করতে চান?")
    application_date = models.DateTimeField(auto_now_add=True, verbose_name="নিবন্ধনের তারিখ")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')

    class Meta:
        ordering = ['-application_date']
        verbose_name = "Volunteer Member"
        verbose_name_plural = "Volunteer Members"

    def __str__(self):
        return f"{self.full_name} ({self.member_id or 'No ID'})"

    def save(self, *args, **kwargs):
        if not self.member_id:
            today = date.today()
            prefix = today.strftime("%d%m%y")  # e.g. 210826 for 21 Aug 2026
            todays_volunteers = Volunteer.objects.filter(member_id__startswith=prefix).values_list('member_id', flat=True)
            max_seq = 0
            for mid in todays_volunteers:
                if mid and len(mid) == 8 and mid[6:].isdigit():
                    seq = int(mid[6:])
                    if seq > max_seq:
                        max_seq = seq
            next_seq = max_seq + 1
            if next_seq > 99:
                self.member_id = f"{prefix}{next_seq}"
            else:
                self.member_id = f"{prefix}{next_seq:02d}"
        super().save(*args, **kwargs)

class TeamMember(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100)
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    bio = models.TextField(blank=True)
    order = models.IntegerField(default=0, help_text='Order to display on the team page')

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

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
    full_name = models.CharField(max_length=200)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=200, help_text="Area / Thana in Naogaon")
    last_donated = models.DateField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['blood_group', 'full_name']
        verbose_name = "Blood Donor"
        verbose_name_plural = "Blood Donors"

    def __str__(self):
        return f"{self.full_name} ({self.blood_group}) - {self.phone}"
