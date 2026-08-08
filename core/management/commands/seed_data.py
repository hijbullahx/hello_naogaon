from django.core.management.base import BaseCommand
from core.models import SiteSetting, StatCounter, AboutImage
from programs.models import Program
from news.models import Article
from volunteers.models import BloodDonor
from donations.models import Bank, DonationMethod, QRCode
from datetime import date, timedelta

class Command(BaseCommand):
    help = "Seeds initial data for Helpline Hello Naogaon matching reference layout design."

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        # 1. SiteSetting
        site_setting, created = SiteSetting.objects.get_or_create(pk=1)
        site_setting.title = "Helpline Hello Naogaon"
        site_setting.tagline = "সবসময় আপনার পাশে - একটি স্বেচ্ছাসেবী সংগঠন"
        site_setting.hero_badge = "মানবতার পাশে, নওগাঁর প্রতিটি মানুষের জন্য"
        site_setting.hero_title = "Helpline Hello Naogaon"
        site_setting.hero_subtitle = "আমরা একটি অরাজনৈতিক, অলাভজনক ও স্বেচ্ছাসেবী সংগঠন, যা সমাজের অসহায় মানুষের পাশে দাঁড়াতে প্রতিশ্রুতিবদ্ধ।"
        site_setting.about_heading = "আমাদের সম্পর্কে"
        site_setting.about_text = "Helpline Hello Naogaon একটি স্বেচ্ছাসেবী ও মানবিক সংগঠন। আমরা রক্তদান, শিক্ষা সহায়তা, মানবিক সহায়তা, পরিবেশ সুরক্ষা ও দুর্যোগকালীন সেবাসহ বিভিন্ন সামাজিক কার্যক্রম পরিচালনা করে থাকি।"
        site_setting.cta_banner_title = "আসুন, আমরা সবাই মিলে একটি মানবিক ও সুন্দর সমাজ গড়ে তুলি"
        site_setting.cta_banner_button_text = "স্বেচ্ছাসেবক হন"
        site_setting.contact_phone = "+880 1730-XXXXXX"
        site_setting.contact_email = "hello.naogaon@gmail.com"
        site_setting.contact_address = "Helpline Hello Naogaon Public Library, মহাদেবপুর, নওগাঁ - ৬৬০০"
        site_setting.facebook_url = "https://facebook.com/hello.naogaon"
        site_setting.footer_about = "Helpline Hello Naogaon একটি স্বেচ্ছাসেবী সংগঠন। আমাদের লক্ষ্য সমাজকে এগিয়ে নিয়ে যাওয়া এবং অসহায় মানুষের পাশে দাঁড়ানো।"
        site_setting.save()
        self.stdout.write("[OK] SiteSetting initialized.")

        # 2. StatCounters
        stats_data = [
            {"title": "রক্তদান", "value": "500+", "icon_class": "fas fa-tint", "badge_color": "danger", "order": 1},
            {"title": "পরিবারকে সহায়তা", "value": "2,000+", "icon_class": "fas fa-users", "badge_color": "success", "order": 2},
            {"title": "শিক্ষার্থী সহায়তা", "value": "300+", "icon_class": "fas fa-graduation-cap", "badge_color": "warning", "order": 3},
            {"title": "স্বেচ্ছাসেবক", "value": "100+", "icon_class": "fas fa-hands-holding-heart", "badge_color": "primary", "order": 4},
            {"title": "সামাজিক কর্মসূচি", "value": "50+", "icon_class": "fas fa-seedling", "badge_color": "info", "order": 5},
        ]
        for item in stats_data:
            StatCounter.objects.get_or_create(
                title=item["title"],
                defaults={
                    "value": item["value"],
                    "icon_class": item["icon_class"],
                    "badge_color": item["badge_color"],
                    "order": item["order"],
                    "is_active": True
                }
            )
        self.stdout.write("[OK] StatCounters initialized.")

        # 3. Programs
        programs_data = [
            {
                "title": "রক্তদান সেবা",
                "short_description": "জরুরি রক্তদাতা খুঁজে দেয়া ও রক্তদাতা ডাটাবেস পরিচালনা।",
                "description": "জরুরি প্রয়োজনে মুমূর্ষু রোগীদের জন্য বিনামূল্যে রক্তদাতা পরিচালনা ও মেডিকেল ক্যাম্প গঠন।",
                "icon_class": "fas fa-tint",
                "badge_color": "danger",
                "status": "ongoing",
                "order": 1
            },
            {
                "title": "শিক্ষা সহায়তা",
                "short_description": "দরিদ্র শিক্ষার্থীদের বই, শিক্ষা উপকরণ ও বৃত্তি প্রদান।",
                "description": "সুবিধাবঞ্চিত মেধাবী শিক্ষার্থীদের লেখাপড়ার খরচ ও শিক্ষা সামগ্রী সরবরাহ।",
                "icon_class": "fas fa-book-reader",
                "badge_color": "success",
                "status": "ongoing",
                "order": 2
            },
            {
                "title": "মানবিক সহায়তা",
                "short_description": "অসহায় ও দুঃস্থ পরিবারের পাশে দাঁড়ানো।",
                "description": "দুঃস্থ ও প্রতিবন্ধী পরিবারগুলোকে প্রয়োজনীয় খাদ্য ও নগদ আর্থিক সাহায্য প্রদান।",
                "icon_class": "fas fa-hands-holding-child",
                "badge_color": "warning",
                "status": "ongoing",
                "order": 3
            },
            {
                "title": "পরিবেশ কর্মসূচি",
                "short_description": "বৃক্ষরোপণ ও পরিবেশ সচেতনতা বৃদ্ধি।",
                "description": "সবুজ নওগাঁ গড়ার লক্ষ্যে উপজেলার প্রতিটি এলাকায় বিনামূল্যে ফলজ ও বনজ চারা রোপণ।",
                "icon_class": "fas fa-leaf",
                "badge_color": "success",
                "status": "ongoing",
                "order": 4
            },
            {
                "title": "দুর্যোগ সহায়তা",
                "short_description": "বন্যা, ঝড় ও দুর্ঘটনায় জরুরি সহায়তা প্রদান।",
                "description": "প্রাকৃতিক ও দুর্ঘটনাকবলিত এলাকার দুর্গত মানুষের মাঝে দ্রুত ত্রাণ বিতরণ।",
                "icon_class": "fas fa-ambulance",
                "badge_color": "info",
                "status": "ongoing",
                "order": 5
            },
        ]
        for p in programs_data:
            Program.objects.get_or_create(
                title=p["title"],
                defaults=p
            )
        self.stdout.write("[OK] Programs initialized.")

        # 4. News Articles
        articles_data = [
            {
                "title": "বৃক্ষরোপণ কর্মসূচি সম্পন্ন",
                "content": "নওগাঁর বিভিন্ন এলাকায় শতাধিক বৃক্ষরোপণ কর্মসূচি সফলভাবে সম্পন্ন করা হয়েছে। এতে স্থানীয় তরুণরা স্বতঃস্ফূর্তভাবে অংশগ্রহণ করেন।",
            },
            {
                "title": "রক্তদান কর্মসূচি সফল",
                "content": "স্বেচ্ছামূলক রক্তদান কর্মসূচিতে অনেকেই আগ্রহের সাথে অংশগ্রহণ করে বিনামূল্যে রক্ত প্রদান করেছেন।",
            },
            {
                "title": "শীতবস্ত্র বিতরণ",
                "content": "মহাদেবপুর উপজেলার বিভিন্ন গ্রামের দরিদ্র ও বয়োবৃদ্ধদের মাঝে শীতবস্ত্র বিতরণ করা হয়েছে।",
            },
        ]
        for art in articles_data:
            Article.objects.get_or_create(
                title=art["title"],
                defaults={
                    "content": art["content"],
                    "is_published": True
                }
            )
        self.stdout.write("[OK] Articles initialized.")

        # 5. Bank Accounts & Donation Methods
        bank, _ = Bank.objects.get_or_create(
            account_number="1234567890",
            defaults={
                "bank_name": "Dutch-Bangla Bank",
                "account_name": "Helpline Hello Naogaon",
                "swift_code": "0902600925",
                "branch": "Naogaon Branch",
                "is_active": True
            }
        )
        
        bkash_method, _ = DonationMethod.objects.get_or_create(name="bKash", defaults={"is_active": True})
        nagad_method, _ = DonationMethod.objects.get_or_create(name="Nagad", defaults={"is_active": True})
        rocket_method, _ = DonationMethod.objects.get_or_create(name="Rocket", defaults={"is_active": True})
        
        self.stdout.write("[OK] Bank & Donation methods initialized.")

        # 6. Blood Donors
        donors_data = [
            {"full_name": "আরিফুল ইসলাম", "blood_group": "A+", "phone": "01711002233", "location": "মহাদেবপুর, নওগাঁ"},
            {"full_name": "সাব্বির রহমান", "blood_group": "O+", "phone": "01822334455", "location": "নওগাঁ সদর"},
            {"full_name": "তানভীর আহমেদ", "blood_group": "B+", "phone": "01933445566", "location": "পত্নীতলা, নওগাঁ"},
        ]
        for d in donors_data:
            BloodDonor.objects.get_or_create(
                phone=d["phone"],
                defaults=d
            )
        self.stdout.write("[OK] Blood Donors initialized.")

        # 7. Team Members
        from volunteers.models import TeamMember, Volunteer
        team_data = [
            {"name": "আরিফুল ইসলাম", "role": "সভাপতি & প্রতিষ্ঠাতা", "bio": "সামাজিক উন্নয়ন ও মানবিক সেবায় নিয়োজিত।", "order": 1},
            {"name": "সাব্বির রহমান", "role": "সাধারণ সম্পাদক", "bio": "রক্তদান ক্যাম্প ও শিক্ষা সহায়তা কার্যক্রম সমন্বয়ক।", "order": 2},
            {"name": "তানভীর আহমেদ", "role": "সাংগঠনিক সম্পাদক", "bio": "পরিবেশ ও স্বেচ্ছাসেবক টিম পরিচালক।", "order": 3},
        ]
        for tm in team_data:
            TeamMember.objects.get_or_create(
                name=tm["name"],
                defaults=tm
            )
        self.stdout.write("[OK] Team Members initialized.")

        # 8. Volunteers
        volunteer_data = [
            {"full_name": "মো: রফিকুল ইসলাম", "email": "rofiq@gmail.com", "phone": "01711223344", "address": "মহাদেবপুর, নওগাঁ", "status": "approved"},
            {"full_name": "মো: নাজমুল হাসান", "email": "nazmul@gmail.com", "phone": "01822334455", "address": "নওগাঁ সদর", "status": "approved"},
        ]
        for vol in volunteer_data:
            Volunteer.objects.get_or_create(
                phone=vol["phone"],
                defaults=vol
            )
        self.stdout.write("[OK] Volunteers initialized.")

        # 9. Financial Transactions
        from donations.models import FinancialTransaction
        from datetime import date

        fin_data = [
            {
                "transaction_type": "income",
                "title": "মহাদেবপুর প্রবাসী সমিতি অনুদান",
                "category": "শিক্ষা সহায়তা",
                "amount": 25000.00,
                "payment_method": "Bank Transfer",
                "trx_id": "DBBL98273641",
                "donor_name": "আনিসুর রহমান (প্রবাসী)",
                "date": date(2024, 6, 1),
                "note": "অসহায় শিক্ষার্থীদের বই খাতা ক্রয়ের জন্য।"
            },
            {
                "transaction_type": "income",
                "title": "রক্তদান ক্যাম্প ফান্ড",
                "category": "রক্তদান কর্মসূচি",
                "amount": 12000.00,
                "payment_method": "bKash",
                "trx_id": "BK87634521",
                "donor_name": "শুভাকাঙ্ক্ষীবৃন্দ",
                "date": date(2024, 6, 5),
                "note": "ব্লাড গ্রুপিং কিট কেনা।"
            },
            {
                "transaction_type": "expense",
                "title": "রক্তদান ক্যাম্পের স্বাস্থ্য কিট ও ব্যানার ক্রয়",
                "category": "রক্তদান কর্মসূচি",
                "amount": 4500.00,
                "payment_method": "Cash",
                "trx_id": "EXP-101",
                "donor_name": "মেসার্স নওগাঁ প্যাথলজি",
                "date": date(2024, 6, 6),
                "note": "ব্যানার, তুলা, অ্যালকোহল ও সিরিঞ্জ।"
            },
            {
                "transaction_type": "income",
                "title": "সাধারণ তহবিল অনুদান",
                "category": "সাধারণ তহবিল",
                "amount": 15000.00,
                "payment_method": "Nagad",
                "trx_id": "NG99210088",
                "donor_name": "মো: জহুরুল হক",
                "date": date(2024, 6, 8),
                "note": "সংগঠনের জরুরি ফান্ড।"
            },
            {
                "transaction_type": "expense",
                "title": "দরিদ্র শিক্ষার্থীদের মাঝে খাতা ও কলম বিতরণ",
                "category": "শিক্ষা সহায়তা",
                "amount": 8000.00,
                "payment_method": "Cash",
                "trx_id": "EXP-102",
                "donor_name": "স্টেশন লাইব্রেরি",
                "date": date(2024, 6, 10),
                "note": "৫০ জন শিক্ষার্থীকে খাতা-কলম সেট প্রদান।"
            },
        ]
        for item in fin_data:
            FinancialTransaction.objects.get_or_create(
                title=item["title"],
                defaults=item
            )
        self.stdout.write("[OK] Financial Transactions initialized.")

        self.stdout.write(self.style.SUCCESS("All seed data successfully created!"))
