import React, { memo, useEffect, useRef } from 'react';
import './MagneticButton.css';

const PARTICLE_COUNT = 20;

function seededRandom(seed) {
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

const MagneticButton = ({
  label = 'Start Now',
  onClick = () => {}
}) => {
  const particleFieldRef = useRef(null);

  useEffect(() => {
    const field = particleFieldRef.current;
    if (!field) return;
    field.replaceChildren();

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';

      const randX = seededRandom(i) * 100 - 50;  
      const randY = seededRandom(i + 100) * 80 - 40;
      const randDur = 1 + seededRandom(i + 200) * 2;

      particle.style.setProperty('--x', `${randX}px`);
      particle.style.setProperty('--y', `${randY}px`);
      particle.style.animation = `particleFloat ${randDur}s infinite`;
      particle.style.left = '50%';
      particle.style.top = '50%';

      field.appendChild(particle);
    }

    return () => {
      if (field) {
        field.replaceChildren();
      }
    };
  }, []);

  return (
    <div className="btn-container">
      <div className="particles-field" ref={particleFieldRef} aria-hidden="true"></div>
      <button
        type="button"
        className="btn magnetic white-button"
        onClick={onClick}
        aria-label={label}
      >
        {label}
      </button>
    </div>
  );
};

export default memo(MagneticButton);
