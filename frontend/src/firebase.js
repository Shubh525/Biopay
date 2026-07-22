/**
 * Firebase Configuration — Phone OTP Authentication
 *
 * This file initializes Firebase for phone number OTP verification
 * during login and Google login flows.
 *
 * Required environment variable:
 *   VITE_FIREBASE_API_KEY
 *   VITE_FIREBASE_AUTH_DOMAIN
 *   VITE_FIREBASE_PROJECT_ID
 *   VITE_FIREBASE_APP_ID
 *   VITE_FIREBASE_MEASUREMENT_ID
 *
 * Set these in .env.local (never commit .env.local).
 */

import { initializeApp } from 'firebase/app';
import { getAuth, RecaptchaVerifier, signInWithPhoneNumber } from 'firebase/auth';
import { getAnalytics } from 'firebase/analytics';

const firebaseConfig = {
  apiKey:        import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain:    import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId:     import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  appId:         import.meta.env.VITE_FIREBASE_APP_ID,
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID,
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// getAnalytics can throw on localhost AND in production (ad blockers, missing
// measurementId, unsupported browsers). Always wrap so OTP imports never break.
let analytics = null;
try {
  if (typeof window !== 'undefined' && !window.location.hostname.includes('localhost')) {
    analytics = getAnalytics(app);
  }
} catch (e) {
  console.warn('Firebase Analytics failed to initialize (non-critical):', e.message);
}

/**
 * Set up an invisible reCAPTCHA verifier on a given button element.
 * Must be called before sending OTP.
 *
 * @param {string} buttonId - The DOM ID of the button that triggers OTP
 * @returns {RecaptchaVerifier}
 */
export function setupRecaptcha(buttonId) {
  // Clear existing verifier if any
  if (window.recaptchaVerifier) {
    window.recaptchaVerifier.clear();
    window.recaptchaVerifier = null;
  }

  window.recaptchaVerifier = new RecaptchaVerifier(auth, buttonId, {
    size: 'invisible',
    callback: () => {
      // reCAPTCHA solved — will proceed with OTP
    },
    'expired-callback': () => {
      // Reset reCAPTCHA
      console.warn('reCAPTCHA expired — user needs to retry');
    },
  });

  return window.recaptchaVerifier;
}

/**
 * Send OTP to a phone number via Firebase.
 *
 * @param {string} phoneNumber - Full phone number with country code (e.g. "+911234567890")
 * @returns {Promise<import('firebase/auth').ConfirmationResult>}
 */
export async function sendOtp(phoneNumber) {
  const appVerifier = window.recaptchaVerifier;
  if (!appVerifier) {
    throw new Error('reCAPTCHA not initialized. Call setupRecaptcha first.');
  }
  return signInWithPhoneNumber(auth, phoneNumber, appVerifier);
}

export { auth, analytics };
export default app;
