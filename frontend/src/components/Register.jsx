import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import './Register.css';
import API_BASE from '../api.js';

export const Register = () => {
  const [email, setEmail] = useState('');
  const [number, setNumber] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const isMounted = useRef(true);
  const submitControllerRef = useRef(null);

  useEffect(() => {
    return () => {
      isMounted.current = false;
      submitControllerRef.current?.abort();
    };
  }, []);

  // 📝 Submit Form
  const handleSubmit = (e) => {
    e.preventDefault();

    if (loading) return;

    submitControllerRef.current = new AbortController();
    setLoading(true);

    axios.post(
      `${API_BASE}/api/register_user`,
      {
        username: name.trim(),
        email: email.trim(),
        phone: number.trim(),
        password
      },
      {
        timeout: 10000,
        signal: submitControllerRef.current.signal
      }
    )
      .then(response => {
        if (response.data.error) {
          if (isMounted.current) {
            alert(response.data.error);
          }
        } else {
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('name', name.trim());
          alert('🎉 Registration successful!');
          
          setName('');
          setEmail('');
          setNumber('');
          setPassword('');
          
          navigate('/login');
        }
      })
      .catch(err => {
        if (
          axios.isCancel(err) ||
          err.code === 'ERR_CANCELED'
        ) {
          return;
        }

        if (isMounted.current) {
          console.error('Registration failed:', err);
          alert(err.response?.data?.error || 'Something went wrong. Please try again.');
        }
      })
      .finally(() => {
        if (isMounted.current) {
          setLoading(false);
        }
      });
  };

  return (
    <div className="register-container">
      <video
        className="register-background-video"
        preload="metadata"
        autoPlay
        loop
        muted
        playsInline
        disablePictureInPicture
        onError={(e) => {
          console.error('Register video failed to load', e);
        }}
      >
        <source src="/videos/login.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      <div className="register-overlay">
        <div className="register-card">
          <h2 className="create-account-text">Create an Account</h2>

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
                minLength={2}
                maxLength={50}
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
                placeholder="Enter phone number"
                autoComplete="tel"
                inputMode="numeric"
                pattern="[0-9]{10}"
                minLength={10}
                maxLength={10}
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
                  title="Password must contain uppercase letter, lowercase letter, and number"
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

            <button type="submit" className="btn-primary" disabled={loading} aria-busy={loading}>
              {loading ? 'Registering...' : 'Register'}
            </button>
            
            <p className="register-link">
              Already have an account? <Link to="/login">Login</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;
