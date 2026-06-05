/* ============================================================
   MindFlow — Register Page Logic
   register.js
   ============================================================ */
'use strict';

/* ── DOM refs ── */
const form            = document.getElementById('registerForm');
const fullNameInput   = document.getElementById('fullName');
const emailInput      = document.getElementById('email');
const passwordInput   = document.getElementById('password');
const confirmInput    = document.getElementById('confirmPassword');
const termsInput      = document.getElementById('terms');

const nameGroup       = document.getElementById('nameGroup');
const emailGroup      = document.getElementById('emailGroup');
const passwordGroup   = document.getElementById('passwordGroup');
const confirmGroup    = document.getElementById('confirmGroup');

const nameError       = document.getElementById('nameError');
const emailError      = document.getElementById('emailError');
const passwordError   = document.getElementById('passwordError');
const confirmError    = document.getElementById('confirmError');
const termsError      = document.getElementById('termsError');

const nameStatus      = document.getElementById('nameStatus');
const emailStatus     = document.getElementById('emailStatus');
const confirmStatus   = document.getElementById('confirmStatus');

const togglePw1       = document.getElementById('togglePw1');
const togglePw2       = document.getElementById('togglePw2');
const eye1            = document.getElementById('eye1');
const eye2            = document.getElementById('eye2');

const strengthWrap    = document.getElementById('strengthWrap');
const strengthLabel   = document.getElementById('strengthLabel');
const bars            = [document.getElementById('sb1'), document.getElementById('sb2'),
                         document.getElementById('sb3'), document.getElementById('sb4')];

const reqLen          = document.getElementById('req-len');
const reqUpper        = document.getElementById('req-upper');
const reqNum          = document.getElementById('req-num');
const reqSpecial      = document.getElementById('req-special');

const progressBar     = document.getElementById('progressBar');
const registerBtn     = document.getElementById('registerBtn');
const formError       = document.getElementById('formError');
const formSuccess     = document.getElementById('formSuccess');
const googleBtn       = document.getElementById('googleBtn');
const appleBtn        = document.getElementById('appleBtn');

/* ============================================================
   PROGRESS BAR
   Updates based on how many fields are filled & valid
   ============================================================ */
function updateProgress() {
  let score = 0;
  if (fullNameInput.value.trim().length >= 2)   score += 25;
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value)) score += 25;
  if (getPasswordScore(passwordInput.value) >= 2) score += 25;
  if (confirmInput.value && confirmInput.value === passwordInput.value) score += 25;
  progressBar.style.width = score + '%';
}

/* ============================================================
   FIELD STATE HELPER
   ============================================================ */
function setField(group, errEl, statusEl, state, msg = '') {
  group.classList.remove('success', 'error');
  if (state === 'success') {
    group.classList.add('success');
    if (statusEl) statusEl.textContent = '✅';
    errEl.textContent = '';
  } else if (state === 'error') {
    group.classList.add('error');
    if (statusEl) statusEl.textContent = '❌';
    errEl.innerHTML = `⚠ ${msg}`;
  } else {
    if (statusEl) statusEl.textContent = '';
    errEl.textContent = '';
  }
}

/* ============================================================
   VALIDATORS
   ============================================================ */
