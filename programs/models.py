from django.db import models

class Program(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    )
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=255, blank=True, help_text="Short description for card display")
    description = models.TextField()
    icon_class = models.CharField(max_length=50, default='fas fa-hands-helping', help_text="e.g. 'fas fa-tint', 'fas fa-book-reader'")
    badge_color = models.CharField(max_length=30, default='success', help_text="Color: danger, success, warning, primary, info")
    image = models.ImageField(upload_to='programs/', blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="প্রোগ্রামের জন্য প্রয়োজনীয় আর্থিক সহায়তার পরিমাণ (ঐচ্ছিক)")
    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="সংগৃহীত অনুদানের পরিমাণ")
    order = models.IntegerField(default=0)
    is_featured_board = models.BooleanField(
        default=False, 
        verbose_name="সামনে বোর্ড/ব্যানার পপআপ", 
        help_text="চলমান কার্যক্রম হিসেবে হোমপেজে ৫ সেকেন্ডের পপআপ বোর্ড/ব্যানার আকারে প্রদর্শন করবে"
    )

    class Meta:
        ordering = ['order', '-id']

    @property
    def needs_funding(self):
        if self.status == 'completed':
            return False
        return bool(self.target_amount and self.target_amount > 0)

    @property
    def progress_percent(self):
        if self.target_amount and self.target_amount > 0:
            raised = float(self.raised_amount or 0)
            target = float(self.target_amount)
            if raised <= 0:
                return 0
            pct = (raised / target) * 100
            if pct >= 100:
                return 100
            if pct < 1:
                val = round(pct, 2)
                if val == 0:
                    val = 0.1
                return int(val) if val == int(val) else val
            return int(round(pct))
        return 0

    def save(self, *args, **kwargs):
        if self.status != 'ongoing':
            self.is_featured_board = False
        super().save(*args, **kwargs)
        if self.is_featured_board and self.status == 'ongoing':
            # Ensure only ONE program has is_featured_board=True
            Program.objects.filter(is_featured_board=True).exclude(pk=self.pk).update(is_featured_board=False)

    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='events/', blank=True, null=True)

    def __str__(self):
        return self.title

class SuccessStory(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='success_stories/', blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
