# Helpline Hello Naogaon - Technical Documentation & Admin Guide

Welcome to the **Helpline Hello Naogaon** website documentation. This document provides a complete overview of the application architecture, data models, template layouts, dynamic Django Admin management capabilities, and setup instructions.

---

## 📌 Project Overview

**Helpline Hello Naogaon** is a modern, responsive web portal for a voluntary non-profit organization based in Naogaon, Bangladesh. The website features:
- **Top Green Contact Header Bar**: Displays phone number, email address, social links (Facebook, YouTube, WhatsApp), and a direct contact button.
- **Header Navigation**: Custom brand branding with tagline and dynamic links for Home, About Us, Programs, Blood Donors, Volunteers, News, Gallery, Donate, and Contact.
- **Hero Banner Section**: Fully dynamic hero badge, title, subtitle, CTA buttons, and background/side image.
- **Floating Stat Counter Bar**: Dynamic counter cards showing statistics like Blood Donations, Assisted Families, Student Support, Volunteers, and Social Initiatives with custom icons and color badges.
- **About Us Section**: Dynamic text, CTA link, and 5-photo collage grid (1 featured main photo + 4 small grid photos).
- **Our Programs Section**: Interactive 5-column grid featuring circular top icon badges, top program photos, titles, short descriptions, and detail links.
- **Mid-Page Call to Action Banner**: Full-width dark green forest overlay banner with a golden CTA button encouraging volunteer registration.
- **Two-Column Grid (News & Donation Box)**:
  - **Recent News**: Horizontal card list with thumbnail image, date badge, title, and excerpt.
  - **Donate Box**: Mobile banking badges (bKash, Nagad, Rocket), uploadable QR Code image, and Bank Account details (Bank Name, Account Number, Routing Number).
- **Footer**: 4-column layout containing organization bio, social icons, quick links, contact info, and Google Map location iframe.

---

## 📁 Directory & File Architecture

```
hello_naogaon/
├── core/                        # Core app handling home, about, contact & site settings
│   ├── admin.py                 # Admin registration for SiteSetting, StatCounter, AboutImage, ContactMessage
│   ├── models.py                # SiteSetting, StatCounter, AboutImage, ContactMessage models
│   ├── views.py                 # Main home, about, contact view controllers
│   └── management/commands/
│       └── seed_data.py         # Management command to populate initial data
├── programs/                    # Programs, Events, and Success Stories app
│   ├── admin.py                 # ProgramAdmin with icon_class, badge_color & order editing
│   ├── models.py                # Program, Event, SuccessStory models
│   └── views.py                 # Program list, detail, and event views
├── news/                        # News & Articles app
│   ├── admin.py                 # ArticleAdmin and CategoryAdmin
│   ├── models.py                # Article, Category models
│   └── views.py                 # News list and article detail views
├── volunteers/                  # Volunteers & Blood Donors app
│   ├── admin.py                 # VolunteerAdmin, TeamMemberAdmin, BloodDonorAdmin
│   ├── models.py                # Volunteer, TeamMember, BloodDonor models
│   └── views.py                 # Blood donors list and volunteer application form
├── gallery/                     # Photo Gallery app
│   ├── models.py                # Album, Photo models
│   └── views.py                 # Gallery grid view
├── donations/                   # Donations & Payment Accounts app
│   ├── models.py                # Bank, QRCode, DonationMethod, Campaign models
│   └── views.py                 # Donation page view
├── static/
│   └── css/
│       └── style.css            # Custom CSS design system matching reference image
├── templates/
│   ├── base.html                # Master HTML template (Header, Navbar, Footer)
│   ├── core/
│   │   ├── home.html            # Main redesigned Homepage template matching image
│   │   ├── about.html           # About page template
│   │   └── contact.html         # Contact page template
│   ├── volunteers/
│   │   ├── blood_donors.html    # Blood Donors database list with blood group filter
│   │   └── volunteer_form.html  # Volunteer application form
│   └── gallery/
│       └── gallery.html         # Photo gallery grid
├── DOCUMENTATION.md             # Project documentation (this file)
└── manage.py
```

---

## 🛠️ Dynamic Django Admin Management Guide

## 🛠️ Dynamic Django Admin Management Guide

