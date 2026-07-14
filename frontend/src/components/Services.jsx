import React, { memo } from "react";
import "./Services.css";

const Services = () => {
  return (
    <main className="services-container" aria-labelledby="services-heading">
      <video
        className="services-background"
        autoPlay
        loop
        muted
        playsInline
        preload="metadata"
        disablePictureInPicture
        tabIndex={-1}
        aria-hidden="true"
        onError={() => {
          if (import.meta.env.DEV) {
            console.error("Services video failed to load");
          }
        }}
      >
        <source src="/videos/login.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      <div className="services-overlay">
        <div className="services-content">
          <h1 id="services-heading" className="services-title">
            Our Services
          </h1>
          <p className="services-subtitle">
            ConnectbioPay combines biometric authentication with secure digital payments.
          </p>

          <div className="services-grid" role="list">
            <article className="service-card" role="listitem">
              <h3>🔐 Biometric Authentication</h3>
              <p>
                Secure access using Fujitsu PalmSecure sensors with advanced AES encryption and
                real-time verification.
              </p>
            </article>

            <article className="service-card" role="listitem">
              <h3>💳 Contactless Payments</h3>
              <p>
                Enable instant, touch-free transactions using your palm as a unique identifier —
                no cards or phones required.
              </p>
            </article>

            <article className="service-card" role="listitem">
              <h3>📊 Analytics Dashboard</h3>
              <p>
                View transaction insights, user authentication stats, and live performance
                metrics through our secure web dashboard.
              </p>
            </article>

            <article className="service-card" role="listitem">
              <h3>🧠 AI-Powered Fraud Detection</h3>
              <p>
                Detect unusual behavior and prevent fraudulent activity using machine learning
                integrated into every scan.
              </p>
            </article>
          </div>
        </div>
      </div>
    </main>
  );
};

export default memo(Services);
