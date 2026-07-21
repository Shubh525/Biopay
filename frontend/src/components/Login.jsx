import React, {
  useState,
  useEffect,
  useCallback,
  useRef
} from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import './Login.css';
import { useAuth } from './AuthContext';
import API_BASE from '../api.js';
import { setupRecaptcha, sendOtp } from '../firebase.js';

// ── Country codes for Forgot Password dialog ──────────────────────────────────
const COUNTRY_CODES = [
  { code: '+91',  label: '🇮🇳 +91  India' },
  { code: '+1',   label: '🇺🇸 +1   USA / Canada' },
  { code: '+44',  label: '🇬🇧 +44  UK' },
  { code: '+971', label: '🇦🇪 +971 UAE' },
  { code: '+65',  label: '🇸🇬 +65  Singapore' },
  { code: '+61',  label: '🇦🇺 +61  Australia' },
  { code: '+49',  label: '🇩🇪 +49  Germany' },
  { code: '+33',  label: '🇫🇷 +33  France' },
  { code: '+81',  label: '🇯🇵 +81  Japan' },
  { code: '+86',  label: '🇨🇳 +86  China' },
  { code: '+55',  label: '🇧🇷 +55  Brazil' },
  { code: '+27',  label: '🇿🇦 +27  South Africa' },
  { code: '+234', label: '🇳🇬 +234 Nigeria' },
];

