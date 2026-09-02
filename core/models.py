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
        Safely converts any Google Map link format into a working, responsive iframe:
        - Full <iframe> code
        - Direct /embed URL
        - Google Maps place link (https://www.google.com/maps/place/...)
        - Google Maps shortlink (https://maps.app.goo.gl/...)
        - Coordinates link (https://www.google.com/maps/@lat,lng,...)
        - Query link (https://maps.google.com/?q=...)
        - Plain text address
        """
        default_iframe = '<iframe src="https://maps.google.com/maps?q=Naogaon,+Bangladesh&hl=bn&z=14&output=embed" width="100%" height="100%" style="border:0; min-height: 150px;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
        
        if not self.google_map_embed_url or not self.google_map_embed_url.strip():
            return default_iframe

        raw = self.google_map_embed_url.strip()

        # 1. If it's a full <iframe> HTML tag
        if '<iframe' in raw.lower():
            import re
            src_match = re.search(r'src=["\'](.*?)["\']', raw, re.IGNORECASE)
            if src_match:
                src_url = src_match.group(1)
                return f'<iframe src="{src_url}" width="100%" height="100%" style="border:0; min-height: 150px;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
            return raw

        # 2. If it's already an embed URL
        if 'output=embed' in raw or '/embed' in raw:
            return f'<iframe src="{raw}" width="100%" height="100%" style="border:0; min-height: 150px;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'

        import re
        import urllib.parse

        # 3. If it's a Google Maps shortlink (maps.app.goo.gl or goo.gl/maps)
        if 'maps.app.goo.gl' in raw or 'goo.gl/maps' in raw:
            try:
                import requests
                r = requests.get(raw, allow_redirects=True, timeout=5)
                raw = r.url
            except Exception:
                pass

        # 4. If it's a Google Maps place URL
        if 'google.com/maps/place/' in raw:
            part = raw.split('google.com/maps/place/')[1]
            place_name = part.split('/')[0].split('?')[0].replace('+', ' ')
            place_name = urllib.parse.unquote(place_name)
            coords = re.search(r'@([0-9\.\-]+),([0-9\.\-]+)', raw)
            if coords:
                q = f'{coords.group(1)},{coords.group(2)}'
            else:
                q = place_name
            src_url = f'https://maps.google.com/maps?q={urllib.parse.quote(q)}&hl=bn&z=14&output=embed'
            return f'<iframe src="{src_url}" width="100%" height="100%" style="border:0; min-height: 150px;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'

        # 5. If it contains @lat,lng coordinates
        coords = re.search(r'@([0-9\.\-]+),([0-9\.\-]+)', raw)
        if coords:
            q = f'{coords.group(1)},{coords.group(2)}'
            src_url = f'https://maps.google.com/maps?q={urllib.parse.quote(q)}&hl=bn&z=14&output=embed'
            return f'<iframe src="{src_url}" width="100%" height="100%" style="border:0; min-height: 150px;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'

        # 6. If it contains query param ?q=
        if 'q=' in raw:
            parsed = urllib.parse.urlparse(raw)
            params = urllib.parse.parse_qs(parsed.query)
            if 'q' in params and params['q']:
                q_val = params['q'][0]
                src_url = f'https://maps.google.com/maps?q={urllib.parse.quote(q_val)}&hl=bn&z=14&output=embed'
                return f'<iframe src="{src_url}" width="100%" height="100%" style="border:0; min-height: 150px;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'

        # 7. Generic fallback for any address or search query
        clean_query = raw.replace('https://', '').replace('http://', '').replace('www.', '')
        src_url = f'https://maps.google.com/maps?q={urllib.parse.quote(clean_query)}&hl=bn&z=14&output=embed'
        return f'<iframe src="{src_url}" width="100%" height="100%" style="border:0; min-height: 150px;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'

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


class PasswordResetOTP(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='password_reset_otps')
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Password Reset OTP"
        verbose_name_plural = "Password Reset OTPs"

    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and timezone.now() <= self.expires_at and self.attempts < 5

    def __str__(self):
        return f"OTP for {self.user.username} ({self.otp_code})"


