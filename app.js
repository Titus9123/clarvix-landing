/* ================================================================
   CLARVIX — app.js
   ─ Multilingual support (EN / ES / HE)
   ─ Order modal + Fiverr redirect flow
   ─ Services tab switcher (Audit / Lead Gen)
   ─ Scroll animations
   ─ Nav scroll effect
   ================================================================ */

/* ══════════════════════════════════════════════════════════════
   1. LANGUAGE SYSTEM
   ══════════════════════════════════════════════════════════════ */

let currentLang = document.documentElement.lang || 'en';

// Smart redirect to preferred language on load
try {
  var saved = localStorage.getItem('clarvix_lang');
  var path = window.location.pathname;
  if (saved === 'es' && currentLang === 'en' && !path.includes('es.html')) {
    window.location.replace('es.html' + window.location.hash);
  } else if (saved === 'en' && currentLang === 'es' && path.includes('es.html')) {
    window.location.replace('index.html' + window.location.hash);
  } else {
    // Save current as preference
    localStorage.setItem('clarvix_lang', currentLang);
  }
} catch (e) { }

document.addEventListener('DOMContentLoaded', function () {
  initScrollAnimations();
  initScoreBars();
});

/* ══════════════════════════════════════════════════════════════
   2. ORDER MODAL — Fiverr Redirect Flow
   ══════════════════════════════════════════════════════════════ */

var selectedPackage = 'basic'; // default

/**
 * Opens the order directly on Fiverr.
 * @param {string} [pkg] - 'basic' | 'standard' | 'premium' (optional, defaults to 'basic')
 */
function openOrder(pkg) {
  var url = FIVERR_BASIC;
  if (pkg === 'standard') {
    url = typeof FIVERR_STANDARD !== 'undefined' ? FIVERR_STANDARD : FIVERR_BASIC;
  } else if (pkg === 'premium') {
    url = typeof FIVERR_PREMIUM !== 'undefined' ? FIVERR_PREMIUM : FIVERR_BASIC;
  }

  window.open(url, '_blank', 'noopener,noreferrer');
}

function closeOrder() {
  var overlay = document.getElementById('orderOverlay');
  if (overlay) overlay.classList.remove('open');
  document.body.style.overflow = '';
}

function handleOverlayClick(e) {
  if (e.target === document.getElementById('orderOverlay')) closeOrder();
}

/**
 * Validates and submits the order — redirects to the correct Fiverr gig.
 * @param {Event} e
 */
function submitOrder(e) {
  e.preventDefault();
  hideError();

  var name = document.getElementById('businessName').value.trim();
  var url = document.getElementById('websiteUrl').value.trim();

  // Basic validation
  var hasError = false;
  if (!name) {
    document.getElementById('businessName').classList.add('error');
    hasError = true;
  }
  if (!url) {
    document.getElementById('websiteUrl').classList.add('error');
    hasError = true;
  }
  if (hasError) {
    showError();
    return;
  }

  // Remove error states on valid inputs
  document.getElementById('businessName').classList.remove('error');
  document.getElementById('websiteUrl').classList.remove('error');

  // Show loading state
  var btn = document.getElementById('orderSubmit');
  var submitText = btn.querySelector('.submit-text');
  var loadingText = btn.querySelector('.submit-loading');
  btn.disabled = true;
  submitText.style.display = 'none';
  loadingText.style.display = 'inline';

  // Determine the Fiverr URL based on selected package
  // FIVERR_BASIC and FIVERR_PREMIUM are defined in index.html <head>
  var fiverUrl = (selectedPackage === 'premium') ? FIVERR_PREMIUM : FIVERR_BASIC;

  // Open Fiverr in new tab after a brief delay (feels intentional)
  setTimeout(function () {
    window.open(fiverUrl, '_blank', 'noopener,noreferrer');

    // Reset button and show success message
    btn.disabled = false;
    submitText.style.display = 'inline';
    loadingText.style.display = 'none';

    showSuccessState(name);
  }, 800);
}

function showError() {
  var err = document.getElementById('formError');
  if (err) err.classList.add('visible');
}

function hideError() {
  var err = document.getElementById('formError');
  if (err) err.classList.remove('visible');

  // Also clear input error states
  var inputs = document.querySelectorAll('.form-input.error');
  inputs.forEach(function (i) { i.classList.remove('error'); });
}

