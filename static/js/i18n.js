/**
 * Helpline Hello Naogaon — Hybrid Translation Engine
 * Strategy: Local Dictionary (instant) → Local Cache → Neural API (dynamic content)
 * Covers: All dashboard, navbar, footer, forms, tables, buttons, and admin-written content.
 */

// ════════════════════════════════════════════════════════════
// 1. COMPREHENSIVE LOCAL DICTIONARY (instant, no network needed)
// ════════════════════════════════════════════════════════════
const HN_DICT = {
  // ── Admin Panel / Dashboard ──────────────────────────────
  "প্রধান অ্যাডমিন কন্ট্রোল প্যানেল": "Main Admin Control Panel",
  "পরিচালনা পর্ষদ ড্যাশবোর্ড": "Executive Board Dashboard",
  "অ্যাডমিন ড্যাশবোর্ড": "Admin Dashboard",
  "সভাপতি ড্যাশবোর্ড": "President Dashboard",
  "সাধারণ সম্পাদক ড্যাশবোর্ড": "General Secretary Dashboard",
  "কোষাধ্যক্ষ ড্যাশবোর্ড": "Treasurer Dashboard",
  "সাধারণ পরিষদ সদস্য ড্যাশবোর্ড": "General Council Dashboard",
  "লগইন করেছেন:": "Logged in:",
  "প্রধান অ্যাডমিন": "Super Admin",
  "Super Admin": "Super Admin",
  "ফুল অ্যাডমিন অ্যাক্সেস": "Full Admin Access",
  "পর্যবেক্ষণ মোড (View Only)": "Observation Mode (View Only)",
  "হিসাব বিবরণী (View Only)": "Financial Statement (View Only)",
  "অর্থায়ন নিয়ন্ত্রণ অনুমোদিত": "Finance Control Authorized",
  "মূল ওয়েবসাইট": "Main Website",
  "ওয়েবসাইট ভিজিট": "Visit Website",
  "ব্যাকএন্ড": "Backend",
  "লগআউট": "Logout",
  "কন্ট্রোল প্যানেল": "Control Panel",

  // ── Sidebar Menu ─────────────────────────────────────────
  "হোম পেজ সেকশন": "Home Page Sections",
  "হোম পেজ": "Home Page",
  "হোম": "Home",
  "কার্যক্রম": "Programs",
  "রক্তদাতা": "Blood Donors",
  "রক্তদাতা ডাটাবেস": "Blood Donor Database",
  "স্বেচ্ছাসেবক ও টিম": "Volunteers & Team",
  "স্বেচ্ছাসেবক": "Volunteers",
  "সংবাদ": "News",
  "সংবাদ ও প্রেস রিলিজ প্রকাশনা": "News & Press Release",
  "অর্থায়ন ও আয়-ব্যয়": "Finance & Accounts",
  "অর্থায়ন ও আয়-ব্যয় বিবরণী": "Finance & Balance Sheet",
  "অর্থায়ন ও আয়-ব্যয় নিয়ন্ত্রণ": "Finance & Account Management",
  "অনুদান ও ব্যাংক": "Donations & Bank",
  "গ্যালারি": "Gallery",
  "আমার আর্থিক সহায়তা ও অনুদান": "My Contributions & Donations",
  "আমাদের সম্পর্কে": "About Us",

  // ── Team Members / Volunteers Section ───────────────────
  "টিম মেম্বার ও পরিচালনা পর্ষদ (Team Members": "Team Members & Executive Committee",
  "টিম মেম্বার ও পরিচালনা পর্ষদ": "Team Members & Executive Committee",
  "স্বেচ্ছাসেবক ডাটাবেস": "Volunteer Database",
  "কোনো টিম মেম্বার তথ্য যোগ করা হয়নি।": "No team member information has been added.",
  "নতুন টিম মেম্বার যোগ করুন": "Add New Team Member",
  "সদস্যের নাম ও আইডি": "Member Name & ID",
  "পদবী / ভূমিকা (Role)": "Designation / Role",
  "যোগাযোগ (ফোন ও ইমেইল)": "Contact (Phone & Email)",
  "লগইন ইউজার": "Login User",
  "অ্যাকশন": "Action",
  "ঠিকানা": "Address",
  "ছবি": "Photo",

  // ── Table Headers ────────────────────────────────────────
  "#": "#",
  "স্বেচ্ছাসেবকের নাম": "Volunteer Name",
  "ইমেইল": "Email",
  "ফোন নম্বর": "Phone Number",
  "আবেদনের তারিখ": "Application Date",
  "শিরোনাম": "Title",
  "প্রকাশের তারিখ": "Published Date",
  "তারিখ ও সময়": "Date & Time",
  "তারিখ": "Date",
  "খাত / প্রোগ্রাম": "Sector / Program",
  "খাতের নাম / বিবরণ": "Sector / Description",
  "ক্যাটাগরি": "Category",
  "দাতা / গ্রহণকারী": "Donor / Recipient",
  "পেমেন্ট মাধ্যম": "Payment Method",
  "পেমেন্ট মাধ্যম & Trx ID": "Payment Method & Trx ID",

  // ── Roles ────────────────────────────────────────────────
  "সভাপতি": "President",
  "সাধারণ সম্পাদক": "General Secretary",
  "কোষাধ্যক্ষ": "Treasurer",
  "সাধারণ পরিষদ সদস্য": "General Council Member",
  "পরিচালনা পর্ষদ": "Executive Committee",
  "পরিচালনা পর্ষদ ও ডাটাবেস": "Executive Committee & Database",
  "হেল্পলাইন হ্যালো নওগাঁ — পরিচালনা পর্ষদ ড্যাশবোর্ড": "Helpline Hello Naogaon — Executive Board Dashboard",

  // ── Finance ──────────────────────────────────────────────
  "তহবিল ও আয়-ব্যয়ের হিসাব খাতা": "Financial Ledger & Fund Accounts",
  "মোট আয়": "Total Income",
  "মোট ব্যয়": "Total Expense",
  "বর্তমান তহবিল ব্যালেন্স": "Current Fund Balance",
  "মোট অনুদানের পরিমাণ": "Total Donations Received",
  "অনুমোদিত অনুদানের সংখ্যা": "Approved Donations Count",
  "মোট সদস্য": "Total Members",
  "মোট রক্তদাতা": "Total Blood Donors",
  "তহবিল স্থিতি": "Fund Balance",
  "আয়": "Income",
  "ব্যয়": "Expense",
  "নতুন আয়/অনুদান লিখুন": "Add New Income/Donation",
  "নতুন ব্যয়/খরচ লিখুন": "Add New Expense",
  "এক্সেল রিপোর্ট ডাউনলোড": "Download Excel Report",
  "হিসাব বিবরণী প্রিন্ট করুন": "Print Statement",

  // ── Buttons & Actions ────────────────────────────────────
  "সংরক্ষণ করুন": "Save",
  "সম্পাদনা করুন": "Edit",
  "সম্পাদনা": "Edit",
  "মুছে ফেলুন": "Delete",
  "যুক্ত করুন": "Add",
  "যাচাই করুন": "Verify",
  "যাচাই": "Verify",
  "আপলোড করুন": "Upload",
  "আপলোড": "Upload",
  "বাতিল": "Cancel",
  "বিস্তারিত": "Details",
  "বিস্তারিত দেখুন": "View Details",
  "বিস্তারিত জানুন": "Learn More",
  "বিস্তারিত পড়ুন": "Read More",
  "প্রকাশ করুন": "Publish",
  "অনুমোদন করুন": "Approve",
  "প্রত্যাখ্যান করুন": "Reject",
  "পরিবর্তন সংরক্ষণ করুন": "Save Changes",
  "আপডেট করুন": "Update",
  "নতুন যোগ করুন": "Add New",
  "ফিল্টার করুন": "Filter",
  "অনুসন্ধান করুন": "Search",
  "অনুসন্ধান": "Search",
  "ফিল্টার": "Filter",
  "পেমেন্ট করুন": "Pay Now",
  "পেমেন্টে এগিয়ে যান": "Proceed to Payment",
  "সহায়তা দিন": "Donate Now",
  "এখনই সহায়তা পাঠান": "Send Support Now",
  "নিবন্ধন করুন": "Register",
  "যোগাযোগ করুন": "Contact",

  // ── Status Labels ────────────────────────────────────────
  "অনুমোদিত": "Approved",
  "অপেক্ষমাণ": "Pending",
  "ব্যর্থ": "Failed",
  "সক্রিয়": "Active",
  "নিষ্ক্রিয়": "Inactive",
  "চলমান": "Ongoing",
  "সম্পন্ন": "Completed",
  "প্রকাশিত": "Published",
  "অপ্রকাশিত": "Unpublished",
  "অনুপলব্ধ": "Unavailable",
  "হ্যাঁ": "Yes",
  "না": "No",
  "লিঙ্ক নেই": "No link",
  "সংযুক্ত নেই": "Not linked",
  "কোনো তথ্য নেই": "No data",
  "কোনো তথ্য পাওয়া যায়নি।": "No information found.",
  "কোনো রক্তদাতা পাওয়া যায়নি।": "No blood donors found.",
  "কোনো সংবাদ পাওয়া যায়নি।": "No news found.",
  "কোনো ছবি নেই।": "No photo available.",
  "কোনো তহবিল তথ্য পাওয়া যায়নি।": "No fund data found.",
  "জন": "members",
  "জন)": "members)",

  // ── Forms & Inputs ───────────────────────────────────────
  "পূর্ণ নাম": "Full Name",
  "আপনার নাম": "Your Name",
  "মোবাইল নম্বর": "Mobile Number",
  "ফোন নম্বর": "Phone Number",
  "ইমেইল এড্রেস": "Email Address",
  "ইমেইল ঠিকানা": "Email Address",
  "পেশা": "Occupation",
  "বয়স": "Age",
  "লিঙ্গ": "Gender",
  "পুরুষ": "Male",
  "মহিলা": "Female",
  "পাসওয়ার্ড": "Password",
  "ইউজারনেম": "Username",
  "নতুন পাসওয়ার্ড": "New Password",
  "পাসওয়ার্ড নিশ্চিত করুন": "Confirm Password",
  "সদস্য আইডি": "Member ID",
  "সদস্য আইডি (Member ID)": "Member ID",
  "পরিমাণ (টাকা)": "Amount (BDT)",
  "সহায়তার পরিমাণ (টাকা)": "Donation Amount (BDT)",
  "মন্তব্য / বিবরণ": "Note / Description",
  "মন্তব্য": "Note",

  // ── Hero & Branding ──────────────────────────────────────
  "হেল্পলাইন হ্যালো নওগাঁ": "Helpline Hello Naogaon",
  "মানবতার পাশে, নওগাঁর প্রতিটি মানুষের জন্য": "Standing for humanity, for every person in Naogaon",
  "মানব সেবায় আমরা": "Serving Humanity",
  "একটি অরাজনৈতিক সংগঠন": "A Non-Political Organisation",
  "আমরা একটি অরাজনৈতিক, অলাভজনক ও স্বেচ্ছাসেবী সংগঠন, যা সমাজের অসহায় মানুষের পাশে দাঁড়াতে প্রতিশ্রুতিবদ্ধ।":
    "We are a non-political, non-profit voluntary organisation committed to standing by the underprivileged.",
  "আসুন, আমরা সবাই মিলে একটি মানবিক ও সুন্দর সমাজ গড়ে তুলি":
    "Let us all join hands to build a compassionate and beautiful society",

  // ── Navbar ───────────────────────────────────────────────
  "আমাদের কার্যক্রম": "Our Programs",
  "রক্তদাতা হন": "Become a Donor",
  "আর্থিক সহায়তা": "Donate",
  "আর্থিক সহায়তা ও অনুদান": "Financial Support & Contributions",
  "লগইন": "Login",
  "লগইন করুন": "Sign In",

  // ── Footer ───────────────────────────────────────────────
  "দ্রুত লিঙ্ক": "Quick Links",
  "যোগাযোগ": "Contact",
  "আমাদের অবস্থান": "Our Location",

  // ── Auth ─────────────────────────────────────────────────
  "পাসওয়ার্ড ভুলে গেছেন?": "Forgot Password?",
  "ইউজারনেম বা ইমেইল": "Username or Email",
  "ওটিপি (OTP) কোড পাঠান": "Send OTP Code",
  "ওটিপি যাচাই করুন": "Verify OTP",
  "নতুন পাসওয়ার্ড সংরক্ষণ করুন": "Save New Password",
  "পুনরায় পাঠান": "Resend",
  "ওটিপি পাননি? পুনরায় পাঠান": "Didn't receive OTP? Resend",

  // ── Blood Donor ──────────────────────────────────────────
  "জরুরি রক্তদাতা ডাটাবেস": "Emergency Blood Donor Database",
  "রক্তের গ্রুপ": "Blood Group",
  "সর্বশেষ রক্তদান": "Last Blood Donation",
  "সর্বশেষ দান:": "Last Donated:",
  "অবস্থান:": "Location:",
  "বিভাগ": "Division",
  "জেলা": "District",
  "উপজেলা / থানা": "Upazila / Thana",
  "সকল বিভাগ": "All Divisions",
  "সকল জেলা": "All Districts",
  "সকল উপজেলা": "All Upazilas",
  "সকল": "All",
  "রক্তদাতাদের তালিকা": "Blood Donors List",

  // ── Gallery ──────────────────────────────────────────────
  "গ্যালারি": "Gallery",
  "আমাদের গ্যালারি": "Our Gallery",
  "ছবি যোগ করুন": "Add Photo",

  // ── Misc Numbers & Dates ─────────────────────────────────
  "জানুয়ারি": "January", "ফেব্রুয়ারি": "February", "মার্চ": "March",
  "এপ্রিল": "April", "মে": "May", "জুন": "June",
  "জুলাই": "July", "আগস্ট": "August", "সেপ্টেম্বর": "September",
  "অক্টোবর": "October", "নভেম্বর": "November", "ডিসেম্বর": "December",
};

