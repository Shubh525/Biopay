import { Suspense } from 'react';
import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
} from "react-router-dom";

import Layout from "../Layout";
import PageNotFound from "./PageNotFound";
import RouteProtection from "./RouteProtection";

// Lazy-loaded page components — each page loads only when navigated to
import {
  Home,
  DeviceDetails,
  AboutUs,
  Diagnostic,
  Login,
  Register,
  HomePage,
  ContactUs,
  Services,
  Work,
} from './LazyLoadPages';

// Minimal loading fallback
const PageLoader = () => (
  <div style={{
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '60vh',
    color: '#888',
    fontSize: '1rem',
  }}>
    Loading&hellip;
  </div>
);

// Helper to wrap lazy components with Suspense
const Lazy = ({ children }) => (
  <Suspense fallback={<PageLoader />}>{children}</Suspense>
);

export const RouteCompo = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<Layout />}>
      {/* Default Route */}
      <Route index element={<Lazy><Home /></Lazy>} />

      {/* Main Routes */}
      <Route path="home" element={<Lazy><Home /></Lazy>} />
      <Route path="homepage" element={<Lazy><HomePage /></Lazy>} />
      <Route element={<RouteProtection />}>
        <Route path="device-details" element={<Lazy><DeviceDetails /></Lazy>} />
        <Route path="diagnostic" element={<Lazy><Diagnostic /></Lazy>} />
      </Route>
      <Route path="about-us" element={<Lazy><AboutUs /></Lazy>} />
      <Route path="contact-us" element={<Lazy><ContactUs /></Lazy>} />
      <Route path="services" element={<Lazy><Services /></Lazy>} />
      <Route path="work" element={<Lazy><Work /></Lazy>} />

      {/* Auth Routes */}
      <Route path="login" element={<Lazy><Login /></Lazy>} />
      <Route path="register" element={<Lazy><Register /></Lazy>} />

      {/* 404 Route */}
      <Route path="*" element={<PageNotFound />} />
    </Route>
  )
);