const Login = () => {
  // ── Shared state ──────────────────────────────────────────────────────────
  const [input, setInput]               = useState('');
  const [password, setPassword]         = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading]           = useState(false);
  const [errorMsg, setErrorMsg]         = useState('');
  const [successMsg, setSuccessMsg]     = useState('');
  const navigate = useNavigate();
  const { setUserName, setIsLoggedIn } = useAuth();
  const isMounted = useRef(true);

  // ── OTP step state ────────────────────────────────────────────────────────
  const [step, setStep]                         = useState('credentials'); // 'credentials' | 'otp' | 'google-phone'
  const [otp, setOtp]                           = useState('');
  const [phoneMasked, setPhoneMasked]           = useState('');
  const [phoneRaw, setPhoneRaw]                 = useState('');
  const [otpSending, setOtpSending]             = useState(false);
  const [resendCooldown, setResendCooldown]     = useState(0);
  const [confirmationResult, setConfirmationResult] = useState(null);

  // ── Google login state ────────────────────────────────────────────────────
  const [googleEmail, setGoogleEmail]   = useState('');
  const [googleId, setGoogleId]         = useState('');
  const [googleName, setGoogleName]     = useState('');
  const [googlePhone, setGooglePhone]   = useState('');

  // ── Forgot Password state ─────────────────────────────────────────────────
  const [forgotOpen, setForgotOpen]             = useState(false);
  const [forgotStep, setForgotStep]             = useState('phone'); // 'phone' | 'otp' | 'reset'
  const [forgotCountryCode, setForgotCountryCode] = useState('+91');
  const [forgotPhone, setForgotPhone]           = useState('');
  const [forgotOtp, setForgotOtp]               = useState('');
  const [forgotConfirmation, setForgotConfirmation] = useState(null);
  const [forgotNewPassword, setForgotNewPassword]   = useState('');
  const [forgotConfirmPassword, setForgotConfirmPassword] = useState('');
  const [forgotLoading, setForgotLoading]       = useState(false);
  const [forgotOtpSending, setForgotOtpSending] = useState(false);
  const [forgotResendCooldown, setForgotResendCooldown] = useState(0);
  const [forgotError, setForgotError]           = useState('');
  const [forgotShowNew, setForgotShowNew]       = useState(false);
  const [forgotShowConfirm, setForgotShowConfirm] = useState(false);

  // ── Clear errors on step transitions ─────────────────────────────────────
  useEffect(() => { setErrorMsg(''); }, [step]);
  useEffect(() => { setForgotError(''); }, [forgotStep]);

  // ── Auto-dismiss success message after 5 s ────────────────────────────────
  useEffect(() => {
    if (!successMsg) return;
    const t = setTimeout(() => setSuccessMsg(''), 5000);
    return () => clearTimeout(t);
  }, [successMsg]);

  // ── Resend cooldown — login OTP ───────────────────────────────────────────
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const t = setInterval(() => {
      setResendCooldown(prev => {
        if (prev <= 1) { clearInterval(t); return 0; }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(t);
  }, [resendCooldown]);

  // ── Resend cooldown — forgot password OTP ────────────────────────────────
  useEffect(() => {
    if (forgotResendCooldown <= 0) return;
    const t = setInterval(() => {
      setForgotResendCooldown(prev => {
        if (prev <= 1) { clearInterval(t); return 0; }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(t);
  }, [forgotResendCooldown]);

  // ── Firebase OTP sender (login / google flows) ───────────────────────────
  const firebaseSendOtp = async (phone) => {
    try {
      setOtpSending(true);
      const fullPhone = phone.startsWith('+') ? phone : `+91${phone}`;
      setupRecaptcha('recaptcha-container');
      const result = await sendOtp(fullPhone);
      setConfirmationResult(result);
      setResendCooldown(30);
      return true;
    } catch (err) {
      console.error('Firebase OTP error:', err);
      if (err.code === 'auth/too-many-requests') {
        setErrorMsg('Too many OTP requests. Please try again later.');
      } else if (err.code === 'auth/invalid-phone-number') {
        setErrorMsg('Invalid phone number format.');
      } else {
        setErrorMsg('Failed to send OTP. Please try again.');
      }
      return false;
    } finally {
      if (isMounted.current) setOtpSending(false);
    }
  };

  // ── Step 1: Submit credentials ────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;
    setErrorMsg('');
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/login`, {
        identifier: input.trim(),
        password,
      });
      const data = response.data;

      if (data.msg === 'user not registered' || data.msg === 'incorrect password') {
        setErrorMsg(data.msg);
        return;
      }

      if (data.otp_required) {
        setPhoneMasked(data.phone_masked);
        setPhoneRaw(data.phone);
        const sent = await firebaseSendOtp(data.phone);
        if (sent) setStep('otp');
        return;
      }

    } catch (error) {
      console.error('Login failed', error);
      setErrorMsg(
        error.response?.data?.msg ||
        error.response?.data?.error ||
        'Login failed. Please try again.'
      );
    } finally {
      if (isMounted.current) setLoading(false);
    }
  };

  // ── Step 2: Verify OTP ────────────────────────────────────────────────────
  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    if (loading || !otp.trim()) return;
    setLoading(true);
    try {
      if (!confirmationResult) {
        setErrorMsg('OTP session expired. Please log in again.');
        resetToCredentials();
        return;
      }
      await confirmationResult.confirm(otp.trim());

      const response = await axios.post(`${API_BASE}/api/login/verify-otp`, {
        identifier: input.trim(),
      });
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('name', response.data.name);
      setUserName(response.data.name);
      setIsLoggedIn(true);
      navigate('/home');
    } catch (error) {
      console.error('OTP verification failed', error);
      if (error.code === 'auth/invalid-verification-code') {
        setErrorMsg('Invalid OTP. Please try again.');
      } else if (error.code === 'auth/code-expired') {
        setErrorMsg('OTP expired. Please resend.');
      } else {
        setErrorMsg(error.response?.data?.error || 'Verification failed. Please try again.');
      }
    } finally {
      if (isMounted.current) setLoading(false);
    }
  };

  // ── Resend OTP (login) ────────────────────────────────────────────────────
  const handleResendOtp = async () => {
    if (resendCooldown > 0 || otpSending) return;
    await firebaseSendOtp(phoneRaw);
  };

  // ── Reset back to credentials ─────────────────────────────────────────────
  const resetToCredentials = () => {
    setStep('credentials');
    setOtp('');
    setPhoneMasked('');
    setPhoneRaw('');
    setConfirmationResult(null);
    setGoogleEmail('');
    setGoogleId('');
    setGooglePhone('');
    setGoogleName('');
    setLoading(false);
    setErrorMsg('');
  };

  // ── Google Login handler ──────────────────────────────────────────────────
  const handleGoogleResponse = useCallback(async (response) => {
    const token = response?.credential;
    if (!token) { setErrorMsg('Google login failed'); return; }

    let profile;
    try {
      profile = JSON.parse(atob(token.split('.')[1]));
    } catch {
      setErrorMsg('Invalid Google token');
      return;
    }

    const email = profile.email;
    const gId   = profile.sub;

    try {
      const res  = await axios.post(`${API_BASE}/api/google-login`, { email, google_id: gId });
      const data = res.data;

      if (data.error === 'PHONE_REQUIRED') {
        setGoogleEmail(email);
        setGoogleId(gId);
        setGoogleName(data.name || profile.name || '');
        setStep('google-phone');
        return;
      }

      if (data.otp_required) {
        setGoogleEmail(email);
        setGoogleId(gId);
        setGoogleName(data.name || '');
        setPhoneMasked(data.phone_masked);
        setPhoneRaw(data.phone);
        const sent = await firebaseSendOtp(data.phone);
        if (sent) {
          setStep('otp');
          setInput(email);
        }
        return;
      }
    } catch (err) {
      if (err.response?.data?.error === 'NO_BIO_REGISTRATION') {
        setErrorMsg('Google account not registered. Please register first.');
        navigate('/register');
      } else {
        setErrorMsg('Google login failed');
      }
    }
  }, [navigate]);

  // ── Google Login: Submit phone number ─────────────────────────────────────
  const handleGooglePhoneSubmit = async (e) => {
    e.preventDefault();
    if (loading || !googlePhone.trim()) return;
    setErrorMsg('');
    setLoading(true);
    try {
      const res  = await axios.post(`${API_BASE}/api/google-login`, {
        email:     googleEmail,
        google_id: googleId,
        phone:     googlePhone.trim(),
      });
      const data = res.data;
      if (data.otp_required) {
        setPhoneMasked(data.phone_masked);
        setPhoneRaw(data.phone);
        setGoogleName(data.name || googleName);
        const sent = await firebaseSendOtp(data.phone);
        if (sent) {
          setStep('otp');
          setInput(googleEmail);
        }
      }
    } catch (error) {
      console.error('Google phone submit failed', error);
      setErrorMsg(error.response?.data?.error || 'Failed to verify phone. Please try again.');
    } finally {
      if (isMounted.current) setLoading(false);
    }
  };

  // ── Google Login: Verify OTP ──────────────────────────────────────────────
  const handleGoogleOtpVerify = async (e) => {
    e.preventDefault();
    if (loading || !otp.trim()) return;
    setLoading(true);
    try {
      if (!confirmationResult) {
        setErrorMsg('OTP session expired. Please try again.');
        resetToCredentials();
        return;
      }
      await confirmationResult.confirm(otp.trim());

      const response = await axios.post(`${API_BASE}/api/google-login/verify-otp`, {
        email: googleEmail,
      });
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('name', response.data.name);
      setUserName(response.data.name);
      setIsLoggedIn(true);
      navigate('/home');
    } catch (error) {
      console.error('Google OTP verification failed', error);
      if (error.code === 'auth/invalid-verification-code') {
        setErrorMsg('Invalid OTP. Please try again.');
      } else {
        setErrorMsg(error.response?.data?.error || 'Verification failed.');
      }
    } finally {
      if (isMounted.current) setLoading(false);
    }
  };

  // ── Forgot Password: open / close ─────────────────────────────────────────
  const openForgotDialog = () => {
    setForgotOpen(true);
    setForgotStep('phone');
    setForgotPhone('');
    setForgotOtp('');
    setForgotNewPassword('');
    setForgotConfirmPassword('');
    setForgotConfirmation(null);
    setForgotError('');
    setForgotResendCooldown(0);
  };

  const closeForgotDialog = () => {
    setForgotOpen(false);
    setForgotStep('phone');
    setForgotError('');
    setForgotConfirmation(null);
  };

  // ── Forgot Password: Step A — Send OTP ───────────────────────────────────
  const handleForgotSendOtp = async (e) => {
    e.preventDefault();
    if (forgotOtpSending || !forgotPhone.trim()) return;
    setForgotError('');
    setForgotOtpSending(true);
    try {
      const fullPhone = `${forgotCountryCode}${forgotPhone.trim()}`;
      setupRecaptcha('forgot-recaptcha-container');
      const result = await sendOtp(fullPhone);
      setForgotConfirmation(result);
      setForgotResendCooldown(30);
      setForgotStep('otp');
    } catch (err) {
      console.error('Forgot OTP error:', err);
      if (err.code === 'auth/too-many-requests') {
        setForgotError('Too many requests. Please try again later.');
      } else if (err.code === 'auth/invalid-phone-number') {
        setForgotError('Invalid phone number.');
      } else {
        setForgotError('Failed to send OTP. Please try again.');
      }
    } finally {
      if (isMounted.current) setForgotOtpSending(false);
    }
  };

  // ── Forgot Password: Resend OTP ───────────────────────────────────────────
  const handleForgotResendOtp = async () => {
    if (forgotResendCooldown > 0 || forgotOtpSending) return;
    setForgotError('');
    setForgotOtpSending(true);
    try {
      const fullPhone = `${forgotCountryCode}${forgotPhone.trim()}`;
      setupRecaptcha('forgot-recaptcha-container');
      const result = await sendOtp(fullPhone);
      setForgotConfirmation(result);
      setForgotResendCooldown(30);
    } catch {
      setForgotError('Failed to resend OTP. Please try again.');
    } finally {
      if (isMounted.current) setForgotOtpSending(false);
    }
  };

  // ── Forgot Password: Step B — Verify OTP ─────────────────────────────────
  const handleForgotVerifyOtp = async (e) => {
    e.preventDefault();
    if (!forgotOtp.trim() || !forgotConfirmation) return;
    setForgotError('');
    setForgotLoading(true);
    try {
      await forgotConfirmation.confirm(forgotOtp.trim());
      setForgotStep('reset');
    } catch (err) {
      if (err.code === 'auth/invalid-verification-code') {
        setForgotError('Invalid OTP. Please try again.');
      } else if (err.code === 'auth/code-expired') {
        setForgotError('OTP expired. Please resend.');
      } else {
        setForgotError('Verification failed. Please try again.');
      }
    } finally {
      if (isMounted.current) setForgotLoading(false);
    }
  };

  // ── Forgot Password: Step C — Reset Password ──────────────────────────────
  const handleForgotReset = async (e) => {
    e.preventDefault();
    setForgotError('');
    if (forgotNewPassword !== forgotConfirmPassword) {
      setForgotError('Passwords do not match.');
      return;
    }
    if (forgotNewPassword.length < 8) {
      setForgotError('Password must be at least 8 characters.');
      return;
    }
    setForgotLoading(true);
    try {
      await axios.post(`${API_BASE}/api/reset-password`, {
        phone:       `${forgotCountryCode}${forgotPhone.trim()}`,
        newPassword: forgotNewPassword,
      });
      closeForgotDialog();
      setSuccessMsg('✓ Password reset successfully. Please log in with your new password.');
    } catch (err) {
      setForgotError(err.response?.data?.error || 'Password reset failed. Please try again.');
    } finally {
      if (isMounted.current) setForgotLoading(false);
    }
  };

  // ── Google SDK init ───────────────────────────────────────────────────────
  useEffect(() => {
    const initGoogle = () => {
      if (window.google && step === 'credentials') {
        window.google.accounts.id.initialize({
          client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
          callback: handleGoogleResponse,
        });
        const googleBtn = document.getElementById('googleBtn');
        if (googleBtn) {
          googleBtn.innerHTML = '';
          window.google.accounts.id.renderButton(googleBtn, {
            type: 'standard', theme: 'outline', size: 'large', width: 380,
          });
        }
      }
    };

    if (window.google) {
      initGoogle();
    } else {
      const script = document.createElement('script');
      script.src    = 'https://accounts.google.com/gsi/client';
      script.async  = true;
      script.defer  = true;
      script.onload = initGoogle;
      document.head.appendChild(script);
    }

    return () => {
      if (window.google) window.google.accounts.id.cancel();
    };
  }, [handleGoogleResponse, step]);

  useEffect(() => {
    return () => { isMounted.current = false; };
  }, []);

  const isGoogleFlow      = !!googleEmail;
  const otpSubmitHandler  = isGoogleFlow ? handleGoogleOtpVerify : handleVerifyOtp;

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="login-container">

      {/* Permanent invisible reCAPTCHA containers — always in the DOM */}
      <div id="recaptcha-container"        style={{ display: 'none' }} />
      <div id="forgot-recaptcha-container" style={{ display: 'none' }} />

      <video
        className="login-background-video"
        autoPlay loop muted playsInline preload="none" poster=""
        onError={(e) => console.error('Login video failed to load', e)}
      >
        <source src="/videos/login.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      <div className="login-overlay">
        <div className="login-card">

          {/* ─── STEP: Credentials ─── */}
          {step === 'credentials' && (
            <>
              <h1 className="welcome-text">Welcome Back</h1>

              {successMsg && <div className="auth-success">{successMsg}</div>}
              {errorMsg   && <div className="auth-error">{errorMsg}</div>}

              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label>Phone or Email</label>
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Enter phone or email"
                    autoComplete="username"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Password</label>
                  <div className="password-wrapper">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter password"
                      autoComplete="current-password"
                      required
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      aria-pressed={showPassword}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      onClick={() => setShowPassword(prev => !prev)}
                    >
                      {showPassword ? 'Hide' : 'Show'}
                    </button>
                  </div>
                </div>

                {/* Forgot Password link */}
                <button
                  type="button"
                  className="forgot-link"
                  onClick={openForgotDialog}
                >
                  Forgot Password?
                </button>

                <button
                  type="submit"
                  className="btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Logging In...' : 'Log In'}
                </button>

                {/* Google Sign-In */}
                <div className="google-wrapper">
                  <img
                    className="google-icon"
                    src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                    alt="Google sign in"
                  />
                  <span className="google-text">Sign in with Google</span>
                  <div id="googleBtn"></div>
                </div>

                <p className="register-link">
                  Don't have an account? <Link to="/register">Register</Link>
                </p>
              </form>
            </>
          )}

          {/* ─── STEP: OTP Verification ─── */}
          {step === 'otp' && (
            <>
              <h1 className="welcome-text">Verify OTP</h1>
              <p className="otp-subtitle">
                We've sent a verification code to<br />
                <span className="otp-phone-display">{phoneMasked}</span>
              </p>

              {errorMsg && <div className="auth-error">{errorMsg}</div>}

              <form onSubmit={otpSubmitHandler}>
                <div className="form-group">
                  <label>Enter OTP</label>
                  <input
                    type="text"
                    className="otp-input"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="● ● ● ● ● ●"
                    inputMode="numeric"
                    maxLength={6}
                    autoComplete="one-time-code"
                    autoFocus
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="btn-primary btn-verify"
                  disabled={loading || otp.length < 6}
                >
                  {loading ? 'Verifying...' : 'Verify & Login'}
                </button>

                <div className="otp-actions">
                  <button
                    type="button"
                    className="otp-resend-btn"
                    onClick={handleResendOtp}
                    disabled={resendCooldown > 0 || otpSending}
                  >
                    {otpSending
                      ? 'Sending...'
                      : resendCooldown > 0
                        ? `Resend OTP in ${resendCooldown}s`
                        : 'Resend OTP'}
                  </button>

                  <button
                    type="button"
                    className="otp-back-btn"
                    onClick={resetToCredentials}
                  >
                    ← Back to Login
                  </button>
                </div>
              </form>
            </>
          )}

          {/* ─── STEP: Google Login — Enter Phone ─── */}
          {step === 'google-phone' && (
            <>
              <h1 className="welcome-text">Phone Verification</h1>
              <p className="otp-subtitle">
                Enter your phone number to verify your Google account
              </p>

              {errorMsg && <div className="auth-error">{errorMsg}</div>}

              <form onSubmit={handleGooglePhoneSubmit}>
                <div className="form-group">
                  <label>Phone Number</label>
                  <input
                    type="tel"
                    value={googlePhone}
                    onChange={(e) => setGooglePhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                    placeholder="Enter 10-digit phone number"
                    inputMode="numeric"
                    pattern="[0-9]{10}"
                    minLength={10}
                    maxLength={10}
                    autoFocus
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="btn-primary btn-verify"
                  disabled={loading || googlePhone.length < 10}
                >
                  {loading ? 'Sending OTP...' : 'Send OTP'}
                </button>

                <div className="otp-actions">
                  <button
                    type="button"
                    className="otp-back-btn"
                    onClick={resetToCredentials}
                  >
                    ← Back to Login
                  </button>
                </div>
              </form>
            </>
          )}

        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════════════════
          FORGOT PASSWORD DIALOG
      ═══════════════════════════════════════════════════════════════════ */}
      {forgotOpen && (
        <div
          className="forgot-overlay"
          onClick={(e) => { if (e.target === e.currentTarget) closeForgotDialog(); }}
        >
          <div className="forgot-dialog">

            {/* Progress steps indicator */}
            <div className="forgot-steps">
              {['phone', 'otp', 'reset'].map((s, i) => (
                <div
                  key={s}
                  className={`forgot-step-dot ${forgotStep === s ? 'active' : ''} ${['phone', 'otp', 'reset'].indexOf(forgotStep) > i ? 'done' : ''}`}
                />
              ))}
            </div>

            {/* Close button */}
            <button
              className="forgot-close-btn"
              onClick={closeForgotDialog}
              aria-label="Close dialog"
            >
              ✕
            </button>

            {/* ── Step A: Phone Input ── */}
            {forgotStep === 'phone' && (
              <>
                <h2 className="forgot-title">Forgot Password</h2>
                <p className="forgot-subtitle">
                  Enter the phone number linked to your account. We'll send an OTP to verify it's you.
                </p>

                {forgotError && <div className="auth-error">{forgotError}</div>}

                <form onSubmit={handleForgotSendOtp}>
                  <div className="form-group">
                    <label>Country Code</label>
                    <select
                      className="country-code-select"
                      value={forgotCountryCode}
                      onChange={(e) => setForgotCountryCode(e.target.value)}
                    >
                      {COUNTRY_CODES.map(({ code, label }) => (
                        <option key={code} value={code}>{label}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Phone Number</label>
                    <input
                      type="tel"
                      value={forgotPhone}
                      onChange={(e) => setForgotPhone(e.target.value.replace(/\D/g, '').slice(0, 15))}
                      placeholder="Enter your phone number"
                      inputMode="numeric"
                      autoFocus
                      required
                    />
                  </div>

                  <button
                    id="forgot-send-btn"
                    type="submit"
                    className="btn-primary btn-verify"
                    disabled={forgotOtpSending || forgotPhone.trim().length < 7}
                  >
                    {forgotOtpSending ? 'Sending OTP...' : 'Send OTP'}
                  </button>
                </form>
              </>
            )}

            {/* ── Step B: OTP Verification ── */}
            {forgotStep === 'otp' && (
              <>
                <h2 className="forgot-title">Enter OTP</h2>
                <p className="forgot-subtitle">
                  Code sent to{' '}
                  <strong>
                    {forgotCountryCode} {forgotPhone.replace(/(\d{3})(\d+)(\d{3})/, '$1•••$3')}
                  </strong>
                </p>

                {forgotError && <div className="auth-error">{forgotError}</div>}

                <form onSubmit={handleForgotVerifyOtp}>
                  <div className="form-group">
                    <label>Verification Code</label>
                    <input
                      type="text"
                      className="otp-input"
                      value={forgotOtp}
                      onChange={(e) => setForgotOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      placeholder="● ● ● ● ● ●"
                      inputMode="numeric"
                      maxLength={6}
                      autoComplete="one-time-code"
                      autoFocus
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    className="btn-primary btn-verify"
                    disabled={forgotLoading || forgotOtp.length < 6}
                  >
                    {forgotLoading ? 'Verifying...' : 'Verify OTP'}
                  </button>

                  <div className="otp-actions">
                    <button
                      type="button"
                      className="otp-resend-btn"
                      onClick={handleForgotResendOtp}
                      disabled={forgotResendCooldown > 0 || forgotOtpSending}
                    >
                      {forgotOtpSending
                        ? 'Sending...'
                        : forgotResendCooldown > 0
                          ? `Resend in ${forgotResendCooldown}s`
                          : 'Resend OTP'}
                    </button>

                    <button
                      type="button"
                      className="otp-back-btn"
                      onClick={() => setForgotStep('phone')}
                    >
                      ← Change Number
                    </button>
                  </div>
                </form>
              </>
            )}

            {/* ── Step C: Set New Password ── */}
            {forgotStep === 'reset' && (
              <>
                <h2 className="forgot-title">Set New Password</h2>
                <p className="forgot-subtitle">
                  Choose a strong password — min 8 chars, one uppercase, one number.
                </p>

                {forgotError && <div className="auth-error">{forgotError}</div>}

                <form onSubmit={handleForgotReset}>
                  <div className="form-group">
                    <label>New Password</label>
                    <div className="password-wrapper">
                      <input
                        type={forgotShowNew ? 'text' : 'password'}
                        value={forgotNewPassword}
                        onChange={(e) => setForgotNewPassword(e.target.value)}
                        placeholder="Enter new password"
                        autoComplete="new-password"
                        minLength={8}
                        autoFocus
                        required
                      />
                      <button
                        type="button"
                        className="password-toggle"
                        onClick={() => setForgotShowNew(p => !p)}
                        aria-label={forgotShowNew ? 'Hide' : 'Show'}
                      >
                        {forgotShowNew ? 'Hide' : 'Show'}
                      </button>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Confirm Password</label>
                    <div className="password-wrapper">
                      <input
                        type={forgotShowConfirm ? 'text' : 'password'}
                        value={forgotConfirmPassword}
                        onChange={(e) => setForgotConfirmPassword(e.target.value)}
                        placeholder="Confirm new password"
                        autoComplete="new-password"
                        minLength={8}
                        required
                      />
                      <button
                        type="button"
                        className="password-toggle"
                        onClick={() => setForgotShowConfirm(p => !p)}
                        aria-label={forgotShowConfirm ? 'Hide' : 'Show'}
                      >
                        {forgotShowConfirm ? 'Hide' : 'Show'}
                      </button>
                    </div>
                  </div>

                  <button
                    type="submit"
                    className="btn-primary btn-verify"
                    disabled={forgotLoading || !forgotNewPassword || !forgotConfirmPassword}
                  >
                    {forgotLoading ? 'Resetting...' : 'Reset Password'}
                  </button>
                </form>
              </>
            )}

          </div>
        </div>
      )}

    </div>
  );
};

export default Login;
