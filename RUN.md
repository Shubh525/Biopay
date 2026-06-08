# BioPay – Run Commands

A quick reference for starting the backend (Flask + SocketIO) and frontend (Vite + React).

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.10+ | For the Flask backend |
| Node.js | 18+ | For the Vite frontend |
| PostgreSQL | 14+ | Running locally on port `5432` |

---

## 1 · Backend (Flask + SocketIO)

> Runs on **http://localhost:5000**

### First-time setup

```bash
# Navigate to the backend folder
cd backend

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment variables (optional)

Create a `.env` file inside `backend/` to override the default DB URL:

```env
# backend/.env
POSTGRES_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/palm_vein_auth
```

> Default (no .env): `postgresql://postgres:1234@localhost:5432/palm_vein_auth`

### Start the backend

```bash
# From the backend/ folder with venv active
python main.py
```

Expected output:
```
Server is running!
Access it on:
   • Localhost  →  http://127.0.0.1:5000
   • Network    →  http://<your-ip>:5000
```

---

## 2 · Frontend (Vite + React)

> Runs on **http://localhost:5173**

### First-time setup

```bash
# From the project root (where package.json lives)
npm install
```

### Start the frontend

```bash
npm run dev
```

Or equivalently:

```bash
npm start
```

---

## 3 · Run Both (Two terminals)

**Terminal 1 — Backend:**

```bash
cd backend
venv\Scripts\activate        # Windows
python main.py
```

**Terminal 2 — Frontend:**

```bash
npm run dev
```

---

## 4 · Database Setup (PostgreSQL)

Make sure PostgreSQL is running and the database exists:

```sql
-- Run in psql or pgAdmin
CREATE DATABASE palm_vein_auth;
```

The backend calls `init_db()` on startup which auto-creates all tables via SQLAlchemy.

---

## 5 · Quick URLs

| Service | URL |
|---------|-----|
| Frontend (Vite) | http://localhost:5173 |
| Backend API | http://localhost:5000 |
| Backend (network) | http://\<your-ip\>:5000 |

---

## 6 · Production Build (Frontend only)

```bash
npm run build      # Outputs to dist/
npm run preview    # Preview the production build locally
```
