/* ================================================================
   CLARVIX — app.js
   ─ Multilingual support (EN / ES / HE / AR)
   ─ Order modal + mailto intake flow (Audit & Lead Gen)
   ─ Services tab switcher (Audit / Lead Gen)
   ─ Scroll animations
   ─ Nav scroll effect
   ================================================================ */

/* ══════════════════════════════════════════════════════════════
   1. LANGUAGE SYSTEM
   ══════════════════════════════════════════════════════════════ */

let currentLang = document.documentElement.lang || 'en';

document.addEventListener('DOMContentLoaded', function () {
  initScrollAnimations();
  initScoreBars();
});

// Keep internal payment account available for operational use without exposing gateway branding in UI copy.
var PAYONEER_EMAIL = 'clarvix@clarvix.net';

/* ══════════════════════════════════════════════════════════════
   2. AUDIT ORDER MODAL — mailto intake
   ══════════════════════════════════════════════════════════════ */

var selectedPackage = 'standard'; // default

var packageData = {
  basic:    { name: 'Basic',    price: '$45',  desc: 'Core Diagnosis' },
  standard: { name: 'Standard', price: '$85',  desc: 'Full Audit + Benchmark' },
  premium:  { name: 'Premium',  price: '$160', desc: 'Strategic Advanced Audit' }
};