function validateName(live = false) {
  const val = fullNameInput.value.trim();
  if (!val) {
    if (!live) setField(nameGroup, nameError, nameStatus, 'error', 'Full name is required');
    else setField(nameGroup, nameError, nameStatus, 'idle');
    return false;
  }
  if (val.length < 2) {
    setField(nameGroup, nameError, nameStatus, 'error', 'Name must be at least 2 characters');
    return false;
  }
  if (!/^[a-zA-Z\s'-]+$/.test(val)) {
    setField(nameGroup, nameError, nameStatus, 'error', 'Name can only contain letters, spaces, hyphens or apostrophes');
    return false;
  }
  setField(nameGroup, nameError, nameStatus, 'success');
  return true;
}

function validateEmail(live = false) {
  const val = emailInput.value.trim();
  if (!val) {
    if (!live) setField(emailGroup, emailError, emailStatus, 'error', 'Email address is required');
    else setField(emailGroup, emailError, emailStatus, 'idle');
    return false;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
    if (!live || val.includes('@'))
      setField(emailGroup, emailError, emailStatus, 'error', 'Please enter a valid email address');
    return false;
  }
  setField(emailGroup, emailError, emailStatus, 'success');
  return true;
}

/* Password scoring 0-4 */
function getPasswordScore(pw) {
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return score;
}

function updateStrengthUI(pw) {
  if (!pw) {
    strengthWrap.classList.remove('visible');
    bars.forEach(b => { b.className = 'strength-bar'; });
    return;
  }
  strengthWrap.classList.add('visible');

  const score = getPasswordScore(pw);
  const configs = [
    { label: 'Too weak', cls: 'weak',   fill: 1 },
    { label: 'Weak',     cls: 'weak',   fill: 1 },
    { label: 'Fair',     cls: 'fair',   fill: 2 },
    { label: 'Good',     cls: 'good',   fill: 3 },
    { label: 'Strong',   cls: 'strong', fill: 4 },
  ];
  const cfg = configs[score] || configs[0];
  strengthLabel.textContent = cfg.label;
  strengthLabel.className   = `strength-label ${cfg.cls}`;

  bars.forEach((b, i) => {
    b.className = `strength-bar${i < cfg.fill ? ' ' + cfg.cls : ''}`;
  });

  // Requirements checklist
  const checks = {
    'req-len':     pw.length >= 8,
    'req-upper':   /[A-Z]/.test(pw),
    'req-num':     /[0-9]/.test(pw),
    'req-special': /[^A-Za-z0-9]/.test(pw),
  };
  Object.entries(checks).forEach(([id, met]) => {
    document.getElementById(id)?.classList.toggle('met', met);
  });
}

function validatePassword(live = false) {
  const pw = passwordInput.value;
  updateStrengthUI(pw);

  if (!pw) {
    if (!live) setField(passwordGroup, passwordError, null, 'error', 'Password is required');
    else setField(passwordGroup, passwordError, null, 'idle');
    return false;
  }
  if (pw.length < 8) {
    setField(passwordGroup, passwordError, null, 'error', 'Password must be at least 8 characters');
    return false;
  }
  if (getPasswordScore(pw) < 2) {
    setField(passwordGroup, passwordError, null, 'error', 'Password is too weak — add uppercase letters or numbers');
    return false;
  }
  setField(passwordGroup, passwordError, null, 'success');
  // re-validate confirm if already typed
  if (confirmInput.value) validateConfirm(true);
  return true;
}

function validateConfirm(live = false) {
  const val = confirmInput.value;
  if (!val) {
    if (!live) setField(confirmGroup, confirmError, confirmStatus, 'error', 'Please confirm your password');
    else setField(confirmGroup, confirmError, confirmStatus, 'idle');
    return false;
  }
  if (val !== passwordInput.value) {
    setField(confirmGroup, confirmError, confirmStatus, 'error', 'Passwords do not match');
    return false;
  }
  setField(confirmGroup, confirmError, confirmStatus, 'success');
  return true;
}

function validateTerms() {
  if (!termsInput.checked) {
    termsError.innerHTML = '⚠ You must agree to the Terms and Privacy Policy';
    termsError.style.opacity = '1'; termsError.style.transform = 'translateY(0)';
    return false;
  }
  termsError.innerHTML = '';
  termsError.style.opacity = '0';
  return true;
}

/* ============================================================
   REAL-TIME EVENTS
   ============================================================ */
fullNameInput.addEventListener('input',  () => { validateName(true);    updateProgress(); });
fullNameInput.addEventListener('blur',   () => { if (fullNameInput.value) validateName(false); });

emailInput.addEventListener('input',     () => { validateEmail(true);   updateProgress(); });
emailInput.addEventListener('blur',      () => { if (emailInput.value) validateEmail(false); });

passwordInput.addEventListener('input',  () => { validatePassword(true); updateProgress(); });
passwordInput.addEventListener('blur',   () => { if (passwordInput.value) validatePassword(false); });

confirmInput.addEventListener('input',   () => { validateConfirm(true); updateProgress(); });
confirmInput.addEventListener('blur',    () => { if (confirmInput.value) validateConfirm(false); });

termsInput.addEventListener('change',    () => validateTerms());

/* Clear form-level error on any input */
[fullNameInput, emailInput, passwordInput, confirmInput].forEach(el => {
  el.addEventListener('input', () => hideMsg(formError));
});

/* ============================================================
   PASSWORD TOGGLE
   ============================================================ */
togglePw1.addEventListener('click', () => {
  const hidden = passwordInput.type === 'password';
  passwordInput.type = hidden ? 'text' : 'password';
  eye1.textContent   = hidden ? '🙈' : '👁️';
  passwordInput.focus();
});
togglePw2.addEventListener('click', () => {
  const hidden = confirmInput.type === 'password';
  confirmInput.type = hidden ? 'text' : 'password';
  eye2.textContent  = hidden ? '🙈' : '👁️';
  confirmInput.focus();
});

/* ============================================================
   KEYBOARD: Tab flow Email → Password on Enter
   ============================================================ */
fullNameInput.addEventListener('keydown',  e => { if (e.key === 'Enter') { e.preventDefault(); emailInput.focus(); } });
emailInput.addEventListener('keydown',     e => { if (e.key === 'Enter') { e.preventDefault(); passwordInput.focus(); } });
passwordInput.addEventListener('keydown',  e => { if (e.key === 'Enter') { e.preventDefault(); confirmInput.focus(); } });

/* ============================================================
   SHOW / HIDE MESSAGES
   ============================================================ */
function showMsg(el, text, type = 'error') {
  el.innerHTML = (type === 'error' ? '⚠ ' : '✓ ') + text;
  el.classList.add('show');
}
function hideMsg(el) { el.classList.remove('show'); }

/* ============================================================
   LOADING STATE
   ============================================================ */
function setLoading(on) {
  registerBtn.disabled = on;
  registerBtn.classList.toggle('loading', on);
}

/* ============================================================
   FORM SUBMIT
   ============================================================ */
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideMsg(formError);
  hideMsg(formSuccess);

  const ok = [
    validateName(false),
    validateEmail(false),
    validatePassword(false),
    validateConfirm(false),
    validateTerms(),
  ].every(Boolean);

  if (!ok) {
    /* Scroll to first error */
    const firstErr = form.querySelector('.field-group.error');
    firstErr?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return;
  }

  setLoading(true);

  const payload = {
    full_name: fullNameInput.value.trim(),
    email:     emailInput.value.trim(),
    password:  passwordInput.value,
  };

  try {
    /* ── Real API call ──
    const res  = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Registration failed');
    sessionStorage.setItem('mf_token', data.access_token);
    sessionStorage.setItem('mf_user',  JSON.stringify(data.user));
    ── end API ── */

    // Demo simulation
    await simulateRegister(payload.email);

    /* Progress to 100% */
    progressBar.style.width = '100%';
    showMsg(formSuccess, `Welcome to MindFlow, ${payload.full_name.split(' ')[0]}! Redirecting…`, 'success');

    setTimeout(() => {
      window.location.href = './onboarding.html';
    }, 1400);

  } catch (err) {
    setLoading(false);
    showMsg(formError, err.message || 'Something went wrong. Please try again.');
    document.querySelector('.form-card').style.animation = 'shake 0.4s ease';
    setTimeout(() => { document.querySelector('.form-card').style.animation = ''; }, 400);
  }
});

/* ── Demo simulation ── */
function simulateRegister(email) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Simulate "email already in use" for known demo emails
      if (email === 'admin@mindflow.app') {
        reject(new Error('This email is already registered. Try logging in instead.'));
      } else {
        resolve({ token: 'new_user_token', user: { email } });
      }
    }, 1800);
  });
}

/* ============================================================
   SOCIAL BUTTONS (placeholder)
   ============================================================ */
googleBtn.addEventListener('click', () => showMsg(formError, 'Google sign-up coming soon! Use email for now.'));
appleBtn.addEventListener('click',  () => showMsg(formError, 'Apple sign-up coming soon! Use email for now.'));

/* ============================================================
   AUTH GUARD — redirect if already logged in
   ============================================================ */
(function authGuard() {
  const token = localStorage.getItem('mf_token') || sessionStorage.getItem('mf_token');
  if (token) window.location.href = './dashboard.html';
})();
