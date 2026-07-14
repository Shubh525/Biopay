import React, { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion'; //  Import Framer Motion
import './HomePage.css';

function HomePage() {
  const navigate = useNavigate();

  const handleClick = useCallback(() => {
    navigate('/login');
  }, [navigate]);

  return (
    <motion.div
      className="homepage-container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
    >
      <div className="homepage-wrapper with-divider">

        {/* Animated Image */}
        <motion.div
          className="homepage-image-section"
          aria-hidden="true"
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: [0, -10, 0] }}
          transition={{
            duration: 2,
            repeat: Infinity,
            repeatType: "reverse",
          }}



        >
          <img
            src="/images/front.png"
            alt="Connectbiopay Homepage Illustration"
            className="front-image"
            loading="lazy"
            decoding="async"
            draggable="false"
            onError={(e) => {
              console.error("front.png failed to load");

              if (e.currentTarget.src.includes("fallback.png")) {
                e.currentTarget.style.display = "none";
                return;
              }

              e.currentTarget.onerror = null;
              e.currentTarget.src = "/images/fallback.png";
            }}
          />
        </motion.div>

        {/* Animated Divider */}
        <motion.div
          className="vertical-divider"
          initial={{ scaleY: 0 }}
          animate={{ scaleY: 1 }}
          transition={{ duration: 1 }}
        />

        {/* Animated Text Section */}
        <motion.div
          className="homepage-text-section"
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        >
          <h1 className="homepage-heading">
            Begin your<br />
            <span className="highlight-green">ConnectbioPay</span><br />
            Journey today
          </h1>

          <motion.button
            type="button"
            className="homepage-button"
            aria-label="Start ConnectbioPay Journey"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleClick}
          >
            Start Now
          </motion.button>
        </motion.div>
      </div>
    </motion.div>
  );
}

export default HomePage;