function openOrder(pkg) {
  var overlay = document.getElementById('orderOverlay');
  if (!overlay) return;
  selectPackage(pkg || 'standard');
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeOrder() {
  var overlay = document.getElementById('orderOverlay');
  if (overlay) overlay.classList.remove('open');
  document.body.style.overflow = '';
}

function handleOverlayClick(e) {
  if (e.target === document.getElementById('orderOverlay')) closeOrder();
}

function selectPackage(pkg) {
  selectedPackage = pkg || 'standard';
  var ids = ['basic', 'standard', 'premium'];
  ids.forEach(function (id) {
    var el = document.getElementById('pkg' + id.charAt(0).toUpperCase() + id.slice(1));
    var radio = document.getElementById('radio' + id.charAt(0).toUpperCase() + id.slice(1));
    if (el) el.classList.toggle('selected', id === selectedPackage);
    if (radio) radio.classList.toggle('checked', id === selectedPackage);
  });
}

function submitOrder(e) {
  e.preventDefault();
  hideError();

  var name = document.getElementById('businessName').value.trim();
  var url  = document.getElementById('websiteUrl').value.trim();
  var city = (document.getElementById('businessCity') || {}).value || '';

  var hasError = false;
  if (!name) { document.getElementById('businessName').classList.add('error'); hasError = true; }
  if (!url)  { document.getElementById('websiteUrl').classList.add('error');  hasError = true; }
  if (hasError) { showError(); return; }

  document.getElementById('businessName').classList.remove('error');
  document.getElementById('websiteUrl').classList.remove('error');

  var btn = document.getElementById('orderSubmit');
  btn.disabled = true;
  btn.querySelector('.submit-text').style.display = 'none';
  btn.querySelector('.submit-loading').style.display = 'inline';

  var pkg = packageData[selectedPackage];
  var subject = encodeURIComponent('Clarvix Audit Order — ' + pkg.name + ' (' + pkg.price + ')');
  var body = encodeURIComponent(
    'Hi Clarvix,\n\n' +
    'I would like to order the ' + pkg.name + ' audit (' + pkg.price + ').\n\n' +
    'Business Name: ' + name + '\n' +
    'Website: ' + url + '\n' +
    'City / Country: ' + city + '\n\n' +
    'Please send me the payment details provided after confirmation.\n\nThank you.'
  );

  setTimeout(function () {
    window.location.href = 'mailto:' + CONTACT_EMAIL + '?subject=' + subject + '&body=' + body;
    btn.disabled = false;
    btn.querySelector('.submit-text').style.display = 'inline';
    btn.querySelector('.submit-loading').style.display = 'none';
    showAuditSuccessState(name, pkg);
  }, 600);
}

function showAuditSuccessState(businessName, pkg) {
  var form = document.getElementById('orderForm');
  var pkgSelector = document.getElementById('packageSelector');
  if (pkgSelector) pkgSelector.style.display = 'none';
  form.innerHTML =
    '<div class="modal-success visible">' +
    '<span class="success-icon">🚀</span>' +
    '<div class="success-title">Email draft opened!</div>' +
    '<p class="success-sub">Your <strong>' + pkg.name + ' (' + pkg.price + ')</strong> audit request for <strong>' + escHtml(businessName) + '</strong> is ready to send.<br>We\'ll reply with payment details after confirmation within a few hours.</p>' +
    '<p class="success-note">Didn\'t open? Email us directly at <a href="mailto:' + CONTACT_EMAIL + '" style="color:#0ABFBF">' + CONTACT_EMAIL + '</a></p>' +
    '<button onclick="closeOrder()" style="margin-top:24px;background:none;border:1px solid rgba(255,255,255,0.12);color:#8FA3B8;padding:10px 24px;border-radius:8px;cursor:pointer;font-size:0.9rem;font-family:Inter,sans-serif;transition:all 0.2s" onmouseover="this.style.borderColor=\'#0ABFBF\';this.style.color=\'#0ABFBF\'" onmouseout="this.style.borderColor=\'rgba(255,255,255,0.12)\';this.style.color=\'#8FA3B8\'">Close</button>' +
    '</div>';
}

function showError() {
  var err = document.getElementById('formError');
  if (err) err.classList.add('visible');
}

function hideError() {
  var err = document.getElementById('formError');
  if (err) err.classList.remove('visible');
  document.querySelectorAll('.form-input.error').forEach(function (i) { i.classList.remove('error'); });
}

/* ══════════════════════════════════════════════════════════════
   3. LEAD GEN ORDER MODAL — mailto intake
   ══════════════════════════════════════════════════════════════ */

var currentLeadGenPlan = '';

function openLeadGenOrder(planLabel) {
  currentLeadGenPlan = planLabel || '';
  var overlay = document.getElementById('leadgenOverlay');
  var label   = document.getElementById('leadgen-plan-label');
  if (label) label.textContent = planLabel || '';
  if (overlay) {
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

function closeLeadGenOrder() {
  var overlay = document.getElementById('leadgenOverlay');
  if (overlay) overlay.classList.remove('open');
  document.body.style.overflow = '';
}

function submitLeadGenOrder(e) {
  e.preventDefault();

  var name = document.getElementById('lgBusinessName').value.trim();
  var email = document.getElementById('lgEmail').value.trim();
  var icp   = (document.getElementById('lgICP') || {}).value || '';

  var err = document.getElementById('lgFormError');
  if (!name || !email) {
    if (err) err.classList.add('visible');
    return;
  }
  if (err) err.classList.remove('visible');

  var btn = document.getElementById('lgSubmit');
  btn.disabled = true;
  btn.querySelector('.submit-text').style.display = 'none';
  btn.querySelector('.submit-loading').style.display = 'inline';

  var subject = encodeURIComponent('Clarvix Lead Gen Inquiry — ' + currentLeadGenPlan);
  var body = encodeURIComponent(
    'Hi Clarvix,\n\n' +
    'I am interested in the Lead Generation service.\n\n' +
    'Plan: ' + currentLeadGenPlan + '\n' +
    'Business Name: ' + name + '\n' +
    'Email: ' + email + '\n' +
    'Ideal Customer Profile: ' + icp + '\n\n' +
    'Please send me the payment details provided after confirmation.\n\nThank you.'
  );

  setTimeout(function () {
    window.location.href = 'mailto:' + CONTACT_EMAIL + '?subject=' + subject + '&body=' + body;
    btn.disabled = false;
    btn.querySelector('.submit-text').style.display = 'inline';
    btn.querySelector('.submit-loading').style.display = 'none';
    showLeadGenSuccessState(name);
  }, 600);
}

function showLeadGenSuccessState(businessName) {
  var form = document.getElementById('leadgenForm');
  form.innerHTML =
    '<div class="modal-success visible">' +
    '<span class="success-icon">📬</span>' +
    '<div class="success-title">Inquiry sent!</div>' +
    '<p class="success-sub">Your lead generation inquiry for <strong>' + escHtml(businessName) + '</strong> is ready.<br>We\'ll confirm your order and send payment details after confirmation within 24 hours.</p>' +
    '<p class="success-note">Questions? <a href="mailto:' + CONTACT_EMAIL + '" style="color:#0ABFBF">' + CONTACT_EMAIL + '</a></p>' +
    '<button onclick="closeLeadGenOrder()" style="margin-top:24px;background:none;border:1px solid rgba(255,255,255,0.12);color:#8FA3B8;padding:10px 24px;border-radius:8px;cursor:pointer;font-size:0.9rem;font-family:Inter,sans-serif;transition:all 0.2s" onmouseover="this.style.borderColor=\'#0ABFBF\';this.style.color=\'#0ABFBF\'" onmouseout="this.style.borderColor=\'rgba(255,255,255,0.12)\';this.style.color=\'#8FA3B8\'">Close</button>' +
    '</div>';
}

/* ══════════════════════════════════════════════════════════════
   4. AI REVENUE OPTIMIZATION ORDER MODAL — mailto intake
   ══════════════════════════════════════════════════════════════ */

var selectedAiRevTier = 'basic';

var aiRevTierDataByLang = {
  en: {
    basic:    { name: 'Quick Revenue Check',             price: '$199' },
    standard: { name: 'Revenue Diagnostic',              price: '$399' },
    premium:  { name: 'Revenue Optimization Deep Dive', price: '$799' }
  },
  es: {
    basic:    { name: 'Revisión rápida de ingresos',             price: '$199' },
    standard: { name: 'Diagnóstico de ingresos',              price: '$399' },
    premium:  { name: 'Análisis profundo de optimización de ingresos', price: '$799' }
  },
  he: {
    basic:    { name: 'בדיקת הכנסות מהירה',             price: '$199' },
    standard: { name: 'אבחון הכנסות',              price: '$399' },
    premium:  { name: 'צלילה עמוקה לאופטימיזציית הכנסות', price: '$799' }
  },
  ar: {
    basic:    { name: 'مراجعة سريعة للإيرادات',             price: '$199' },
    standard: { name: 'تشخيص الإيرادات',              price: '$399' },
    premium:  { name: 'تعميق تحسين الإيرادات', price: '$799' }
  }
};

var aiRevTierData = aiRevTierDataByLang[currentLang] || aiRevTierDataByLang.en;

function normalizeAiRevTier(tierLabel) {
  var t = String(tierLabel || '').trim().toLowerCase();
  if (!t) return 'basic';
  if (t === 'basic' || t === 'quick revenue check') return 'basic';
  if (t === 'standard' || t === 'revenue diagnostic') return 'standard';
  if (t === 'premium' || t === 'revenue optimization deep dive') return 'premium';
  return t;
}

function openAiRevOrder(tierLabel) {
  selectedAiRevTier = normalizeAiRevTier(tierLabel) || 'basic';
  var overlay = document.getElementById('aiRevOverlay');
  if (!overlay) return;
  selectAiRevTier(selectedAiRevTier);
  var label = document.getElementById('aiRev-tier-label');
  if (label && aiRevTierData[selectedAiRevTier]) {
    label.textContent = aiRevTierData[selectedAiRevTier].name + ' — ' + aiRevTierData[selectedAiRevTier].price;
  }
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeAiRevOrder() {
  var overlay = document.getElementById('aiRevOverlay');
  if (overlay) overlay.classList.remove('open');
  document.body.style.overflow = '';
}

function selectAiRevTier(tierKey) {
  selectedAiRevTier = normalizeAiRevTier(tierKey);
  var options = [
    { key: 'basic',    pkgId: 'aiRevTierBasic',    radioId: 'aiRevRadioBasic' },
    { key: 'standard', pkgId: 'aiRevTierStandard', radioId: 'aiRevRadioStandard' },
    { key: 'premium',  pkgId: 'aiRevTierPremium',  radioId: 'aiRevRadioPremium' }
  ];

  options.forEach(function (opt) {
    var el = document.getElementById(opt.pkgId);
    var radio = document.getElementById(opt.radioId);
    if (el) el.classList.toggle('selected', opt.key === selectedAiRevTier);
    if (radio) radio.classList.toggle('checked', opt.key === selectedAiRevTier);
  });
}

function submitAiRevOrder(e) {
  e.preventDefault();

  var name = document.getElementById('aiRevBusinessName').value.trim();
  var url = document.getElementById('aiRevWebsiteUrl').value.trim();
  var email = document.getElementById('aiRevEmail').value.trim();
  var summary = document.getElementById('aiRevBusinessSummary').value.trim();
  var revenueModel = document.getElementById('aiRevRevenueModel').value.trim();
  var mainConcern = document.getElementById('aiRevMainConcern').value.trim();

  var err = document.getElementById('aiRevFormError');
  if (err) err.classList.remove('visible');

  var hasError = false;
  if (!name) { hasError = true; document.getElementById('aiRevBusinessName').classList.add('error'); }
  if (!url) { hasError = true; document.getElementById('aiRevWebsiteUrl').classList.add('error'); }
  if (!email) { hasError = true; document.getElementById('aiRevEmail').classList.add('error'); }
  if (!mainConcern) { hasError = true; document.getElementById('aiRevMainConcern').classList.add('error'); }

  if (hasError) {
    if (err) err.classList.add('visible');
    return;
  }

  document.getElementById('aiRevBusinessName').classList.remove('error');
  document.getElementById('aiRevWebsiteUrl').classList.remove('error');
  document.getElementById('aiRevEmail').classList.remove('error');
  document.getElementById('aiRevMainConcern').classList.remove('error');

  var btn = document.getElementById('aiRevSubmit');
  btn.disabled = true;
  btn.querySelector('.submit-text').style.display = 'none';
  btn.querySelector('.submit-loading').style.display = 'inline';

  var pkg = aiRevTierData[selectedAiRevTier];
  var subject = encodeURIComponent('Clarvix AI Revenue Optimization — ' + (pkg ? pkg.name : 'Quick Revenue Check'));

  var body = encodeURIComponent(
    'Hi Clarvix,\n\n' +
    'I am interested in AI Revenue Optimization (' + (pkg ? pkg.name : 'Quick Revenue Check') + ').\n\n' +
    'Business Name: ' + name + '\n' +
    'Website: ' + url + '\n' +
    'Your Email: ' + email + '\n' +
    (summary ? ('Business Summary: ' + summary + '\n') : '') +
    (revenueModel ? ('Main Revenue / Monetization Model: ' + revenueModel + '\n') : '') +
    'Main Concern / Goal: ' + mainConcern + '\n\n' +
    'payment details provided after confirmation.\n\nThank you.'
  );

  setTimeout(function () {
    window.location.href = 'mailto:' + CONTACT_EMAIL + '?subject=' + subject + '&body=' + body;
    btn.disabled = false;
    btn.querySelector('.submit-text').style.display = 'inline';
    btn.querySelector('.submit-loading').style.display = 'none';
    showAiRevSuccessState(name, pkg);
  }, 600);
}

function showAiRevSuccessState(businessName, pkg) {
  var form = document.getElementById('aiRevForm');
  var pkgSelector = document.getElementById('aiRevPackageSelector');
  if (pkgSelector) pkgSelector.style.display = 'none';

  var lang = (currentLang || 'en');
  var tierName = (pkg && pkg.name) ? pkg.name : 'Quick Revenue Check';
  var businessEsc = escHtml(businessName);
  var tierEsc = escHtml(tierName);

  var copy = {
    en: {
      title: 'Email draft opened!',
      subPrefix: 'Your ',
      subBetween: ' revenue optimization inquiry for ',
      subSuffix: ' is ready to send.<br>We\'ll reply with next steps shortly.',
      notePrefix: 'Didn\'t open? Email us directly at '
    },
    es: {
      title: 'Borrador de correo listo!',
      subPrefix: 'Tu solicitud de ',
      subBetween: ' de optimización de ingresos para ',
      subSuffix: ' está lista para enviar.<br>Te responderemos con los próximos pasos pronto.',
      notePrefix: '¿No se abrió? Escríbenos directamente en '
    },
    he: {
      title: 'טיוטת אימייל נפתחה!',
      subPrefix: 'הבקשה שלך עבור ',
      subBetween: ' לאופטימיזציית הכנסות עבור ',
      subSuffix: ' מוכנה לשליחה.<br>נחזור אליך עם הצעדים הבאים בקרוב.',
      notePrefix: 'לא נפתח? כתבו לנו ישירות ב- '
    },
    ar: {
      title: 'تم فتح مسودة البريد الإلكتروني!',
      subPrefix: 'طلبك لـ ',
      subBetween: ' لتحسين الإيرادات لـ ',
      subSuffix: ' جاهز للإرسال.<br>سنرد عليك قريباً بالخطوات التالية.',
      notePrefix: 'لم يفتح؟ راسلنا مباشرة على '
    }
  }[lang] || {
    title: 'Email draft opened!',
    subPrefix: 'Your ',
    subBetween: ' revenue optimization inquiry for ',
    subSuffix: ' is ready to send.<br>We\'ll reply with next steps shortly.',
    notePrefix: 'Didn\'t open? Email us directly at '
  };

  form.innerHTML =
    '<div class="modal-success visible">' +
    '<span class="success-icon">🧠</span>' +
    '<div class="success-title">' + copy.title + '</div>' +
    '<p class="success-sub">' + copy.subPrefix + '<strong>' + tierEsc + '</strong>' + copy.subBetween + '<strong>' + businessEsc + '</strong>' + copy.subSuffix + '</p>' +
    '<p class="success-note">' + copy.notePrefix + '<a href="mailto:' + CONTACT_EMAIL + '" style="color:#0ABFBF">' + CONTACT_EMAIL + '</a></p>' +
    '<button onclick="closeAiRevOrder()" style="margin-top:24px;background:none;border:1px solid rgba(255,255,255,0.12);color:#8FA3B8;padding:10px 24px;border-radius:8px;cursor:pointer;font-size:0.9rem;font-family:Inter,sans-serif;transition:all 0.2s" onmouseover="this.style.borderColor=\'#0ABFBF\';this.style.color=\'#0ABFBF\'" onmouseout="this.style.borderColor=\'rgba(255,255,255,0.12)\';this.style.color=\'#8FA3B8\'">Close</button>' +
    '</div>';
}

/** Simple HTML escaping */
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ══════════════════════════════════════════════════════════════
   4. SERVICES TAB SWITCHER
   ══════════════════════════════════════════════════════════════ */

function switchTab(tabId, btn) {
  document.querySelectorAll('.tab-panel').forEach(function (p) { p.classList.remove('active'); });
  var target = document.getElementById('tab-' + tabId);
  if (target) target.classList.add('active');

  document.querySelectorAll('.tab-btn').forEach(function (b) {
    b.classList.remove('active');
    b.setAttribute('aria-selected', 'false');
  });
  if (btn) {
    btn.classList.add('active');
    btn.setAttribute('aria-selected', 'true');
  }

  if (tabId === 'audit') setTimeout(initScoreBars, 100);
}

/* ══════════════════════════════════════════════════════════════
   5. NAV SCROLL EFFECT
   ══════════════════════════════════════════════════════════════ */

var nav = document.getElementById('nav');
window.addEventListener('scroll', function () {
  if (nav) nav.classList.toggle('scrolled', window.scrollY > 20);
}, { passive: true });

/* ══════════════════════════════════════════════════════════════
   6. SMOOTH SCROLL FOR ANCHOR LINKS
   ══════════════════════════════════════════════════════════════ */

document.querySelectorAll('a[href^="#"]').forEach(function (link) {
  link.addEventListener('click', function (e) {
    var id = link.getAttribute('href').slice(1);
    var target = document.getElementById(id);
    if (target) {
      e.preventDefault();
      var top = target.getBoundingClientRect().top + window.scrollY - 72;
      window.scrollTo({ top: top, behavior: 'smooth' });
    }
  });
});

/* ══════════════════════════════════════════════════════════════
   7. SCROLL-TRIGGERED REVEAL ANIMATIONS
   ══════════════════════════════════════════════════════════════ */

function initScrollAnimations() {
  var targets = document.querySelectorAll(
    '.pain-card, .step-card, .deliverable-card, .industry-badge, ' +
    '.pricing-card, .problem-callout, .score-card-demo, ' +
    '.section-tag, .solution-image-col, .solution-text-col, ' +
    '.video-wrapper, .results-text, .results-visual, ' +
    '.lg-pipeline-step, .lg-stat, .payoneer-info'
  );

  targets.forEach(function (el, i) {
    el.classList.add('reveal');
    var mod = i % 3;
    if (mod === 1) el.classList.add('reveal-delay-1');
    if (mod === 2) el.classList.add('reveal-delay-2');
  });

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.10, rootMargin: '0px 0px -36px 0px' });

  targets.forEach(function (el) { observer.observe(el); });
}

/* ══════════════════════════════════════════════════════════════
   8. ANIMATED SCORE BARS
   ══════════════════════════════════════════════════════════════ */

function initScoreBars() {
  var scorePreview = document.querySelector('.score-preview');
  if (!scorePreview) return;

  var fills = scorePreview.querySelectorAll('.sbi-fill');
  var targets = [];
  fills.forEach(function (fill) {
    targets.push(fill.style.width || '0%');
    fill.style.width = '0%';
    fill.style.transition = 'width 1.4s cubic-bezier(0.25, 1, 0.5, 1)';
  });

  var barObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        fills.forEach(function (fill, i) {
          setTimeout(function () { fill.style.width = targets[i]; }, i * 120);
        });
        barObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.35 });

  barObserver.observe(scorePreview);
}
