import React, { useMemo, useState, memo, useCallback } from 'react';
import './ScrollingCustomers.css';

const customers = [
  {
    id: 'nischay',
    name: 'Nischay AG',
    role: 'Co-founder, Jar',
    image: '/customers/nischay.webp',
    description: 'Jar helps users save small amounts of money every day.',
  },
  {
    id: 'aditya',
    name: 'Aditya Shankar',
    role: 'Co-founder, Doubtnut',
    image: '/customers/aditya.webp',
    description: 'Doubtnut is revolutionizing learning for school students.',
  },
  {
    id: 'neha',
    name: 'Neha Tandon Sharma',
    role: 'Founder, Isadora Life',
    image: '/customers/neha.webp',
    description: 'Isadora Life creates wellness products inspired by Ayurveda.',
  },
  {
    id: 'durlabh',
    name: 'Durlabh Rawat',
    role: 'Founder, Barosi',
    image: '/customers/durlabh.webp',
    description: 'Barosi delivers fresh and authentic rural Indian food.',
  },
  {
    id: 'nikita',
    name: 'Nikita Gujral',
    role: 'Founder, AN Fashions',
    image: '/customers/nikita.webp',
    description: 'AN Fashions crafts elegant, contemporary ethnic wear.',
  },
];

customers.forEach(Object.freeze);
Object.freeze(customers);

function ScrollingCustomers() {
  const [hovered, setHovered] = useState(null);

  const handleEnter = useCallback((id) => setHovered(id), []);
  const handleLeave = useCallback(() => setHovered(null), []);
  const handleTouchStart = useCallback((id) => {
    setHovered((prev) => (prev === id ? null : id));
  }, []);

  const tripled = useMemo(
    () => [...customers, ...customers, ...customers],
    []
  );

  return (
    <div className="scroll-container">
      <h2 className="heading">
        Connectbiopay grows with <span className="highlight">you!</span>
      </h2>
      <p className="subheading">2,50,000+ Businesses</p>

      <div className="scroll-wrapper">
        <div className="scroll-track">
          {tripled.map((customer, index) => {
            const cardId = `${customer.id}-${index}`;
            const isActive = hovered === cardId;

            return (
              <div className="customer-wrapper" key={cardId}>
                <div
                  className={`customer-card ${isActive ? 'active' : ''}`}
                  onMouseEnter={() => handleEnter(cardId)}
                  onMouseLeave={handleLeave}
                  onTouchStart={() => handleTouchStart(cardId)}
                  onTouchEnd={handleLeave}
                  onFocus={() => handleEnter(cardId)}
                  onBlur={handleLeave}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      setHovered((prev) => (prev === cardId ? null : cardId));
                    }
                  }}
                  tabIndex={0}
                  role="button"
                  aria-expanded={isActive}
                  aria-label={`${customer.name} - ${customer.role}`}
                >
                  <img
                    src={customer.image}
                    alt={customer.name}
                    loading="lazy"
                    decoding="async"
                    onError={(e) => {
                      if (
                        e.currentTarget.dataset.fallbackLoaded ===
                        'true'
                      ) {
                        e.currentTarget.parentElement?.classList.add(
                          'image-failed'
                        );
                        return;
                      }

                      e.currentTarget.dataset.fallbackLoaded = 'true';
                      e.currentTarget.src = '/customers/fallback.jpg';
                    }}
                  />
                  <div className="customer-info">
                    <strong>{customer.name}</strong>
                    <p>{customer.role}</p>
                    {isActive && (
                      <div className="description visible">
                        {customer.description}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default memo(ScrollingCustomers);
