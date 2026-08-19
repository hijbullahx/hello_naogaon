from django.db import models
from django.utils.translation import gettext_lazy as _

class DonationPageContent(models.Model):
    hero_title = models.CharField(max_length=200, default="চলুন আনন্দ ছড়াই")
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

class FinancialTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'আয় / অনুদান (Income)'),
        ('expense', 'ব্যয় / খরচ (Expense)'),
    ]

    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='income')
    title = models.CharField(max_length=255, help_text="খাতের নাম বা শিরোনাম")
    category = models.CharField(max_length=100, default="সাধারণ অনুদান")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, default="bKash")
    trx_id = models.CharField(max_length=100, blank=True, help_text="Transaction ID / Receipt No")
    donor_name = models.CharField(max_length=200, blank=True, help_text="দাতা বা গ্রহণকারীর নাম")
    date = models.DateField()
    note = models.TextField(blank=True)
    receipt = models.ImageField(upload_to='donations/receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Financial Transaction")
        verbose_name_plural = _("Financial Transactions")
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.title}: ৳{self.amount}"



class ProgramDonation(models.Model):
    STATUS_CHOICES = [
        ('pending', _('অপেক্ষমাণ (Pending)')),
        ('approved', _('অনুমোদিত (Approved)')),
        ('rejected', _('বাতিল (Rejected)')),
    ]

    program = models.ForeignKey('programs.Program', on_delete=models.SET_NULL, null=True, blank=True, related_name='donations', verbose_name=_('কার্যক্রম (Program)'))
    donor_name = models.CharField(max_length=200, verbose_name=_('দাতা/সহায়তাকারীর নাম'))
    donor_email = models.EmailField(blank=True, verbose_name=_('ইমেইল'))
    donor_phone = models.CharField(max_length=20, verbose_name=_('মোবাইল নম্বর'))
    membership_id = models.CharField(max_length=50, blank=True, null=True, help_text=_('মেম্বারশিপ আইডি (যদি থাকে)'), verbose_name=_('মেম্বারশিপ আইডি'))
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('আর্থিক সহায়তার পরিমাণ (BDT)'))
    payment_method = models.CharField(max_length=50, default='bKash', verbose_name=_('পেমেন্ট মেথড'))
    trx_id = models.CharField(max_length=100, blank=True, verbose_name=_('ট্রানজেকশন আইডি / Trx ID'))
    note = models.TextField(blank=True, verbose_name=_('মন্তব্য / নোট'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved', verbose_name=_('স্ট্যাটাস'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('তারিখ ও সময়'))

    class Meta:
        verbose_name = _('Program Donation')
        verbose_name_plural = _('Program Donations')
        ordering = ['-created_at']

    def __str__(self):
        prog_title = self.program.title if self.program else 'সাধারণ কার্যক্রম'
        return f'{self.donor_name} - {prog_title} (৳{self.amount})'
