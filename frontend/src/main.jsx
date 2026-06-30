import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';

import './App.css';
import './index.css';

import { RouteCompo } from './components/RouteCompo.jsx';
import { AuthProvider } from './components/AuthContext.jsx';

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element not found');
}

createRoot(rootElement).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={RouteCompo} />
    </AuthProvider>
  </StrictMode>
);
