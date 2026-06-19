// AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    let isMounted = true;

    const verifyAuth = async () => {
      const token = localStorage.getItem('token');
      const name = localStorage.getItem('name');

      if (!token || !name) return;

      const controller = new AbortController();

      const timeout = setTimeout(() => {
        controller.abort();
      }, 5000);

      try {

        const res = await fetch('http://localhost:5000/api/auth/verify', {
          signal: controller.signal,
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) throw new Error('Invalid token');

        clearTimeout(timeout);

        if (isMounted) {
          setIsLoggedIn(true);
          setUserName(name);
        }
      } catch {
        clearTimeout(timeout);
        localStorage.removeItem('token');
        localStorage.removeItem('name');
        if (isMounted) {
          setIsLoggedIn(false);
          setUserName('');
        }
      }
    };

    verifyAuth();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    setIsLoggedIn(false);
    setUserName('');
    window.location.replace('/login');
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, userName, setIsLoggedIn, setUserName, handleLogout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return context;
};