// Sort keys by length descending so longer phrases are replaced first
const HN_DICT_SORTED = Object.entries(HN_DICT).sort((a, b) => b[0].length - a[0].length);

// ════════════════════════════════════════════════════════════
// 2. CACHE — persistent for neural-translated dynamic content
// ════════════════════════════════════════════════════════════
let translationCache = {};
try {
  const stored = localStorage.getItem('hn_trans_v3');
  if (stored) translationCache = JSON.parse(stored);
} catch (e) { translationCache = {}; }

function saveCache() {
  try { localStorage.setItem('hn_trans_v3', JSON.stringify(translationCache)); } catch (e) {}
}

// ════════════════════════════════════════════════════════════
// 3. NUMERAL CONVERTER
// ════════════════════════════════════════════════════════════
function toBengali(n) { return String(n).replace(/[0-9]/g, d => '০১২৩৪৫৬৭৮৯'[d]); }
function toEnglish(str) {
  if (typeof str !== 'string') return str;
  return str.replace(/[০-৯]/g, d => '০১২৩৪৫৬৭৮৯'.indexOf(d));
}

// ════════════════════════════════════════════════════════════
// 4. HYBRID TRANSLATOR — Dictionary first, then Neural API
// ════════════════════════════════════════════════════════════
function applyDictionary(text) {
  let result = text;
  for (const [bn, en] of HN_DICT_SORTED) {
    if (result.includes(bn)) {
      result = result.replaceAll(bn, en);
    }
  }
  // Currency and digits
  result = result.replaceAll('৳', 'BDT ');
  result = result.replace(/[০-৯]/g, d => '০১২৩৪৫৬৭৮৯'.indexOf(d));
  return result;
}

