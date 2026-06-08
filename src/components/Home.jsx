import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from "./AuthContext";
import axios from 'axios';
import './Home.css';

import backgroundImage from '../assets/images/backgroundok.png';
import homeImage from '../assets/images/home1.png';
import thumbVideo from '../assets/images/thumbok.mp4';
import HeroVideoMask from '../assets/images/thru.mp4';
import backleft from '../assets/images/backleft.mp4';

import MagneticButton from './MagneticButton';
import NoAnimation from './NoAnimation';
// import ScrollingCustomers from './ScrollingCustomers';

import { motion, AnimatePresence } from 'framer-motion';

export const Home = () => {
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const [isPageReady, setIsPageReady] = useState(false);
  const { isLoggedIn, handleLogout } = useAuth();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.get('/routes/home', { headers: { Authorization: `Bearer ${token}` } })
        .then(res => {
          setMessage(res.data.msg);
          setIsLoggedIn(true);
          setTimeout(() => setIsPageReady(true), 200);
        })
        .catch(() => {
          localStorage.removeItem('token');
          setIsPageReady(true);
        });
    } else {
      setIsPageReady(true);
    }
  }, []);



  if (!isPageReady) return <div className="homepage-container" style={{ opacity: 0 }} />;

  return (
    <AnimatePresence>
      <motion.div
        className="homepage-container"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}
      >
        {/* Hero Section */}
        <div className="hero-section">
          <video
            className="hero-video-bg"
            src={thumbVideo}
            autoPlay
            loop
            muted
            playsInline
          />

          <div className="blur-bg"></div>

          <div className="homepage-text-only">
            <motion.div
              className="homepage-text-section"
              initial="hidden"
              animate="visible"
              variants={{
                hidden: {},
                visible: {
                  transition: {
                    staggerChildren: 0.6,
                    delayChildren: 0.2,
                  },
                },
              }}
            >
              <motion.h1 className="homepage-heading glow-text-animated">
                {["Begin your", "Biopay", "Journey today."].map((text, idx) => (
                  <motion.span
                    key={idx}
                    className={`font-${idx + 1}`}
                    variants={{
                      hidden: { opacity: 0, y: 20 },
                      visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
                    }}
                    style={{ display: 'block' }}
                  >
                    {text}
                  </motion.span>
                ))}
              </motion.h1>

              <motion.div
                variants={{
                  hidden: { opacity: 0, y: 20 },
                  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
                }}
              >
                {isLoggedIn ? (
                  <button className="home-button white-button" onClick={handleLogout}>
                    Logout
                  </button>
                ) : (
                  <MagneticButton label="Start Now" onClick={() => navigate('/login')} />
                )}
              </motion.div>
            </motion.div>
          </div>
        </div>

        {/* Scroll Overlay Section */}
        <div className="scroll-overlay">
          {/* Left Column */}
          <div className="left-pane">
            <video
              className="left-pane-bg-video"
              src={backleft}
              autoPlay
              muted
              loop
              playsInline
            />

            <NoAnimation />
            <motion.img
              src={homeImage}
              alt="Home Visual"
              className="home1-image"
            />
          </div>

          {/* Right Column */}
          <motion.div
            className="right-pane"
            initial={{ x: 100, opacity: 0 }}
            whileInView={{ x: 0, opacity: 1 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.8 }}
          >
            <div className="black-card hero-taglines-container">
              <p className="hero-tagline-bold very-large">Your Fingerprint Is the Future.</p>
              <p className="hero-tagline emphasis">
                No wallet. No phone. No passwords.<br />
                Just your fingerprint — your identity, your access, your payment.
              </p>
              <p className="hero-tagline-faded italic">
                Touch once. Pay instantly. Unlock anywhere.<br />
                No waiting. No typing. No compromises.
              </p>
              <p className="hero-tagline">
                Effortless. Secure. Built around you.
              </p>
              <p className="hero-tagline-bold">
                For users: instant trust.<br />
                For businesses: faster, smarter service.
              </p>
              <p className="hero-tagline emphasis">
                Encrypted by default. Trusted by design.<br />
                You’re always in control.
              </p>
              <p className="hero-tagline-bold highlight">
                Welcome to biometric freedom.<br />
                Fast. Frictionless. Limitless.
              </p>
            </div>
          </motion.div>
        </div>

        {/* Scrolling Customers */}
        <section className="scrolling-customers-section">
          {/* <ScrollingCustomers /> */}
        </section>
      </motion.div>
    </AnimatePresence>
  );
};
