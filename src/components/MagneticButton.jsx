import React, { useEffect, useRef } from 'react';
import './MagneticButton.css';

function seededRandom(seed) {
  const x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

const MagneticButton = ({ label = 'Start Now', onClick }) => {
  const particleFieldRef = useRef(null);

  useEffect(() => {
    const field = particleFieldRef.current;
    if (!field) return;
    field.innerHTML = '';

    const particleCount = 20;

    for (let i = 0; i < particleCount; i++) {
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
  }, []);

  return (
    <div className="btn-container">
      <div className="particles-field" ref={particleFieldRef}></div>
      <button className="btn magnetic white-button" onClick={onClick}>
        {label}
      </button>
    </div>
  );
};

export default MagneticButton;
