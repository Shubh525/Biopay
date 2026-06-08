import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import loginVideo from '../assets/images/login.mp4'; // Background video
import './Register.css';

export const Register = () => {
  const [email, setEmail] = useState('');
  const [number, setNumber] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [bioId, setBioId] = useState('');
  const [scanning, setScanning] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  // 🖐 Scan Palm Vein
  const handleScanBioId = async () => {
    try {
      setScanning(true);
      const res = await axios.get('http://localhost:5000/api/scan_bio_id');
      if (res.data && res.data.bio_id_base64) {
        setBioId(res.data.bio_id_base64);
        alert('✅ Palm vein captured successfully!');
      } else {
        alert('Failed to capture palm vein. Please try again.');
      }
    } catch (err) {
      console.error('Scan error:', err);
      alert('Error capturing biometric data.');
    } finally {
      setScanning(false);
    }
  };

  // 📝 Submit Form
  const handleSubmit = (e) => {
    e.preventDefault();

    if (!bioId) {
      alert('Please scan or enter your palm vein ID before registering!');
      return;
    }

    axios.post('http://localhost:5000/api/register_user', {
      bio_id: bioId,
      username: name,
      email,
      phone: number,
      password
    })
      .then(response => {
        if (response.data.error) {
          alert(response.data.error);
        } else {
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('name', name);
          alert('🎉 Registration successful!');
          navigate('/login');
        }
      })
      .catch(err => {
        console.error('Registration failed:', err);
        alert('Something went wrong. Please try again.');
      });
  };

  return (
    <div className="register-container">
      <video className="register-background-video" autoPlay loop muted>
        <source src={loginVideo} type="video/mp4" />
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
                placeholder="Enter Name"
                required
              />
            </div>

            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter email"
                required
              />
            </div>

            <div className="form-group">
              <label>Phone Number</label>
              <input
                type="text"
                value={number}
                onChange={(e) => setNumber(e.target.value)}
                placeholder="Enter phone number"
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
                  required
                />
                <span onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? 'Hide' : 'Show'}
                </span>
              </div>
            </div>

            {/* 👇 Bio ID Input + Scan Button */}
            <div className="form-group">
              <label>Palm Vein Bio ID</label>
              <div className="bioid-wrapper">
                <input
                  type="text"
                  value={bioId}
                  onChange={(e) => setBioId(e.target.value)}
                  placeholder="Enter or scan palm vein ID"
                  required
                />
                <button
                  type="button"
                  className="btn-scan"
                  onClick={handleScanBioId}
                  disabled={scanning}
                >
                  {scanning ? 'Scanning...' : 'Scan Palm Vein'}
                </button>
              </div>
            </div>

            <button type="submit" className="btn-primary">Register</button>
            
            <p className="register-link">
              Already have an account? <Link to="/login">Login</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};
