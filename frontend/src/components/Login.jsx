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


const Login = () => {
  // ── Shared state ──
  const [input, setInput] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setUserName, setIsLoggedIn } = useAuth();
  const isMounted = useRef(true);

  // ── OTP step state ──
  const [step, setStep] = useState('credentials'); // 'credentials' | 'otp' | 'google-phone'
  const [otp, setOtp] = useState('');
  const [phoneMasked, setPhoneMasked] = useState('');
  const [phoneRaw, setPhoneRaw] = useState('');
  const [otpSending, setOtpSending] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [confirmationResult, setConfirmationResult] = useState(null);

  // ── Google login state ──
  const [googleEmail, setGoogleEmail] = useState('');
  const [googleId, setGoogleId] = useState('');
  const [googleName, setGoogleName] = useState('');
  const [googlePhone, setGooglePhone] = useState('');

  // ── Resend cooldown timer ──
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setInterval(() => {
      setResendCooldown(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [resendCooldown]);

  // ── Firebase OTP sender ──
  const firebaseSendOtp = async (phone) => {
    try {
      setOtpSending(true);
      const fullPhone = phone.startsWith('+') ? phone : `+91${phone}`;
      setupRecaptcha('otp-send-btn');
      const result = await sendOtp(fullPhone);
      setConfirmationResult(result);
      setResendCooldown(30);
      return true;
    } catch (err) {
      console.error('Firebase OTP error:', err);
      // Provide user-friendly message for common errors
      if (err.code === 'auth/too-many-requests') {
        alert('Too many OTP requests. Please try again later.');
      } else if (err.code === 'auth/invalid-phone-number') {
        alert('Invalid phone number format.');
      } else {
        alert('Failed to send OTP. Please try again.');
      }
      return false;
    } finally {
      if (isMounted.current) setOtpSending(false);
    }
  };

  // ── Step 1: Submit credentials ──
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/login`, {
        identifier: input.trim(),
        password: password
      });

      const data = response.data;

      if (data.msg === 'user not registered' || data.msg === 'incorrect password') {
        alert(data.msg);
        return;
      }

      if (data.otp_required) {
        setPhoneMasked(data.phone_masked);
        setPhoneRaw(data.phone);

        // Send OTP via Firebase
        const sent = await firebaseSendOtp(data.phone);
        if (sent) {
          setStep('otp');
        }
        return;
      }

    } catch (error) {
      console.error("Login failed", error);
      const msg = error.response?.data?.msg || error.response?.data?.error || "Login failed. Please try again.";
      alert(msg);
    } finally {
      if (isMounted.current) setLoading(false);
    }
  };

  // ── Step 2: Verify OTP ──
  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    if (loading || !otp.trim()) return;

    setLoading(true);
    try {
      // Verify OTP with Firebase
      if (!confirmationResult) {
        alert('OTP session expired. Please log in again.');
        resetToCredentials();
        return;
      }

      await confirmationResult.confirm(otp.trim());

      // Firebase verified — now get our JWT from backend
      const response = await axios.post(`${API_BASE}/api/login/verify-otp`, {
        identifier: input.trim()
      });

      localStorage.setItem("token", response.data.token);
      localStorage.setItem("name", response.data.name);
      setUserName(response.data.name);
      setIsLoggedIn(true);
      navigate('/home');

    } catch (error) {
      console.error("OTP verification failed", error);
      if (error.code === 'auth/invalid-verification-code') {
        alert('Invalid OTP. Please try again.');
      } else if (error.code === 'auth/code-expired') {
        alert('OTP expired. Please resend.');
      } else {
        alert(error.response?.data?.error || 'Verification failed. Please try again.');
      }
    } finally {
      if (isMounted.current) setLoading(false);
    }
  };

  // ── Resend OTP ──
  const handleResendOtp = async () => {
    if (resendCooldown > 0 || otpSending) return;
    await firebaseSendOtp(phoneRaw);
  };

  // ── Reset back to credentials ──
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
  };

  // ── Google Login handler ──
  const handleGoogleResponse = useCallback(async (response) => {
    const token = response?.credential;

    if (!token) {
      alert("Google login failed");
      return;
    }

    let profile;
    try {
      profile = JSON.parse(
        atob(token.split('.')[1])
      );
    } catch (err) {
      alert("Invalid Google token");
      return;
    }

    const email = profile.email;
    const gId = profile.sub;

    try {
      const res = await axios.post(`${API_BASE}/api/google-login`, {
        email: email,
        google_id: gId
      });

      const data = res.data;

      // User needs to provide phone number
      if (data.error === 'PHONE_REQUIRED') {
        setGoogleEmail(email);
        setGoogleId(gId);
        setGoogleName(data.name || profile.name || '');
        setStep('google-phone');
        return;
      }

      // OTP required for existing user with phone
      if (data.otp_required) {
        setGoogleEmail(email);
        setGoogleId(gId);
        setGoogleName(data.name || '');
        setPhoneMasked(data.phone_masked);
        setPhoneRaw(data.phone);

        const sent = await firebaseSendOtp(data.phone);
        if (sent) {
          setStep('otp');
          // Mark this as a Google login OTP flow
          setInput(email);
        }
        return;
      }

    } catch (err) {
      if (err.response?.data?.error === "NO_BIO_REGISTRATION") {
        alert("Google account not registered. Please register first.");
        navigate("/register");
      } else {
        alert("Google login failed");
      }
    }
  }, [navigate]);

  // ── Google Login: Submit phone number ──
  const handleGooglePhoneSubmit = async (e) => {
    e.preventDefault();
    if (loading || !googlePhone.trim()) return;

    setLoading(true);
    try {
      // Send phone to backend to save & get OTP flow
      const res = await axios.post(`${API_BASE}/api/google-login`, {
        email: googleEmail,
        google_id: googleId,
        phone: googlePhone.trim()
      });

      const data = res.data;
      if (data.otp_required) {
        setPhoneMasked(data.phone_masked);
        setPhoneRaw(data.phone);
        setGoogleName(data.name || googleName);

        const sent = await firebaseSendOtp(data.phone);
        if (sent) {
          setStep('otp');
          setInput(googleEmail); // Use email as identifier for OTP verification
        }
      }
    } catch (error) {
      console.error("Google phone submit failed", error);
      alert(error.response?.data?.error || "Failed to verify phone. Please try again.");
    } finally {
      if (isMounted.current) setLoading(false);
    }
  };

  // ── Google Login: Verify OTP ──
  const handleGoogleOtpVerify = async (e) => {
    e.preventDefault();
    if (loading || !otp.trim()) return;

    setLoading(true);
    try {
      if (!confirmationResult) {
        alert('OTP session expired. Please try again.');
        resetToCredentials();
        return;
      }

      await confirmationResult.confirm(otp.trim());

      // Firebase verified — get JWT from backend
      const response = await axios.post(`${API_BASE}/api/google-login/verify-otp`, {
        email: googleEmail
      });

      localStorage.setItem("token", response.data.token);
      localStorage.setItem("name", response.data.name);
      setUserName(response.data.name);
      setIsLoggedIn(true);
      navigate('/home');

    } catch (error) {
      console.error("Google OTP verification failed", error);
      if (error.code === 'auth/invalid-verification-code') {
        alert('Invalid OTP. Please try again.');
      } else {
        alert(error.response?.data?.error || 'Verification failed.');
      }
    } finally {
      if (isMounted.current) setLoading(false);
    }
  };

  // ── Google SDK init — dynamically load script ──
  useEffect(() => {
    let script = null;

    const initGoogle = () => {
      if (window.google && step === 'credentials') {
        window.google.accounts.id.initialize({
          client_id: "764744594384-acr8oe0tt7qhdfrl8088f3gai0s91330.apps.googleusercontent.com",
          callback: handleGoogleResponse,
        });

        const googleBtn = document.getElementById("googleBtn");
        if (googleBtn) {
          googleBtn.innerHTML = "";

          window.google.accounts.id.renderButton(
            googleBtn,
            {
              type: "standard",
              theme: "outline",
              size: "large",
              width: 380
            }
          );
        }
      }
    };

    // If Google SDK already loaded, init immediately
    if (window.google) {
      initGoogle();
    } else {
      // Dynamically load the Google Sign-In script
      script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = initGoogle;
      document.head.appendChild(script);
    }

    return () => {
      if (window.google) {
        window.google.accounts.id.cancel();
      }
    };
  }, [handleGoogleResponse, step]);

  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  // ── Determine which OTP verification handler to use ──
  const isGoogleFlow = !!googleEmail;
  const otpSubmitHandler = isGoogleFlow ? handleGoogleOtpVerify : handleVerifyOtp;

  return (
    <div className="login-container">
      <video
        className="login-background-video"
        autoPlay
        loop
        muted
        playsInline
        preload="none"
        poster=""
        onError={(e) => {
          console.error("Login video failed to load", e);
        }}
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

                <button
                  id="otp-send-btn"
                  type="submit"
                  className="btn-primary"
                  disabled={loading}
                >
                  {loading ? "Logging In..." : "Log In"}
                </button>

                {/* Real Google Button – must be visible for popup */}
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
                  {loading ? "Verifying..." : "Verify & Login"}
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
                  id="otp-send-btn"
                  type="submit"
                  className="btn-primary btn-verify"
                  disabled={loading || googlePhone.length < 10}
                >
                  {loading ? "Sending OTP..." : "Send OTP"}
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
    </div>
  );
};

export default Login;
