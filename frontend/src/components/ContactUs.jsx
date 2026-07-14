"use client";

import { useEffect, useState } from "react";
import "./ContactUs.css";
import teamPhoto from "../assets/images/17263.jpg";

export default function ContactUs() {
  const [isVisible, setIsVisible] = useState({
    hero: false,
    form: false,
    info: false,
    faq: false
  });


  useEffect(() => {
    const observerOptions = {
      threshold: 0.2,
      rootMargin: "0px 0px -100px 0px"
    };

    const observerCallback = (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const section = entry.target.dataset.section;

          if (section) {
            setIsVisible(prev => ({
              ...prev,
              [section]: true
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

    const sections = document.querySelectorAll('[data-section]');
    sections.forEach(section => observer.observe(section));

    return () => {
      sections.forEach(section => {
        observer.unobserve(section);
      });

      observer.disconnect();
    };
  }, []);


  const [focusedInput, setFocusedInput] = useState(null);

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (isSubmitting) return;

    try {
      setIsSubmitting(true);

      console.log(formData);

      alert("Message sent successfully!");

      setFormData({
        name: "",
        email: "",
        subject: "",
        message: "",
      });

    } catch (error) {
      console.error(error);

    } finally {
      setIsSubmitting(false);
    }
  };

  return (

    <div className="contact-us-page">

      <section
        className={`hero-section ${isVisible.hero ? 'visible' : ''}`}
        data-section="hero"
      >
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <h2 className="animated-title">Get In Touch With Connectbiopay</h2>
              <div className="animated-paragraph">
                <p>
                  Have questions about our biometric payment solutions? Ready to
                  transform your payment experience?
                </p>
                <p>
                  Our team is here to help you navigate the future of contactless
                  payments. Whether you're a business looking to implement Connectbiopay
                  or a curious individual wanting to learn more, we're just a
                  message away.
                </p>
                <p>
                  Reach out today and discover how connectbiopcan revolutionize your
                  payment experience with secure, simple palm biometric
                  technology.
                </p>
              </div>
            </div>

            <div className="hero-image">
              <img
                src={teamPhoto}
                alt="Contact Connectbiopay team"
                className="hero-img"
                loading="lazy"
                decoding="async"
              />

            </div>
          </div>
        </div>
      </section>


      <section
        className={`contact-form-section ${isVisible.form ? 'visible' : ''}`}
        data-section="form"
      >
        <div className="container">
          <h2 className="section-title">Send Us A Message</h2>
          <div className="contact-container">
            <div className="contact-form">

              <form onSubmit={handleSubmit}>

                <div className={`form-group ${focusedInput === 'name' ? 'focused' : ''}`}>
                  <label htmlFor="name" className="form-label">
                    <span className="label-text">Full Name</span>
                  </label>
                  <input
                    type="text"
                    id="name"
                    placeholder="Your name"
                    required
                    onFocus={() => setFocusedInput('name')}
                    onBlur={() => setFocusedInput(null)}
                  />
                  <div className="input-focus-effect"></div>
                </div>
                <div className={`form-group ${focusedInput === 'email' ? 'focused' : ''}`}>
                  <label htmlFor="email" className="form-label">
                    <span className="label-text">Email Address</span>
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    autoComplete="email"
                    placeholder="Your email"
                    required
                    maxLength={100}
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        email: e.target.value,
                      })
                    }
                    onFocus={() => setFocusedInput('email')}
                    onBlur={() => setFocusedInput(null)}
                  />
                  <div className="input-focus-effect"></div>
                </div>
                <div className={`form-group ${focusedInput === 'subject' ? 'focused' : ''}`}>
                  <label htmlFor="subject" className="form-label">
                    <span className="label-text">Subject</span>
                  </label>
                  <input
                    type="text"
                    id="subject"
                    name="subject"
                    placeholder="Subject"
                    required
                    maxLength={100}
                    value={formData.subject}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        subject: e.target.value,
                      })
                    }
                    onFocus={() => setFocusedInput('subject')}
                    onBlur={() => setFocusedInput(null)}
                  />
                  <div className="input-focus-effect"></div>
                </div>
                <div className={`form-group ${focusedInput === 'message' ? 'focused' : ''}`}>
                  <label htmlFor="message" className="form-label">
                    <span className="label-text">Message</span>
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    rows="5"
                    placeholder="Your message"
                    required
                    maxLength={1000}
                    value={formData.message}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        message: e.target.value,
                      })
                    }
                    onFocus={() => setFocusedInput('message')}
                    onBlur={() => setFocusedInput(null)}
                  ></textarea>
                  <div className="input-focus-effect"></div>
                </div>
                <button
                  type="submit"
                  className="submit-btn"
                  disabled={isSubmitting}
                >
                  <span className="btn-text">Send Message</span>
                  <span className="btn-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </span>
                </button>
              </form>
            </div>
            <div
              className={`contact-info ${isVisible.info ? 'visible' : ''}`}
              data-section="info"
            >
              <div className="info-item">
                <div className="info-icon">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    className="icon"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <div className="info-content">
                  <h3>Email Us</h3>
                  <p><a href="mailto:info@connectbiopay.com">info@connectbiopay.com</a></p>
                  <p><a href="mailto:support@connectbiopay.com">support@connectbiopay.com</a></p>
                </div>
              </div>
              <div className="info-item">
                <div className="info-icon">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    className="icon"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                    />
                  </svg>
                </div>
                <div className="info-content">
                  <h3>Call Us</h3>
                  <p><a href="tel:+919876543210">+91 98765 43210</a></p>
                  <p><a href="tel:+15551234567">+1 (555) 123-4567</a></p>
                </div>
              </div>
              <div className="info-item">
                <div className="info-icon">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    className="icon"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                </div>
                <div className="info-content">
                  <h3>Visit Us</h3>
                  <p>UPES Campus, Dehradun</p>
                  <p>Uttarakhand, India</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>


      <section
        className={`faq-section ${isVisible.faq ? 'visible' : ''}`}
        data-section="faq"
      >
        <div className="container">
          <h2 className="section-title">Frequently Asked Questions</h2>
          <div className="faq-container">
            <div className="faq-item">
              <h3>How secure is palm biometric technology?</h3>
              <p>
                Palm biometric technology is one of the most secure forms of
                biometric authentication. It captures thousands of unique data
                points that are nearly impossible to replicate. Our system also
                includes advanced liveness detection to prevent spoofing
                attempts.
              </p>
            </div>
            <div className="faq-item">
              <h3>How can businesses integrate Connectbiopay?</h3>
              <p>
                We offer seamless integration solutions for businesses of all
                sizes. Our team works directly with your technical staff to
                implement Connectbiopay into your existing payment infrastructure with
                minimal disruption to your operations.
              </p>
            </div>
            <div className="faq-item">
              <h3>Is my biometric data stored securely?</h3>
              <p>
                Absolutely. Connectbiopay employs end-to-end encryption and secure
                tokenization. Your biometric data is never stored as raw
                images—only as encrypted mathematical representations that
                cannot be reverse-engineered.
              </p>
            </div>
            <div className="faq-item">
              <h3>How long does implementation take?</h3>
              <p>
                Typical implementation timelines range from 2-4 weeks, depending
                on the complexity of your existing systems. Our team provides
                comprehensive support throughout the entire process.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