The Admin Panel (`/admin/`) has been completely customized using **Django Jazzmin** and custom CSS to match the exact visual branding (`#004d34` / `#006a4e` emerald theme, Bengali welcome header, custom model icons, and responsive tabs):

- **Header Bar**: Branded as **Helpline Hello Naogaon Admin** with direct top menu link to *"ওয়েবসাইট দেখুন"*.
- **Sidebar Icons**: Custom color-coded FontAwesome icons for Site Settings, Stat Counters, About Images, Programs, News, Gallery, Blood Donors, and Donations.
- **Custom CSS Theme**: [static/css/admin_custom.css](file:///d:/Projects/hello_naogaon/static/css/admin_custom.css) enforces matching emerald header, active menu highlight, rounded card components, and Bengali typography.
- Navigate to **Site Settings**:
  - `tagline`: Header tagline (e.g. `সবসময় আপনার পাশে - একটি স্বেচ্ছাসেবী সংগঠন`)
  - `logo`: Upload organization logo image
  - `hero_badge`: Text badge above main title (e.g. `মানবতার পাশে, নওগাঁর প্রতিটি মানুষের জন্য`)
  - `hero_title`: Main heading (e.g. `Helpline Hello Naogaon`)
  - `hero_subtitle`: Subheading text
  - `hero_image`: Upload custom hero side photo
  - `contact_phone`, `contact_email`, `contact_address`: Displayed in top bar, contact page, and footer
  - `facebook_url`, `youtube_url`, `whatsapp_number`: Social icon links
  - `footer_about`: Footer organization description text
  - `google_map_embed_url`: Iframe URL string for Google Map embed in footer

### 2. Stat Counter Cards (`Stat Counters`)
- Navigate to **Core > Stat Counters**:
  - `title`: e.g. `রক্তদান`, `পরিবারকে সহায়তা`, `শিক্ষার্থী সহায়তা`
  - `value`: e.g. `500+`, `2,000+`, `300+`
  - `icon_class`: FontAwesome icon class (e.g. `fas fa-tint`, `fas fa-users`, `fas fa-graduation-cap`, `fas fa-hands-holding-heart`, `fas fa-seedling`)
  - `badge_color`: Icon circle background color (`danger`, `success`, `warning`, `primary`, `info`)
  - `order`: Integer order of display

### 3. Homepage About Photo Collage (`About Images`)
- Navigate to **Core > About Images**:
  - `image`: Upload photo
  - `is_featured`: Check `True` for the 1 large main left image in the About collage. Keep `False` for the 4 smaller sub-images on the right.

### 4. Programs & Services (`Programs`)
- Navigate to **Programs > Programs**:
  - `title`: Program title (e.g. `রক্তদান সেবা`, `শিক্ষা সহায়তা`)
  - `short_description`: Concise sentence for card display
  - `description`: Detailed text for full page
  - `icon_class`: FontAwesome icon class for top circular card badge
  - `badge_color`: Badge color theme
  - `image`: Upload program photo
  - `status`: Set to `ongoing` to show on homepage

### 5. Bank Accounts & QR Codes (`Donations`)
- Navigate to **Donations > Bank Accounts** and **QR Codes**:
  - Add bank name, account holder name, account number, and routing number.
  - Upload QR code image under **QR Codes**.

### 6. Blood Donors Database (`Volunteers > Blood Donors`)
- Add registered blood donors with full name, blood group (`A+`, `O+`, etc.), phone number, location, and availability status.

---

## 🚀 Setup & Execution Instructions

### 1. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Seed Default Data (Populate Homepage Data matching reference design)
```bash
python manage.py seed_data
```

### 3. Run Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser. Access admin panel at `http://127.0.0.1:8000/admin/`.

---

## 🎨 Design Tokens & Theme Colors

| Element | CSS Variable / Hex Code | Usage |
|---|---|---|
| Primary Green | `#006a4e` | Buttons, headers, icon badges, section titles |
| Dark Green | `#004d34` | Top bar, footer background, hover state |
| Accent Yellow | `#ffc107` | Mid-page CTA button |
| Secondary Blue | `#0288d1` | Secondary CTA buttons |
| Background Light | `#fcfcfc` / `#f8fafc` | Page background & section cards |
