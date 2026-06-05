/* ============================================================
   MindFlow — Login Page Logic
   login.js
   ============================================================ */

'use strict';

/* ── DOM refs ── */
const form         = document.getElementById('loginForm');
const emailInput   = document.getElementById('email');
const passwordInput= document.getElementById('password');
const emailGroup   = document.getElementById('emailGroup');
const passwordGroup= document.getElementById('passwordGroup');
const emailError   = document.getElementById('emailError');
const passwordError= document.getElementById('passwordError');
const emailStatus  = document.getElementById('emailStatus');
const togglePwBtn  = document.getElementById('togglePw');
const eyeIcon      = document.getElementById('eyeIcon');
const loginBtn     = document.getElementById('loginBtn');
const btnLoader    = document.getElementById('btnLoader');
const formError    = document.getElementById('formError');
const formSuccess  = document.getElementById('formSuccess');
const rememberMe   = document.getElementById('rememberMe');
const googleBtn    = document.getElementById('googleBtn');
const appleBtn     = document.getElementById('appleBtn');

/* ============================================================
   VALIDATION HELPERS
   ============================================================ */
const validators = {
  email(val) {
    if (!val.trim()) return 'Email address is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) return 'Please enter a valid email address';
    return null;
  },
  password(val) {
    if (!val) return 'Password is required';
    if (val.length < 6) return 'Password must be at least 6 characters';
    return null;
  }
};

function setFieldState(group, errorEl, statusEl, state, message = '') {
  group.classList.remove('success', 'error');
  if (state === 'success') {
    group.classList.add('success');
    if (statusEl) statusEl.textContent = '✅';
    errorEl.textContent = '';
  } else if (state === 'error') {
    group.classList.add('error');
    if (statusEl) statusEl.textContent = '❌';
    errorEl.innerHTML = `⚠ ${message}`;
  } else {
    if (statusEl) statusEl.textContent = '';
    errorEl.textContent = '';
  }
}

function validateEmail(live = false) {
  const err = validators.email(emailInput.value);
  if (err) {
    if (!live || emailInput.value.length > 3) setFieldState(emailGroup, emailError, emailStatus, 'error', err);
    return false;
  }
  setFieldState(emailGroup, emailError, emailStatus, 'success');
  return true;
}

function validatePassword(live = false) {
  const err = validators.password(passwordInput.value);
  if (err) {
    if (!live || passwordInput.value.length > 2) setFieldState(passwordGroup, passwordError, null, 'error', err);
    return false;
  }
  setFieldState(passwordGroup, passwordError, null, 'success');
  return true;
}

/* ============================================================
   REAL-TIME VALIDATION
   ============================================================ */
emailInput.addEventListener('input', () => validateEmail(true));
emailInput.addEventListener('blur',  () => {
  if (emailInput.value) validateEmail(false);
});

passwordInput.addEventListener('input', () => validatePassword(true));
passwordInput.addEventListener('blur', () => {
  if (passwordInput.value) validatePassword(false);
});

/* ============================================================
   TOGGLE PASSWORD VISIBILITY
   ============================================================ */
togglePwBtn.addEventListener('click', () => {
  const isHidden = passwordInput.type === 'password';
  passwordInput.type = isHidden ? 'text' : 'password';
  eyeIcon.textContent = isHidden ? '🙈' : '👁️';
  passwordInput.focus();
});

/* ============================================================
   CLEAR MESSAGES ON INPUT
   ============================================================ */
[emailInput, passwordInput].forEach(el => {
  el.addEventListener('input', () => hideMessage(formError));
});

/* ============================================================
   SHOW / HIDE MESSAGES
   ============================================================ */
function showMessage(el, text, type = 'error') {
  el.innerHTML = (type === 'error' ? '⚠ ' : '✓ ') + text;
  el.classList.add('show');
}
function hideMessage(el) {
  el.classList.remove('show');
}

/* ============================================================
   LOADING STATE
   ============================================================ */
function setLoading(on) {
  loginBtn.disabled = on;
  loginBtn.classList.toggle('loading', on);
}

