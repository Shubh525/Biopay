import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

function Footer() {
  useEffect(() => {
    const blobs = document.querySelectorAll(".footer-bg-blob");
    const footer = document.querySelector(".bunsen-footer");

    if (!footer) {
      return () => { };
    }

    let animationFrame= null;

    const handleMouseMove = (e) => {
      if (!blobs.length) return;
      const centerX = window.innerWidth / 2;
      const centerY = window.innerHeight / 2;
      const deltaX = e.clientX - centerX;
      const deltaY = e.clientY - centerY;

      if (animationFrame !== null) {
  cancelAnimationFrame(animationFrame);
}
      animationFrame = requestAnimationFrame(() => {
        blobs.forEach((blob, i) => {
          const movementFactor = 30 + i * 5;
          const x = deltaX / movementFactor;
          const y = deltaY / movementFactor;
          blob.style.transform = `translate(${x}px, ${y}px)`;
        });
      });
    };

    // Viewport detection logic
    let observer = null;

    if (window.IntersectionObserver) {
      observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              blobs.forEach((blob) => blob.classList.add('animate'));
            } else {
              blobs.forEach((blob) => blob.classList.remove('animate'));
            }
          });
        },

        {
          threshold: 0.2,
        }
      );
    }

    if (footer && observer) {
      observer.observe(footer);
    }

    window.addEventListener(
  "mousemove",
  handleMouseMove
);
    return () => {
      window.removeEventListener(
        "mousemove",
        handleMouseMove
      );

      if (animationFrame !== undefined) {
        cancelAnimationFrame(animationFrame);
      }
      if (
        footer &&
        observer &&
        document.body.contains(footer)
      ) {
        observer.unobserve(footer);
      }

      if (observer) {
        observer.disconnect();
      }
    };

  }, []);

  return (
    <footer
      className="bunsen-footer"
      aria-label="Site Footer"
    >

      <div className="footer-bg-blob blob-1"></div>
      <div className="footer-bg-blob blob-2"></div>
      <div className="footer-bg-blob blob-3"></div>
      <div className="footer-bg-blob blob-4"></div>
      <div className="footer-bg-blob blob-5"></div>
      <div className="footer-bg-blob blob-6"></div>
      <div className="footer-bg-blob blob-7"></div>
      <div className="footer-bg-blob blob-8"></div>

      <div className="cta-section">
        <h2 className="plain-heading floating-text">
          Ready to begin your journey?
        </h2>



        <Link
  to="/"
  state={{ scrollToTop: true }}
  className="cta-button"
>
  Get started&nbsp;&nbsp;→
</Link>
      </div>

      <div className="footer-main">
        <hr className="footer-divider" />

        <div className="footer-top-centered">
          <div className="footer-logo">
            <h2 className="solid-text">CONNECTBIOPAY</h2>



          </div>

          <div className="footer-columns">
            <div className="footer-col">
              <h4>What</h4>
              <ul>
                <li>
                  <Link to="/services">Services</Link>
                </li>
                <li>
                  <Link to="/work">Work</Link>
                </li>
              </ul>
            </div>

            <div className="footer-col">
              <h4>Who</h4>
              <ul>
                <li>
                  <Link to="/about-us">About Us</Link>
                </li>
              </ul>
            </div>

            <div className="footer-col">
              <h4>Connect</h4>
              <ul>
                <li>
                  <a
                    href="https://www.linkedin.com/company/connectbiopay/"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    LinkedIn
                  </a>
                </li>
                <li>
                  <Link to="/contact-us">Contact Us</Link>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="footer-bottom-center">
            <p><a href="mailto:connectbiopay@gmail.com">connectbiopay@gmail.com</a></p>
            <p><a href="tel:+911234567890">+91 12345 67890</a></p>

            <div className="footer-links">
              <a href="/" onClick={(e) => e.preventDefault()}>
                Terms & Conditions
              </a>

              <a href="/" onClick={(e) => e.preventDefault()}>
                Privacy Policy
              </a>
            </div>

            <p className="copyright">
              © Copyright 2025 CONNECTBIOPAY. All Rights Reserved.
            </p>
          </div>
        </div>
      </div>

      <div className="footer-fade-bottom"></div>
    </footer>
  );
}

export default Footer;
