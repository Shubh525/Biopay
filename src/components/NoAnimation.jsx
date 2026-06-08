import React, { useEffect, useState } from 'react';
import './NoAnimation.css';

const phrases = ['Cash?', 'Card?', 'Problem!'];

function NoAnimation() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % phrases.length);
    }, 2500); 
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="animated-no-section">
      <div className="static-no">No</div>
      <div className="scrolling-word-container">
        <div
          className="scrolling-words"
          style={{ transform: `translateY(-${index * 8.5}vw)` }} 
        >
          {phrases.map((phrase, i) => (
            <div key={i} className="scrolling-word">
              {phrase}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default NoAnimation;
