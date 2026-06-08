import React, { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { RxHamburgerMenu } from 'react-icons/rx';
import logo from '../assets/images/logo.png';
import './Navbar.css';
import { useAuth } from './AuthContext';
import { motion, AnimatePresence } from 'framer-motion';

// Google Font Import (Injects Montserrat via JS)
const fontLink = document.createElement('link');
fontLink.href = 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap';
fontLink.rel = 'stylesheet';
document.head.appendChild(fontLink);

const NavBar = () => {
  const [showMenu, setShowMenu] = useState(false);
  const [showNavbar, setShowNavbar] = useState(false);
  const { isLoggedIn, userName, handleLogout } = useAuth();
  const location = useLocation();

  const isHomePage = location.pathname === '/home';

  useEffect(() => {
    if (!isHomePage) return;
    const handleScroll = () => {
      setShowNavbar(window.scrollY > 30);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isHomePage]);

  const handleMenuToggle = () => {
    setShowMenu(!showMenu);
  };

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
            key={showMenu ? 'menuMobile' : 'menuWeb'}
            className={`nav-container ${showMenu ? 'menuMobile' : 'menuWeb'}`}
            onClick={() => setShowMenu(false)}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            <div className="nav1 left-links">
              <NavLink to="/home">Home</NavLink>
              <NavLink to="/aboutUs">About Us</NavLink>
              <NavLink to="/contactUs">Contact Us</NavLink>
              {isLoggedIn && (
                <>
                  <NavLink to="/deviceDetails">Device Details</NavLink>
                  <NavLink to="/diagnostic">Diagnostic</NavLink>
                </>
              )}
            </div>

            <div className="nav1 lognav">
              {isLoggedIn ? (
                <>
                  <span className="btnlogin">Welcome, {userName}</span>
                  <button onClick={handleLogout} className="btnregister btnlogout">Logout</button>
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
            whileTap={{ scale: 0.85 }}
            onClick={handleMenuToggle}
            aria-label="Toggle menu"
          >
            <RxHamburgerMenu />
          </motion.button>
        </div>
      </div>
    </header>
  );
};

export default NavBar;
