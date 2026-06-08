import React, { useEffect } from 'react';
import NavBar from './components/NavBar';
import { Outlet, useLocation } from 'react-router-dom';
import Footer from './components/Footer';

const Layout = () => {
  const location = useLocation();

  useEffect(() => {
 
    if (location.pathname === '/' && location.state?.scrollToTop) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      window.scrollTo({ top: 0, behavior: 'auto' });
    }
  }, [location]);

  return (
    <>
      <NavBar />
      <main>
        <Outlet />
      </main>
      <Footer />
    </>
  );
};

export default Layout;
