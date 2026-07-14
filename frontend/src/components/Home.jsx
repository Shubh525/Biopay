import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from "./AuthContext";
import './Home.css';

import homeImage from '../assets/images/home1.webp';

import MagneticButton from './MagneticButton';
import NoAnimation from './NoAnimation';
// import ScrollingCustomers from './ScrollingCustomers';

import { motion, AnimatePresence } from 'framer-motion';

export const Home = () => {
  const navigate = useNavigate();

  const handleStartNow = useCallback(() => {
    navigate('/login');
  }, [navigate]);

  // Trust AuthContext for login state — no duplicate API call needed
  const { isLoggedIn, handleLogout } = useAuth();

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
            src="/videos/thumbok.mp4"
            autoPlay
            loop
            muted
            playsInline
            preload="none"
            poster=""
            onError={(e) => {
              console.error("Hero video failed to load", e);
            }}
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
                  <button
                    type="button"
                    className="home-button white-button"
                    onClick={handleLogout}
                  >
                    Logout
                  </button>
                ) : (
                  <MagneticButton
                    label="Start Now"
                    onClick={handleStartNow}
                  />
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
              src="/videos/backleft.mp4"
              autoPlay
              muted
              loop
              playsInline
              preload="none"
              poster=""
              onError={(e) => {
                console.error("Left video failed to load", e);
              }}
            />

            <NoAnimation />
            <motion.img
              src={homeImage}
              alt="Home Visual"
              className="home1-image"
              loading="lazy"
              draggable="false"
              onError={(e) => {
                e.currentTarget.style.display = "none";
              }}
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
