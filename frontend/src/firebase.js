/**
 * Firebase — Phone Number Authentication
 *
 * Follows the official Firebase Phone Auth guide:
 * https://firebase.google.com/docs/auth/web/phone-auth
 *
 * Step 1 — Set up the reCAPTCHA verifier (RecaptchaVerifier)
 * Step 2 — Send OTP via signInWithPhoneNumber → get ConfirmationResult
 * Step 3 — Confirm the OTP via confirmationResult.confirm(code)
 *
 * Environment variables required in .env.local:
 *   VITE_FIREBASE_API_KEY
 *   VITE_FIREBASE_AUTH_DOMAIN
 *   VITE_FIREBASE_PROJECT_ID
 *   VITE_FIREBASE_STORAGE_BUCKET
 *   VITE_FIREBASE_APP_ID
 *   VITE_FIREBASE_MEASUREMENT_ID
 */

import { initializeApp } from 'firebase/app';
import {
  getAuth,
  RecaptchaVerifier,
  signInWithPhoneNumber,
} from 'firebase/auth';
import { getAnalytics } from 'firebase/analytics';

// ── App init ──────────────────────────────────────────────────────────────────

const firebaseConfig = {
  apiKey:        import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain:    import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId:     import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  appId:         import.meta.env.VITE_FIREBASE_APP_ID,
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
};

const app  = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Analytics — optional; crashes on localhost and with ad blockers, so always guard.
let analytics = null;
try {
  if (typeof window !== 'undefined' && !window.location.hostname.includes('localhost')) {
    analytics = getAnalytics(app);
  }
} catch (e) {
  console.warn('[Firebase] Analytics init skipped (non-critical):', e.message);
}

// ── Step 1: reCAPTCHA setup ───────────────────────────────────────────────────

/**
 * Initialise an *invisible* reCAPTCHA verifier and attach it to the given
 * DOM container element.
 *
 * Firebase docs requirement:
 *   • The container element MUST already be in the DOM when this is called.
 *   • For invisible reCAPTCHA the element can be a hidden <div>.
 *   • You must clear & recreate the verifier before every new OTP send
 *     (otherwise Firebase throws "reCAPTCHA has already been rendered").
 *
 * @param {string} containerId  - DOM id of the reCAPTCHA container element
 * @returns {RecaptchaVerifier}
 */
export function setupRecaptcha(containerId) {
  // Tear down any existing verifier before creating a new one (Firebase requirement)
  if (window.recaptchaVerifier) {
    try {
      window.recaptchaVerifier.clear();
      console.log('[Firebase] Previous reCAPTCHA verifier cleared.');
    } catch {
      // ignore — element may have already been removed
    }
    window.recaptchaVerifier = null;
  }

  console.log(`[Firebase] Creating RecaptchaVerifier on #${containerId}`);

  window.recaptchaVerifier = new RecaptchaVerifier(auth, containerId, {
    size: 'invisible',
    callback: () => {
      // reCAPTCHA solved — signInWithPhoneNumber will proceed automatically
      console.log('[Firebase] reCAPTCHA solved ✓');
    },
    'expired-callback': () => {
      console.warn('[Firebase] reCAPTCHA expired — user must retry.');
    },
  });

  return window.recaptchaVerifier;
}

// ── Step 2: Send OTP ──────────────────────────────────────────────────────────

/**
 * Send a one-time password to the given phone number via Firebase.
 *
 * Prerequisite: setupRecaptcha() MUST be called first on this page load.
 *
 * @param {string} phoneNumber  E.164 format, e.g. "+911234567890"
 * @returns {Promise<import('firebase/auth').ConfirmationResult>}
 *          Store the returned ConfirmationResult — you need it for Step 3.
 */
export async function sendOtp(phoneNumber) {
  const appVerifier = window.recaptchaVerifier;

  if (!appVerifier) {
    throw new Error(
      '[Firebase] reCAPTCHA not initialised. Call setupRecaptcha() before sendOtp().'
    );
  }

  console.log(`[Firebase] Sending OTP to ${phoneNumber} …`);

  try {
    const confirmationResult = await signInWithPhoneNumber(auth, phoneNumber, appVerifier);
    console.log('[Firebase] OTP sent successfully ✓  Store confirmationResult for verification.');
    return confirmationResult;
  } catch (err) {
    // Reset the verifier so the user can retry (Firebase requirement after failure)
    if (window.recaptchaVerifier) {
      try { window.recaptchaVerifier.clear(); } catch { /* ignore */ }
      window.recaptchaVerifier = null;
    }
    console.error('[Firebase] signInWithPhoneNumber failed:', err.code, err.message);
    throw err;   // re-throw so callers can handle auth/* error codes
  }
}

// ── Step 3: Verify OTP ────────────────────────────────────────────────────────
// Callers do:  await confirmationResult.confirm(otpCode)
// This is handled directly in Login.jsx / Register.jsx using the stored result.

export { auth, analytics };
export default app;
