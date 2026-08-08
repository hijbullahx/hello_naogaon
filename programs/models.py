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
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']

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
