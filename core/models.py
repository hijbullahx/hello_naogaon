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
    google_map_embed_url = models.TextField(
        blank=True, 
        default='', 
        help_text="Google Map Embed Code (<iframe...>) বা ম্যাপের লিঙ্ক দিন।"
    )

    @property
    def google_map_embed_html(self):
        """
        Safely returns responsive Google Map iframe HTML, supporting:
        1. Full iframe tags (<iframe src="..."></iframe>)
        2. Embed URLs (https://www.google.com/maps/embed?pb=...)
        3. Standard Google Maps URLs
        """
        default_iframe = '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d14515.77259163777!2d88.7516806!3d24.8105741!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x39fc96fb24aa7a8d%3A0x7d0251aa3d4be0c2!2sNaogaon%2C%20Bangladesh!5e0!3m2!1sen!2sbd!4v1700000000000!5m2!1sen!2sbd" width="100%" height="100%" style="border:0; min-height: 150px;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
        
        if not self.google_map_embed_url or not self.google_map_embed_url.strip():
            return default_iframe

        raw = self.google_map_embed_url.strip()

        # If it's a full <iframe>
        if '<iframe' in raw.lower():
            import re
            src_match = re.search(r'src=["\'](.*?)["\']', raw, re.IGNORECASE)
            if src_match:
                src_url = src_match.group(1)
                return f'<iframe src="{src_url}" width="100%" height="100%" style="border:0; min-height: 150px;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
            return raw

        # If it's an embed URL or standard URL
        if raw.startswith('http://') or raw.startswith('https://'):
            return f'<iframe src="{raw}" width="100%" height="100%" style="border:0; min-height: 150px;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'

        return default_iframe

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


