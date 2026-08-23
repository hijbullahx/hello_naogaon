/**
 * Helpline Hello Naogaon - Bilingual i18n System
 * Default: Bengali (bn) | Toggle: English (en)
 * Uses data-i18n="key" attributes to translate static text
 * Uses data-i18n-attr="attr:key" for attributes like placeholder, title, etc.
 */

const HN_TRANSLATIONS = {

  /* ─────────────────── NAVBAR ─────────────────── */
  "nav.home":             { bn: "হোম",              en: "Home" },
  "nav.about":            { bn: "আমাদের সম্পর্কে",  en: "About Us" },
  "nav.programs":         { bn: "কার্যক্রম",          en: "Programs" },
  "nav.blood_donors":     { bn: "রক্তদাতা",           en: "Blood Donors" },
  "nav.volunteers":       { bn: "স্বেচ্ছাসেবক",      en: "Volunteer" },
  "nav.news":             { bn: "সংবাদ",             en: "News" },
  "nav.gallery":          { bn: "গ্যালারি",           en: "Gallery" },
  "nav.donate":           { bn: "আর্থিক সহায়তা",    en: "Donate" },
  "nav.login":            { bn: "লগইন",              en: "Login" },
  "nav.logout":           { bn: "লগআউট",            en: "Logout" },
  "nav.dashboard":        { bn: "অ্যাডমিন ড্যাশবোর্ড", en: "Admin Dashboard" },

  /* ─────────────────── BRAND / TAGLINE ─────────────────── */
  "brand.tagline":        { bn: "মানব সেবায় আমরা",      en: "Serving Humanity" },
  "brand.subtagline":     { bn: "একটি অরাজনৈতিক সংগঠন", en: "A Non-Political Organisation" },

  /* ─────────────────── FOOTER ─────────────────── */
  "footer.quick_links":   { bn: "দ্রুত লিঙ্ক",          en: "Quick Links" },
  "footer.contact":       { bn: "যোগাযোগ",              en: "Contact" },
  "footer.location":      { bn: "আমাদের অবস্থান",       en: "Our Location" },
  "footer.home":          { bn: "হোম",                  en: "Home" },
  "footer.about":         { bn: "আমাদের সম্পর্কে",      en: "About Us" },
  "footer.programs":      { bn: "কার্যক্রম",              en: "Programs" },
  "footer.blood_donors":  { bn: "রক্তদাতা",              en: "Blood Donors" },
  "footer.volunteers":    { bn: "স্বেচ্ছাসেবক",          en: "Volunteer" },
  "footer.donate":        { bn: "আর্থিক সহায়তা",        en: "Donate" },

  /* ─────────────────── HOME PAGE ─────────────────── */
  "home.hero.programs_btn":    { bn: "আমাদের কার্যক্রম",  en: "Our Programs" },
  "home.hero.blood_btn":       { bn: "রক্তদাতা হন",       en: "Become a Donor" },
  "home.about.heading":        { bn: "আমাদের সম্পর্কে",   en: "About Us" },
  "home.about.learn_more":     { bn: "বিস্তারিত জানুন",   en: "Learn More" },
  "home.programs.heading":     { bn: "আমাদের কার্যক্রম",  en: "Our Programs" },
  "home.programs.detail":      { bn: "বিস্তারিত",          en: "Details" },
  "home.programs.donate_btn":  { bn: "সহায়তা দিন",        en: "Donate Now" },
  "home.programs.need_label":  { bn: "আর্থিক প্রয়োজন:",   en: "Funding Need:" },
  "home.programs.raised":      { bn: "সংগৃহীত:",           en: "Raised:" },
  "home.programs.target":      { bn: "লক্ষ্যমাত্রা:",      en: "Target:" },
  "home.news.heading":         { bn: "সাম্প্রতিক সংবাদ",   en: "Latest News" },
  "home.news.view_all":        { bn: "সব দেখুন",           en: "View All" },
  "home.donate.heading":       { bn: "আর্থিক সহায়তা করুন", en: "Make a Donation" },
  "home.donate.detail_btn":    { bn: "বিস্তারিত ও ফরম",    en: "Details & Form" },
  "home.donate.subtitle":      { bn: "আপনার সামান্য আর্থিক সহায়তা আমাদের বড় কাজে মানুষের পাশে দাঁড়াতে সহায়তা করবে।",
                                  en: "Your small financial contribution helps us stand by people in their greatest need." },
  "home.bank.heading":         { bn: "ব্যাংক একাউন্ট",    en: "Bank Account" },

  /* ─── home fallback stat titles ─── */
  "stat.blood":           { bn: "রক্তদান",              en: "Blood Donations" },
  "stat.families":        { bn: "পরিবারকে সহায়তা",      en: "Families Helped" },
  "stat.students":        { bn: "শিক্ষার্থী সহায়তা",    en: "Students Supported" },
  "stat.volunteers":      { bn: "স্বেচ্ছাসেবক",          en: "Volunteers" },
  "stat.programs":        { bn: "সামাজিক কর্মসূচি",      en: "Social Programs" },

  /* ─── home fallback program titles ─── */
  "prog.blood_service":   { bn: "রক্তদান সেবা",          en: "Blood Donation Service" },
  "prog.blood_desc":      { bn: "জরুরি রক্তদাতা খুঁজে দেয়া ও রক্তদাতা ডাটাবেস পরিচালনা।",
                             en: "Finding emergency blood donors and managing donor database." },
  "prog.edu":             { bn: "শিক্ষা সহায়তা",         en: "Education Support" },
  "prog.edu_desc":        { bn: "দরিদ্র শিক্ষার্থীদের বই, শিক্ষা উপকরণ ও বৃত্তি প্রদান।",
                             en: "Providing books, educational materials and scholarships to poor students." },
  "prog.human":           { bn: "মানবিক সহায়তা",         en: "Humanitarian Aid" },
  "prog.human_desc":      { bn: "অসহায় ও দুঃস্থ পরিবারের পাশে দাঁড়ানো।",
                             en: "Standing by helpless and distressed families." },
  "prog.env":             { bn: "পরিবেশ কর্মসূচি",        en: "Environment Program" },
  "prog.env_desc":        { bn: "বৃক্ষরোপণ ও পরিবেশ সচেতনতা বৃদ্ধি।",
                             en: "Tree plantation and environmental awareness campaigns." },
  "prog.disaster":        { bn: "দুর্যোগ সহায়তা",         en: "Disaster Relief" },
  "prog.disaster_desc":   { bn: "বন্যা, ঝড় ও দুর্ঘটনায় জরুরি সহায়তা প্রদান।",
                             en: "Emergency assistance during floods, storms and accidents." },

  /* ─── home modal / donation form ─── */
  "modal.donate_title":   { bn: "আর্থিক সহায়তা প্রদান",       en: "Make a Donation" },
  "modal.identity_q":     { bn: "আপনি কীভাবে সহায়তা প্রদান করবেন?", en: "How would you like to donate?" },
  "modal.general_donor":  { bn: "সাধারণ শুভাকাঙ্ক্ষী",         en: "General Donor" },
  "modal.member_donor":   { bn: "সংস্থার সদস্য (Member)",       en: "Organisation Member" },
  "modal.member_id":      { bn: "সদস্য আইডি (Member ID)",       en: "Member ID" },
  "modal.verify_btn":     { bn: "যাচাই",                        en: "Verify" },
  "modal.member_hint":    { bn: "আইডি দিলে নাম ও মোবাইল স্বয়ংক্রিয়ভাবে লোড হবে।",
                             en: "Name and mobile will auto-load when you enter the ID." },
  "modal.your_name":      { bn: "আপনার নাম",    en: "Your Name" },
  "modal.mobile":         { bn: "মোবাইল নম্বর", en: "Mobile Number" },
  "modal.amount":         { bn: "সহায়তার পরিমাণ (টাকা)", en: "Donation Amount (BDT)" },
  "modal.note":           { bn: "মন্তব্য / দোয়া (ঐচ্ছিক)", en: "Note / Message (Optional)" },
  "modal.cancel":         { bn: "বাতিল",         en: "Cancel" },
  "modal.pay_btn":        { bn: "পেমেন্টে এগিয়ে যান", en: "Proceed to Payment" },

  /* ─────────────────── ABOUT PAGE ─────────────────── */
  "about.title":          { bn: "আমাদের সম্পর্কে", en: "About Us" },
  "about.mission":        { bn: "আমাদের লক্ষ্য",   en: "Our Mission" },
  "about.vision":         { bn: "আমাদের রূপকল্প",  en: "Our Vision" },
  "about.team":           { bn: "আমাদের দল",       en: "Our Team" },
  "about.team_empty":     { bn: "দলের সদস্যদের তথ্য শীঘ্রই যোগ করা হবে।",
                             en: "Team member information will be added soon." },

  /* ─────────────────── PROGRAMS PAGE ─────────────────── */
  "programs.title":       { bn: "আমাদের কার্যক্রমসমূহ",    en: "Our Programs" },
  "programs.subtitle":    { bn: "হেল্পলাইন হ্যালো নওগাঁর সকল সামাজিক ও মানবিক কার্যক্রম",
                             en: "All social and humanitarian initiatives of Helpline Hello Naogaon" },
  "programs.detail":      { bn: "বিস্তারিত দেখুন",          en: "View Details" },
  "programs.donate":      { bn: "সহায়তা দিন",               en: "Donate" },
  "programs.empty":       { bn: "এখনো কোনো কার্যক্রম যোগ করা হয়নি।",
                             en: "No programs have been added yet." },
  "programs.raised":      { bn: "সংগৃহীত",                  en: "Raised" },
  "programs.target":      { bn: "লক্ষ্যমাত্রা",             en: "Target" },
  "programs.ongoing":     { bn: "চলমান",                    en: "Ongoing" },
  "programs.completed":   { bn: "সম্পন্ন",                  en: "Completed" },

  /* ─────────────────── NEWS PAGE ─────────────────── */
  "news.title":           { bn: "সংবাদ ও ঘোষণা",            en: "News & Announcements" },
  "news.read_more":       { bn: "বিস্তারিত পড়ুন",           en: "Read More" },
  "news.back":            { bn: "সংবাদ তালিকায় ফিরুন",       en: "Back to News" },
  "news.empty":           { bn: "এখনো কোনো সংবাদ প্রকাশিত হয়নি।",
                             en: "No news has been published yet." },
  "news.published_on":    { bn: "প্রকাশিত:",                 en: "Published:" },

  /* ─────────────────── GALLERY PAGE ─────────────────── */
  "gallery.title":        { bn: "আমাদের গ্যালারি",           en: "Our Gallery" },
  "gallery.subtitle":     { bn: "হেল্পলাইন হ্যালো নওগাঁর বিভিন্ন কার্যক্রমের ছবি",
                             en: "Photos from various Helpline Hello Naogaon activities" },
  "gallery.empty":        { bn: "গ্যালারিতে এখনো কোনো ছবি নেই।",
                             en: "No photos in the gallery yet." },

  /* ─────────────────── BLOOD DONORS PAGE ─────────────────── */
  "blood.title":          { bn: "জরুরি রক্তদাতা ডাটাবেস",    en: "Emergency Blood Donor Database" },
  "blood.subtitle":       { bn: "মুমূর্ষু রোগীর প্রয়োজনে স্বেচ্ছাসেবী রক্তদাতাদের সরাসরি তালিকা ও সার্বক্ষণিক সহায়তা",
                             en: "Direct list of volunteer blood donors for critical patients and round-the-clock support" },
  "blood.register_btn":   { bn: "রক্তদাতা হিসেবে নাম লিখান",  en: "Register as Blood Donor" },
  "blood.search_label":   { bn: "অনুসন্ধান",                  en: "Search" },
  "blood.group_label":    { bn: "রক্তের গ্রুপ",               en: "Blood Group" },
  "blood.all":            { bn: "সকল",                        en: "All" },
  "blood.division":       { bn: "বিভাগ ফিল্টার",              en: "Division Filter" },
  "blood.district":       { bn: "জেলা ফিল্টার",               en: "District Filter" },
  "blood.thana":          { bn: "থানা / উপজেলা ফিল্টার",       en: "Thana / Upazila Filter" },
  "blood.filter_btn":     { bn: "ফিল্টার",                    en: "Filter" },
  "blood.list_title":     { bn: "রক্তদাতাদের তালিকা",          en: "Blood Donor List" },
  "blood.add_btn":        { bn: "নতুন রক্তদাতা যুক্ত হন",      en: "Join as New Donor" },
  "blood.contact":        { bn: "যোগাযোগ করুন",               en: "Contact" },
  "blood.available":      { bn: "সক্রিয়",                     en: "Active" },
  "blood.unavailable":    { bn: "অনুপলব্ধ",                  en: "Unavailable" },
  "blood.last_donated":   { bn: "সর্বশেষ দান:",               en: "Last Donated:" },
  "blood.location":       { bn: "অবস্থান:",                   en: "Location:" },
  "blood.no_results":     { bn: "কোনো রক্তদাতা পাওয়া যায়নি।",
                             en: "No blood donors found." },
  "blood.all_division":   { bn: "সকল বিভাগ",                  en: "All Divisions" },
  "blood.all_district":   { bn: "সকল জেলা",                   en: "All Districts" },
  "blood.all_upazila":    { bn: "সকল থানা / উপজেলা",          en: "All Thanas / Upazilas" },

  /* ─────────────────── VOLUNTEER / REGISTRATION ─────────────────── */
  "vol.title":            { bn: "স্বেচ্ছাসেবক নিবন্ধন",      en: "Volunteer Registration" },
  "vol.submit":           { bn: "নিবন্ধন করুন",               en: "Register" },
  "vol.success":          { bn: "নিবন্ধন সফল হয়েছে!",        en: "Registration Successful!" },
  "vol.name":             { bn: "পূর্ণ নাম",                  en: "Full Name" },
  "vol.phone":            { bn: "মোবাইল নম্বর",               en: "Mobile Number" },
  "vol.email":            { bn: "ইমেইল (ঐচ্ছিক)",             en: "Email (Optional)" },
  "vol.blood_group":      { bn: "রক্তের গ্রুপ",               en: "Blood Group" },
  "vol.address":          { bn: "ঠিকানা",                     en: "Address" },
  "vol.contribution":     { bn: "মাসিক আর্থিক অবদান (ঐচ্ছিক)", en: "Monthly Contribution (Optional)" },

  /* ─────────────────── DONATE PAGE ─────────────────── */
  "donate.title":         { bn: "আর্থিক সহায়তা করুন",        en: "Make a Donation" },
  "donate.bank":          { bn: "ব্যাংক একাউন্টে পাঠান",      en: "Send to Bank Account" },
  "donate.online":        { bn: "অনলাইনে দান করুন",           en: "Donate Online" },
  "donate.amount":        { bn: "পরিমাণ (টাকা)",              en: "Amount (BDT)" },
  "donate.name":          { bn: "আপনার নাম",                  en: "Your Name" },
  "donate.mobile":        { bn: "মোবাইল নম্বর",               en: "Mobile Number" },
  "donate.pay":           { bn: "পেমেন্ট করুন",               en: "Pay Now" },

  /* ─────────────────── LOGIN / AUTH ─────────────────── */
  "auth.login_title":     { bn: "লগইন",                       en: "Login" },
  "auth.username":        { bn: "ইউজারনেম বা ইমেইল",           en: "Username or Email" },
  "auth.password":        { bn: "পাসওয়ার্ড",                  en: "Password" },
  "auth.login_btn":       { bn: "লগইন করুন",                  en: "Sign In" },
  "auth.forgot":          { bn: "পাসওয়ার্ড ভুলে গেছেন?",      en: "Forgot Password?" },
};

