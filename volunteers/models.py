from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Volunteer(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='volunteer_profile', null=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.full_name

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
