import React, { memo, useEffect, useState } from 'react';
import './NoAnimation.css';

const phrases = ['Cash?', 'Card?', 'Problem!'];
const PHRASE_COUNT = phrases.length;

function NoAnimation() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (!PHRASE_COUNT) return;

    const interval = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % PHRASE_COUNT);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="animated-no-section">
      <div className="static-no">No</div>
      <div className="scrolling-word-container" aria-live="polite">
        <div
          className="scrolling-words"
          style={{ transform: `translateY(-${index * 8.5}vw)` }}
        >
          {phrases.map((phrase) => (
            <div key={phrase} className="scrolling-word">
              {phrase}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default memo(NoAnimation);
