/**
 * Centralised API base URL.
 * Reads from the VITE_API_URL environment variable at build time.
 *
 * Local dev  → set VITE_API_URL=http://localhost:5000 in .env
 * Production → set VITE_API_URL=https://api.connectbiopay.com in Vercel dashboard
 *
 * Never hardcode http://localhost:5000 in components — always import from here.
 */
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export default API_BASE;
