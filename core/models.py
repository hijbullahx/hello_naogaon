from django.db import models

class SiteSetting(models.Model):
    title = models.CharField(max_length=200, default='Helpline Hello Naogaon')
    hero_title = models.CharField(max_length=200, default='Welcome to Helpline Hello Naogaon')
    hero_subtitle = models.TextField(default='We are dedicated to helping our community.')
    about_text = models.TextField(blank=True, default='')
    mission_text = models.TextField(blank=True, default='')
    vision_text = models.TextField(blank=True, default='')
    contact_email = models.EmailField(blank=True, default='')
    contact_phone = models.CharField(max_length=50, blank=True, default='')
    contact_address = models.TextField(blank=True, default='')

    def __str__(self):
        return "Site Settings"

    class Meta:
        verbose_name_plural = "Site Settings"

class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
