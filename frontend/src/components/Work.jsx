import React, { memo } from "react";
import "./Work.css";
import bgVideo from "../assets/images/login.mp4";

const Work = () => {
  return (
    <main className="work-container" aria-labelledby="work-heading" aria-describedby="work-subtitle">
      <video
        className="work-background"
        autoPlay
        loop
        muted
        playsInline
        preload="metadata"
        disablePictureInPicture
        tabIndex={-1}
        aria-hidden="true"
        onError={() => {
          if (typeof import.meta !== "undefined" && import.meta.env.DEV) {
            console.error("Work video failed to load");
          }
        }}
      >
        <source src={bgVideo} type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      <div className="work-overlay">
        <div className="work-content">
          <h1 id="work-heading" className="work-title">
            Our Work
          </h1>
          <p id="work-subtitle" className="work-subtitle">
            Real-world applications of ConnectbioPay in industries and organizations.
          </p>

          <div className="work-grid" role="list" aria-labelledby="work-heading">
            <article className="work-card" role="listitem">
              <h3>🏦 Banking & Finance</h3>
              <p>
                Integrated biometric payment authentication systems to improve transaction
                security and reduce card fraud.
              </p>
            </article>

            <article className="work-card" role="listitem">
              <h3>🏥 Healthcare</h3>
              <p>
                Enabled secure patient identification and record access through palm-based
                verification in hospitals and clinics.
              </p>
            </article>

            <article className="work-card" role="listitem">
              <h3>🏫 Education</h3>
              <p>
                Deployed student access systems for attendance, library, and cafeteria payments
                with seamless biometric validation.
              </p>
            </article>

            <article className="work-card" role="listitem">
              <h3>🏢 Corporate Access</h3>
              <p>
                Implemented secure entry and payroll systems for enterprise clients using palm
                vein authentication.
              </p>
            </article>
          </div>
        </div>
      </div>
    </main>
  );
};

export default memo(Work);
