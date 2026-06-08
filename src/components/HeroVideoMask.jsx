import React from 'react';
import './HeroVideoMask.css';
import videoBg from '../assets/images/thru.mp4';

const HeroVideoMask = () => {
  return (
    <div className="hero-wrapper">
      <video className="hero-video" autoPlay loop muted playsInline>
        <source src={videoBg} type="video/mp4" />
      </video>

      <div className="video-overlay" />

      <div className="video-text-mask">
        <h1 className="mask-text">BIOPAY</h1>
      </div>
    </div>
  );
};

export default HeroVideoMask;
