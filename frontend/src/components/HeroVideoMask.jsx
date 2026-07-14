import React from 'react';
import './HeroVideoMask.css';
import videoBg from '../assets/images/thru.mp4';

const HeroVideoMask = () => {
  return (
    <div className="hero-wrapper">
      <video
        className="hero-video"
        autoPlay
        loop
        muted
        playsInline
        preload="metadata"
        onError={() => {
          console.error("Video failed to load");
        }}
      >
        <source src={videoBg} type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      <div className="video-overlay" />

      <div className="video-text-mask">
        <h1
          className="mask-text"
          aria-label="CONNECTBIOPAY"
        >
          CONNECTBIOPAY
        </h1>
      </div>
    </div>
  );
};

export default HeroVideoMask;
