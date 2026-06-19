import React, { useEffect } from 'react';
import NavBar from './components/NavBar';
import { Outlet, useLocation } from 'react-router-dom';
import Footer from './components/Footer';

const Layout = () => {
  const location = useLocation();

  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (location.pathname === '/' && location.state?.scrollToTop) {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        window.scrollTo({ top: 0, behavior: 'auto' });
      }
    }
  }, [location.pathname, location.state]);

  return (
    <>
      <NavBar />
      <main id="main-content">
        <Outlet />
      </main>
      <Footer />
    </>
  );
};

export default Layout;
