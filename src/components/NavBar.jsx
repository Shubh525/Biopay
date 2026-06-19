import React, { useState, useEffect, useCallback } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { RxHamburgerMenu } from 'react-icons/rx';
import './Navbar.css';
import { useAuth } from './AuthContext';
import { motion, AnimatePresence } from 'framer-motion';

const NavBar = () => {
  const [showMenu, setShowMenu] = useState(false);
  const [showNavbar, setShowNavbar] = useState(false);
  const { isLoggedIn, userName, handleLogout } = useAuth();
  const location = useLocation();

  const isHomePage = location.pathname === '/home';

  useEffect(() => {
    const existing = document.querySelector(
      'link[href*="Montserrat"]'
    );

    if (!existing) {
      const fontLink = document.createElement('link');
      fontLink.href =
        'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap';
      fontLink.rel = 'stylesheet';

      document.head.appendChild(fontLink);
    }
  }, []);

  useEffect(() => {
    if (!isHomePage) return;
    const handleScroll = () => {
      setShowNavbar(window.scrollY > 30);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isHomePage]);

  useEffect(() => {
    if (!isHomePage) {
      setShowNavbar(true);
    }
  }, [isHomePage]);

  const handleMenuToggle = () => {
    setShowMenu(prev => !prev);
  };

  const closeMenu = useCallback(() => setShowMenu(false), []);

  return (
    <header className={`header-wrapper ${!isHomePage || showNavbar ? 'show' : ''}`}>
      <div className="Main-container" style={{ fontFamily: "'Montserrat', sans-serif" }}>
        
        <div className="logo-nav">
          <NavLink to="/home">
            <h3 className="logo-text">BioPay</h3>
          </NavLink>
        </div>

        <AnimatePresence>
          <motion.nav
            key="navbar"
            className={`nav-container ${showMenu ? 'menuMobile' : 'menuWeb'}`}
            aria-label="Primary navigation"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            <div className="nav1 left-links">
              <NavLink to="/home" onClick={closeMenu}>Home</NavLink>
              <NavLink to="/about-us" onClick={closeMenu}>About Us</NavLink>
              <NavLink to="/contact-us" onClick={closeMenu}>Contact Us</NavLink>
              {isLoggedIn && (
                <>
                  <NavLink to="/device-details" onClick={closeMenu}>Device Details</NavLink>
                  <NavLink to="/diagnostic" onClick={closeMenu}>Diagnostic</NavLink>
                </>
              )}
            </div>

            <div className="nav1 lognav">
              {isLoggedIn ? (
                <>
                  <span className="btnlogin" aria-label={`Welcome, ${userName || 'User'}`}>Welcome, {userName || 'User'}</span>
                  <button type="button" onClick={handleLogout} className="btnregister btnlogout">Logout</button>
                </>
              ) : (
                <>
                  <NavLink to="/login" className="btnlogin">Login</NavLink>
                  <NavLink to="/register" className="btnregister">Register</NavLink>
                </>
              )}
            </div>
          </motion.nav>
        </AnimatePresence>

        <div className="ham-menu">
          <motion.button
            type="button"
            whileTap={{ scale: 0.85 }}
            onClick={handleMenuToggle}
            aria-label={showMenu ? 'Close menu' : 'Open menu'}
            aria-expanded={showMenu}
          >
            <RxHamburgerMenu />
          </motion.button>
        </div>
      </div>
    </header>
  );
};

export default NavBar;