function hasBanglaLeft(text) {
  return /[\u0980-\u09FF]/.test(text);
}

async function translateText(text) {
  if (!text || !text.trim()) return text;
  const key = text.trim();

  // Step 1: Apply local dictionary
  const afterDict = applyDictionary(key);

  // Step 2: If no Bengali remains, we're done
  if (!hasBanglaLeft(afterDict)) {
    return afterDict;
  }

  // Step 3: Check neural cache
  if (translationCache[key]) return translationCache[key];

  // Step 4: Neural API call for unknown dynamic content
  try {
    const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=bn&tl=en&dt=t&q=${encodeURIComponent(key)}`;
    const res = await fetch(url);
    if (res.ok) {
      const data = await res.json();
      if (data?.[0] && Array.isArray(data[0])) {
        const translated = data[0].map(item => item[0]).filter(Boolean).join('');
        if (translated) {
          translationCache[key] = translated;
          saveCache();
          return translated;
        }
      }
    }
  } catch (err) {
    // API failed — return dictionary partial result
  }

  return afterDict;
}

// ════════════════════════════════════════════════════════════
// 5. MAIN ENGINE
// ════════════════════════════════════════════════════════════
const HN_I18N = {
  currentLang: localStorage.getItem('hn_lang') || 'bn',

  isProtected(text) {
    if (!text) return true;
    const t = text.trim();
    if (/^HHN[0-9]+/i.test(t) || /^HN-[A-Z0-9-]+/i.test(t)) return true;
    if (/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(t)) return true;
    if (/^(http|https):\/\/[^ "]+$/.test(t)) return true;
    return false;
  },

  hasBangla(text) { return /[\u0980-\u09FF]/.test(text); },

  async translateDOM(root = document.body) {
    if (this.currentLang !== 'en') return;

    const textNodes = [];
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    let node;

    while ((node = walker.nextNode())) {
      const parent = node.parentElement;
      if (!parent) continue;
      if (parent.classList.contains('notranslate') || parent.classList.contains('font-monospace')) continue;
      if (['SCRIPT', 'STYLE', 'CODE', 'PRE', 'TEXTAREA'].includes(parent.tagName)) continue;

      const raw = node.nodeValue;
      if (!raw || !raw.trim()) continue;

      if (this.hasBangla(raw) && !this.isProtected(raw)) {
        if (typeof node._orig_text === 'undefined') node._orig_text = raw;
        textNodes.push(node);
      }
    }

    // Phase 1: Apply dictionary instantly (synchronous, no waiting)
    for (const n of textNodes) {
      const orig = n._orig_text;
      if (orig) {
        const quick = applyDictionary(orig);
        n.nodeValue = quick;
      }
    }

    // Phase 2: For any remaining Bengali text, fetch from neural API
    const stillBengali = textNodes.filter(n => hasBanglaLeft(n.nodeValue));
    const batchSize = 10;
    for (let i = 0; i < stillBengali.length; i += batchSize) {
      const batch = stillBengali.slice(i, i + batchSize);
      await Promise.all(batch.map(async (n) => {
        const orig = n._orig_text;
        if (orig) {
          n.nodeValue = await translateText(orig);
        }
      }));
    }

    // Phase 3: Placeholders and titles
    const inputs = root.querySelectorAll('input[placeholder], textarea[placeholder], [title]');
    for (const el of inputs) {
      if (el.classList.contains('notranslate') || el.classList.contains('font-monospace')) continue;

      if (el.placeholder && this.hasBangla(el.placeholder)) {
        if (!el.hasAttribute('data-orig-placeholder')) el.setAttribute('data-orig-placeholder', el.placeholder);
        el.placeholder = await translateText(el.getAttribute('data-orig-placeholder'));
      }
      if (el.title && this.hasBangla(el.title)) {
        if (!el.hasAttribute('data-orig-title')) el.setAttribute('data-orig-title', el.title);
        el.title = await translateText(el.getAttribute('data-orig-title'));
      }
    }
  },

  restoreOriginalBangla(root = document.body) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    let node;
    while ((node = walker.nextNode())) {
      if (typeof node._orig_text !== 'undefined') node.nodeValue = node._orig_text;
    }
    root.querySelectorAll('[data-orig-placeholder]').forEach(el => el.placeholder = el.getAttribute('data-orig-placeholder'));
    root.querySelectorAll('[data-orig-title]').forEach(el => el.title = el.getAttribute('data-orig-title'));
  },

  updateButtonUI() {
    const lang = this.currentLang;
    const btn = document.getElementById('hn-lang-toggle');
    if (btn) {
      btn.setAttribute('data-lang', lang);
      const bnSpan = btn.querySelector('.hn-lang-bn');
      const enSpan = btn.querySelector('.hn-lang-en');
      const activeSpan = btn.querySelector('.hn-lang-active');
      if (bnSpan) bnSpan.style.display = lang === 'bn' ? 'none' : 'inline';
      if (enSpan) enSpan.style.display = lang === 'en' ? 'none' : 'inline';
      if (activeSpan) activeSpan.textContent = lang === 'bn' ? 'বাং' : 'EN';
    }
    document.documentElement.lang = lang === 'bn' ? 'bn-BD' : 'en';
  },

  async apply() {
    this.updateButtonUI();
    if (this.currentLang === 'en') {
      await this.translateDOM(document.body);
    } else {
      this.restoreOriginalBangla(document.body);
    }
  },

  async toggle() {
    this.currentLang = this.currentLang === 'bn' ? 'en' : 'bn';
    localStorage.setItem('hn_lang', this.currentLang);
    await this.apply();
  },

  init() {
    this.updateButtonUI();
    const run = () => {
      if (this.currentLang === 'en') this.apply();

      if (window.MutationObserver) {
        const obs = new MutationObserver((mutations) => {
          if (this.currentLang === 'en') {
            for (const m of mutations) {
              for (const node of m.addedNodes) {
                if (node.nodeType === Node.ELEMENT_NODE) this.translateDOM(node);
              }
            }
          }
        });
        obs.observe(document.body, { childList: true, subtree: true });
      }
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', run);
    } else {
      run();
    }
  }
};

HN_I18N.init();