/* ============================================================
   REMEMBER ME — persist email
   ============================================================ */
(function restoreEmail() {
  const saved = localStorage.getItem('mf_remember_email');
  if (saved) {
    emailInput.value = saved;
    rememberMe.checked = true;
    validateEmail(false);
  }
})();

/* ============================================================
   FORM SUBMIT
   ============================================================ */
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideMessage(formError);
  hideMessage(formSuccess);

  // Full validation
  const emailOk    = validateEmail(false);
  const passwordOk = validatePassword(false);
  if (!emailOk || !passwordOk) return;

  const email    = emailInput.value.trim();
  const password = passwordInput.value;

  // Remember me
  if (rememberMe.checked) {
    localStorage.setItem('mf_remember_email', email);
  } else {
    localStorage.removeItem('mf_remember_email');
  }

  setLoading(true);

  try {
    /* ── Real API call (uncomment when backend is ready) ──
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, remember_me: rememberMe.checked })
    });
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.message || 'Login failed. Please try again.');
    }

    // Store token
    const storage = rememberMe.checked ? localStorage : sessionStorage;
    storage.setItem('mf_token', data.access_token);
    storage.setItem('mf_user', JSON.stringify(data.user));
    ── end API call ── */

    // ── Demo simulation (remove when backend is ready) ──
    await simulateLogin(email, password);

    showMessage(formSuccess, 'Login successful! Redirecting to your dashboard…', 'success');

    // Redirect after short delay
    setTimeout(() => {
      window.location.href = './dashboard.html';
    }, 1200);

  } catch (err) {
    setLoading(false);
    showMessage(formError, err.message || 'Something went wrong. Please try again.');

    // Shake the form card
    const card = document.querySelector('.form-card');
    card.style.animation = 'none';
    card.offsetHeight; // reflow
    card.style.animation = 'shake 0.4s ease';
  }
});

/* ── Demo login simulation ── */
function simulateLogin(email, password) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Demo credentials
      if (email === 'sarah@demo.com' && password === 'Password123!') {
        resolve({ token: 'demo_token_123', user: { name: 'Sarah Williams', email } });
      } else if (email.includes('@') && password.length >= 6) {
        // Accept any valid-format credentials for demo
        resolve({ token: 'demo_token_456', user: { name: 'Demo User', email } });
      } else {
        reject(new Error('Invalid email or password. Try: sarah@demo.com / Password123!'));
      }
    }, 1600);
  });
}

/* ── Shake animation ── */
const styleEl = document.createElement('style');
styleEl.textContent = `
  @keyframes shake {
    0%,100% { transform: translateX(0); }
    20%      { transform: translateX(-8px); }
    40%      { transform: translateX(8px); }
    60%      { transform: translateX(-5px); }
    80%      { transform: translateX(5px); }
  }
`;
document.head.appendChild(styleEl);

/* ============================================================
   SOCIAL LOGIN BUTTONS (placeholder)
   ============================================================ */
googleBtn.addEventListener('click', () => {
  // TODO: Implement Google OAuth
  showMessage(formError, 'Google login coming soon! Use email/password for now.');
});
appleBtn.addEventListener('click', () => {
  // TODO: Implement Apple OAuth
  showMessage(formError, 'Apple login coming soon! Use email/password for now.');
});

/* ============================================================
   KEYBOARD SHORTCUT — Enter on email jumps to password
   ============================================================ */
emailInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    passwordInput.focus();
  }
});

/* ============================================================
   INPUT FIELD FOCUS EFFECTS
   ============================================================ */
[emailInput, passwordInput].forEach(input => {
  input.addEventListener('focus', () => {
    input.closest('.field-wrap').style.transform = 'scale(1.01)';
  });
  input.addEventListener('blur', () => {
    input.closest('.field-wrap').style.transform = 'scale(1)';
  });
});

/* ============================================================
   AUTH GUARD — redirect if already logged in
   ============================================================ */
(function authGuard() {
  const token = localStorage.getItem('mf_token') || sessionStorage.getItem('mf_token');
  if (token) {
    window.location.href = './dashboard.html';
  }
})();
