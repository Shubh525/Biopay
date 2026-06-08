import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import './Login.css';
import loginVideo from '../assets/images/login.mp4';
import { useAuth } from './AuthContext';

const Login = () => {
  const [input, setInput] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const { setUserName, setIsLoggedIn } = useAuth();

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post("http://localhost:5000/api/login", {
      identifier: input,
      password: password
    })
    .then(response => {
      if (response.data.msg === 'user not register' || response.data.msg === 'incorrect password') {
        alert(response.data.msg);
      } else {
        localStorage.setItem("token", response.data.token);
        localStorage.setItem("name", response.data.name);
        setUserName(response.data.name);
        setIsLoggedIn(true);
        navigate('/home');
      }
      setInput('');
      setPassword('');
    })
    .catch(error => {
      console.error("Login failed", error);
      alert("Login failed. Please try again.");
    });
  };

  const handleGoogleResponse = async (response) => {
    const token = response.credential;
    const profile = JSON.parse(atob(token.split('.')[1]));
    const googleEmail = profile.email;
    const googleId = profile.sub;

    try {
      const res = await axios.post("http://localhost:5000/api/google-login", {
        email: googleEmail,
        google_id: googleId
      });

      localStorage.setItem("token", res.data.token);
      localStorage.setItem("name", res.data.name);
      setUserName(res.data.name);
      setIsLoggedIn(true);
      navigate("/home");
    } catch (err) {
      if (err.response?.data?.error === "NO_BIO_REGISTRATION") {
        alert("Google account not registered. Please register biometric.");
        navigate("/register");
      } else {
        alert("Google login failed");
      }
    }
  };

  useEffect(() => {
    if (window.google) {
      google.accounts.id.initialize({
        client_id: "764744594384-acr8oe0tt7qhdfrl8088f3gai0s91330.apps.googleusercontent.com",
        callback: handleGoogleResponse,
      });

      google.accounts.id.renderButton(
        document.getElementById("googleBtn"),
        {
          type: "standard",
          theme: "outline",
          size: "large",
          width: 380
        }
      );
    }
  }, []);

  return (
    <div className="login-container">
      <video className="login-background-video" autoPlay loop muted playsInline>
        <source src={loginVideo} type="video/mp4" />
      </video>

      <div className="login-overlay">
        <div className="login-card">
          <h1 className="welcome-text">Welcome Back</h1>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Phone or Email</label>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Enter phone or email"
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

            <button type="submit" className="btn-primary">Log In</button>

            {/* Real Google Button – must be visible for popup */}
            <div className="google-wrapper">
  <img
    className="google-icon"
    src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
  />
  <span className="google-text">Sign in with Google</span>
  <div id="googleBtn"></div>
</div>


            <p className="register-link">
              Don't have an account? <Link to="/register">Register</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
