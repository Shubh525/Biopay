# 🚀 BioPay — Deployment Guide

> **Audience:** Deployment Team  
> **Last Updated:** June 2026  
> **Version:** 1.0.0

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Pre-Deployment Checklist](#2-pre-deployment-checklist)
3. [Environment Configuration](#3-environment-configuration)
4. [Database Setup](#4-database-setup)
5. [Backend Deployment](#5-backend-deployment)
6. [Frontend Deployment](#6-frontend-deployment)
7. [Hardware Integration](#7-hardware-integration)
8. [Running in Production](#8-running-in-production)
9. [Reverse Proxy Setup (Nginx)](#9-reverse-proxy-setup-nginx)
10. [Post-Deployment Verification](#10-post-deployment-verification)
11. [Rollback Procedure](#11-rollback-procedure)
12. [Known Issues & Fixes](#12-known-issues--fixes)

---

## 1. System Requirements

### Server Requirements

| Component       | Minimum           | Recommended       |
|-----------------|-------------------|-------------------|
| OS              | Ubuntu 22.04 LTS  | Ubuntu 24.04 LTS  |
| CPU             | 2 cores           | 4+ cores          |
| RAM             | 4 GB              | 8 GB              |
| Storage         | 20 GB             | 50 GB SSD         |
| Python          | 3.10+             | 3.11+             |
| Node.js         | 18+               | 20 LTS            |
| PostgreSQL      | 14+               | 16+               |
| npm             | 9+                | 10+               |

### Hardware Requirements

| Device                   | Notes                                                   |
|--------------------------|---------------------------------------------------------|
| Fujitsu PalmSecure F Pro | Required for production biometric scanning             |
| USB 2.0 / 3.0 port       | Required for device connection                          |
| Fujitsu SDK              | Must be installed and licensed on the host machine      |

> ⚠️ **Note:** If the physical Fujitsu PalmSecure device is **not available**, set `SIMULATE=true` in environment variables to run in simulation mode (development/staging only).

---

## 2. Pre-Deployment Checklist

Before deploying, confirm all of the following:

- [ ] Python 3.10+ installed on the host
- [ ] Node.js 18+ and npm installed
- [ ] PostgreSQL 14+ running and accessible
- [ ] Database `palm_vein_auth` created
- [ ] All environment variables configured (see [Section 3](#3-environment-configuration))
- [ ] Virtual environment created for the backend
- [ ] Python dependencies installed via `pip install -r requirements.txt`
- [ ] Node dependencies installed via `npm install`
- [ ] Frontend production build compiled via `npm run build`
- [ ] Fujitsu PalmSecure SDK installed (or `SIMULATE=true` set for non-hardware deployments)
- [ ] Firewall ports opened: `5000` (backend), `80`/`443` (Nginx/frontend)
- [ ] SSL certificate configured (for HTTPS in production)

---

## 3. Environment Configuration

Create a `.env` file in the `backend/` directory, or set these as system environment variables.

```env
# ─── Database ─────────────────────────────────────────────────
POSTGRES_URL=postgresql://postgres:<PASSWORD>@localhost:5432/palm_vein_auth

# ─── Security ─────────────────────────────────────────────────
PALM_AUTH_AES_KEY=<your-32-character-aes-256-key>
SESSION_SECRET=<your-random-session-secret-key>

# ─── Hardware ─────────────────────────────────────────────────
SIMULATE=false          # Set to "true" for simulation mode (no hardware)

# ─── Email / OTP ──────────────────────────────────────────────
SMTP_EMAIL=your@gmail.com
SMTP_PASSWORD=your-gmail-app-password

# ─── Server ───────────────────────────────────────────────────
PORT=5000
```

### Environment Variable Reference

| Variable             | Default                                               | Required | Description                                              |
|----------------------|-------------------------------------------------------|----------|----------------------------------------------------------|
| `POSTGRES_URL`       | `postgresql://postgres:1234@localhost:5432/palm_vein_auth` | Yes  | PostgreSQL connection string                             |
| `PALM_AUTH_AES_KEY`  | `palm_vein_default_key_2025`                          | **Yes**  | AES-256 key for biometric template encryption            |
| `SESSION_SECRET`     | (random)                                              | **Yes**  | Flask session secret — **must be set in production**     |
| `SIMULATE`           | `false`                                               | No       | `true` = simulate biometric hardware                     |
| `SMTP_EMAIL`         | —                                                     | Yes      | Gmail address for OTP email delivery                     |
| `SMTP_PASSWORD`      | —                                                     | Yes      | Gmail App Password for OTP delivery                      |
| `PORT`               | `5000`                                                | No       | Backend server port                                      |

> 🔒 **Security:** Never commit `.env` to version control. Never use default keys in production.

---

## 4. Database Setup

### Step 1 — Create the Database

```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create the database
CREATE DATABASE palm_vein_auth;

-- Verify
\l
```

### Step 2 — Initialize Schema

The schema is automatically created on first backend startup via SQLAlchemy's `init_db()`. Tables created:

| Table               | Description                          |
|---------------------|--------------------------------------|
| `users`             | Registered users with biometric data |
| `transactions`      | Payment transaction records          |
| `contact_messages`  | Contact form submissions             |

> No manual migration scripts are needed. Schema is auto-initialized on backend startup.

### Step 3 — Verify Connection

```bash
cd backend
python -c "from palm_secure.db import init_db; init_db(); print('DB OK')"
```

---

## 5. Backend Deployment

```bash
# 1. Navigate to the backend directory
cd f:/biopay/biopay/backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set environment variables (or use .env file)
export POSTGRES_URL="postgresql://postgres:<PASSWORD>@localhost:5432/palm_vein_auth"
export PALM_AUTH_AES_KEY="<your-aes-key>"
export SESSION_SECRET="<your-session-secret>"
export SMTP_EMAIL="your@gmail.com"
export SMTP_PASSWORD="your-app-password"
export SIMULATE="false"

# 6. Start the backend
python main.py
```

The backend will start at:
- **Local:** `http://127.0.0.1:5000`
- **Network:** `http://<server-ip>:5000`

### Running as a System Service (Linux — systemd)

Create `/etc/systemd/system/biopay-backend.service`:

```ini
[Unit]
Description=BioPay Flask Backend
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/opt/biopay/backend
EnvironmentFile=/opt/biopay/backend/.env
ExecStart=/opt/biopay/backend/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable biopay-backend
sudo systemctl start biopay-backend
sudo systemctl status biopay-backend
```

---

## 6. Frontend Deployment

### Build the Production Bundle

```bash
# From project root
cd f:/biopay/biopay

# Install dependencies
npm install

# Build for production
npm run build
```

The compiled static assets will be output to `/dist`.

### Serve the Frontend

**Option A — Nginx (Recommended)**  
See [Section 9](#9-reverse-proxy-setup-nginx) for Nginx configuration.

**Option B — Preview Server (Staging Only)**

```bash
npm run preview
# Preview available at http://localhost:4173
```

> ⚠️ Do **not** use `npm run dev` or `npm run preview` in production. Serve the `/dist` folder via Nginx or another static web server.

---

## 7. Hardware Integration

### Fujitsu PalmSecure Device

1. Connect the Fujitsu PalmSecure F Pro device via USB.
2. Ensure the Fujitsu SDK is installed on the host machine.
3. Confirm the device is detected:

```bash
python -c "from palm_secure.device import PalmSecureDevice; d = PalmSecureDevice(); print(d.get_status())"
```

4. Verify device detection via the API:

```bash
curl http://localhost:5000/api/device/status
```

Expected response:
```json
{
  "connected": true,
  "device_name": "Fujitsu PalmSecure F Pro",
  "status": "ready"
}
```

### USB Permissions (Linux)

On Linux, udev rules may be needed to allow non-root USB access:

```bash
# Create udev rule for Fujitsu PalmSecure (VID/PID from constants.py)
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="04c5", MODE="0666"' \
  | sudo tee /etc/udev/rules.d/99-palmsecure.rules

sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

## 8. Running in Production

### Quick Start (Both Services)

```bash
# Terminal 1 — Backend
cd f:/biopay/biopay/backend
.\venv\Scripts\activate      # Windows
python main.py

# Terminal 2 — Frontend (dev only)
cd f:/biopay/biopay
npm run dev
```

### Production Setup

In production:
- Backend runs as a **systemd service** (see Section 5)
- Frontend `/dist` is served via **Nginx** (see Section 9)
- All traffic routes through Nginx on port `80`/`443`

---

## 9. Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Serve React frontend (static files)
    root /opt/biopay/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to Flask backend
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy WebSocket (Socket.IO)
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
sudo nginx -t         # Test config
sudo systemctl reload nginx
```

---

## 10. Post-Deployment Verification

After deployment, run these checks:

| Check                         | Command / URL                                    | Expected Result                  |
|-------------------------------|--------------------------------------------------|----------------------------------|
| Backend health                | `curl http://localhost:5000/api/device/status`   | JSON with device status          |
| Database connection           | `python -c "from palm_secure.db import init_db; init_db()"`  | No errors             |
| Diagnostics                   | `curl http://localhost:5000/api/diagnostics/run` | Full diagnostic JSON report      |
| Frontend loads                | Open `http://localhost:5173` (dev) or `http://yourdomain.com` (prod) | Landing page renders |
| Registration flow             | Navigate to `/register` and complete form        | User created in DB               |
| Login flow                    | Navigate to `/login` and authenticate            | JWT returned, dashboard loads    |
| OTP email delivery            | Trigger OTP flow                                 | Email received within 60 seconds |

---

## 11. Rollback Procedure

If a deployment fails:

1. **Backend:** Revert to the previous virtualenv snapshot or re-checkout the previous git tag, then restart the service.
2. **Frontend:** Replace the `/dist` folder with the previous build artifact.
3. **Database:** If schema changes were made, restore from the PostgreSQL backup taken before deployment.

```bash
# Restore PostgreSQL backup
pg_restore -U postgres -d palm_vein_auth /backups/palm_vein_auth_<date>.dump
```

---

## 12. Known Issues & Fixes

| Issue                               | Cause                                              | Fix                                                                     |
|-------------------------------------|----------------------------------------------------|-------------------------------------------------------------------------|
| `DeviceNotFoundError` on startup    | PalmSecure USB device not detected                 | Set `SIMULATE=true`, or check USB connection and udev rules             |
| `psycopg2` connection refused       | PostgreSQL not running or wrong credentials        | Verify `POSTGRES_URL` and ensure PostgreSQL service is active           |
| CORS errors in browser              | Backend CORS locked to `localhost:5173`            | Update `Flask-CORS` allowed origins in `demo_app.py` for production URL |
| npm audit vulnerabilities           | 16 vulnerabilities reported in `npm audit`         | Run `npm audit fix` before building; review remaining with `npm audit`  |
| Socket.IO connection drops          | Eventlet/WebSocket proxy misconfiguration          | Ensure Nginx is configured with `Upgrade` and `Connection` headers      |
| JWT token not refreshed             | Frontend doesn't re-request token after expiry     | Implement token refresh or force re-login on 401 responses              |

---

> 📬 For escalations, contact the **BioPay Backend Lead** with logs from `python main.py` and the output of `curl /api/diagnostics/run`.
