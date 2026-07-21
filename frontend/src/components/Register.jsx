import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import './Register.css';
import API_BASE from '../api.js';
import { setupRecaptcha, sendOtp } from '../firebase.js';
import { useAuth } from './AuthContext';

export const Register = () => {
  // ── Form state ────────────────────────────────────────────────────────────
  const [name, setName]           = useState('');
  const [email, setEmail]         = useState('');
  const [number, setNumber]       = useState('');
  const [password, setPassword]   = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading]     = useState(false);
  const [errorMsg, setErrorMsg]   = useState('');

  // ── OTP state ─────────────────────────────────────────────────────────────
  const [step, setStep]                     = useState('form'); // 'form' | 'otp'
  const [otp, setOtp]                       = useState('');
  const [otpSending, setOtpSending]         = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [confirmationResult, setConfirmationResult] = useState(null);
  const [registeredPhone, setRegisteredPhone] = useState(''); // E.164 from backend

  const navigate  = useNavigate();
  const { setUserName, setIsLoggedIn } = useAuth();
  const isMounted = useRef(true);
  const submitControllerRef = useRef(null);

  useEffect(() => {
    return () => {
      isMounted.current = false;
      submitControllerRef.current?.abort();
    };
  }, []);

  // ── Clear error on step change ────────────────────────────────────────────
  useEffect(() => { setErrorMsg(''); }, [step]);

  // ── Resend cooldown timer ─────────────────────────────────────────────────
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

  // ── Firebase OTP sender ───────────────────────────────────────────────────
  const firebaseSendOtp = async (phone) => {
    try {
      setOtpSending(true);
      // phone from backend is already E.164 (e.g. "+91XXXXXXXXXX")
      const fullPhone = phone.startsWith('+') ? phone : `+91${phone}`;
      setupRecaptcha('register-recaptcha-container');
      const result = await sendOtp(fullPhone);
      setConfirmationResult(result);
      setResendCooldown(30);
      return true;
    } catch (err) {
      console.error('Register OTP error:', err);
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

  // ── Step 1: Submit registration form ─────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading || otpSending) return;
    setErrorMsg('');

    submitControllerRef.current = new AbortController();
    setLoading(true);

    try {
      const response = await axios.post(
        `${API_BASE}/api/register_user`,
        {
          username: name.trim(),
          email:    email.trim(),
          phone:    number.trim(),
          password,
        },
        { timeout: 10000, signal: submitControllerRef.current.signal }
      );

      const data = response.data;

      if (data.error) {
        setErrorMsg(data.error);
        return;
      }

      if (data.otp_required) {
        setRegisteredPhone(data.phone); // E.164 phone from backend
        const sent = await firebaseSendOtp(data.phone);
        if (sent) setStep('otp');
        return;
      }

      setErrorMsg('Unexpected response. Please try again.');

    } catch (err) {
      if (axios.isCancel(err) || err.code === 'ERR_CANCELED') return;
      console.error('Registration failed:', err);
      setErrorMsg(err.response?.data?.error || 'Something went wrong. Please try again.');
    } finally {
      if (isMounted.current) setLoading(false);
    }
  };

  // ── Step 2: Verify OTP → auto-login ──────────────────────────────────────
  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    if (loading || !otp.trim()) return;
    setErrorMsg('');
    setLoading(true);
    try {
      if (!confirmationResult) {
        setErrorMsg('OTP session expired. Please register again.');
        setStep('form');
        return;
      }

      // Confirm OTP with Firebase
      await confirmationResult.confirm(otp.trim());

      // Firebase confirmed → get JWT from backend and auto-login
      const response = await axios.post(`${API_BASE}/api/register_user/verify-otp`, {
        phone: registeredPhone,
        email: email.trim(),
      });

      localStorage.setItem('token', response.data.token);
      localStorage.setItem('name', response.data.name);
      setUserName(response.data.name);
      setIsLoggedIn(true);
      navigate('/home');

    } catch (err) {
      console.error('OTP verify failed:', err);
      if (err.code === 'auth/invalid-verification-code') {
        setErrorMsg('Invalid OTP. Please try again.');
      } else if (err.code === 'auth/code-expired') {
        setErrorMsg('OTP expired. Please resend.');
      } else {
        setErrorMsg(err.response?.data?.error || 'Verification failed. Please try again.');
      }
    } finally {
      if (isMounted.current) setLoading(false);
    }
  };

  // ── Resend OTP ────────────────────────────────────────────────────────────
  const handleResend = async () => {
    if (resendCooldown > 0 || otpSending) return;
    await firebaseSendOtp(registeredPhone);
  };

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="register-container">

      {/* Permanent invisible reCAPTCHA container */}
      <div id="register-recaptcha-container" style={{ display: 'none' }} />

      <video
        className="register-background-video"
        preload="metadata" autoPlay loop muted playsInline disablePictureInPicture
        onError={(e) => console.error('Register video failed to load', e)}
      >
        <source src="/videos/login.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      <div className="register-overlay">
        <div className="register-card">

          {/* ── STEP: Registration Form ── */}
          {step === 'form' && (
            <>
              <h2 className="create-account-text">Create an Account</h2>
              {errorMsg && <div className="auth-error">{errorMsg}</div>}

              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label>Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    onBlur={(e) => setName(e.target.value.trim())}
                    placeholder="Enter Name"
                    autoComplete="name"
                    minLength={2} maxLength={50}
                    title="Enter your full name"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onBlur={(e) => setEmail(e.target.value.trim())}
                    placeholder="Enter email"
                    autoComplete="email"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Phone Number</label>
                  <input
                    type="tel"
                    value={number}
                    onChange={(e) => setNumber(e.target.value.replace(/\D/g, '').slice(0, 10))}
                    placeholder="Enter 10-digit phone number"
                    autoComplete="tel"
                    inputMode="numeric"
                    pattern="[0-9]{10}"
                    minLength={10} maxLength={10}
                    title="Enter a valid 10-digit phone number"
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
                      autoComplete="new-password"
                      minLength={8}
                      pattern="(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}"
                      title="Uppercase, lowercase, and a number — min 8 characters"
                      required
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() => setShowPassword(prev => !prev)}
                      aria-pressed={showPassword}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword ? 'Hide' : 'Show'}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn-primary"
                  disabled={loading || otpSending}
                  aria-busy={loading || otpSending}
                >
                  {(loading || otpSending) ? 'Sending OTP...' : 'Register'}
                </button>

                <p className="register-link">
                  Already have an account? <Link to="/login">Login</Link>
                </p>
              </form>
            </>
          )}

          {/* ── STEP: OTP Verification ── */}
          {step === 'otp' && (
            <>
              <h2 className="create-account-text">Verify Your Number</h2>
              <p className="otp-subtitle">
                We've sent a 6-digit code to<br />
                <span className="otp-phone-display">
                  {registeredPhone.replace(/(\+\d{2})(\d+)(\d{4})/, '$1 ••••••$3')}
                </span>
              </p>

              {errorMsg && <div className="auth-error">{errorMsg}</div>}

              <form onSubmit={handleVerifyOtp}>
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
                  {loading ? 'Verifying...' : 'Verify & Continue'}
                </button>

                <div className="otp-actions">
                  <button
                    type="button"
                    className="otp-resend-btn"
                    onClick={handleResend}
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
                    onClick={() => { setStep('form'); setOtp(''); }}
                  >
                    ← Back
                  </button>
                </div>
              </form>
            </>
          )}

        </div>
      </div>
    </div>
  );
};

export default Register;
