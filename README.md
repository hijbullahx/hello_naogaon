# 🌟 Helpline Hello Naogaon (হেল্পলাইন হ্যালো নওগাঁ)
### *A Comprehensive Web Portal, Dynamic CMS, Voluntary Management & Financial Ledger System*

[![Django](https://img.shields.io/badge/Django-5.2+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)](#)

---

## 📖 সূচিপত্র (Table of Contents)

1. [প্রকল্প পরিচিতি (Project Overview)](#-প্রকল্প-পরিচিতি-project-overview)
2. [মূল বৈশিষ্ট্যসমূহ (Key Features & Highlights)](#-মূল-বৈশিষ্ট্যসমূহ-key-features--highlights)
3. [সিস্টেম আর্কিটেকচার ও টেকনোলজি স্ট্যাক (Architecture & Tech Stack)](#-সিস্টেম-আর্কিটেকচার-ও-টেকনোলজি-স্ট্যাক-architecture--tech-stack)
4. [ডিরেক্টরি ও প্রজেক্ট স্ট্রাকচার (Directory & Codebase Structure)](#-ডিরেক্টরি-ও-প্রজেক্ট-স্ট্রাকচার-directory--codebase-structure)
5. [প্রতিটি অ্যাপ ও মডিউলের বিস্তারিত কার্যপ্রণালী (App & Module Breakdown)](#-প্রতিটি-অ্যাপ-ও-মডিউলের-বিস্তারিত-কার্যপ্রণালী-app--module-breakdown)
   - [১. Core App (সাইট সেটিংস, হোম, অ্যাবাউট, ওটিপি অথেনটিকেশন ও কাস্টম ড্যাশবোর্ড)](#১-core-app)
   - [২. Volunteers App (স্বেচ্ছাসেবক, টিম মেম্বার কোটা ও রক্তদাতা ডাটাবেস)](#২-volunteers-app)
   - [৩. Donations App (অনলাইন পেমেন্ট গেটওয়ে, ম্যানুয়াল অনুদান ও আর্থিক হিসাব খাতা)](#৩-donations-app)
   - [৪. Programs App (কার্যক্রম, ইভেন্ট ও সাফল্যের গল্প)](#৪-programs-app)
   - [৫. News App (সংবাদ ও নোটিশ প্রকাশনা)](#৫-news-app)
   - [৬. Gallery App (ছবি ও অ্যালবাম গ্যালারি)](#৬-gallery-app)
6. [ডাটাবেস মডেল ও সম্পর্ক (Database Models & Relationships)](#-ডাটাবেস-মডেল-ও-সম্পর্ক-database-models--relationships)
7. [রোল-বেসড অ্যাক্সেস কন্ট্রোল (RBAC & Permissions Matrix)](#-রোল-বেসড-অ্যাক্সেস-কন্ট্রোল-rbac--permissions-matrix)
8. [লোকাল সেটআপ ও ডেভেলপমেন্ট গাইড (Local Development Setup)](#-লোকাল-সেটআপ-ও-ডেভেলপমেন্ট-গাইড-local-development-setup)
9. [এনভায়রনমেন্ট ভেরিয়েবলসমূহ (Environment Variables Specification)](#-এনভায়রনমেন্ট-ভেরিয়েবলসমূহ-environment-variables-specification)
10. [প্রোডাকশন ডিপ্লয়মেন্ট গাইড (Production Deployment - cPanel / VPS)](#-প্রোডাকশন-ডিপ্লয়মেন্ট-গাইড-production-deployment---cpanel--vps)
11. [অ্যাডমিন ও কন্ট্রোল প্যানেল গাইড (Admin Panel & CMS Management Manual)](#-অ্যাডমিন-ও-কন্ট্রোল-প্যানেল-গাইড-admin-panel--cms-management-manual)
12. [সিকিউরিটি ও ট্রাবলশুটিং (Security & Troubleshooting FAQ)](#-সিকিউরিটি-ও-ট্রাবলশুটিং-security--troubleshooting-faq)

---

## 📌 প্রকল্প পরিচিতি (Project Overview)

**Helpline Hello Naogaon (হেল্পলাইন হ্যালো নওগাঁ)** হলো বাংলাদেশের নওগাঁ জেলা ভিত্তিক একটি অরাজনৈতিক, অলাভজনক ও সামাজিক মানবিক স্বেচ্ছাসেবী সংগঠনের জন্য তৈরি একটি পূর্ণাঙ্গ, আধুনিক ও ডাইনামিক ওয়েব পোর্টাল এবং ম্যানেজমেন্ট প্ল্যাটফর্ম।

সংগঠনটি মূলত:
- জরুরি রক্তদাতা ব্যবস্থাপনা ও বিনামূল্যে রক্তদান ক্যাম্পেইন,
- সুবিধাবঞ্চিত শিক্ষার্থীদের শিক্ষাবৃত্তি ও শিক্ষা উপকরণ বিতরণ,
- অসচ্ছল পরিবার ও বিধবাদের মানবিক খাদ্য ও চিকিৎসা সহায়তা প্রদান,
- প্রাকৃতিক দুর্যোগ ও শীতার্তদের মাঝে জরুরি ত্রাণ বিতরণ, এবং
- সামাজিক বৃক্ষরোপণ ও পরিবেশ সুরক্ষা কার্যক্রম পরিচালনা করে থাকে।

এই সফটওয়্যারটি একই সাথে **একটি আকর্ষক ও দ্রুতগতির পাবলিক ওয়েবসাইট** এবং **একটি স্বয়ংসম্পূর্ণ প্রশাসনিক কন্ট্রোল প্যানেল (Custom Admin Panel)** হিসেবে কাজ করে। ফলে কোনো কোডিং জ্ঞান ছাড়াই অ্যাডমিন ও পরিচালনা পর্ষদ ওয়েবসাইটের প্রতিটি লেখা, ছবি, ব্যানার, কাউন্টার, রক্তদাতার তালিকা, আর্থিক খতিয়ান এবং অনুদান ব্যবস্থা সরাসরি পরিচালনা করতে পারেন।

---

## 🚀 মূল বৈশিষ্ট্যসমূহ (Key Features & Highlights)

### 🎨 ১. ব্যবহারকারী-বান্ধব ইন্টারফেস ও ফ্রন্টএন্ড
- **রেসপনসিভ ডিজাইন (Mobile First)**: কম্পিউটার, ট্যাব এবং যেকোনো মোবাইল ডিভাইসে শতভাগ অপ্টিমাইজড ভিউ।
- **দ্বিভাষিক সমর্থন (Bilingual Support - বাংলা ও ইংরেজি)**: রিয়েল-টাইম ক্লায়েন্ট-সাইড ট্রান্সলেশন সুইচ (`HN_I18N`) যা মুহূর্তের মধ্যে পুরো ইন্টারফেসকে বাংলা বা ইংরেজিতে রূপান্তর করে।
- **ডাইনামিক কাউন্টার ও স্ট্যাট বার**: হোমপেজে অ্যানিমেটেড পরিসংখ্যান কার্ড (রক্তদান, পরিবার সহায়তা, স্বেচ্ছাসেবক সংখ্যা ইত্যাদি)।
- **৫-ছবির আধুনিক কোলাজ গ্রিড**: আমাদের সম্পর্কে সেকশনে ১টি মূল ফিচার্ড ছবি ও ৪টি সাব-গ্রিড ছবির স্টাইলিশ উপস্থাপনা।
- **অভিযোগ ও পরামর্শ বক্স**: সাধারণ নাগরিক ও শুভাকাঙ্ক্ষীদের জন্য সহজ পপআপ ফর্ম।

### 🩸 ২. রক্তদাতা ডাটাবেস ও স্মার্ট ক্যালকুলেটর
- **রক্তের গ্রুপভিত্তিক ফিল্টারিং**: A+, A-, B+, B-, O+, O-, AB+, AB- দিয়ে তাৎক্ষণিক অনুসন্ধান।
- **ভৌগোলিক ড্রপডাউন (Geo Filtering)**: বাংলাদেশের বিভাগ, জেলা এবং উপজেলা ভিত্তিক রক্তদাতা খোঁজার সুবিধা (`api/bd-geo/`)।
- **৯০ দিনের রক্তদানের যোগ্যতা ক্যালকুলেটর**: শেষ রক্তদানের তারিখের ভিত্তিতে স্বয়ংক্রিয়ভাবে গণনা করা হয় দাতা বর্তমানে রক্তদানের জন্য উপযুক্ত কিনা (Eligible) অথবা কতদিন পর উপযুক্ত হবেন (Days until eligible)।
- **প্রাইভেসি কন্ট্রোল**: রক্তদাতা চাইলে তার নম্বর সর্বসাধারণের জন্য দৃশ্যমান রাখতে পারেন বা গোপন রাখতে পারেন।
- **অটো-সিঙ্ক প্রযুক্তি**: কোনো নতুন স্বেচ্ছাসেবক বা পরিচালনা পরিষদ সদস্য নিবন্ধনকালে রক্তের গ্রুপ দিলে তিনি স্বয়ংক্রিয়ভাবে রক্তদাতা ডাটাবেসে যুক্ত হন।

### 🤝 ৩. স্বেচ্ছাসেবক ও কার্যনির্বাহী পরিষদ ব্যবস্থাপনা
- **ইউনিক সদস্য আইডি জেনারেশন (Unique Member ID Algorithm)**:
  - স্বেচ্ছাসেবকদের জন্য: `YYMMDDXX` (যেমন: `26091801`)।
  - টিম মেম্বারদের জন্য: `HHNYYMMDDXX` (যেমন: `HHN26091801`)।
  - প্রতিটি আইডি ডাটাবেসের সকল টেবিল জুড়ে নিশ্চিতভাবে ইউনিক রাখা হয়।
- **কার্যনির্বাহী পদের কোটা নিয়ন্ত্রণ (Strict Role Quota)**:
  - সভাপতি (President): সর্বোচ্চ ১ জন।
  - সাধারণ সম্পাদক (General Secretary): সর্বোচ্চ ১ জন।
  - কোষাধ্যক্ষ (Treasurer): সর্বোচ্চ ১ জন।
  - সাধারণ পরিষদ সদস্য (Council Members): সর্বোচ্চ ৪ জন।
  - অতিরিক্ত বা নকল এন্ট্রি আটকাতে ডাটাবেস লেভেলে কাস্টম ভ্যালিডেশন।
- **স্বেচ্ছাসেবকদের আর্থিক অঙ্গীকার (Pledge Tracking)**: আবেদন ফর্মে মাসিক/সাপ্তাহিক/বাৎসরিক চাঁদার প্রতিশ্রুতি সংরক্ষণ।

### 💳 ৪. অনুদান গেটওয়ে ও পূর্ণাঙ্গ ফাইন্যান্সিয়াল লেজার (Income-Expense Ledger)
- **মাল্টি-চ্যানেল পেমেন্ট গেটওয়ে (SSLCommerz Support)**:
  - বিকাশ, নগদ, রকেট, উপায়, ভিসা, মাস্টারকার্ড, অ্যামেক্স এবং ইন্টারনেট ব্যাংকিংয়ের মাধ্যমে সরাসরি অনুদান সংগ্রহ।
  - টেস্ট স্যান্ডবক্স ও লাইভ প্রোডাকশন সুইচিং ব্যবস্থা।
  - ইনস্ট্যান্ট পেমেন্ট নোটিফিকেশন (IPN) ও অটো-ভ্যালিডেশন।
  - ডাইনামিক ডিজিটাল অনুদান রসিদ (Donation Receipt Print & Download)।
- **ম্যানুয়াল অনুদান চ্যানেল**: ডাচ-বাংলা ব্যাংক, বিকাশ/নগদ মার্চেন্ট ও পার্সোনাল কিউআর কোড স্ক্যান ব্যবস্থা।
- **আর্থিক খতিয়ান ও হিসাব নিকাশ (Financial Bookkeeping)**:
  - সকল আয় ও ব্যয়ের নির্ভুল ডাটাবেস এন্ট্রি (ক্যাটাগরি, ভাউচার নম্বর, রসিদের ছবি আপলোড)।
  - অটোমেটিক লাইভ ব্যালেন্স শিট: মোট আয়, মোট ব্যয় এবং অবশিষ্ট তহবিলের স্বয়ংক্রিয় যোগফল।
  - **এক্সেল রিপোর্ট এক্সপোর্ট (Export to Excel)**: নির্দিষ্ট তারিখ ও ফিল্টার অনুযায়ী হিসাবপত্র এক ক্লিকে `.xlsx` ফাইলে ডাউনলোড।
  - **অফিসিয়াল প্রিন্টেবল স্টেটমেন্ট**: প্যাড ফরম্যাটে প্রিন্ট করার উপযোগী ভাউচার ও ব্যালেন্স শিট।

### 🔐 ৫. শক্তিশালী সিকিউরিটি ও কাস্টম অথেনটিকেশন
- **মাল্টি-আইডেন্টিফায়ার লগইন (MultiIdentifierAuthBackend)**: ব্যবহারকারী তার **ইউজারনেম**, **ইমেইল** অথবা **সদস্য আইডি (Member ID)** — যেকোনো একটি এবং পাসওয়ার্ড দিয়ে লগইন করতে পারেন।
- **নিরাপদ ৬-ডিজিটের ইমেইল ওটিপি পাসওয়ার্ড রিসেট**:
  - টোকেনভিত্তিক ট্র্যাকিং, ১০ মিনিটের মেয়াদোত্তীর্ণতা ও সর্বোচ্চ ৫ বার চেষ্টার সীমা (Rate Limiting)।
  - ক্লায়েন্ট-সাইড লাইভ ওটিপি ভ্যালিডেশন এবং ইমেইল মাস্কিং সুরক্ষা (যেমন: `h****5@gmail.com`)।
- **ব্র্যান্ডেড রেসপনসিভ এইচটিএমএল ইমেইল ইঞ্জিন (`send_system_email`)**: স্বয়ংক্রিয় শুভেচ্ছা, নিবন্ধন কনফার্মেশন ও পাসওয়ার্ড রিসেট নোটিফিকেশন।
- **এসএমএস গেটওয়ে ইন্টিগ্রেশন (`sms_utils.py`)**: লোকাল বাল্ক এসএমএস এপিআই রেডি।

---

## 🏗️ সিস্টেম আর্কিটেকচার ও টেকনোলজি স্ট্যাক (Architecture & Tech Stack)

```mermaid
graph TD
    Client["ব্যবহারকারী / ব্রাউজার (Desktop & Mobile)"] --> NGINX["ওয়েব সার্ভার (NGINX / LiteSpeed / Apache)"]
    NGINX --> WSGI["WSGI / Passenger Application"]
    WSGI --> DjangoCore["Django Framework (v5.2+)"]
    
    subgraph "Django Core Framework"
        DjangoCore --> Middleware["Security & CSRF Middleware"]
        Middleware --> Router["URL Routing (urls.py)"]
        Router --> CoreApp["Core App (CMS, Auth, Dashboard)"]
        Router --> VolApp["Volunteers App (Donors, Council)"]
        Router --> DonApp["Donations App (Gateway, Ledger)"]
        Router --> ProgApp["Programs App"]
        Router --> NewsApp["News App"]
        Router --> GallApp["Gallery App"]
    end
    
    DonApp --> PGW["SSLCommerz Payment Gateway"]
    CoreApp --> SMTP["SMTP Mail Server (mail.helplinehellonaogaon.com)"]
    CoreApp --> SMS["Bulk SMS Gateway API"]
    
    DjangoCore --> Database[("Database: SQLite3 / MySQL (utf8mb4)")]
    DjangoCore --> Storage["Media & Static Storage (/media, /static)"]
```

### প্রযুক্তিগত উপাদানসমূহ:
- **ব্যাকএন্ড**: Python 3.10+, Django 5.2 (MVT আর্কিটেকচার), django-environ
- **ডাটাবেস**:
  - ডেভেলপমেন্ট: SQLite 3
  - প্রোডাকশন: MySQL / MariaDB (`utf8mb4_unicode_ci` চারসেট এনকোডিং)
- **ফ্রন্টএন্ড**:
  - HTML5, Semantic Elements, Schema.org Organization Structured Data
  - CSS3, Custom Design System (`static/css/style.css`), Bootstrap 5.3
  - FontAwesome 6 Icons
  - Vanilla JavaScript & AJAX
- **পেমেন্ট গেটওয়ে**: SSLCommerz API v4, Direct Mobile Banking QR Integration
- **রিপোর্ট ইঞ্জিন**: openpyxl (Excel Generation), Print-friendly HTML Engines
- **ইমেইল সিস্টেম**: Django SMTP MultiAlternatives Engine with Responsive HTML Templates

---

## 📁 ডিরেক্টরি ও প্রজেক্ট স্ট্রাকচার (Directory & Codebase Structure)

```
hello_naogaon/
├── manage.py                     # Django management CLI script
├── requirements.txt              # প্রজেক্ট ডিপেনডেন্সি তালিকা
├── db.sqlite3                    # লোকাল ডেভেলপমেন্ট ডাটাবেস
├── .env                          # এনভায়রনমেন্ট কনফিগারেশন (গোপনীয়)
├── .env.example                  # স্যাম্পল এনভায়রনমেন্ট কনফিগারেশন ফাইল
├── DOCUMENTATION.md              # পূর্ববর্তী ডকুমেন্টেশন ফাইল
├── README.md                     # এই ফাইল (মাস্টার এন্ড-টু-এন্ড ডকুমেন্টেশন)
│
├── hello_naogaon/                # মেইন প্রজেক্ট কনফিগারেশন প্যাকেজ
│   ├── __init__.py
│   ├── settings.py               # গ্লোবাল সেটিংস, Jazzmin, সিকিউরিটি, ডাটাবেস
│   ├── urls.py                   # রুট URL রাউটিং
│   ├── wsgi.py                   # প্রোডাকশন WSGI গেটওয়ে
│   └── asgi.py                   # ASGI গেটওয়ে
│
├── core/                         # কোর ইঞ্জিন (CMS, Auth, Dashboard, Settings)
│   ├── backends.py               # Username/Email/MemberID মাল্টি-আইডেন্টিফায়ার ব্যাকএন্ড
│   ├── context_processors.py     # গ্লোবাল সাইট সেটিংস ও ড্যাশবোর্ড কাউন্টার ইঞ্জেক্টর
│   ├── email_utils.py            # ব্র্যান্ডেড এইচটিএমএল ইমেইল ডিসপ্যাচ ইঞ্জিন
│   ├── sms_utils.py              # বাল্ক এসএমএস গেটওয়ে হ্যান্ডলার
│   ├── models.py                 # SiteSetting, StatCounter, AboutImage, PasswordResetOTP
│   ├── views.py                  # হোমপেজ, অ্যাবাউট পেজ, কমপ্লেইন সাবমিশন
│   ├── views_auth.py             # কাস্টম ৬-ডিজিট ওটিপি পাসওয়ার্ড রিসেট ও ভ্যালিডেশন
│   ├── views_dashboard.py        # ৯৩ কেবি কাস্টম অ্যাডমিন কন্ট্রোল প্যানেল ও ফাইন্যান্স লেজার
│   ├── urls.py                   # কোর অ্যাপের URL রাউটস
│   └── management/commands/
│       └── seed_data.py          # প্রাথমিক ডেমো ডাটা পপুলেট করার কমান্ড
│
├── volunteers/                   # স্বেচ্ছাসেবক, কার্যনির্বাহী পরিষদ ও রক্তদাতা অ্যাপ
│   ├── models.py                 # Volunteer, TeamMember, BloodDonor এবং সিঙ্ক লজিক
│   ├── views.py                  # রক্তদাতা তালিকা, ফর্ম, ও বিডি জিও এপিআই
│   └── urls.py
│
├── donations/                    # অনুদান, পেমেন্ট গেটওয়ে ও ফাইন্যান্সিয়াল ট্রানজ্যাকশন
│   ├── models.py                 # Campaign, Bank, QRCode, ProgramDonation, FinancialTransaction
│   ├── gateway.py                # SSLCommerz সেশন ক্রিয়েশন, ভ্যালিডেশন ও হ্যান্ডলিং
│   ├── views.py                  # ডোনেশন পেজ, চেকআউট, আইপিএন ও রসিদ
│   ├── templates/donations/      # ডোনেশন পেজ, চেকআউট গেটওয়ে ও ডিজিটাল রসিদ টেমপ্লেট
│   └── urls.py
│
├── programs/                     # কার্যক্রম, ইভেন্ট ও ক্যাম্পেইন অ্যাপ
│   ├── models.py                 # Program, Event, SuccessStory
│   ├── views.py                  # প্রোগ্রাম লিস্ট, ডিটেইল ও ইভেন্ট ভিউ
│   └── urls.py
│
├── news/                         # সংবাদ, নোটিশ ও প্রেস রিলিজ অ্যাপ
│   ├── models.py                 # Article, Category
│   ├── views.py                  # নিউজ লিস্ট ও ডিটেইল ভিউ
│   └── urls.py
│
├── gallery/                      # ফটো গ্যালারি ও মিডিয়া অ্যালবাম অ্যাপ
│   ├── models.py                 # Album, Photo
│   ├── views.py                  # গ্যালারি গ্রিড ভিউ
│   └── urls.py
│
├── templates/                    # গ্লোবাল এইচটিএমএল টেমপ্লেটসমূহ
│   ├── base.html                 # মাস্টার লেআউট (হেডার, টপবার, ফন্ট, ফুটার, ম্যাপ)
│   ├── core/                     # home.html, about.html
│   ├── dashboard/                # index.html (মেইন ড্যাশবোর্ড), print_financial_statement.html
│   ├── volunteers/               # blood_donors.html, volunteer_form.html
│   ├── programs/                 # program_list.html, program_detail.html
│   ├── news/                     # news_list.html, news_detail.html
│   ├── gallery/                  # gallery.html
│   ├── registration/             # login.html, password_reset_*.html
│   └── emails/                   # system_email.html (রেসপনসিভ ইমেইল টেমপ্লেট)
│
├── static/                       # স্ট্যাটিক অ্যাসেটস (CSS, JS, Fonts, Images)
│   ├── css/                      # style.css, admin_custom.css
│   └── js/                       # কাস্টম স্ক্রিপ্টসমূহ
│
├── media/                        # ইউজার ও অ্যাডমিনের আপলোডকৃত ফাইলসমূহ
└── venv/                         # পাইথন ভার্চুয়াল এনভায়রনমেন্ট
```

---

## 🔍 প্রতিটি অ্যাপ ও মডিউলের বিস্তারিত কার্যপ্রণালী (App & Module Breakdown)

### ১. Core App

`core` অ্যাপটি সমগ্র সিস্টেমের কেন্দ্রবিন্দু। এটি সাইট-ওয়াইড সেটিংস, মূল পেজসমূহ, ওটিপি নিরাপত্তা এবং কাস্টম ড্যাশবোর্ড পরিচালনা করে।

#### মূল মডেলসমূহ:
- **`SiteSetting`**:
  - সিঙ্গেলটন মডেল (আইডি ১)।
  - ওয়েবসাইটের নাম, ট্যাগলাইন, লোগো, ফোন, ইমেইল, অফিস ঠিকানা ও সোশ্যাল মিডিয়া লিঙ্ক সংরক্ষণ করে।
  - **`google_map_embed_html` প্রোপার্টি**: একটি অত্যন্ত বুদ্ধিমান গুগল ম্যাপ পার্সার। এটি যেকোনো ফরম্যাটের গুগল ম্যাপ লিঙ্ককে (আইফ্রেম কোড, শর্টলিঙ্ক `maps.app.goo.gl`, কোঅর্ডিনেট `@lat,lng`, বা সাধারণ ঠিকানা) স্বয়ংক্রিয়ভাবে রেসপনসিভ ও লাইভ গুগল ম্যাপ আইফ্রেমে কনভার্ট করে।
- **`StatCounter`**:
  - হোমপেজের ফ্লোটিং কাউন্টার বার (যেমন: রক্তদান ৫০০+, পরিবার সহায়তা ২০০০+)।
  - আইকন ক্লাস (`fas fa-tint`), বুটস্ট্র্যাপ ব্যাজ কালার ও ডিসপ্লে অর্ডার নিয়ন্ত্রণ করে।
- **`AboutImage`**:
  - আমাদের সম্পর্কে সেকশনের ফটো কোলাজ গ্রিড (১টি বড় ফিচার্ড ছবি এবং ৪টি সাব-গ্রিড ছবি)।
- **`PasswordResetOTP`**:
  - ফরগট পাসওয়ার্ডের জন্য সিকিউর ৬-ডিজিটের ওটিপি সংরক্ষণ।
  - `expires_at` (১০ মিনিট লাইফটাইম), `attempts` (সর্বোচ্চ ৫ বার ভুল কোড দেওয়ার সীমা) এবং `is_valid()` মেথড।

#### অথেনটিকেশন ও সিকিউরিটি (`backends.py` & `views_auth.py`):
1. **মাল্টি-আইডেন্টিফায়ার অথেনটিকেশন**:
   - `MultiIdentifierAuthBackend` ব্যবহার করে ইউজাররা ৩ উপায়ে লগইন করতে পারেন:
     - `Username`
     - `Email`
     - `Member ID` (স্বেচ্ছাসেবক বা টিম মেম্বারের নির্দিষ্ট কোড)
2. **ওটিপি পাসওয়ার্ড রিসেট ফ্লো**:
   - ধাপ ১: ব্যবহারকারী তার ইমেইল বা ইউজারনেম দেন।
   - ধাপ ২: সিস্টেমে অ্যাকাউন্ট থাকলে ইমেইলটি মাস্ক করে স্ক্রিনে দেখানো হয় (যেমন `h****5@gmail.com`) এবং ৬ ডিজিটের গোপন ওটিপি ইমেইলে যায়।
   - ধাপ ৩: এজ্যাক্স এন্ডপয়েন্ট (`/api/validate-otp/`) দিয়ে রিয়েল-টাইমে ওটিপি যাচাই হয়।
   - ধাপ ৪: ওটিপি সঠিক হলে নতুন পাসওয়ার্ড নির্ধারণ ফর্ম উন্মুক্ত হয় এবং পাসওয়ার্ড আপডেট হয়ে স্বয়ংক্রিয়ভাবে সেশন ক্লোজ হয়।

#### কাস্টম কার্ডলি ড্যাশবোর্ড (`views_dashboard.py`):
ডিফল্ট জ্যাঙ্গো অ্যাডমিনের বিকল্প হিসেবে তৈরি ৯৩ কেবির এই ড্যাশবোর্ডটি সেকশন-ভিত্তিক কার্ড স্টাইলে ডিজাইন করা:
- হোম পেজের কন্টেন্ট পরিবর্তন (লোগো, টাইটেল, হিরো ব্যানার, ফুটার, ম্যাপ)।
- কাউন্টার কার্ড অ্যাড/এডিট/ডিলিট।
- অ্যাবাউট সেকশনের ছবি বাল্ক আপলোড ও ডিলিট।
- সংবাদ ও নোটিশ প্রকাশ।
- অনুদান ক্যাম্পেইন ও জরুরি আবেদন তৈরি।
- ফাইন্যান্সিয়াল ট্রানজ্যাকশন এন্ট্রি ও এক্সেল শিট ডাউনলোড।
- ভলান্টিয়ার অনুমোদন ও রক্তের গ্রুপ পর্যবেক্ষণ।

---

### ২. Volunteers App

স্বেচ্ছাসেবক নিবন্ধন, পরিচালনা পর্ষদ এবং জীবন রক্ষাকারী রক্তদাতাদের ডাটাবেস হ্যান্ডেল করে এই অ্যাপটি।

#### মূল মডেলসমূহ:
- **`Volunteer`**:
  - নাম, ফোন, ইমেইল, রক্তের গ্রুপ, বিভাগ, জেলা, উপজেলা, পেশা এবং বিস্তারিত ঠিকানা।
  - `contribution_frequency` এবং `contribution_amount`: নিয়মিত চাঁদা বা আর্থিক প্রতিশ্রুতির পরিমাণ।
  - `member_id`: স্বয়ংক্রিয় ৮-ডিজিট ইউনিক নম্বর (`YYMMDDXX`)।
  - `is_eligible_to_donate`: শেষ রক্তদানের তারিখ থেকে ৯০ দিন পূর্ণ হয়েছে কিনা তা স্বয়ংক্রিয়ভাবে রিটার্ন করে।
- **`TeamMember` (পরিচালনা পরিষদ)**:
  - কার্যনির্বাহী সদস্যদের জন্য পদবী: সভাপতি, সাধারণ সম্পাদক, কোষাধ্যক্ষ, সাধারণ পরিষদ সদস্য এবং অন্যান্য।
  - **পদবী কোটা ভ্যালিডেশন (`clean()` মেথড)**: সভাপতি, সাধারণ সম্পাদক ও কোষাধ্যক্ষ পদে ১ জনের বেশি হতে পারবে না। সাধারণ পরিষদ সদস্য পদে সর্বোচ্চ ৪ জন হতে পারবে।
  - `member_id`: প্রিফিক্সসহ ইউনিক আইডি (`HHNYYMMDDXX`)।
- **`BloodDonor` (রক্তদাতা ডাটাবেস)**:
  - রক্তের গ্রুপ, ফোন, এলাকা, সর্বশেষ রক্তদানের তারিখ এবং সক্রিয়তার স্ট্যাটাস।
  - **`sync_to_blood_donor()` লজিক**: যখনই কোনো ভলান্টিয়ার বা টিম মেম্বার রক্তের গ্রুপসহ সেভ হন, সিস্টেম স্বয়ংক্রিয়ভাবে ব্যাকগ্রাউন্ডে তাকে ব্লাড ডোনার ডাটাবেসে এন্ট্রি বা আপডেট করে।

#### জিওগ্রাফিক ফিল্টারিং এপিআই (`views.py`):
- `/volunteers/api/bd-geo/`: বাংলাদেশের সকল বিভাগ, জেলা ও উপজেলার ক্যাশড ও দ্রুতগতির জিও-জেসন ডাটা পরিবেশন করে, যার ফলে পাবলিক ফর্ম ও সার্চ ফিল্টারে ক্যাসকেডিং ড্রপডাউন (বিভাগ বাছাই করলে জেলা, জেলা বাছাই করলে উপজেলা) কাজ করে।

---

### ৩. Donations App

এই অ্যাপটি সংগঠনের সকল আর্থিক লেনদেন, অনুদান সংগ্রহ ও ফান্ডিং ক্যাম্পেইন পরিচালনা করে।

#### মূল ফিচার ও মডেলসমূহ:
- **`DonationPageContent`**: অনুদান পেজের হিরো ব্যানার, কেন দান করবেন, স্বচ্ছতা ও জবাবদিহিতা সংক্রান্ত লেখা।
- **`Campaign`**: নির্দিষ্ট লক্ষ্যমাত্রার ক্যাম্পেইন (যেমন: শীতবস্ত্র বিতরণ, লক্ষ্যমাত্রা: ৫,০০,০০০ টাকা, সংগৃহীত: ২,৫০,০০০ টাকা)।
- **`EmergencyAppeal`**: জরুরি বন্যা বা চিকিৎসা সহায়তার ফ্লোটিং অ্যালার্ট বক্স।
- **`Bank` & `QRCode`**: ব্যাংক হিসাব (ডাচ বাংলা, রাউটিং নম্বর ইত্যাদি) এবং মোবাইল ব্যাংকিং কিউআর কোড।
- **`PaymentGatewaySetting`**:
  - SSLCommerz, ShurjoPay, AamarPay বা bKash এর ক্রেডেনশিয়ালস (Store ID, Store Password/Secret Key)।
  - এক ক্লিকে **স্যান্ডবক্স (Sandbox)** থেকে **লাইভ প্রোডাকশনে (Live Production)** রূপান্তর করার টগল।
- **`ProgramDonation`**:
  - ওয়েবসাইটের মাধ্যমে আসা প্রতিটি অনলাইন ডোনেশন বা সদস্য মাসিক ফির রেকর্ড।
  - ট্রানজ্যাকশন আইডি, পেমেন্ট চ্যানেল (বিকাশ/কার্ড), অনুদানের ধরন (সাধারণ, স্বেচ্ছাসেবক ফি, জরুরি তহবিল) এবং স্ট্যাটাস (অপেক্ষমাণ/অনুমোদিত/ব্যর্থ)।
  - ডিজিটাল মানি রসিদ পেজ (`/donations/receipt/<id>/`)।
- **`FinancialTransaction` (সংগঠনের মূল হিসাব খাতা)**:
  - আয় (Income) ও ব্যয় (Expense) ট্র্যাকিং।
  - প্রতিটি ব্যয়ের বিপরীতে ভাউচার নম্বর, খরচের খাত, তারিখ, টাকা এবং রসিদের স্ক্যান কপি আপলোড।
  - **এক্সেল এক্সপোর্ট (`export_financial_excel`)**: অডিট বা বার্ষিক সাধারণ সভার জন্য সম্পূর্ণ আয়-ব্যয়ের খতিয়ান মাইক্রোসফট এক্সেলে এক্সপোর্ট।
  - **প্রিন্টেবল স্টেটমেন্ট (`print_financial_statement`)**: লেটারহেড প্যাডে প্রিন্ট করার উপযোগী ক্যাশ রিপোর্ট।

---

### ৪. Programs App

- **`Program`**: নিয়মিত সেবা কার্যক্রম (যেমন: ফ্রি মেডিকেল ক্যাম্প, খাদ্য বিতরণ, রক্তদান সেবা)।
  - লক্ষ্যমাত্রা অর্থ (`target_amount`) ও সংগৃহীত অর্থ (`raised_amount`) দিলে স্বয়ংক্রিয় প্রগ্রেস বার (`progress_percent`) প্রদর্শিত হয়।
- **`Event`**: আসন্ন ইভেন্টের তারিখ, সময় ও ভেন্যু।
- **`SuccessStory`**: সংগঠনের সফলতার গল্প ও উপকারভোগীদের প্রতিক্রিয়া।

---

### ৫. News App

- **`Article` & `Category`**:
  - সামাজিক উদ্যোগের খবর, গণমাধ্যমে প্রকাশিত সংবাদ, বিজ্ঞপ্তি ও ছবিসহ ফিচার আর্টিকেল।
  - প্রকাশনা নিয়ন্ত্রণ (`is_published`) এবং প্রকাশের তারিখ অনুযায়ী সাজানো।

---

### ৬. Gallery App

- **`Album` & `Photo`**:
  - বিভিন্ন কর্মসূচির ছবি অ্যালবাম আকারে সংরক্ষণ ও প্রদর্শন।
  - রেসপনসিভ লাইটবক্স গ্রিডে ফুল রেজোলিউশন ছবি দেখার ব্যবস্থা।

---

## 🗄️ ডাটাবেস মডেল ও সম্পর্ক (Database Models & Relationships)

```mermaid
erDiagram
    SiteSetting ||--o{ StatCounter : "controls display"
    SiteSetting ||--o{ AboutImage : "collage photos"
    
    User ||--o| Volunteer : "has profile"
    User ||--o| TeamMember : "has executive profile"
    User ||--o{ PasswordResetOTP : "generates"
    
    Volunteer ||--o{ BloodDonor : "auto-syncs to"
    TeamMember ||--o{ BloodDonor : "auto-syncs to"
    
    Program ||--o{ FinancialTransaction : "linked expense/income"
    Program ||--o{ ProgramDonation : "receives donations"
    
    DonationMethod ||--o{ QRCode : "contains"
    Album ||--o{ Photo : "contains photos"
    Category ||--o{ Article : "categorizes"
```

---

## 👥 রোল-বেসড অ্যাক্সেস কন্ট্রোল (RBAC & Permissions Matrix)

ড্যাশবোর্ডে (`/dashboard/`) ব্যবহারকারীর পদবী ও রোলের ওপর ভিত্তি করে ডায়নামিক পারমিশন ও ইন্টারফেস প্রদর্শিত হয়:

| রোল / ব্যবহারকারী | সিএমএস ও কন্টেন্ট এডিট | ভলান্টিয়ার ও টিম ব্যবস্থাপনা | আয়-ব্যয় ও হিসাব খাতা এডিট | আর্থিক রিপোর্ট ও প্রিন্ট | ড্যাশবোর্ড ভিউ টাইপ |
|---|:---:|:---:|:---:|:---:|---|
| **Super Admin (প্রধান অ্যাডমিন)** | ✅ হ্যাঁ | ✅ হ্যাঁ | ✅ হ্যাঁ | ✅ হ্যাঁ | পূর্ণ নিয়ন্ত্রণ (Full Access) |
| **Staff Admin (সাধারণ অ্যাডমিন)** | ✅ হ্যাঁ | ✅ হ্যাঁ | ✅ হ্যাঁ | ✅ হ্যাঁ | অ্যাডমিন কন্ট্রোল |
| **সভাপতি (President)** | ❌ না | ❌ না | ❌ না | ✅ হ্যাঁ | লিডারশিপ ওভারভিউ ও অডিট |
| **সাধারণ সম্পাদক (General Secretary)** | ❌ না | ❌ না | ❌ না | ✅ হ্যাঁ | লিডারশিপ ওভারভিউ ও অডিট |
| **কোষাধ্যক্ষ (Treasurer)** | ❌ না | ❌ না | ✅ হ্যাঁ (সম্পূর্ণ) | ✅ হ্যাঁ (এক্সেল ও প্রিন্ট) | ফাইন্যান্সিয়াল কন্ট্রোল প্যানেল |
| **সাধারণ পরিষদ সদস্য (Council Member)** | ❌ না | ❌ না | ❌ না | ❌ না | ব্যক্তিগত প্রোফাইল ও ডিরেক্টরি |
| **সাধারণ স্বেচ্ছাসেবক / ভিজিটর** | ❌ না | ❌ না | ❌ না | ❌ না | শুধু পাবলিক ওয়েবসাইট |

---

## 💻 লোকাল সেটআপ ও ডেভেলপমেন্ট গাইড (Local Development Setup)

লোকাল কম্পিউটারে প্রজেক্টটি চালু করতে নিচের ধাপগুলো অনুসরণ করুন:

### ১. পূর্বশর্ত (Prerequisites)
- **Python 3.10** বা এর চেয়ে নতুন সংস্করণ
- **Git**
- **pip** ও **virtualenv**

### ২. ভার্চুয়াল এনভায়রনমেন্ট তৈরি ও ডিপেনডেন্সি ইনস্টলেশন
টার্মিনাল বা কমান্ড প্রম্পট (PowerShell) ওপেন করে প্রজেক্ট ফোল্ডারে যান:

```bash
# প্রজেক্ট ফোল্ডারে প্রবেশ
cd d:\Projects\hello_naogaon

# ভার্চুয়াল এনভায়রনমেন্ট তৈরি (যদি না থাকে)
python -m venv venv

# ভার্চুয়াল এনভায়রনমেন্ট অ্যাক্টিভেট করুন
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate

# প্রয়োজনীয় প্যাকেজ ইনস্টল করুন
pip install -r requirements.txt
```

### ৩. এনভায়রনমেন্ট কনফিগারেশন (.env)
প্রজেক্ট রুটে `.env.example` ফাইলের একটি কপি তৈরি করে সেটির নাম দিন `.env`:

```bash
cp .env.example .env
```
লোকাল টেস্টের জন্য ডিফল্ট SQLite ডাটাবেস রাখা আছে, তাই অতিরিক্ত কনফিগারেশন ছাড়াই কাজ করবে।

### ৪. ডাটাবেস মাইগ্রেশন ও ডিফল্ট ডাটা পপুলেশন
```bash
# ডাটাবেস টেবিল তৈরি
python manage.py makemigrations
python manage.py migrate

# রেফারেন্স ডিজাইনের প্রাথমিক ডাটা সিড করুন (SiteSettings, Programs, Stats, Donors)
python manage.py seed_data
```

### ৫. সুপার অ্যাডমিন অ্যাকাউন্ট তৈরি
```bash
python manage.py createsuperuser
```
*(ব্যবহারকারীর নাম, ইমেইল ও পাসওয়ার্ড প্রদান করুন)*

### ৬. ডেভেলপমেন্ট সার্ভার চালু
```bash
python manage.py runserver
```
সার্ভার চালু হলে ব্রাউজারে প্রবেশ করুন:
- **পাবলিক ওয়েবসাইট**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **কাস্টম অ্যাডমিন ড্যাশবোর্ড**: [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/) অথবা [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **ক্লাসিক্যাল জ্যাঙ্গো অ্যাডমিন**: [http://127.0.0.1:8000/django-admin/](http://127.0.0.1:8000/django-admin/)

---

## ⚙️ এনভায়রনমেন্ট ভেরিয়েবলসমূহ (Environment Variables Specification)

প্রজেক্টের রুট ডিরেক্টরিতে `.env` ফাইলে নিচের ভেরিয়েবলগুলো সংজ্ঞায়িত করা যায়:

| ভেরিয়েবলের নাম | ডিফল্ট মান | বিবরণ |
|---|---|---|
| `SECRET_KEY` | `django-insecure-...` | জ্যাঙ্গোর ক্রিপ্টোগ্রাফিক সিক্রেট কি (প্রোডাকশনে গোপন রাখুন) |
| `DEBUG` | `True` | ডেভেলপমেন্টে `True`, প্রোডাকশনে অবশ্যই `False` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,...` | অনুমোদিত ডোমেইন নামের কমা-সেপারেটেড তালিকা |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:8000,...` | অনুমোদিত CSRF অরিজিনাল ডোমেইন |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | ডাটাবেস কানেকশন স্ট্রিং (MySQL: `mysql://user:pass@host:3306/dbname`) |
| `SECURE_SSL_REDIRECT` | `False` | প্রোডাকশনে HTTPS ফোর্স করতে `True` করুন |
| `SESSION_COOKIE_SECURE` | `False` | HTTPS কুকি সুরক্ষার জন্য প্রোডাকশনে `True` করুন |
| `CSRF_COOKIE_SECURE` | `False` | HTTPS CSRF কুকির জন্য প্রোডাকশনে `True` করুন |
| `EMAIL_BACKEND` | `...smtp.EmailBackend` | ইমেইল পাঠানোর ব্যাকএন্ড |
| `EMAIL_HOST` | `mail.helplinehellonaogaon.com`| SMTP মেইল সার্ভার হোস্ট |
| `EMAIL_PORT` | `465` | SSL এর জন্য ৪৬৫, TLS এর জন্য ৫৮৭ |
| `EMAIL_USE_SSL` | `True` | পোর্ট ৪৬৫ এর ক্ষেত্রে `True` |
| `EMAIL_HOST_USER` | `info@...` | SMTP ব্যবহারকারী ইমেইল |
| `EMAIL_HOST_PASSWORD` | `******` | মেইলবক্সের পাসওয়ার্ড |
| `DEFAULT_FROM_EMAIL`| `info@...` | প্রেরক হিসেবে প্রদর্শিত ইমেইল ঠিকানা |
| `SMS_API_URL` | `""` | বাল্ক এসএমএস গেটওয়ে পোস্ট ইউআরএল |
| `SMS_API_TOKEN` | `""` | এসএমএস গেটওয়ে অথেনটিকেশন টোকেন |

---

## 🚀 প্রোডাকশন ডিপ্লয়মেন্ট গাইড (Production Deployment - cPanel / VPS)

### ক. cPanel (Shared / Cloud Hosting with Python Selector)
1. **cPanel এ লগইন করে 'Setup Python App' এ যান**:
   - Python Version: **3.10** বা **3.11** নির্বাচন করুন।
   - Application Root: `/home/username/hello_naogaon`
   - Application URL: `helplinehellonaogaon.com`
2. **ফাইলসমূহ আপলোড করুন**:
   - Git এর মাধ্যমে ক্লোন করুন অথবা জিপ ফাইল এক্সট্রাক্ট করুন।
   - `media/` ও `static/` ফোল্ডারের পারমিশন ৭৫৫ নিশ্চিত করুন।
3. **cPanel MySQL ডাটাবেস তৈরি করুন**:
   - cPanel থেকে MySQL Database এবং User তৈরি করে সকল প্রিভিলেজ দিন।
   - Collation দিন: `utf8mb4_unicode_ci`।
   - `.env` ফাইলে ডাটাবেস ইউআরএল সেট করুন:
     ```env
     DATABASE_URL=mysql://cp_user:cp_password@localhost:3306/cp_dbname
     DEBUG=False
     SECURE_SSL_REDIRECT=True
     ```
4. **ডিপেনডেন্সি ইনস্টল ও মাইগ্রেশন**:
   - cPanel টার্মিনাল বা SSH ওপেন করে ভার্চুয়াল এনভায়রনমেন্ট অ্যাক্টিভেট করুন:
     ```bash
     source /home/username/virtualenv/hello_naogaon/3.10/bin/activate
     pip install -r requirements.txt
     python manage.py migrate
     python manage.py collectstatic --noinput
     ```
5. **Passenger WSGI ফাইল (`passenger_wsgi.py`) কনফিগারেশন**:
   ```python
   import os
   import sys
   sys.path.insert(0, os.path.dirname(__file__))
   from hello_naogaon.wsgi import application
   ```
6. **Restart Python App** বাটনে ক্লিক করুন।

### খ. VPS / Cloud Server (Ubuntu + NGINX + Gunicorn)
1. **Gunicorn Systemd সার্ভিস ফাইল তৈরি করুন (`/etc/systemd/system/hellonaogaon.service`)**:
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
2. **NGINX রিভার্স প্রক্সি কনফিগারেশন (`/etc/nginx/sites-available/hellonaogaon`)**:
   ```nginx
   server {
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
3. **Certbot দিয়ে ফ্রি SSL ইনস্টল করুন**:
   ```bash
   sudo certbot --nginx -d helplinehellonaogaon.com -d www.helplinehellonaogaon.com
   ```

---

## 🛠️ অ্যাডমিন ও কন্ট্রোল প্যানেল গাইড (Admin Panel & CMS Management Manual)

অ্যাডমিন প্যানেলটি পরিচালনা করা অত্যন্ত সহজ। লগইন করার পর `/dashboard/` এ প্রবেশ করলে নিচের সেকশনগুলো পাওয়া যায়:

### ১. হোম পেজ কাস্টমাইজেশন (Home Page CMS)
- **হেডার ও হিরো সেকশন**: ওয়েবসাইটের নাম, লোগো, স্লোগান, হিরো ব্যানার ইমেজ, ফোন নম্বর ও সোশ্যাল মিডিয়া লিঙ্ক এক ক্লিকে পরিবর্তনযোগ্য।
- **কাউন্টার কার্ডসমূহ**: যেকোনো নতুন অর্জনের সংখ্যা (যেমন: রক্তদান ১০০০+, পরিবার সহায়তা ৩০০০+) আপডেট করুন।
- **আমাদের সম্পর্কে ফটো কোলাজ**: মূল ফিচার্ড ছবি নির্বাচন করুন এবং সাব-গ্রিডের জন্য একসাথে একাধিক ছবি (`multiple upload`) নির্বাচন করে আপলোড করুন।
- **ফুটার ও ম্যাপ**: গুগল ম্যাপ থেকে যেকোনো লিঙ্ক এনে পেস্ট করলে ফুটারের ম্যাপ নিজে থেকেই আপডেট হয়ে যাবে।

### ২. রক্তদাতা ব্যবস্থাপনা (Blood Donors)
- নতুন রক্তদাতার নাম, রক্তের গ্রুপ ও ফোন নম্বর এন্ট্রি।
- রক্তের গ্রুপ ও উপজেলা অনুযায়ী ফিল্টারিং।
- রক্তদাতার সক্রিয়তা ও প্রাইভেসি অন/অফ।

### ৩. অনুদান ও ফাইন্যান্স কন্ট্রোল (Finance & Donations)
- **ব্যাংক ও কিউআর কোড**: বিকাশ, নগদ ও ব্যাংকের একাউন্ট নম্বর পরিবর্তন।
- **অনলাইন গেটওয়ে**: SSLCommerz Store ID ও Password বসিয়ে মুহূর্তের মধ্যে লাইভ পেমেন্ট চালু করা।
- **ক্যাশ বুক / ট্রানজ্যাকশন এন্ট্রি**:
  - কোনো অনুদান আসলে `Income` ক্যাটাগরিতে যোগ করুন।
  - কোনো ত্রাণ বা ইভেন্ট খরচ হলে `Expense` ক্যাটাগরিতে ভাউচারসহ যোগ করুন।
  - স্বয়ংক্রিয় ব্যালেন্স ও হিস্ট্রি তৈরি হবে।
  - **Download Excel** বাটনে চাপ দিয়ে তাৎক্ষণিক এক্সেল শিট ডাউনলোড করুন।
  - **Print Statement** বাটনে চাপ দিয়ে অফিসিয়াল ক্যাশ শিট প্রিন্ট করুন।

### ৪. টিম মেম্বার ও ভলান্টিয়ার অনুমোদন
- নতুন আবেদনগুলো পর্যালোচনা করে অ্যাপ্রুভ বা রিজেক্ট করুন।
- পরিচালনা পর্ষদের সদস্যদের পদবী অনুযায়ী সাজান।

---

## 🔒 সিকিউরিটি ও ট্রাবলশুটিং (Security & Troubleshooting FAQ)

### সাধারণ সমস্যা ও সমাধান:

#### ১. ছবি আপলোড করার সময় সাইজ লিমিট সমস্যা দেখালে কী করবেন?
- **কারণ**: সার্ভার স্টোরেজ ও দ্রুত লোডিংয়ের জন্য ছবিতে সর্বোচ্চ ১ মেগাবাইট (1 MB) সীমা দেওয়া আছে।
- **সমাধান**: ছবি বড় হলে মেসেজে নির্দেশিত অনুযায়ী সাইজ কিছুটা কমিয়ে (যেমন: TinyPNG বা ResizePixel ব্যবহার করে) আপলোড করুন।

#### ২. পাসওয়ার্ড ভুলে গেলে ইমেইলে ওটিপি না আসলে কী করবেন?
- `.env` ফাইলে `EMAIL_HOST`, `EMAIL_HOST_USER` ও `EMAIL_HOST_PASSWORD` ঠিক আছে কিনা চেক করুন।
- সার্ভারের পোর্ট ৪৬৫ (SSL) বা ৫৮৭ (TLS) ওপেন আছে কিনা নিশ্চিত করুন।
- মেইলের স্প্যাম ফোল্ডার চেক করুন।

#### ৩. গুগল ম্যাপ প্রদর্শিত হচ্ছে না কেন?
- গুগল ম্যাপে গিয়ে আপনার লোকেশন সার্চ করে "Share" এ ক্লিক করুন।
- "Embed a map" থেকে আইফ্রেম কোডটি অথবা সাধারণ "Share Link" টি কপি করে ড্যাশবোর্ডের সাইট সেটিংসে পেস্ট করে সংরক্ষণ করুন। সিস্টেম নিজে থেকেই সেটিকে প্রপার আইফ্রেমে পরিণত করবে।

#### ৪. CSRF Verification Failed Error দেখালে:
- `.env` ফাইলের `CSRF_TRUSTED_ORIGINS` এ আপনার পূর্ণ ডোমেইনটি (`https://helplinehellonaogaon.com`) প্রটোকলসহ যুক্ত করুন।

---

## 📞 যোগাযোগ ও সহায়তা (Support & Contacts)

- **সংগঠনের নাম**: Helpline Hello Naogaon (হেল্পলাইন হ্যালো নওগাঁ)
- **প্রধান কার্যালয়**: মহাদেবপুর, নওগাঁ - ৬৬০০, রাজশাহী, বাংলাদেশ
- **ইমেইল**: `info@helplinehellonaogaon.com` / `hello.naogaon@gmail.com`
- **অফিসিয়াল ওয়েবসাইট**: [https://helplinehellonaogaon.com](https://helplinehellonaogaon.com)

---
*© Helpline Hello Naogaon. All Rights Reserved.*