/* ─────────────────────────────────────────────────────────
   CORE ENGINE
   ───────────────────────────────────────────────────────── */
const HN_I18N = {
  currentLang: localStorage.getItem('hn_lang') || 'bn',

  t(key) {
    const entry = HN_TRANSLATIONS[key];
    if (!entry) return null;
    return entry[this.currentLang] || entry['bn'];
  },

  applyAll() {
    const lang = this.currentLang;
    // 1. Translate all [data-i18n] text elements
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const val = this.t(key);
      if (val !== null) el.textContent = val;
    });
    // 2. Translate [data-i18n-html] (innerHTML — safe only for known content)
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
      const key = el.getAttribute('data-i18n-html');
      const val = this.t(key);
      if (val !== null) el.innerHTML = val;
    });
    // 3. Translate attributes e.g. data-i18n-attr="placeholder:key,title:key2"
    document.querySelectorAll('[data-i18n-attr]').forEach(el => {
      const pairs = el.getAttribute('data-i18n-attr').split(',');
      pairs.forEach(pair => {
        const [attr, key] = pair.trim().split(':');
        const val = this.t(key);
        if (val !== null) el.setAttribute(attr.trim(), val);
      });
    });
    // 4. Update <html lang>
    document.documentElement.lang = lang === 'bn' ? 'bn-BD' : 'en';
    // 5. Update toggle button appearance
    const btn = document.getElementById('hn-lang-toggle');
    if (btn) {
      btn.setAttribute('data-lang', lang);
      btn.querySelector('.hn-lang-bn').style.display = lang === 'bn' ? 'none' : 'inline';
      btn.querySelector('.hn-lang-en').style.display = lang === 'en' ? 'none' : 'inline';
      btn.querySelector('.hn-lang-active').textContent = lang === 'bn' ? 'বাং' : 'EN';
    }
  },

  toggle() {
    this.currentLang = this.currentLang === 'bn' ? 'en' : 'bn';
    localStorage.setItem('hn_lang', this.currentLang);
    this.applyAll();
  },

  init() {
    // Run on DOM ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.applyAll());
    } else {
      this.applyAll();
    }
  }
};

HN_I18N.init();