function showSuccessState(businessName) {
  // Replace form content with a success message
  var form = document.getElementById('orderForm');
  var pkgSelector = document.getElementById('packageSelector');

  pkgSelector.style.display = 'none';

  form.innerHTML = '<div class="modal-success visible">' +
    '<span class="success-icon">🚀</span>' +
    '<div class="success-title">' +
    (currentLang === 'es' ? 'Fiverr se abrió en una pestaña nueva' : 'Fiverr opened in a new tab') +
    '</div>' +
    '<p class="success-sub">' +
    (currentLang === 'es'
      ? 'Completa tu pedido para <strong>' + escHtml(businessName) + '</strong> en Fiverr. Recibirás tu auditoría en 48&nbsp;horas o menos una vez confirmado el pedido.'
      : 'Complete your order for <strong>' + escHtml(businessName) + '</strong> on Fiverr. You\'ll receive your audit within 48&nbsp;hours of order confirmation.'
    ) +
    '</p>' +
    '<p class="success-note">' +
    (currentLang === 'es'
      ? '¿No se abrió Fiverr? <a href="' + (selectedPackage === 'premium' ? FIVERR_PREMIUM : FIVERR_BASIC) + '" target="_blank" rel="noopener noreferrer" style="color:#0ABFBF">Haz clic aquí</a>'
      : 'Fiverr didn\'t open? <a href="' + (selectedPackage === 'premium' ? FIVERR_PREMIUM : FIVERR_BASIC) + '" target="_blank" rel="noopener noreferrer" style="color:#0ABFBF">Click here</a>'
    ) +
    '</p>' +
    '<button onclick="closeOrder()" style="margin-top:24px;background:none;border:1px solid rgba(255,255,255,0.12);color:#8FA3B8;padding:10px 24px;border-radius:8px;cursor:pointer;font-size:0.9rem;font-family:Inter,sans-serif;transition:all 0.2s" onmouseover="this.style.borderColor=\'#0ABFBF\';this.style.color=\'#0ABFBF\'" onmouseout="this.style.borderColor=\'rgba(255,255,255,0.12)\';this.style.color=\'#8FA3B8\'">' +
    (currentLang === 'es' ? 'Cerrar' : 'Close') +
    '</button>' +
    '</div>';
}

/** Simple HTML escaping to prevent XSS in the success message */
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ══════════════════════════════════════════════════════════════
   3. SERVICES TAB SWITCHER
   ══════════════════════════════════════════════════════════════ */

/**
 * Switches between the Audit and Lead Generation service tabs.
 * @param {string} tabId - 'audit' | 'leadgen'
 * @param {HTMLElement} btn - the clicked button element
 */
function switchTab(tabId, btn) {
  // Update panel visibility
  var panels = document.querySelectorAll('.tab-panel');
  panels.forEach(function (p) { p.classList.remove('active'); });
  var target = document.getElementById('tab-' + tabId);
  if (target) target.classList.add('active');

  // Update button states
  var buttons = document.querySelectorAll('.tab-btn');
  buttons.forEach(function (b) {
    b.classList.remove('active');
    b.setAttribute('aria-selected', 'false');
  });
  if (btn) {
    btn.classList.add('active');
    btn.setAttribute('aria-selected', 'true');
  }

  // Re-trigger score bar animation if switching to audit tab
  if (tabId === 'audit') {
    setTimeout(initScoreBars, 100);
  }
}

/* ══════════════════════════════════════════════════════════════
   4-OLD. VIDEO PLACEHOLDER
   ══════════════════════════════════════════════════════════════ */

function openVideo() {
  var placeholder = document.getElementById('video-placeholder');
  if (!placeholder) return;
  placeholder.innerHTML =
    '<div style="width:100%;aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;' +
    'background:linear-gradient(135deg,#0D1B2A,#0F2236);color:#8FA3B8;font-size:1rem;' +
    'font-family:Inter,sans-serif;text-align:center;padding:32px;">' +
    '<div>' +
    '<p style="font-size:2.5rem;margin-bottom:16px;">🎬</p>' +
    '<p style="color:#0ABFBF;font-weight:700;margin-bottom:10px;font-size:1.05rem;">Video coming soon</p>' +
    '<p style="font-size:0.85rem;max-width:360px;line-height:1.6;">' +
    'Record your Loom walkthrough and replace the placeholder in <code style="color:#0ABFBF">index.html</code>' +
    '</p>' +
    '</div>' +
    '</div>';
}

/* ══════════════════════════════════════════════════════════════
   5. NAV SCROLL EFFECT
   ══════════════════════════════════════════════════════════════ */

var nav = document.getElementById('nav');
window.addEventListener('scroll', function () {
  if (window.scrollY > 20) {
    nav.classList.add('scrolled');
  } else {
    nav.classList.remove('scrolled');
  }
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
      var offset = 72;
      var top = target.getBoundingClientRect().top + window.scrollY - offset;
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
    '.lg-pipeline-step, .lg-stat, .leadgen-card'
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

  // Cache target widths, reset to 0
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
          setTimeout(function () {
            fill.style.width = targets[i];
          }, i * 120);
        });
        barObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.35 });

  barObserver.observe(scorePreview);
}
