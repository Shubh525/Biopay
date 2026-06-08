// MaskButton.jsx
import React from 'react';
import './MaskButton.css';

const MaskButton = ({ label = 'Start Now', onClick }) => {
  return (
    <div className="mask-button-container">
      <span className="mas">{label}</span>
      <button type="button" className="mask-button" onClick={onClick}>
        {label}
      </button>
    </div>
  );
};

export default MaskButton;
