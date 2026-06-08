import React from "react";
import "./Work.css";
import bgVideo from "../assets/images/login.mp4";

const Work = () => {
  return (
    <div className="work-container">
      <video className="work-background" autoPlay loop muted playsInline>
        <source src={bgVideo} type="video/mp4" />
      </video>

      <div className="work-overlay">
        <div className="work-content">
          <h1 className="work-title">Our Work</h1>
          <p className="work-subtitle">
            Real-world applications of BioPay in industries and organizations.
          </p>

          <div className="work-grid">
            <div className="work-card">
              <h3>🏦 Banking & Finance</h3>
              <p>
                Integrated biometric payment authentication systems to improve transaction
                security and reduce card fraud.
              </p>
            </div>

            <div className="work-card">
              <h3>🏥 Healthcare</h3>
              <p>
                Enabled secure patient identification and record access through palm-based
                verification in hospitals and clinics.
              </p>
            </div>

            <div className="work-card">
              <h3>🏫 Education</h3>
              <p>
                Deployed student access systems for attendance, library, and cafeteria payments
                with seamless biometric validation.
              </p>
            </div>

            <div className="work-card">
              <h3>🏢 Corporate Access</h3>
              <p>
                Implemented secure entry and payroll systems for enterprise clients using palm
                vein authentication.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Work;
