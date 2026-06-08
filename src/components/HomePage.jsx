import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion'; // ✅ Import Framer Motion
import './HomePage.css';

function HomePage() {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate('/login');
  };

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
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: [0, -10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <img
            src="/images/front.png"
            alt="Front Visual"
            className="front-image"
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
            <span className="highlight-green">BioPay</span><br />
            Journey today
          </h1>

          <motion.button
            className="homepage-button"
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
