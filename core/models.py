from django.db import models

class SiteSetting(models.Model):
    title = models.CharField(max_length=200, default='Helpline Hello Naogaon')
    tagline = models.CharField(max_length=255, default='সবসময় আপনার পাশে - একটি স্বেচ্ছাসেবী সংগঠন')
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    
    # Hero Section Settings
    hero_badge = models.CharField(max_length=200, default='মানবতার পাশে, নওগাঁর প্রতিটি মানুষের জন্য')
    hero_title = models.CharField(max_length=200, default='Helpline Hello Naogaon')
    hero_subtitle = models.TextField(default='আমরা একটি অরাজনৈতিক, অলাভজনক ও স্বেচ্ছাসেবী সংগঠন, যা সমাজের অসহায় মানুষের পাশে দাঁড়াতে প্রতিশ্রুতিবদ্ধ।')
    hero_image = models.ImageField(upload_to='site/', blank=True, null=True)
    
    # About Section Settings
    about_heading = models.CharField(max_length=200, default='আমাদের সম্পর্কে')
    about_text = models.TextField(blank=True, default='Helpline Hello Naogaon একটি স্বেচ্ছাসেবী ও মানবিক সংগঠন। আমরা রক্তদান, শিক্ষা সহায়তা, মানবিক সহায়তা, পরিবেশ সুরক্ষা ও দুর্যোগকালীন সেবাসহ বিভিন্ন সামাজিক কার্যক্রম পরিচালনা করে থাকি।')
    mission_text = models.TextField(blank=True, default='')
    vision_text = models.TextField(blank=True, default='')

    # CTA Banner Settings
    cta_banner_title = models.CharField(max_length=255, default='আসুন, আমরা সবাই মিলে একটি মানবিক ও সুন্দর সমাজ গড়ে তুলি')
    cta_banner_button_text = models.CharField(max_length=100, default='স্বেচ্ছাসেবক হন')

    # Contact & Social Media
    contact_email = models.EmailField(blank=True, default='hello.naogaon@gmail.com')
    contact_phone = models.CharField(max_length=50, blank=True, default='+880 1730-XXXXXX')
    contact_address = models.TextField(blank=True, default='Helpline Hello Naogaon Public Library, মহাদেবপুর, নওগাঁ - ৬৬০০')
    facebook_url = models.URLField(blank=True, default='https://facebook.com/hello.naogaon')
    youtube_url = models.URLField(blank=True, default='')
    whatsapp_number = models.CharField(max_length=50, blank=True, default='+880 1730-XXXXXX')
    footer_about = models.TextField(blank=True, default='Helpline Hello Naogaon একটি স্বেচ্ছাসেবী সংগঠন। আমাদের লক্ষ্য সমাজকে এগিয়ে নিয়ে যাওয়া এবং অসহায় মানুষের পাশে দাঁড়ানো।')
    google_map_embed_url = models.TextField(blank=True, default='')

    def __str__(self):
        return "Site Settings"

    class Meta:
        verbose_name_plural = "Site Settings"

class StatCounter(models.Model):
    title = models.CharField(max_length=100)
    value = models.CharField(max_length=50)
    icon_class = models.CharField(max_length=50, help_text="e.g. 'fas fa-tint', 'fas fa-users'")
    badge_color = models.CharField(max_length=30, default='danger', help_text="bootstrap badge color: danger, success, warning, primary, info")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Stat Counter"
        verbose_name_plural = "Stat Counters"

    def __str__(self):
        return f"{self.value} {self.title}"

class AboutImage(models.Model):
    image = models.ImageField(upload_to='about/')
    caption = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False, help_text="Set True for the large main image in the About grid")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['-is_featured', 'order']
        verbose_name = "About Image"
        verbose_name_plural = "About Images"

    def __str__(self):
        return self.caption or f"About Image {self.id}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

