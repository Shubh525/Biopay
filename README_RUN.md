# BioPay — Run Guide & Architecture

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| PostgreSQL | 14+ | Database |
| pip | latest | Python package manager |

---

## 1. Database Setup (PostgreSQL)

BioPay uses PostgreSQL. Create the database before starting the backend.

```sql
-- Run in psql or any PostgreSQL client
CREATE DATABASE palm_vein_auth;
```

The default connection string (used if `POSTGRES_URL` env var is not set):

```
postgresql://postgres:1234@localhost:5432/palm_vein_auth
```

> Change credentials in `backend/palm_secure/db.py` or set the `POSTGRES_URL` environment variable.

---

## 2. Backend (Flask + SocketIO)

```powershell
# Navigate to the backend directory
cd backend

# (Recommended) Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install all Python dependencies
pip install -r requirements.txt

# (Optional) Set environment variables
$env:SIMULATE = "true"                        # Use "true" for hardware simulation mode
$env:POSTGRES_URL = "postgresql://postgres:1234@localhost:5432/palm_vein_auth"
$env:PALM_AUTH_AES_KEY = "your_secret_aes_key"
$env:SESSION_SECRET = "your_session_secret"
$env:SMTP_EMAIL = "your@gmail.com"            # For OTP email sending
$env:SMTP_PASSWORD = "your_app_password"      # Gmail App Password

# Start the backend server
python main.py
```

The backend will start at:
- **Localhost** → http://127.0.0.1:5000
- **Network** → http://\<your-local-ip\>:5000

> **Simulation Mode**: Set `SIMULATE=true` to run without physical Fujitsu PalmSecure hardware. The server will return mock biometric data for testing.

---

## 3. Frontend (React + Vite)

Open a **new terminal** (keep the backend running):

```powershell
# From the project root (f:\biopay\biopay)
cd f:\biopay\biopay

# Install Node dependencies (only needed once)
npm install

# Start the development server
npm run dev
```

The frontend will be available at:
- **http://localhost:5173**

### Other Frontend Commands

```powershell
npm run build      # Build production bundle (outputs to /dist)
npm run preview    # Preview the production build locally
npm run lint       # Run ESLint
```

---

## 4. Running Both Together (Quick Start)

```powershell
# Terminal 1 — Backend
cd f:\biopay\biopay\backend
.\venv\Scripts\activate
python main.py

# Terminal 2 — Frontend
cd f:\biopay\biopay
npm run dev
```

---

## 5. Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `SIMULATE` | `false` | `true` = simulate biometric hardware |
| `POSTGRES_URL` | `postgresql://postgres:1234@localhost:5432/palm_vein_auth` | PostgreSQL connection string |
| `PALM_AUTH_AES_KEY` | `palm_vein_default_key_2025` | AES-256 key for bio template encryption |
| `SESSION_SECRET` | random | Flask session secret key |
| `SMTP_EMAIL` | — | Gmail address for OTP sending |
| `SMTP_PASSWORD` | — | Gmail App Password for OTP sending |
| `PORT` | `5000` | Backend server port |

---

---

# Architecture

## Overview

BioPay is a **full-stack biometric payment authentication system** that uses palm-vein scanning (Fujitsu PalmSecure SDK) to identify and authenticate users. It follows a classic **client-server** architecture with real-time WebSocket support.

```
┌────────────────────────────────────────────────────────┐
│                    USER BROWSER                        │
│         React 19 + Vite + TailwindCSS v4              │
│           (http://localhost:5173)                      │
└───────────────────┬────────────────────────────────────┘
                    │  HTTP REST + WebSocket (Socket.IO)
                    │  Axios (CORS: localhost:5173)
                    ▼
┌────────────────────────────────────────────────────────┐
│              FLASK BACKEND (Python)                    │
│         Flask + Flask-SocketIO + Eventlet              │
│           (http://0.0.0.0:5000)                       │
│                                                        │
│  ┌─────────────────┐   ┌────────────────────────────┐ │
│  │  REST API Layer │   │  WebSocket (SocketIO)      │ │
│  │  (demo_app.py)  │   │  Real-time device events   │ │
│  └────────┬────────┘   └────────────────────────────┘ │
│           │                                            │
│  ┌────────▼────────────────────────────────────────┐  │
│  │           palm_secure Package (SDK)             │  │
│  │  ┌──────────┐ ┌────────────┐ ┌──────────────┐  │  │
│  │  │ device.py│ │diagnostics │ │securityLayer │  │  │
│  │  │ (USB HW) │ │   .py      │ │   .py (AES)  │  │  │
│  │  └──────────┘ └────────────┘ └──────────────┘  │  │
│  │  ┌──────────┐ ┌────────────┐ ┌──────────────┐  │  │
│  │  │models.py │ │  db.py     │ │  jwt_utils   │  │  │
│  │  │(ORM)     │ │(SQLAlchemy)│ │  .py (PyJWT) │  │  │
│  │  └──────────┘ └────────────┘ └──────────────┘  │  │
│  └─────────────────────────────────────────────────┘  │
└───────────────────┬────────────────────────────────────┘
                    │  SQLAlchemy ORM
                    ▼
┌────────────────────────────────────────────────────────┐
│                  PostgreSQL Database                   │
│   Tables: users | transactions | contact_messages      │
└────────────────────────────────────────────────────────┘
                    ▲
                    │  USB (pyusb)
┌───────────────────┴────────────────────────────────────┐
│         Fujitsu PalmSecure Hardware Device             │
│         (or simulated via SIMULATE=true)               │
└────────────────────────────────────────────────────────┘
```

