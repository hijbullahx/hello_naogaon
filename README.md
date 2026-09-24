# 🌟 Helpline Hello Naogaon
### *A Comprehensive Web Portal, Dynamic CMS, Voluntary Management & Financial Ledger System*

[![Django](https://img.shields.io/badge/Django-5.2+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Payment Gateway](https://img.shields.io/badge/SSLCommerz-Ready-0070BA?style=for-the-badge)](https://www.sslcommerz.com/)
[![Status](https://img.shields.io/badge/Build-Production--Ready-brightgreen?style=for-the-badge)](#)

---

## 📖 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features & Highlights](#-key-features--highlights)
3. [System Architecture & Tech Stack](#-system-architecture--tech-stack)
4. [Directory & Codebase Structure](#-directory--codebase-structure)
5. [In-Depth App & Module Breakdown](#-in-depth-app--module-breakdown)
   - [1. Core App (CMS, Custom Dashboard, Auth & OTP)](#1-core-app)
   - [2. Volunteers App (Volunteers, Team Council & Blood Donors)](#2-volunteers-app)
   - [3. Donations App (Payment Gateway, Campaigns & Financial Ledger)](#3-donations-app)
   - [4. Programs App (Community Services, Events & Impact)](#4-programs-app)
   - [5. News App (Press Releases, Notices & Articles)](#5-news-app)
   - [6. Gallery App (Albums & High-Resolution Media)](#6-gallery-app)
6. [Database Schema & Entity Relationships](#-database-schema--entity-relationships)
7. [Role-Based Access Control (RBAC) Matrix](#-role-based-access-control-rbac-matrix)
8. [Local Development & Setup Guide](#-local-development--setup-guide)
9. [Environment Variables Specification](#-environment-variables-specification)
10. [Production Deployment Guide (cPanel & Ubuntu VPS)](#-production-deployment-guide-cpanel--ubuntu-vps)
11. [Admin Panel & CMS Management Manual](#-admin-panel--cms-management-manual)
12. [Security Features & Troubleshooting FAQ](#-security-features--troubleshooting-faq)
13. [API Endpoints Reference](#-api-endpoints-reference)
14. [Contact & Support](#-contact--support)

---

## 📌 Project Overview

**Helpline Hello Naogaon** is an enterprise-grade, modern web portal and administrative management platform created for a non-profit, non-political voluntary organization based in Naogaon, Bangladesh.

The organization actively serves communities across several vital humanitarian domains:
- **Emergency Blood Donation**: Maintaining an active donor network and organizing free blood donation camps.
- **Educational Support**: Providing academic scholarships and learning supplies to underprivileged students.
- **Humanitarian Assistance**: Supplying food rations, medical relief, and financial aid to impoverished families and widows.
- **Disaster Relief**: Immediate mobilization of warm clothing during winter and flood relief logistics.
- **Social Initiatives**: Tree plantation programs and public health awareness campaigns.

The platform is architected as a **dual-interface solution**:
1. **A fast, beautiful, SEO-optimized public portal** featuring real-time bilingual switching (English & Bengali), floating stats counters, an interactive photo collage, online donations, program trackers, and a blood donor search engine.
2. **A tailor-made, Cardly-style Custom Admin Control Panel (`/dashboard/`)** that replaces the standard technical backend with an intuitive, section-by-section CMS, automated financial ledger, Excel report exporter, and volunteer management tools.

---

## 🚀 Key Features & Highlights

### 🎨 1. Front-End & User Experience
- **Mobile-First Responsive Layout**: Crafted using Bootstrap 5.3 and custom design tokens (`static/css/style.css`), ensuring pixel-perfect layout across smartphones, tablets, and desktop displays.
- **Dynamic Bilingual Translation Engine (`HN_I18N`)**: Instant, client-side translation toggle between Bengali and English across navigation, headers, labels, and forms without page reloads.
- **Interactive Floating Statistics**: Animated counters showcasing verified metrics (Blood Donated, Families Assisted, Volunteers, Student Scholarships).
- **Modern 5-Photo Collage Grid**: Dynamic About section featuring 1 primary featured photo and 4 sub-grid imagery items.
- **Citizen Feedback / Complaint Box**: Modal popup enabling citizens and donors to submit queries, feedback, or grievances directly into the admin inbox.
- **Smart Google Maps Integration**: Converts any Google Maps format (full iframe embed code, short URL `maps.app.goo.gl`, place search URL, or coordinate link `@lat,lng`) into a responsive, fluid iframe automatically.

### 🩸 2. Blood Donors Network & Smart Eligibility
- **Blood Group Filtering**: Instant search across 8 blood groups (`A+`, `A-`, `B+`, `B-`, `O+`, `O-`, `AB+`, `AB-`).
- **Cascading Bangladesh Geo-Filtering**: Real-time filtering by Division, District, and Upazila powered by `/volunteers/api/bd-geo/`.
- **Automated 90-Day Donation Eligibility Calculator**: Computes whether a donor is medically eligible to donate blood based on their `last_donated` date, including an exact day-counter (`days_until_eligible`).
- **Privacy Controls**: Donors can toggle their contact number public or private (`is_public_details`).
- **Background Auto-Sync Engine**: Whenever a new volunteer or team member registers and supplies a blood group, the system automatically creates or updates their record in the `BloodDonor` database without manual intervention.

### 🤝 3. Volunteer & Executive Leadership Management
- **Automated Unique Member ID Generation**:
  - General Volunteers: `YYMMDDXX` (e.g., `26091801`).
  - Executive Council Members: `HHNYYMMDDXX` (e.g., `HHN26091801`).
  - Strict global collision prevention logic guaranteeing uniqueness across all models.
- **Executive Council Role Quota Validation**:
  - President (সভাপতি): Maximum 1 individual.
  - General Secretary (সাধারণ সম্পাদক): Maximum 1 individual.
  - Treasurer (কোষাধ্যক্ষ): Maximum 1 individual.
  - General Council Members (সাধারণ পরিষদ সদস্য): Maximum 4 individuals.
  - Database-level constraint checking in `clean()` preventing duplicate or excess appointments.
- **Volunteer Financial Pledges**: Records periodic membership dues (Monthly, Weekly, Yearly, or One-time) alongside pledged amounts.

### 💳 4. Online Payment Gateway & Financial Bookkeeping
- **Integrated Payment Gateway (SSLCommerz)**:
  - Supports bKash, Nagad, Rocket, Upay, Visa, MasterCard, Amex, and Internet Banking.
  - Instant Payment Notification (IPN) webhook listener for automated transaction reconciliation.
  - One-click toggle between **Sandbox (Testing)** and **Live Production** modes.
  - Instant digital donation receipt generation (`/donations/receipt/<id>/`).
- **Manual Payment Channels**: Pre-configured Dutch-Bangla Bank details, routing numbers, and scan-to-pay QR codes.
- **Complete Double-Entry Financial Ledger (`FinancialTransaction`)**:
  - Categorized tracking of all organization Incomes and Expenses.
  - File upload for expense receipts, voucher numbers, and transaction IDs.
  - Real-time balance calculations: Total Revenue, Total Expenditures, and Net Available Funds.
  - **Excel Export Engine**: Instant download of complete financial data in `.xlsx` format powered by `openpyxl`.
  - **Printable Official Statement**: Clean, letterhead-style printable layout (`print_financial_statement.html`) for annual audits and board meetings.

### 🔐 5. Security & Authentication Architecture
- **Multi-Identifier Authentication Backend (`MultiIdentifierAuthBackend`)**:
  - Allows members and administrators to log in using their **Username**, **Email Address**, or **Member ID**.
- **Secure 6-Digit Email OTP Password Reset**:
  - Time-limited (10-minute expiration), single-use tokens with rate-limiting (max 5 failed attempts).
  - Client-side Ajax validation (`/api/validate-otp/`) and email masking (`h****5@gmail.com`) for identity protection.
- **Branded HTML Email Dispatcher (`send_system_email`)**: Multi-part responsive emails for registration confirmations, financial receipts, and credential resets.
- **Local SMS Gateway Dispatcher (`sms_utils.py`)**: Ready for direct integration with Bangladeshi SMS aggregators (e.g., Greenweb, BulkSMSBD).

---

## 🏗️ System Architecture & Tech Stack

```mermaid
graph TD
    User["Client Browser (Mobile / Desktop)"] --> WebServer["Reverse Proxy (NGINX / LiteSpeed)"]
    WebServer --> WSGI["WSGI / Passenger Application"]
    WSGI --> DjangoCore["Django Framework (v5.2+)"]
    
    subgraph "Django Application Layer"
        DjangoCore --> Security["Security & CSRF Middlewares"]
        Security --> URLRouter["URL Routing (urls.py)"]
        URLRouter --> Core["core app: CMS, Auth, Dashboard, OTP"]
        URLRouter --> Volunteers["volunteers app: Donors, Council, Sync"]
        URLRouter --> Donations["donations app: Gateway, Ledger, Receipts"]
        URLRouter --> Programs["programs app: Projects, Events"]
        URLRouter --> News["news app: Articles, Categories"]
        URLRouter --> Gallery["gallery app: Albums, Photos"]
    end
    
    Donations --> SSLCommerz["SSLCommerz Gateway API"]
    Core --> SMTP["SMTP Mail Server (mail.helplinehellonaogaon.com)"]
    Core --> SMS["Bulk SMS Gateway API"]
    
    DjangoCore --> DB[("Database: SQLite3 (Dev) / MySQL (Prod utf8mb4)")]
    DjangoCore --> MediaStorage["Static & Media Assets (/static, /media)"]
```

### Core Technologies:
| Layer | Technologies Used |
|---|---|
| **Backend Framework** | Python 3.10+, Django 5.2.15, `django-environ` |
| **Database** | SQLite3 (Development), MySQL / MariaDB with `utf8mb4_unicode_ci` (Production) |
| **Admin Interface** | Custom Cardly Dashboard (`/dashboard/`) & Django Jazzmin (`/django-admin/`) |
| **Frontend** | HTML5, Semantic Elements, Bootstrap 5.3.2, FontAwesome 6, Custom CSS |
| **Client Scripts** | Vanilla JS, Fetch API, jQuery / AJAX for dynamic lookups |
| **Payment Integration**| SSLCommerz REST API v4, bKash/Nagad direct merchant channels |
| **Reporting Tools** | `openpyxl` (Excel Spreadsheet Generation), Print-friendly HTML |
| **Email System** | Django SMTP `EmailMultiAlternatives` with custom HTML responsive templates |

---

## 📁 Directory & Codebase Structure

```
hello_naogaon/
├── manage.py                     # Django CLI management script
├── requirements.txt              # Production Python dependencies
├── db.sqlite3                    # Local SQLite database instance
├── .env                          # Secret environment variables (ignored by Git)
├── .env.example                  # Template environment configuration file
├── DOCUMENTATION.md              # High-level architecture documentation
├── README.md                     # Master technical & operational documentation
│
├── hello_naogaon/                # Main project configuration package
│   ├── __init__.py
│   ├── settings.py               # Settings, Jazzmin UI tweaks, database, security
│   ├── urls.py                   # Master URL routing table
│   ├── wsgi.py                   # WSGI gateway for web server integration
│   └── asgi.py                   # ASGI gateway
│
├── core/                         # Core App: CMS, Auth, OTP & Dashboard
│   ├── backends.py               # Multi-Identifier authentication backend
│   ├── context_processors.py     # Global SiteSetting & dashboard stats injectors
│   ├── email_utils.py            # Unified branded HTML email dispatcher
│   ├── sms_utils.py              # Bulk SMS gateway integration
│   ├── models.py                 # SiteSetting, StatCounter, AboutImage, PasswordResetOTP
│   ├── views.py                  # Public homepage, about page, complaint submission
│   ├── views_auth.py             # OTP generation, rate-limiting & password reset
│   ├── views_dashboard.py        # 93KB Custom Admin Control Panel & financial ledger
│   ├── urls.py                   # Core URL routing
│   └── management/commands/
│       └── seed_data.py          # Database seeding command for default content
│
├── volunteers/                   # Volunteers, Council & Blood Donors App
│   ├── models.py                 # Volunteer, TeamMember, BloodDonor & auto-sync logic
│   ├── views.py                  # Blood donors directory, registration form, geo API
│   └── urls.py
│
├── donations/                    # Financial Management & Payment Gateway App
│   ├── models.py                 # Campaign, Bank, QRCode, ProgramDonation, FinancialTransaction
│   ├── gateway.py                # SSLCommerz session initialization, validation, IPN
│   ├── views.py                  # Donation page, checkout redirect, receipt & API lookups
│   ├── templates/donations/      # Donation page, gateway checkout & receipt templates
│   └── urls.py
│
├── programs/                     # Programs, Events & Success Stories App
│   ├── models.py                 # Program, Event, SuccessStory
│   ├── views.py                  # Program listing, detail views, funding progress
│   └── urls.py
│
├── news/                         # News & Press Announcements App
│   ├── models.py                 # Article, Category
│   ├── views.py                  # News listing & article reader
│   └── urls.py
│
├── gallery/                      # Photo Gallery & Media App
│   ├── models.py                 # Album, Photo
│   ├── views.py                  # High-resolution gallery grid
│   └── urls.py
│
├── templates/                    # Global HTML Templates
│   ├── base.html                 # Master layout (Header, Nav, I18N, Footer, Modals)
│   ├── core/                     # home.html, about.html
│   ├── dashboard/                # index.html (240KB SPA Dashboard), print_financial_statement.html
│   ├── volunteers/               # blood_donors.html, volunteer_form.html
│   ├── programs/                 # program_list.html, program_detail.html
│   ├── news/                     # news_list.html, news_detail.html
│   ├── gallery/                  # gallery.html
│   ├── registration/             # login.html, password_reset_*.html
│   └── emails/                   # system_email.html (Branded responsive template)
│
├── static/                       # Static Assets
│   ├── css/                      # style.css (custom design system), admin_custom.css
│   └── js/                       # Client scripts
│
└── media/                        # User-uploaded content (logos, photos, receipts)
```

---

## 🔍 In-Depth App & Module Breakdown

### 1. Core App

The `core` application serves as the operational hub of the platform. It handles site-wide branding, front-facing presentation, user authentication, and the administration control panel.

#### Models:
- **`SiteSetting`**:
  - Singleton record (`pk=1`) managing organization branding, title, slogans, hero badges, contact telephone, official email, physical address, and social links (Facebook, YouTube, WhatsApp).
  - **`google_map_embed_html` Property**: A specialized regex parser that handles raw Google Maps URLs, coordinates (`@lat,lng`), share links (`maps.app.goo.gl`), or complete `<iframe>` snippets and converts them into a responsive HTML5 iframe element.
- **`StatCounter`**:
  - Controls the dynamic floating stats bar on the homepage.
  - Configurable properties: `title`, `value` (e.g., `500+`), `icon_class` (FontAwesome), `badge_color`, and display `order`.
- **`AboutImage`**:
  - Manages the homepage 5-image collage grid with an `is_featured` boolean flag to designate the large primary anchor image.
- **`PasswordResetOTP`**:
  - Stores secure 6-digit verification codes generated during forgot-password workflows.
  - Enforces a 10-minute expiration window and terminates sessions after 5 failed verification attempts.

#### Authentication System:
- **`MultiIdentifierAuthBackend` (`core/backends.py`)**: Custom authentication backend allowing users to sign in via standard username, verified email address, or assigned Member ID.
- **OTP Password Reset (`core/views_auth.py`)**:
  - Generates cryptographically secure 6-digit numeric codes using `secrets.randbelow`.
  - Masks the user's destination email on the client screen (e.g., `h****5@gmail.com`).
  - Provides a real-time Ajax validation endpoint (`/api/validate-otp/`) before enabling password change inputs.

#### Custom Cardly Dashboard (`core/views_dashboard.py`):
An extensive, full-featured management dashboard:
- Homepage live CMS editor (Hero, About, Footer, Map).
- Financial ledger management (Income, Expense, Vouchers).
- One-click Excel spreadsheet generation and print-ready financial statement view.
- Volunteer approval and membership roster.

---

### 2. Volunteers App

Manages volunteer applicants, executive council leadership, and blood donors.

#### Models:
- **`Volunteer`**:
  - Attributes: Name, mobile number, email, blood group, division, district, upazila, occupation, physical address, and profile photo.
  - Stores pledge information: `contribution_frequency` (Monthly/Weekly/Yearly/One-Time) and `contribution_amount`.
  - Automatically receives an 8-digit unique ID formatted as `YYMMDDXX`.
  - Provides properties `is_eligible_to_donate` and `days_until_eligible` based on `last_donated`.
- **`TeamMember`**:
  - Executive council profile with formal roles: President, General Secretary, Treasurer, General Council Member, or Custom Designation.
  - Validated via `clean()` to ensure role quotas: only one President, General Secretary, and Treasurer, and a maximum of 4 General Council Members.
  - Automatically receives an ID with the organizational prefix: `HHNYYMMDDXX`.
- **`BloodDonor`**:
  - Repository of blood donors searchable by blood group, division, district, and upazila.
  - Supports privacy toggles via `is_public_details`.
- **Auto-Sync Engine (`sync_to_blood_donor`)**:
  - Automatically invoked whenever a `Volunteer` or `TeamMember` model is saved with an assigned blood group and telephone number. It creates or updates the corresponding `BloodDonor` record.

#### Geo-Data Endpoint:
- `/volunteers/api/bd-geo/`: Supplies JSON structured data for all administrative divisions, districts, and upazilas across Bangladesh for dynamic cascading dropdown menus.

---

### 3. Donations App

Handles online and offline donations, fundraising campaigns, and the organizational accounting ledger.

#### Models:
- **`DonationPageContent`**: CMS content for the donation portal (Hero banner, transparency declarations, appeal texts).
- **`Campaign`**: Time-bound fundraising drives with `goal_amount`, `raised_amount`, and date ranges.
- **`EmergencyAppeal`**: Urgent banners for disaster relief or medical emergencies.
- **`PaymentGatewaySetting`**: Database-driven credentials for payment providers (SSLCommerz, ShurjoPay, AamarPay, bKash Merchant) with a sandbox toggle.
- **`ProgramDonation`**: Records digital donations and voluntary membership fees. Stores gateway transaction IDs (`tran_id`), payment channel details (bKash/Cards), donor information, and approval statuses.
- **`FinancialTransaction` (Organization Ledger)**:
  - Tracks all incoming revenue (`income`) and organizational operational expenses (`expense`).
  - Stores voucher numbers, categories, amounts, payment modes, receipt images, and expense descriptions.

#### Online Gateway Architecture (`donations/gateway.py`):
- Initiates SSLCommerz payment sessions with POST parameters (`total_amount`, `currency=BDT`, `tran_id`, callback URLs).
- Handles redirection to the hosted payment gateway and manages return routes:
  - `/donations/payment-success/`
  - `/donations/payment-fail/`
  - `/donations/payment-cancel/`
  - `/donations/payment-ipn/` (Instant Payment Notification webhook for background verification)
- Issues a printable digital receipt upon successful payment completion (`/donations/receipt/<id>/`).

---

### 4. Programs App

- **`Program`**: Ongoing humanitarian services (Blood Donation Camps, Student Aid, Food Distribution).
  - Includes progress bar calculations: `progress_percent` compares `raised_amount` against `target_amount`.
- **`Event`**: Upcoming calendar initiatives with date, time, and venue coordinates.
- **`SuccessStory`**: Case studies and testimonials showcasing community impact.

---

### 5. News App

- **`Article` & `Category`**:
  - Publication platform for press releases, activity reports, and community notices.
  - Supports featured image uploads, publication status flags, and automatic timestamps.

---

### 6. Gallery App

- **`Album` & `Photo`**:
  - Organizes field photography into categorized photo albums.
  - Rendered using a responsive lightbox grid layout on the public site.

---

## 🗄️ Database Schema & Entity Relationships

```mermaid
erDiagram
    SiteSetting ||--o{ StatCounter : "controls display"
    SiteSetting ||--o{ AboutImage : "manages collage"
    
    User ||--o| Volunteer : "links profile"
    User ||--o| TeamMember : "links executive profile"
    User ||--o{ PasswordResetOTP : "requests"
    
    Volunteer ||--o{ BloodDonor : "auto-syncs to"
    TeamMember ||--o{ BloodDonor : "auto-syncs to"
    
    Program ||--o{ FinancialTransaction : "linked to"
    Program ||--o{ ProgramDonation : "receives"
    
    DonationMethod ||--o{ QRCode : "displays"
    Album ||--o{ Photo : "groups"
    Category ||--o{ Article : "classifies"
```

---

## 👥 Role-Based Access Control (RBAC) Matrix

The custom administration dashboard (`/dashboard/`) dynamically adapts its navigation, cards, and permissions based on user roles:

| User Role | CMS & Site Settings | Volunteer & Team Mgmt | Financial Ledger Edit | Financial Reports & Excel | View Mode |
|---|:---:|:---:|:---:|:---:|---|
| **Super Admin** | ✅ Full Access | ✅ Full Access | ✅ Full Access | ✅ Full Access | Complete Control Panel |
| **Staff Admin** | ✅ Full Access | ✅ Full Access | ✅ Full Access | ✅ Full Access | Administrative Panel |
| **President (সভাপতি)** | ❌ Read Only | ❌ Read Only | ❌ Read Only | ✅ View & Print | Leadership & Audit Mode |
| **General Secretary (সাধারণ সম্পাদক)** | ❌ Read Only | ❌ Read Only | ❌ Read Only | ✅ View & Print | Leadership & Audit Mode |
| **Treasurer (কোষাধ্যক্ষ)** | ❌ Read Only | ❌ Read Only | ✅ Full Access | ✅ Full Access (Excel/Print) | Financial Management Mode |
| **General Council Member** | ❌ None | ❌ None | ❌ None | ❌ None | Personal Member Dashboard |
| **General Volunteer / Public** | ❌ None | ❌ None | ❌ None | ❌ None | Public Website Only |

---

## 💻 Local Development & Setup Guide

Follow these steps to run the application in a local development environment:

### 1. Prerequisites
- **Python 3.10** or higher
- **Git**
- **pip** and **virtualenv**

### 2. Clone Repository & Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/hijbullahx/hello_naogaon.git
cd hello_naogaon

# Create Python virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a local `.env` file by copying `.env.example`:
```bash
cp .env.example .env
```
*(By default, the application will run against SQLite without needing additional database setup).*

### 4. Apply Database Migrations & Seed Default Data
```bash
# Apply schema migrations
python manage.py makemigrations
python manage.py migrate

# Seed default site content, stats, programs, and accounts
python manage.py seed_data
```

### 5. Create a Superuser Account
```bash
python manage.py createsuperuser
```
*(Enter your desired username, email, and password).*

### 6. Start the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
- **Public Portal**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Custom Admin Control Panel**: [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/) or [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Django Jazzmin Admin**: [http://127.0.0.1:8000/django-admin/](http://127.0.0.1:8000/django-admin/)

---

## ⚙️ Environment Variables Specification

Define these keys in your `.env` file to customize application behavior:

| Variable Name | Default Value | Description |
|---|---|---|
| `SECRET_KEY` | `django-insecure-...` | Cryptographic secret key. **Must be changed in production.** |
| `DEBUG` | `True` | Set to `False` in all production environments. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,...` | Comma-delimited list of authorized domain names and IP addresses. |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:8000,...` | List of trusted origins for CSRF protection with reverse proxies. |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | Database connection URI (e.g., `mysql://user:pass@host:3306/dbname`). |
| `SECURE_SSL_REDIRECT` | `False` | Forces all HTTP requests to redirect to HTTPS in production. |
| `SESSION_COOKIE_SECURE`| `False` | Ensures session cookies are transmitted only over HTTPS. |
| `CSRF_COOKIE_SECURE` | `False` | Ensures CSRF cookies are transmitted only over HTTPS. |
| `STATIC_URL` | `/static/` | URL prefix for serving static files. |
| `STATIC_ROOT` | `BASE_DIR / staticfiles` | Directory where `collectstatic` outputs assets for production. |
| `MEDIA_URL` | `/media/` | URL prefix for serving user-uploaded media files. |
| `MEDIA_ROOT` | `BASE_DIR / media` | Filesystem path where uploaded media assets reside. |
| `EMAIL_BACKEND` | `...smtp.EmailBackend` | Django mail backend class. |
| `EMAIL_HOST` | `mail.helplinehellonaogaon.com`| SMTP server hostname. |
| `EMAIL_PORT` | `465` | Port `465` (SSL) or `587` (TLS). |
| `EMAIL_USE_SSL` | `True` | Set to `True` for port 465. |
| `EMAIL_USE_TLS` | `False` | Set to `True` for port 587. |
| `EMAIL_HOST_USER` | `info@...` | SMTP username / mailbox address. |
| `EMAIL_HOST_PASSWORD` | `******` | Password for the SMTP mailbox. |
| `DEFAULT_FROM_EMAIL` | `info@...` | Displayed sender address on dispatched system emails. |
| `SMS_API_URL` | `""` | Bulk SMS HTTP POST gateway endpoint. |
| `SMS_API_TOKEN` | `""` | Authentication token for the SMS gateway provider. |

---

## 🚀 Production Deployment Guide (cPanel & Ubuntu VPS)

### Option A: cPanel with CloudLinux "Setup Python App"
1. **Access cPanel > Setup Python App**:
   - Python Version: Select **3.10** or **3.11**.
   - Application Root: `/home/username/hello_naogaon`
   - Application URL: `helplinehellonaogaon.com`
2. **Deploy Application Code**:
   - Upload code via Git or cPanel File Manager.
   - Verify that `media/` and `static/` directories have standard `755` folder permissions.
3. **Provision a Production MySQL Database**:
   - Create a MySQL Database and Database User via cPanel with full privileges.
   - Ensure database collation is set to `utf8mb4_unicode_ci`.
   - Update your `.env` file:
     ```env
     DATABASE_URL=mysql://cp_user:cp_password@localhost:3306/cp_dbname
     DEBUG=False
     SECURE_SSL_REDIRECT=True
     ALLOWED_HOSTS=helplinehellonaogaon.com,www.helplinehellonaogaon.com
     CSRF_TRUSTED_ORIGINS=https://helplinehellonaogaon.com,https://www.helplinehellonaogaon.com
     ```
4. **Install Dependencies & Run Migrations**:
   Open cPanel Terminal or SSH:
   ```bash
   source /home/username/virtualenv/hello_naogaon/3.10/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
5. **Configure `passenger_wsgi.py`**:
   ```python
   import os
   import sys
   sys.path.insert(0, os.path.dirname(__file__))
   from hello_naogaon.wsgi import application
   ```
6. **Restart Python App** in cPanel.

---

### Option B: Ubuntu VPS (NGINX + Gunicorn + Systemd)
1. **Create Gunicorn Systemd Service (`/etc/systemd/system/hellonaogaon.service`)**:
   ```ini
   [Unit]
   Description=Gunicorn daemon for Helpline Hello Naogaon
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/hello_naogaon
   ExecStart=/var/www/hello_naogaon/venv/bin/gunicorn \
             --access-logfile - \
             --workers 3 \
             --bind unix:/run/hellonaogaon.sock \
             hello_naogaon.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```
2. **Configure NGINX Virtual Host (`/etc/nginx/sites-available/hellonaogaon`)**:
   ```nginx
   server {
       listen 80;
       server_name helplinehellonaogaon.com www.helplinehellonaogaon.com;

       client_max_body_size 10M;

       location /static/ {
           alias /var/www/hello_naogaon/staticfiles/;
       }

       location /media/ {
           alias /var/www/hello_naogaon/media/;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/run/hellonaogaon.sock;
       }
   }
   ```
3. **Enable Site & Install SSL via Let's Encrypt**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/hellonaogaon /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   sudo systemctl enable --now hellonaogaon
   sudo certbot --nginx -d helplinehellonaogaon.com -d www.helplinehellonaogaon.com
   ```

---

## 🛠️ Admin Panel & CMS Management Manual

Access the administrative interface at `/dashboard/` or `/admin/` after logging in with staff credentials:

### 1. Homepage Content Management (Home Page CMS)
- **Header & Hero Section**: Modify organization title, slogans, hero badges, side hero image, hotline number, and social links.
- **Counter Cards**: Update metrics (e.g., `1,200+` Blood Donated, `3,500+` Families Assisted), FontAwesome icons, and badge colors.
- **About Collage**: Designate 1 main featured photo and batch-upload up to 4 sub-grid collage images simultaneously.
- **Footer & Google Maps**: Paste any Google Maps location URL or iframe embed code into `google_map_embed_url`; the parser formats it automatically.

### 2. Blood Donors Roster
- Add, update, or remove blood donors with their blood group, phone number, and location.
- Filter donors by blood type and administrative upazila.
- Toggle visibility and availability flags.

### 3. Financial Bookkeeping & Donations
- **Bank & QR Settings**: Update Dutch-Bangla Bank account information, routing numbers, and bKash/Nagad scan-to-pay QR codes.
- **SSLCommerz Credentials**: Enter your Store ID and Store Password; toggle the Sandbox checkbox off for live transactions.
- **Double-Entry Cash Book**:
  - Add **Income** entries for grants or membership fees.
  - Add **Expense** entries with voucher numbers, expense categories, amounts, and uploaded receipts.
  - Click **Download Excel** to export audited `.xlsx` reports.
  - Click **Print Statement** to generate formatted official balance sheets.

### 4. Volunteers & Executive Council
- Review and approve pending volunteer applications.
- Enforce executive council quotas (President, General Secretary, Treasurer, General Council Members).

---

## 🔒 Security Features & Troubleshooting FAQ

### Security Provisions:
1. **File Size Enforcement (`validate_image_size`)**:
   - Image uploads are dynamically validated to remain under 1MB to protect disk space and ensure optimal page speed.
2. **Rate-Limited OTP Reset**:
   - OTP codes expire after 10 minutes and lock out after 5 consecutive failed attempts.
3. **Database-Level Character Encoding**:
   - Automatic execution of `SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'` ensuring native Bengali script rendering without corruption.

### Troubleshooting FAQ:

#### Q1: Uploaded images show an error message regarding file size?
- **Answer**: Uploaded images must be under 1MB. Optimize high-resolution photos using compression tools (such as TinyPNG or ResizePixel) before uploading.

#### Q2: OTP password reset emails are not being received?
- **Answer**:
  - Verify SMTP settings in `.env` (`EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`).
  - Ensure server port 465 (SSL) or 587 (TLS) is not blocked by your hosting firewall.
  - Check the spam or junk folder of the recipient email address.

#### Q3: Google Maps preview displays a blank box or broken link?
- **Answer**: Search your location on Google Maps, click **Share**, copy either the standard link or the **Embed a map** iframe code, and paste it directly into the Site Settings field. The built-in parser will handle the formatting.

#### Q4: Encountering "CSRF verification failed. Request aborted"?
- **Answer**: Add your full production domain (including `https://`) to `CSRF_TRUSTED_ORIGINS` in your `.env` file (e.g., `CSRF_TRUSTED_ORIGINS=https://helplinehellonaogaon.com`).

---

## 📡 API Endpoints Reference

| Endpoint | Method | Description | Access Level |
|---|:---:|---|:---:|
| `/volunteers/api/bd-geo/` | `GET` | Returns administrative divisions, districts, and upazilas across Bangladesh | Public |
| `/donations/api/member-pledge/` | `GET` | Looks up member pledges and dues by `member_id` query parameter | Public |
| `/api/validate-otp/` | `POST` | Validates a 6-digit OTP code before enabling new password fields | Public / Session |
| `/donations/payment-ipn/` | `POST` | Instant Payment Notification (IPN) webhook listener for SSLCommerz | Payment Gateway |
| `/dashboard/export-excel/` | `GET` | Generates and downloads a `.xlsx` spreadsheet of financial transactions | Staff / Treasurer |

---

## 📞 Contact & Support

- **Organization**: Helpline Hello Naogaon (হেল্পলাইন হ্যালো নওগাঁ)
- **Headquarters**: Mohadevpur, Naogaon - 6600, Rajshahi Division, Bangladesh
- **Email**: `info@helplinehellonaogaon.com` / `hello.naogaon@gmail.com`
- **Official Website**: [https://helplinehellonaogaon.com](https://helplinehellonaogaon.com)

---
*© Helpline Hello Naogaon. All rights reserved.*
