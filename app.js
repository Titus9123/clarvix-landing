/* ================================================================
   CLARVIX — app.js
   ─ Multilingual support (EN / ES / HE / AR)
   ─ Order modal + Payoneer flow (Audit & Lead Gen)
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

/* ══════════════════════════════════════════════════════════════
   2. AUDIT ORDER MODAL — Payoneer Flow
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
    'Please send me the Payoneer payment link.\n\nThank you.'
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
    '<p class="success-sub">Your <strong>' + pkg.name + ' (' + pkg.price + ')</strong> audit request for <strong>' + escHtml(businessName) + '</strong> is ready to send.<br>We\'ll reply with Payoneer payment instructions within a few hours.</p>' +
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
   3. LEAD GEN ORDER MODAL — Payoneer Flow
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
    'Please send me the Payoneer payment details.\n\nThank you.'
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
    '<p class="success-sub">Your lead generation inquiry for <strong>' + escHtml(businessName) + '</strong> is ready.<br>We\'ll confirm your order and send Payoneer payment instructions within 24 hours.</p>' +
    '<p class="success-note">Questions? <a href="mailto:' + CONTACT_EMAIL + '" style="color:#0ABFBF">' + CONTACT_EMAIL + '</a></p>' +
    '<button onclick="closeLeadGenOrder()" style="margin-top:24px;background:none;border:1px solid rgba(255,255,255,0.12);color:#8FA3B8;padding:10px 24px;border-radius:8px;cursor:pointer;font-size:0.9rem;font-family:Inter,sans-serif;transition:all 0.2s" onmouseover="this.style.borderColor=\'#0ABFBF\';this.style.color=\'#0ABFBF\'" onmouseout="this.style.borderColor=\'rgba(255,255,255,0.12)\';this.style.color=\'#8FA3B8\'">Close</button>' +
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
