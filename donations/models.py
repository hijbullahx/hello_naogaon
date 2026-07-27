from django.db import models
from django.utils.translation import gettext_lazy as _

class DonationPageContent(models.Model):
    hero_title = models.CharField(max_length=200, default="আপনার দানে, হাসি ফুটবে ও মুখে")
    hero_subtitle = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to='donations/hero/', blank=True, null=True)
    
    intro_title = models.CharField(max_length=200, default="দান করুন")
    intro_text = models.TextField(blank=True)

    why_donate_title = models.CharField(max_length=200, default="কেন দান করবেন?")
    why_donate_text = models.TextField(blank=True)

    transparency_title = models.CharField(max_length=200, default="স্বচ্ছতা")
    transparency_text = models.TextField(blank=True)
    
    contact_title = models.CharField(max_length=200, default="দানের জন্য যোগাযোগ")
    contact_text = models.TextField(blank=True)

    thank_you_title = models.CharField(max_length=200, default="ধন্যবাদ")
    thank_you_text = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Donation Page Content")
        verbose_name_plural = _("Donation Page Contents")

    def __str__(self):
        return self.hero_title

class Campaign(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='donations/campaigns/')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")
        ordering = ['-start_date']

    def __str__(self):
        return self.title

class DonationImpact(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    icon_class = models.CharField(max_length=50, blank=True, help_text="e.g., 'fas fa-home'")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Donation Impact")
        verbose_name_plural = _("Donation Impacts")
        ordering = ['amount']
        
    def __str__(self):
        return f"BDT {self.amount}: {self.description}"

class EmergencyAppeal(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='donations/appeals/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Emergency Appeal")
        verbose_name_plural = _("Emergency Appeals")
        ordering = ['-created_at']

    def __str__(self):
        return self.title
        
class DonationMethod(models.Model):
    name = models.CharField(max_length=100, help_text='e.g., bKash, Bank Transfer')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Donation Method")
        verbose_name_plural = _("Donation Methods")

    def __str__(self):
        return self.name
        
class Bank(models.Model):
    bank_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50)
    branch = models.CharField(max_length=100, blank=True)
    swift_code = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

class QRCode(models.Model):
    method = models.ForeignKey(DonationMethod, on_delete=models.CASCADE, related_name='qrcodes')
    image = models.ImageField(upload_to='donations/qrcodes/')
    details = models.CharField(max_length=255, blank=True, help_text="e.g., Merchant number, account name")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("QR Code")
        verbose_name_plural = _("QR Codes")

    def __str__(self):
        return f"QR Code for {self.method.name}"

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")

    def __str__(self):
        return self.question

class DonationStatistic(models.Model):
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=50, blank=True, help_text="e.g., 'fas fa-users'")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Donation Statistic")
        verbose_name_plural = _("Donation Statistics")
        
    def __str__(self):
        return f"{self.label}: {self.value}"
