// MaskButton.jsx
import React from 'react';
import './MaskButton.css';

const MaskButton = ({
  label = 'Start Now',
  onClick = () => {}
}) => {
  return (
    <div className="mask-button-container">
      <span className="mas" aria-hidden="true">{label}</span>
      <button
        type="button"
        className="mask-button"
        onClick={onClick}
        aria-label={label}
      >
        {label}
      </button>
    </div>
  );
};

export default React.memo(MaskButton);
