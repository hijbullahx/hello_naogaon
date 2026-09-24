from .models import EmergencyCategory, EmergencyService

def ensure_default_emergency_services():
    """
    Ensures default national and district emergency service categories and numbers
    exist in the database as requested by Helpline Hello Naogaon.
    Admin can edit, add, or delete any of these anytime from the Admin Panel and Dashboard.
    """
    if EmergencyService.objects.exists():
        return

    data = [
        {
            "category": "জাতীয় জরুরি সেবা",
            "icon": "fas fa-shield-alt",
            "badge_color": "danger",
            "order": 1,
            "services": [
                {
                    "title": "জাতীয় জরুরি হটলাইন",
                    "phone_numbers": "৯৯৯",
                    "subtext": "পুলিশ, ফায়ার সার্ভিস ও অ্যাম্বুলেন্স সেবা",
                    "badge_text": "২৪ ঘণ্টা জরুরি",
                    "icon_class": "fas fa-phone-volume",
                    "is_hotline": True,
                    "order": 1
                },
                {
                    "title": "জরুরি তথ্য ও সরকারি সেবা",
                    "phone_numbers": "৩৩৩",
                    "subtext": "সরকারি সেবা, সামাজিক সমস্যা ও তথ্য বাতায়ন",
                    "badge_text": "টোল ফ্রি",
                    "icon_class": "fas fa-info-circle",
                    "is_hotline": True,
                    "order": 2
                }
            ]
        },
        {
            "category": "প্রশাসনিক ও জেলা কার্যালয়",
            "icon": "fas fa-landmark",
            "badge_color": "primary",
            "order": 2,
            "services": [
                {
                    "title": "জেলা প্রশাসক (ডিসি) অফিস, নওগাঁ",
                    "phone_numbers": "০২৫৮৮৮৮২৫২৩ / ০১৭১৫-২৯২৩৭৭",
                    "subtext": "জেলা প্রশাসন ও ম্যাজিস্ট্রেট কোর্ট, নওগাঁ",
                    "badge_text": "প্রশাসন",
                    "icon_class": "fas fa-building",
                    "is_hotline": False,
                    "order": 1
                },
                {
                    "title": "উপজেলা নির্বাহী অফিসার (ইউএনও) - নওগাঁ সদর",
                    "phone_numbers": "০২৫৮৮৮৮১৪৬৬ / ০১৭৩০-৪৬০০০৬",
                    "subtext": "উপজেলা প্রশাসন কার্যালয়, নওগাঁ সদর",
                    "badge_text": "ইউএনও",
                    "icon_class": "fas fa-landmark",
                    "is_hotline": False,
                    "order": 2
                },
                {
                    "title": "সিভিল সার্জন কার্যালয় (স্বাস্থ্য বিভাগ)",
                    "phone_numbers": "০২৫৮৭৭৪৭৩৯১ / ০১৭১১-৫৭০৭৭৮",
                    "subtext": "স্বাস্থ্য ও পরিবার কল্যাণ বিভাগ, নওগাঁ",
                    "badge_text": "স্বাস্থ্য বিভাগ",
                    "icon_class": "fas fa-clinic-medical",
                    "is_hotline": False,
                    "order": 3
                }
            ]
        },
        {
            "category": "জরুরি সেবা (হাসপাতাল, ফায়ার সার্ভিস ও পুলিশ)",
            "icon": "fas fa-first-aid",
            "badge_color": "danger",
            "order": 3,
            "services": [
                {
                    "title": "নওগাঁ ২৫০ শয্যা বিশিষ্ট সদর হাসপাতাল",
                    "phone_numbers": "০১৭৬৯-৯৬০৬৬০ / ০১৭১৬-৪৯১৮২২",
                    "subtext": "জরুরি বিভাগ, বহির্বিভাগ ও ট্রমা সেন্টার",
                    "badge_text": "২৪ ঘণ্টা জরুরি",
                    "icon_class": "fas fa-hospital",
                    "is_hotline": False,
                    "order": 1
                },
                {
                    "title": "নওগাঁ ফায়ার সার্ভিস স্টেশন (কন্ট্রোল রুম)",
                    "phone_numbers": "০১৭৩০-০০০২৪২৬",
                    "subtext": "অগ্নি নির্বাপণ ও উদ্ধার কার্যক্রম কন্ট্রোল রুম",
                    "badge_text": "ফায়ার সার্ভিস",
                    "icon_class": "fas fa-fire-extinguisher",
                    "is_hotline": False,
                    "order": 2
                },
                {
                    "title": "নওগাঁ জেলা পুলিশ কন্ট্রোল রুম",
                    "phone_numbers": "০১৭৬৯-৬৯০০৩৩ / ০১৭১৩-৩৭৩৮২৮",
                    "subtext": "জেলা পুলিশ নিরাপত্তা ও জরুরি কন্ট্রোল ডেস্ক",
                    "badge_text": "পুলিশ কন্ট্রোল",
                    "icon_class": "fas fa-shield-alt",
                    "is_hotline": False,
                    "order": 3
                },
                {
                    "title": "নওগাঁ সদর মডেল থানা (ডিউটি অফিসার)",
                    "phone_numbers": "০১৭৬৯-৬৯১০৬৭",
                    "subtext": "সদর থানা ডিউটি অফিসার ও সাধারণ ডায়েরি",
                    "badge_text": "মডেল থানা",
                    "icon_class": "fas fa-user-shield",
                    "is_hotline": False,
                    "order": 4
                },
                {
                    "title": "ইউনিয়ন পরিষদ সেবা",
                    "phone_numbers": "০১৫৫৩-২৭৭৩৭৬",
                    "subtext": "ইউনিয়ন পরিষদ নাগরিক সনদ ও সেবা সহায়তা",
                    "badge_text": "নাগরিক সেবা",
                    "icon_class": "fas fa-users",
                    "is_hotline": False,
                    "order": 5
                },
                {
                    "title": "উচ্চশিক্ষা ও বিশ্ববিদ্যালয় ভর্তি তথ্য",
                    "phone_numbers": "০১৯১৬-৩১৪৩১৫",
                    "subtext": "বিশ্ববিদ্যালয় ভর্তি, ক্যারিয়ার ও শিক্ষা সহায়তা",
                    "badge_text": "শিক্ষা তথ্য",
                    "icon_class": "fas fa-graduation-cap",
                    "is_hotline": False,
                    "order": 6
                }
            ]
        },
        {
            "category": "অ্যাম্বুলেন্স ও রক্তদান",
            "icon": "fas fa-ambulance",
            "badge_color": "danger",
            "order": 4,
            "services": [
                {
                    "title": "সদর হাসপাতাল অ্যাম্বুলেন্স",
                    "phone_numbers": "০১৭৬৯-৯৬০৬৬০",
                    "subtext": "সরকারি হাসপাতাল জরুরি রোগী পরিবহন",
                    "badge_text": "অ্যাম্বুলেন্স",
                    "icon_class": "fas fa-ambulance",
                    "is_hotline": False,
                    "order": 1
                },
                {
                    "title": "রেড ক্রিসেন্ট অ্যাম্বুলেন্স সেবা",
                    "phone_numbers": "০১৭৩০-০৩৪১৬৯৫",
                    "subtext": "বাংলাদেশ রেড ক্রিসেন্ট সোসাইটি, নওগাঁ ইউনিট",
                    "badge_text": "রেড ক্রিসেন্ট",
                    "icon_class": "fas fa-ambulance",
                    "is_hotline": False,
                    "order": 2
                },
                {
                    "title": "হেল্পলাইন হ্যালো নওগাঁ (রক্তদান)",
                    "phone_numbers": "০১৯১৬-৩১৪৩১৫",
                    "subtext": "জরুরি রক্তের প্রয়োজনে তাৎক্ষণিক স্বেচ্ছাসেবী সহায়তা",
                    "badge_text": "ব্লাড হেল্পলাইন",
                    "icon_class": "fas fa-hand-holding-heart",
                    "is_hotline": False,
                    "order": 3
                }
            ]
        },
        {
            "category": "সরকারি ও আইনি দপ্তর",
            "icon": "fas fa-balance-scale",
            "badge_color": "info",
            "order": 5,
            "services": [
                {
                    "title": "আঞ্চলিক পাসপোর্ট অফিস (নওগাঁ)",
                    "phone_numbers": "০১৭৩৩-৩৯৩৩৮৭ / ০১৭৩৩-৩৯৩৩৪৩",
                    "subtext": "ই-পাসপোর্ট আবেদন, ডেলিভারি ও তথ্য ডেস্ক",
                    "badge_text": "পাসপোর্ট অফিস",
                    "icon_class": "fas fa-passport",
                    "is_hotline": False,
                    "order": 1
                },
                {
                    "title": "উপপরিচালকের কার্যালয় (কৃষি সম্প্রসারণ অধিদপ্তর)",
                    "phone_numbers": "০২৫৮৭৭৩৭৩৯৩",
                    "subtext": "কৃষি পরামর্শ ও কৃষক সেবা বাতায়ন",
                    "badge_text": "কৃষি দপ্তর",
                    "icon_class": "fas fa-seedling",
                    "is_hotline": False,
                    "order": 2
                },
                {
                    "title": "জেলা জজ কোর্ট / আদালত (তথ্য কেন্দ্র)",
                    "phone_numbers": "০৭৪১-৬২২০৫",
                    "subtext": "আইনি সেবা, মামলা তথ্য ও বিচারিক সহায়তা কেন্দ্র",
                    "badge_text": "আদালত তথ্য",
                    "icon_class": "fas fa-balance-scale",
                    "is_hotline": False,
                    "order": 3
                },
                {
                    "title": "নওগাঁ বিদ্যুৎ অভিযোগ কেন্দ্র (নেসকো)",
                    "phone_numbers": "০২৫৮৮৮৮১৯৫৮",
                    "subtext": "বিদ্যুৎ বিভ্রাট ও জরুরি অভিযোগ কেন্দ্র (হটলাইন: ১৬৯৯৯)",
                    "badge_text": "হটলাইন: ১৬৯৯৯",
                    "icon_class": "fas fa-bolt",
                    "is_hotline": False,
                    "order": 4
                }
            ]
        },
        {
            "category": "পরিবহন (নওগাঁ টু ঢাকা বাস কাউন্টার)",
            "icon": "fas fa-bus",
            "badge_color": "success",
            "order": 6,
            "services": [
                {
                    "title": "শাহ ফতেহ আলী (নওগাঁ কাউন্টার)",
                    "phone_numbers": "০১৩২৪-৯৪৬৫৫১ / ০১৭১১-২৮৪৭২৯",
                    "subtext": "নওগাঁ টু ঢাকা নিয়মিত ও এসি বাস সার্ভিস",
                    "badge_text": "বাস কাউন্টার",
                    "icon_class": "fas fa-bus-alt",
                    "is_hotline": False,
                    "order": 1
                },
                {
                    "title": "শ্যামলী পরিবহন (নওগাঁ কাউন্টার)",
                    "phone_numbers": "০৭৪১-৬২৯০২ / ০১৭২৭-১৯৯৮৮৮",
                    "subtext": "নওগাঁ টু ঢাকা আরামদায়ক বিলাসবহুল বাস সার্ভিস",
                    "badge_text": "বাস কাউন্টার",
                    "icon_class": "fas fa-bus",
                    "is_hotline": False,
                    "order": 2
                }
            ]
        },
        {
            "category": "ফার্মেসি, বই, হোটেল",
            "icon": "fas fa-store",
            "badge_color": "warning",
            "order": 7,
            "services": [
                {
                    "title": "আল রাজি ফার্মেসি (সরস্বতীপুর)",
                    "phone_numbers": "০১৭৪৫-১৩২৫৯৩",
                    "subtext": "ঔষধ, প্রাথমিক জরুরি চিকিৎসা ও স্বাস্থ্যপণ্য",
                    "badge_text": "ফার্মেসি",
                    "icon_class": "fas fa-pills",
                    "is_hotline": False,
                    "order": 1
                },
                {
                    "title": "কথা কলি লাইব্রেরি (নওগাঁ সদর)",
                    "phone_numbers": "০১৭১৬-৫২৬০০৯",
                    "subtext": "পাঠ্যপুস্তক, সৃজনশীল বই ও স্টেশনারি সামগ্রী",
                    "badge_text": "লাইব্রেরি",
                    "icon_class": "fas fa-book",
                    "is_hotline": False,
                    "order": 2
                },
                {
                    "title": "হোটেল অবকাশ",
                    "phone_numbers": "০১৭২৭-৬৬৪৭৯৯",
                    "subtext": "নিরাপদ ও মানসম্মত আবাসিক হোটেল",
                    "badge_text": "আবাসিক",
                    "icon_class": "fas fa-hotel",
                    "is_hotline": False,
                    "order": 3
                }
            ]
        }
    ]

    for cat_data in data:
        services = cat_data.pop("services")
        cat_obj, _ = EmergencyCategory.objects.get_or_create(
            name=cat_data["category"],
            defaults={
                "icon": cat_data["icon"],
                "badge_color": cat_data["badge_color"],
                "order": cat_data["order"],
                "is_active": True
            }
        )
        for s_data in services:
            EmergencyService.objects.get_or_create(
                category=cat_obj,
                title=s_data["title"],
                defaults={
                    "phone_numbers": s_data["phone_numbers"],
                    "subtext": s_data.get("subtext", ""),
                    "badge_text": s_data.get("badge_text", ""),
                    "icon_class": s_data.get("icon_class", "fas fa-phone-alt"),
                    "is_hotline": s_data.get("is_hotline", False),
                    "order": s_data.get("order", 0),
                    "is_active": True
                }
            )
