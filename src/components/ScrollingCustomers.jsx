import React, { useState } from 'react';
import './ScrollingCustomers.css';

const customers = [
  {
    id: 'nischay',
    name: 'Nischay AG',
    role: 'Co-founder, Jar',
    image: '/customers/nischay.jpg',
    description: 'Jar helps users save small amounts of money every day.',
  },
  {
    id: 'aditya',
    name: 'Aditya Shankar',
    role: 'Co-founder, Doubtnut',
    image: '/customers/aditya.jpg',
    description: 'Doubtnut is revolutionizing learning for school students.',
  },
  {
    id: 'neha',
    name: 'Neha Tandon Sharma',
    role: 'Founder, Isadora Life',
    image: '/customers/neha.jpg',
    description: 'Isadora Life creates wellness products inspired by Ayurveda.',
  },
  {
    id: 'durlabh',
    name: 'Durlabh Rawat',
    role: 'Founder, Barosi',
    image: '/customers/durlabh.jpg',
    description: 'Barosi delivers fresh and authentic rural Indian food.',
  },
  {
    id: 'nikita',
    name: 'Nikita Gujral',
    role: 'Founder, AN Fashions',
    image: '/customers/nikita.jpg',
    description: 'AN Fashions crafts elegant, contemporary ethnic wear.',
  },
];

function ScrollingCustomers() {
  const [hovered, setHovered] = useState(null);

  const tripled = [...customers, ...customers, ...customers];

  return (
    <div className="scroll-container">
      <h2 className="heading">
        Biopay grows with <span className="highlight">you!</span>
      </h2>
      <p className="subheading">2,50,000+ Businesses</p>

      <div className="scroll-wrapper">
        <div className="scroll-track">
          {tripled.map((customer, index) => (
            <div className="customer-wrapper" key={`${customer.id}-${index}`}>
              <div
                className={`customer-card ${
                  hovered === `${customer.id}-${index}` ? 'active' : ''
                }`}
                onMouseEnter={() => setHovered(`${customer.id}-${index}`)}
                onMouseLeave={() => setHovered(null)}
              >
                <img src={customer.image} alt={customer.name} />
                <div className="customer-info">
                  <strong>{customer.name}</strong>
                  <p>{customer.role}</p>
                  {hovered === `${customer.id}-${index}` && (
                    <div className="description">{customer.description}</div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ScrollingCustomers;