---

## Frontend Architecture

**Stack:** React 19 · React Router DOM v7 · Vite 7 · TailwindCSS v4 · Framer Motion · Axios · Socket.IO Client

### Page / Route Structure

| Route | Component | Description |
|-------|-----------|-------------|
| `/` or `/home` | `Home.jsx` | Landing page with hero, features |
| `/homepage` | `HomePage.jsx` | Post-login dashboard |
| `/login` | `Login.jsx` | Login with password or biometric |
| `/register` | `Register.jsx` | User registration with palm scan |
| `/deviceDetails` | `DeviceDetails.jsx` | Connected device info |
| `/diagnostic` | `Diagnostic.jsx` | Hardware diagnostics dashboard |
| `/aboutUs` | `AboutUs.jsx` | About page |
| `/contactUs` | `ContactUs.jsx` | Contact form |
| `/services` | `Services.jsx` | Services overview |
| `/work` | `Work.jsx` | How it works |

### Key Frontend Modules

| File | Role |
|------|------|
| `Layout.jsx` | Root layout wrapper with Navbar + Footer |
| `AuthContext.jsx` | Global auth state (JWT token, user info) |
| `NavBar.jsx` | Top navigation bar |
| `MagneticButton.jsx` | Animated magnetic hover button |
| `ScrollingCustomers.jsx` | Infinite logo scroll animation |

---

## Backend Architecture

**Stack:** Flask 3.1 · Flask-SocketIO · Flask-CORS · Flask-Limiter · SQLAlchemy · bcrypt · PyJWT · eventlet · cryptography

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/register_user` | Register user with bio enrollment template |
| `POST` | `/api/login` | Password-based login |
| `POST` | `/api/google-login` | Google OAuth login (requires prior bio registration) |
| `GET/POST` | `/api/scan_bio_id` | Capture palm-vein enrollment template |
| `GET/POST` | `/api/scan_auth_feature` | Capture palm-vein auth feature |
| `POST` | `/api/validate_bio` | Validate live palm scan against stored templates |
| `GET` | `/api/device/status` | USB device detection & status |
| `GET` | `/api/diagnostics/run` | Full hardware + system diagnostics |
| `POST` | `/api/send-otp/email` | Generate & email a 6-digit OTP |
| `POST` | `/api/verify-otp` | Verify OTP submission |
| `POST` | `/api/transactions` | Create a new transaction |
| `GET` | `/api/transactions` | List all transactions |
| `GET` | `/api/transactions/<id>` | Get a transaction by ID |

### palm_secure Package (SDK Wrapper)

| Module | Responsibility |
|--------|---------------|
| `device.py` | USB communication with Fujitsu PalmSecure via `pyusb`; enrollment & auth template capture |
| `diagnostics.py` | USB subsystem, driver, permissions, network, and device detection checks |
| `securityLayer.py` | AES-256-CBC encryption/decryption of biometric templates |
| `jwt_utils.py` | JWT token generation and decoding (PyJWT) |
| `models.py` | SQLAlchemy ORM models: `User`, `Transaction`, `ContactMessage` |
| `db.py` | Database engine, session factory, `init_db()` |
| `constants.py` | SDK-level constants (USB VID/PID, config values) |
| `exceptions.py` | Custom exceptions: `DeviceNotFoundError`, `ConnectionError`, `OperationError` |
| `utils.py` | Shared utility functions |

### Database Schema

```
users
├── id (UUID, PK)
├── username (unique)
├── email (unique)
├── phone
├── password_hash (bcrypt)
├── bio_id_hash (bcrypt)
└── bio_id_encrypted (AES-256-CBC base64)

transactions
├── id (UUID, PK)
├── user_id
├── amount
├── description
├── status
└── timestamp

contact_messages
├── id (UUID, PK)
├── email
├── phone
├── message
└── timestamp
```

### Security Design

- **Biometric data** is stored **double-secured**: bcrypt hash (for fast rejection) + AES-256-CBC encrypted template (for SDK comparison)
- **Passwords** use bcrypt with `rounds=12`
- **JWT tokens** protect authenticated routes
- **Rate limiting**: Registration 5/min, Login 10/min, global 200/day 50/hour
- **CORS** is locked to `localhost:5173` only

---

## Data Flow — Registration

```
User fills form + places palm on scanner
        │
        ▼
Frontend: POST /api/scan_bio_id
        │  ← returns Base64 enrollment template
        ▼
Frontend: POST /api/register_user  {username, email, phone, password, bio_id}
        │
        ▼
Backend:
  1. Validate & hash password (bcrypt rounds=12)
  2. Hash bio_id (bcrypt)
  3. Encrypt bio_id (AES-256-CBC) → bio_id_encrypted
  4. Save User to PostgreSQL
  5. Return JWT token
```

## Data Flow — Authentication (Palm Scan)

```
User places palm on scanner
        │
        ▼
Frontend: POST /api/scan_auth_feature
        │  ← returns Base64 auth feature
        ▼
Frontend: POST /api/validate_bio  {bio_id: auth_feature}
        │
        ▼
Backend:
  1. For each User in DB:
     a. Decrypt stored enrollment template (AES)
     b. Call Java bridge: compare(enrollment_template, auth_feature)
     c. If "MATCH" → generate JWT → return user info + token
  2. If no match → return 404
```
