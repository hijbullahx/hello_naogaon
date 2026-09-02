/**
 * Helpline Hello Naogaon - 100% Fully Automated Dynamic Translation Engine (No Static Dictionaries)
 * Translates WHATEVER is on the screen automatically in real-time.
 * Works across all static UI, dynamic database content, custom admin paragraphs, news, and forms.
 */

// In-Memory & Persistent Cache for lightning-fast 0ms repeated translations
let translationCache = {};
try {
  const stored = localStorage.getItem('hn_auto_translation_cache');
  if (stored) translationCache = JSON.parse(stored);
} catch (e) {
  translationCache = {};
}

function saveCache() {
  try {
    localStorage.setItem('hn_auto_translation_cache', JSON.stringify(translationCache));
  } catch (e) {}
}

// Bengali to English Numeral Converter
function convertBengaliDigits(str) {
  if (typeof str !== 'string') return str;
  const bn = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
  const en = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
  let res = str;
  for (let i = 0; i < 10; i++) {
    res = res.replaceAll(bn[i], en[i]);
  }
  return res;
}

// Universal Real-Time Neural Translation API Fetcher (Zero Static Words)
async function translateTextOnline(text) {
  if (!text || !text.trim()) return text;
  const key = text.trim();

  // Return from local cache if already translated before
  if (translationCache[key]) {
    return translationCache[key];
  }

  try {
    const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=bn&tl=en&dt=t&q=${encodeURIComponent(key)}`;
    const response = await fetch(url);
    if (response.ok) {
      const data = await response.json();
      if (data && data[0] && Array.isArray(data[0])) {
        const translated = data[0].map(item => item[0]).filter(Boolean).join('');
        if (translated) {
          translationCache[key] = translated;
          saveCache();
          return translated;
        }
      }
    }
  } catch (err) {
    console.warn('Auto translation request failed:', err);
  }

  // Fallback: convert digits if API fails
  return convertBengaliDigits(key);
}

// Main 100% Dynamic Engine
const HN_I18N = {
  currentLang: localStorage.getItem('hn_lang') || 'bn',

  hasBangla(text) {
    return /[\u0980-\u09FF]/.test(text);
  },

  isProtected(text) {
    if (!text) return true;
    const t = text.trim();
    // Do NOT translate Member IDs (HHN...), emails, URLs, or phone numbers
    if (/^HHN[0-9]+/i.test(t) || /^HN-[A-Z0-9-]+/i.test(t)) return true;
    if (/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(t)) return true;
    if (/^(http|https):\/\/[^ "]+$/.test(t)) return true;
    return false;
  },

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
        if (typeof node._orig_text === 'undefined') {
          node._orig_text = raw;
        }
        textNodes.push(node);
      }
    }

    // Process nodes in fast parallel batches
    const batchSize = 12;
    for (let i = 0; i < textNodes.length; i += batchSize) {
      const batch = textNodes.slice(i, i + batchSize);
      await Promise.all(batch.map(async (n) => {
        const orig = n._orig_text;
        if (orig) {
          const en = await translateTextOnline(orig);
          n.nodeValue = en;
        }
      }));
    }

    // Auto-translate Placeholders and Titles
    const inputs = root.querySelectorAll('input[placeholder], textarea[placeholder], [title]');
    inputs.forEach(async (el) => {
      if (el.classList.contains('notranslate') || el.classList.contains('font-monospace')) return;

      if (el.placeholder && this.hasBangla(el.placeholder)) {
        if (!el.hasAttribute('data-orig-placeholder')) {
          el.setAttribute('data-orig-placeholder', el.placeholder);
        }
        const origPh = el.getAttribute('data-orig-placeholder');
        el.placeholder = await translateTextOnline(origPh);
      }

      if (el.title && this.hasBangla(el.title)) {
        if (!el.hasAttribute('data-orig-title')) {
          el.setAttribute('data-orig-title', el.title);
        }
        const origTitle = el.getAttribute('data-orig-title');
        el.title = await translateTextOnline(origTitle);
      }
    });
  },

  restoreOriginalBangla(root = document.body) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    let node;
    while ((node = walker.nextNode())) {
      if (typeof node._orig_text !== 'undefined') {
        node.nodeValue = node._orig_text;
      }
    }

    const inputs = root.querySelectorAll('[data-orig-placeholder], [data-orig-title]');
    inputs.forEach((el) => {
      if (el.hasAttribute('data-orig-placeholder')) {
        el.placeholder = el.getAttribute('data-orig-placeholder');
      }
      if (el.hasAttribute('data-orig-title')) {
        el.title = el.getAttribute('data-orig-title');
      }
    });
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
      if (this.currentLang === 'en') {
        this.apply();
      }

      // Auto-translate any dynamically opened modals or newly injected elements
      if (window.MutationObserver) {
        const observer = new MutationObserver((mutations) => {
          if (this.currentLang === 'en') {
            for (const m of mutations) {
              for (const node of m.addedNodes) {
                if (node.nodeType === Node.ELEMENT_NODE) {
                  this.translateDOM(node);
                }
              }
            }
          }
        });
        observer.observe(document.body, { childList: true, subtree: true });
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
