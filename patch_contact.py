"""
patch_contact.py
Patches all 4 landing page HTML files to:
1. Make service select optional (no required)
2. Add honeypot anti-spam field
3. Replace inline JS submit handler with hardened version
"""
import os, re

LANDING = os.path.dirname(os.path.abspath(__file__))
FILES = ['index.html', 'es.html', 'he.html', 'ar.html']

# 1. Remove required from select
OLD_SELECT = '<select name="service" required>'
NEW_SELECT = '<select name="service">'

# 2. Honeypot to inject BEFORE the submit button (after textarea)
HONEYPOT = '''              <!-- Anti-spam honeypot – hidden from real users -->
              <input type="text" name="_gotcha" style="display:none!important" tabindex="-1" autocomplete="off" aria-hidden="true">
'''

HONEYPOT_MARKER = '<button type="submit" class="btn btn-primary btn-full"'

# 3. Hardened JS submit handler (replaces the existing one)
OLD_HANDLER_PATTERN = r"document\.getElementById\('contactForm'\)\.addEventListener\('submit', async function\(e\) \{.*?\}\);"

NEW_HANDLER = """document.getElementById('contactForm').addEventListener('submit', async function(e) {
  e.preventDefault();

  // ── Rate limiting: 1 submission per 60s per session ──────────────
  var lastSub = sessionStorage.getItem('clarvix_last_contact');
  if (lastSub && (Date.now() - parseInt(lastSub)) < 60000) {
    alert('Please wait a moment before sending another message.');
    return;
  }

  // ── Honeypot check ────────────────────────────────────────────────
  if (document.querySelector('input[name="_gotcha"]').value !== '') return;

  // ── Sanitize helper (strip HTML/script tags, trim, limit length) ──
  function sanitize(val, maxLen) {
    if (!val) return '';
    // Strip HTML tags
    val = val.replace(/<[^>]*>/g, '');
    // Strip potential script injections
    val = val.replace(/javascript:/gi, '').replace(/on\\w+\\s*=/gi, '');
    // Trim and limit
    return val.trim().substring(0, maxLen || 1000);
  }

  // ── Validate & sanitize each field ───────────────────────────────
  var nameEl    = this.querySelector('input[name="name"]');
  var emailEl   = this.querySelector('input[name="email"]');
  var companyEl = this.querySelector('input[name="company"]');
  var serviceEl = this.querySelector('select[name="service"]');
  var msgEl     = this.querySelector('textarea[name="message"]');

  var name    = sanitize(nameEl    ? nameEl.value    : '', 120);
  var email   = sanitize(emailEl   ? emailEl.value   : '', 200);
  var company = sanitize(companyEl ? companyEl.value : '', 200);
  var service = sanitize(serviceEl ? serviceEl.value : '', 80);
  var message = sanitize(msgEl     ? msgEl.value     : '', 3000);

  if (name.length < 2) {
    alert('Please enter your name (at least 2 characters).');
    return;
  }
  if (!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(email)) {
    alert('Please enter a valid email address.');
    return;
  }

  // Write sanitized values back
  if (nameEl)    nameEl.value    = name;
  if (emailEl)   emailEl.value   = email;
  if (companyEl) companyEl.value = company;
  if (serviceEl) serviceEl.value = service;
  if (msgEl)     msgEl.value     = message;

  var btn = this.querySelector('button[type="submit"]');
  var origText = btn.textContent;
  btn.textContent = 'Sending\u2026';
  btn.disabled = true;

  try {
    var formData = new FormData(this);
    var resp = await fetch(this.action, {
      method: 'POST',
      body: formData,
      headers: { 'Accept': 'application/json' }
    });
    if (resp.ok) {
      sessionStorage.setItem('clarvix_last_contact', Date.now().toString());
      document.getElementById('formWrapper').style.display = 'none';
      var succ = document.getElementById('formSuccess');
      if (succ) succ.style.display = 'block';
    } else {
      throw new Error('Server error ' + resp.status);
    }
  } catch (err) {
    btn.textContent = origText;
    btn.disabled = false;
    alert('Something went wrong. Please try again or email us at contact@clarvix.net');
  }
});"""

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html

    # 1. Remove required from select
    html = html.replace(OLD_SELECT, NEW_SELECT)

    # 2. Add honeypot before submit button (only if not already there)
    if '_gotcha' not in html:
        html = html.replace(HONEYPOT_MARKER, HONEYPOT + HONEYPOT_MARKER, 1)

    # 3. Replace JS submit handler (use lambda to avoid backslash issues in replacement)
    html = re.sub(OLD_HANDLER_PATTERN, lambda m: NEW_HANDLER, html, flags=re.DOTALL)

    if html == original:
        print(f'  [!] No changes in {os.path.basename(filepath)}')
    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  [OK] Patched: {os.path.basename(filepath)}')

print('Patching contact forms...')
for fname in FILES:
    fpath = os.path.join(LANDING, fname)
    if os.path.exists(fpath):
        patch_file(fpath)
    else:
        print(f'  [skip] Not found: {fname}')

print('Done.')
