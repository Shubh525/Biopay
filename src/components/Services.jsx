import React from "react";
import "./Services.css";
import bgVideo from "../assets/images/login.mp4";

const Services = () => {
  return (
    <div className="services-container">
      <video className="services-background" autoPlay loop muted playsInline>
        <source src={bgVideo} type="video/mp4" />
      </video>

      <div className="services-overlay">
        <div className="services-content">
          <h1 className="services-title">Our Services</h1>
          <p className="services-subtitle">
            BioPay combines biometric authentication with secure digital payments.
          </p>

          <div className="services-grid">
            <div className="service-card">
              <h3>🔐 Biometric Authentication</h3>
              <p>
                Secure access using Fujitsu PalmSecure sensors with advanced AES encryption and
                real-time verification.
              </p>
            </div>

            <div className="service-card">
              <h3>💳 Contactless Payments</h3>
              <p>
                Enable instant, touch-free transactions using your palm as a unique identifier —
                no cards or phones required.
              </p>
            </div>

            <div className="service-card">
              <h3>📊 Analytics Dashboard</h3>
              <p>
                View transaction insights, user authentication stats, and live performance
                metrics through our secure web dashboard.
              </p>
            </div>

            <div className="service-card">
              <h3>🧠 AI-Powered Fraud Detection</h3>
              <p>
                Detect unusual behavior and prevent fraudulent activity using machine learning
                integrated into every scan.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Services;
