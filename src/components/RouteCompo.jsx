import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
} from "react-router-dom";

import Layout from "../Layout";
import PageNotFound from "./PageNotFound";
import { Home } from "./Home";
import DeviceDetails from "./DeviceDetails";
import AboutUs from "./AboutUs";
import Diagnostic from "./Diagnostic";
import Login from "./Login";
import { Register } from "./Register";
import HomePage from "./HomePage";
import ContactUs from "./ContactUs";
import Services from "./Services";
import Work from "./Work";
import RouteProtection from "./RouteProtection";

export const RouteCompo = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<Layout />}>
      {/* Default Route */}
      <Route index element={<Home />} />

      {/* Main Routes */}
      <Route path="home" element={<Home />} />
      <Route path="homepage" element={<HomePage />} />
      <Route element={<RouteProtection />}>
        <Route path="device-details" element={<DeviceDetails />} />
        <Route path="diagnostic" element={<Diagnostic />} />
      </Route>
      <Route path="about-us" element={<AboutUs />} />
      <Route path="contact-us" element={<ContactUs />} />
      <Route path="services" element={<Services />} />
      <Route path="work" element={<Work />} />

      {/* Auth Routes */}
      <Route path="login" element={<Login />} />
      <Route path="register" element={<Register />} />

      {/* 404 Route */}
      <Route path="*" element={<PageNotFound />} />
    </Route>
  )
);