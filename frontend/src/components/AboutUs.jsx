"use client";

import { useEffect, useState } from "react";
import "./AboutUs.css";

export default function AboutUs() {
  const [isVisible, setIsVisible] = useState({
    hero: false,
    vision: false,
    founder: false,
    video: false,
  });

  // Intersection Observer setup
  useEffect(() => {
    const observerOptions = {
      threshold: 0.2,
      rootMargin: "0px 0px -100px 0px",
    };

    const observerCallback = (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const section = entry.target.dataset.section;

          if (section) {
            setIsVisible((prev) => ({
              ...prev,
              [section]: true,
            }));
          }
        }
      });
    };

    if (!window.IntersectionObserver) return;

    const observer = new IntersectionObserver(
      observerCallback,
      observerOptions
    );

    // Observe all sections
    const sections = document.querySelectorAll("[data-section]");
    sections.forEach((section) => observer.observe(section));

    return () => {
      sections.forEach((section) => {
        observer.unobserve(section);
      });

      observer.disconnect();
    };
  }, []);

  return (
    <div className="about-us-page">
      {/* Hero Section */}
      <section
        className={`hero-section ${isVisible.hero ? "visible" : ""}`}
        data-section="hero"
      >
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <h2 className="animated-title">Connectbiopay| Secure. Simple. Pay.</h2>
              <div className="animated-paragraph">
                <p>
                  Redefining identity-driven payments through palm biometrics.
                </p>
                <p>
                  Connectbiopay is a next-gen biometric payment platform that enables
                  secure, contactless transactions using only your palm—no
                  cards, no phones, no passwords.
                </p>
                <p>
                  Built with enterprise-grade security and cutting-edge AI,
                  Connectbiopay replaces traditional authentication with
                  liveness-verified palm biometric verification. At the point of
                  payment, users simply scan their palm. Our advanced system
                  confirms identity using sophisticated palm pattern
                  recognition, backed by intelligent liveness detection to
                  eliminate fraud.
                </p>
              </div>
            </div>

            <div className="hero-image">
              <img
                src="/About-us/Connectbiopay-Fulcrum.jpg"
                alt="Biometric payment technology"
                className="hero-img"
                loading="lazy"
                decoding="async"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Vision Section */}
      <section
        className={`vision-section ${isVisible.vision ? "visible" : ""}`}
        data-section="vision"
      >
        <div className="container">
          <div className="vision-content">
            <h2 className="animated-title">Our Vision</h2>
            <p className="animated-paragraph">
              To make payments effortless, secure, and truly personal—by letting
              your identity become your wallet.
            </p>
          </div>
        </div>
      </section>

      {/* Meet The Founder Section */}
      <section
        className={`founder-section ${isVisible.founder ? "visible" : ""}`}
        data-section="founder"
      >
        <div className="container">
          <h2 className="section-title">Meet The Founder</h2>
          <div className="founder-content">
            <div className="founder-text">
              <p>
                "As a first-year student at UPES with a passion for fintech
                innovation, I founded Connectbiopay to revolutionize how we
                think about payment security and accessibility."
              </p>
              <p>
                Hailing from Gwalior, Madhya Pradesh, I combine fresh academic
                perspectives with entrepreneurial drive to build payment
                solutions that are both cutting-edge and user-friendly. My
                vision for  merges technical innovation with practical
                application, creating a system where your unique biometric
                identity becomes your most secure financial tool.
              </p>
              <div className="founder-info">
                <h3>Yuvraj Singh</h3>
                <p>CEO & Founder</p>
              </div>
            </div>
            <div className="founder-image">
              <img
                src="/About-us/Photo 2.svg"
                alt="Yuvraj Singh - CEO & Founder"
                className="founder-img"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Video Section */}
      <section
        className={`video-section ${isVisible.video ? "visible" : ""}`}
        data-section="video"
      >
        <div className="container">
          <div className="video-container">
            <div
              className="relative"
              style={{ maxWidth: "1500px", margin: "0 auto" }}
            >
              <video
                className="rounded-lg"
                style={{ width: "100%", height: "auto", maxHeight: "450px" }}
                controls
                autoPlay
                muted
                loop
                playsInline
                preload="metadata"
              >
                <source src="/About-us/landscape.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
