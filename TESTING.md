# 🧪 BioPay — Testing Guide

> **Audience:** QA & Testing Team  
> **Last Updated:** June 2026  
> **Version:** 1.0.0

---

## Table of Contents

1. [Test Environment Setup](#1-test-environment-setup)
2. [Running in Simulation Mode](#2-running-in-simulation-mode)
3. [Backend API Testing](#3-backend-api-testing)
4. [Frontend UI Testing](#4-frontend-ui-testing)
5. [Biometric Flow Testing](#5-biometric-flow-testing)
6. [Authentication & Security Testing](#6-authentication--security-testing)
7. [Database Testing](#7-database-testing)
8. [Rate Limiting & Load Testing](#8-rate-limiting--load-testing)
9. [WebSocket / Real-Time Testing](#9-websocket--real-time-testing)
10. [Test Scenarios & Checklist](#10-test-scenarios--checklist)
11. [Common Bugs & What to Look For](#11-common-bugs--what-to-look-for)
12. [Reporting Issues](#12-reporting-issues)

---

## 1. Test Environment Setup

### Prerequisites

Ensure these are installed on the test machine:

| Tool            | Version   | Install Command                     |
|-----------------|-----------|-------------------------------------|
| Python          | 3.10+     | https://python.org                  |
| Node.js         | 18+       | https://nodejs.org                  |
| PostgreSQL      | 14+       | https://postgresql.org              |
| curl / Postman  | Any       | For API testing                     |
| Browser         | Chrome 120+ / Firefox 122+ | For frontend testing    |

### Setting Up the Test Environment

```bash
# 1. Clone or pull the latest code
git pull origin main

# 2. Set up backend
cd f:/biopay/biopay/backend
python -m venv venv
.\venv\Scripts\activate      # Windows
pip install -r requirements.txt

# 3. Set up frontend
cd f:/biopay/biopay
npm install
```

### Test Database

Use a **separate test database** — never run tests against the production database.

```sql
-- In psql
CREATE DATABASE palm_vein_auth_test;
```

Set the environment variable for tests:

```powershell
$env:POSTGRES_URL = "postgresql://postgres:1234@localhost:5432/palm_vein_auth_test"
```

---

## 2. Running in Simulation Mode

Since the Fujitsu PalmSecure hardware may not be available in the test environment, use **Simulation Mode** to mock biometric data.

```powershell
# Enable simulation mode before starting the backend
$env:SIMULATE = "true"
$env:POSTGRES_URL = "postgresql://postgres:1234@localhost:5432/palm_vein_auth_test"
$env:PALM_AUTH_AES_KEY = "test_aes_key_32_characters_long!"
$env:SESSION_SECRET = "test_session_secret"

# Start the backend
cd f:/biopay/biopay/backend
.\venv\Scripts\activate
python main.py
```

In simulation mode:
- `/api/scan_bio_id` returns a **mock palm enrollment template** (Base64 string)
- `/api/scan_auth_feature` returns a **mock auth feature** (Base64 string)
- `/api/validate_bio` performs **simulated comparison** without real SDK calls
- `/api/device/status` reports the device as **connected: true (simulated)**

> ✅ All registration and authentication flows can be tested end-to-end without hardware.

---

## 3. Backend API Testing

The backend runs at `http://localhost:5000`. All API endpoints are under `/api/`.

### 3.1 Health & Device Status

```bash
# Device status
curl -X GET http://localhost:5000/api/device/status

# Expected (simulation mode):
# { "connected": true, "status": "simulated", ... }
```

### 3.2 User Registration

```bash
# Step 1: Capture palm enrollment template
curl -X POST http://localhost:5000/api/scan_bio_id
# Returns: { "bio_id": "<base64_template>" }

# Step 2: Register user with captured template
curl -X POST http://localhost:5000/api/register_user \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@biopay.com",
    "phone": "9876543210",
    "password": "SecurePass@123",
    "bio_id": "<base64_template_from_step1>"
  }'

# Expected: { "token": "<jwt>", "user": { ... } }
```

### 3.3 Password Login

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@biopay.com",
    "password": "SecurePass@123"
  }'

# Expected: { "token": "<jwt>", "user": { ... } }
```

### 3.4 Biometric Authentication

```bash
# Step 1: Capture auth feature
curl -X POST http://localhost:5000/api/scan_auth_feature
# Returns: { "bio_feature": "<base64_feature>" }

# Step 2: Validate biometric
curl -X POST http://localhost:5000/api/validate_bio \
  -H "Content-Type: application/json" \
  -d '{
    "bio_id": "<base64_feature_from_step1>"
  }'

# Expected (match): { "token": "<jwt>", "user": { ... } }
# Expected (no match): 404 { "error": "No biometric match found" }
```

### 3.5 OTP Flow

```bash
# Send OTP
curl -X POST http://localhost:5000/api/send-otp/email \
  -H "Content-Type: application/json" \
  -d '{ "email": "test@biopay.com" }'

# Verify OTP (use code received in email)
curl -X POST http://localhost:5000/api/verify-otp \
  -H "Content-Type: application/json" \
  -d '{ "email": "test@biopay.com", "otp": "123456" }'
```

### 3.6 Transactions

```bash
# Create transaction
curl -X POST http://localhost:5000/api/transactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt_token>" \
  -d '{
    "amount": 500.00,
    "description": "Test payment"
  }'

# List all transactions
curl -X GET http://localhost:5000/api/transactions \
  -H "Authorization: Bearer <jwt_token>"

# Get specific transaction
curl -X GET http://localhost:5000/api/transactions/<transaction_id> \
  -H "Authorization: Bearer <jwt_token>"
```

### 3.7 Diagnostics

```bash
curl -X GET http://localhost:5000/api/diagnostics/run

# Returns full system diagnostics including:
# - USB subsystem status
# - Driver availability
# - Device detection
# - Database connectivity
# - Network checks
```

### 3.8 Google OAuth Login

```bash
curl -X POST http://localhost:5000/api/google-login \
  -H "Content-Type: application/json" \
  -d '{ "token": "<google_oauth_id_token>" }'

# Note: User must already be registered via biometric enrollment.
# Expected for new users: 404 "User not found. Please register first."
```

---

## 4. Frontend UI Testing

Start the frontend development server:

```bash
cd f:/biopay/biopay
npm run dev
# Available at: http://localhost:5173
```

### Page-by-Page Test Checklist

#### `/` — Landing Page (Home)
- [ ] Page loads without console errors
- [ ] Hero section renders with video/animation
- [ ] Navigation bar links are all clickable and route correctly
- [ ] `ScrollingCustomers` logo animation loops smoothly
- [ ] "Get Started" / CTA buttons navigate correctly
- [ ] Page is responsive on mobile (375px) and desktop (1440px)

#### `/register` — Registration Page
- [ ] Form renders all fields: username, email, phone, password, palm scan
- [ ] Palm scan button triggers `/api/scan_bio_id`
- [ ] Form validates required fields (empty field error messages shown)
- [ ] Email format validated
- [ ] Password strength enforced
- [ ] Submitting with valid data creates a user and redirects to dashboard
- [ ] Duplicate email/username shows appropriate error
- [ ] Loading state shown while API call is in progress

#### `/login` — Login Page
- [ ] Password login works with valid credentials
- [ ] Biometric login button triggers palm scan flow
- [ ] Invalid password shows error message
- [ ] JWT token stored in `AuthContext` after successful login
- [ ] Redirects to `/homepage` after login

#### `/homepage` — Dashboard
- [ ] Accessible only when logged in (redirects to `/login` if unauthenticated)
- [ ] Displays correct user information
- [ ] Transaction list loads
- [ ] Logout clears auth state

#### `/deviceDetails` — Device Details
- [ ] Shows connected/disconnected status from `/api/device/status`
- [ ] Auto-refreshes status

#### `/diagnostic` — Diagnostics
- [ ] Loads diagnostic data from `/api/diagnostics/run`
- [ ] All diagnostic categories display correctly
- [ ] Error states handled gracefully

#### `/contactUs` — Contact Form
- [ ] All fields render and validate
- [ ] Submit sends contact message to backend
- [ ] Success/error message shown after submission

#### `/aboutUs`, `/services`, `/work`
- [ ] Pages render without errors
- [ ] All links and navigation functional

---

## 5. Biometric Flow Testing

### Full Registration → Login Biometric Flow

| Step | Action                                       | Expected Result                                |
|------|----------------------------------------------|------------------------------------------------|
| 1    | Navigate to `/register`                      | Form is displayed                              |
| 2    | Click "Scan Palm" button                     | API call to `/api/scan_bio_id` made            |
| 3    | Simulated palm template returned             | Template stored temporarily in frontend state  |
| 4    | Fill in user details and submit form         | `POST /api/register_user` called               |
| 5    | Backend creates user with encrypted bio data | Response includes JWT token                    |
| 6    | Redirected to dashboard                      | User info visible on `/homepage`               |
| 7    | Log out                                      | Auth state cleared                             |
| 8    | Navigate to `/login`                         | Login page shown                               |
| 9    | Click "Login with Palm" / biometric button   | API call to `/api/scan_auth_feature` made      |
| 10   | Simulated feature returned                   | `POST /api/validate_bio` called                |
| 11   | Match found in DB                            | JWT returned, redirected to dashboard          |

### Biometric Failure Scenarios

| Scenario                     | Expected Behavior                                    |
|------------------------------|------------------------------------------------------|
| No registered users in DB    | `POST /api/validate_bio` returns 404                 |
| Wrong palm (no match)        | Error message displayed on login page                |
| Device disconnected          | `/api/device/status` returns `connected: false`; UI shows error |
| `SIMULATE=false`, no hardware| `DeviceNotFoundError` raised, 503/500 returned       |

---

## 6. Authentication & Security Testing

### JWT Token Validation

| Test                              | How to Test                                              | Expected Result                         |
|-----------------------------------|----------------------------------------------------------|-----------------------------------------|
| Valid token accepted              | Include `Authorization: Bearer <valid_jwt>` header       | 200 OK response                         |
| Expired token rejected            | Use a manually expired token                             | 401 Unauthorized                        |
| Missing token rejected            | Omit `Authorization` header on protected routes          | 401 Unauthorized                        |
| Tampered token rejected           | Modify payload of a valid JWT                            | 401 / 422 response                      |

### Rate Limiting Tests

| Endpoint                  | Limit              | Test Method                                         |
|---------------------------|--------------------|-----------------------------------------------------|
| `/api/register_user`      | 5 requests/min     | Send 6+ rapid POST requests                         |
| `/api/login`              | 10 requests/min    | Send 11+ rapid POST requests                        |
| Global                    | 200/day, 50/hour   | Exceed hourly limit with repeated API calls         |
| **Expected behavior**     | `429 Too Many Requests` returned on limit exceeded     |                                                     |

### AES Encryption Verification

- Register a user and inspect the `bio_id_encrypted` column in the `users` table.
- It should be a Base64-encoded ciphertext — **not** a plaintext palm template.
- Decryption should only succeed with the correct `PALM_AUTH_AES_KEY`.

### CORS Policy

```bash
# This should FAIL (blocked by CORS) — origin is not localhost:5173
curl -H "Origin: http://evil-site.com" \
     -X POST http://localhost:5000/api/login \
     -v 2>&1 | grep "Access-Control"

# Expected: No Access-Control-Allow-Origin header for evil-site.com
```

---

## 7. Database Testing

### Verify Tables Exist

```sql
-- Connect to test DB
psql -U postgres -d palm_vein_auth_test

-- Check tables
\dt

-- Expected: users, transactions, contact_messages
```

### Verify Biometric Data Storage

```sql
-- After registering a user, verify data is hashed and encrypted
SELECT username, email,
       LENGTH(bio_id_hash) AS bio_hash_length,
       LENGTH(bio_id_encrypted) AS bio_encrypted_length,
       LEFT(bio_id_encrypted, 30) AS encrypted_preview
FROM users;

-- bio_id_hash should be a bcrypt hash (~60 chars)
-- bio_id_encrypted should be a Base64 AES ciphertext
-- plaintext palm template should NEVER appear in the DB
```

### Verify Password Hashing

```sql
-- Passwords must never be stored in plaintext
SELECT username, LEFT(password_hash, 10) AS hash_prefix FROM users;
-- Expected prefix: $2b$ (bcrypt)
```

### Transaction Integrity

```sql
SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 5;
-- Verify UUIDs as IDs, proper timestamps, and non-null amounts
```

---

## 8. Rate Limiting & Load Testing

### Rate Limit Trigger Test (curl)

```bash
# Trigger rate limit on registration (send 6 requests quickly)
for i in $(seq 1 6); do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST http://localhost:5000/api/register_user \
    -H "Content-Type: application/json" \
    -d '{"username":"flood'$i'","email":"flood'$i'@test.com","password":"pass","bio_id":"abc"}'
done

# Expected: first 5 → 2xx or 4xx (validation), 6th → 429
```

### Concurrent Connection Test

Use a tool like [k6](https://k6.io/) or [Apache Bench (ab)](https://httpd.apache.org/docs/2.4/programs/ab.html):

```bash
# Example with ab (Apache Bench)
ab -n 100 -c 10 http://localhost:5000/api/device/status

# Metrics to observe:
# - Requests per second
# - Failed requests (should be 0 for status endpoint)
# - Response time (p99 < 1000ms expected)
```

---

## 9. WebSocket / Real-Time Testing

BioPay uses **Socket.IO** for real-time biometric device events.

### Basic WebSocket Connection Test

Using the browser console on `http://localhost:5173`:

```javascript
const socket = io("http://localhost:5000");
socket.on("connect", () => console.log("Connected:", socket.id));
socket.on("device_status", (data) => console.log("Device Event:", data));
socket.on("disconnect", () => console.log("Disconnected"));
```

### Expected Socket Events

| Event             | Trigger                             | Expected Payload                    |
|-------------------|-------------------------------------|-------------------------------------|
| `connect`         | Client connects to Socket.IO        | Socket ID assigned                  |
| `device_status`   | Device status changes               | `{ connected: bool, status: str }`  |
| `scan_complete`   | Palm scan finishes                  | `{ template: "<base64>", ... }`     |
| `disconnect`      | Client disconnects or server stops  | —                                   |

---

## 10. Test Scenarios & Checklist

### Critical Path Tests (Must Pass Before Any Release)

- [ ] User can register with all fields and palm scan
- [ ] Registered user can log in with password
- [ ] Registered user can log in with biometric scan
- [ ] JWT token is returned on all successful logins
- [ ] Unauthenticated access to protected routes is blocked (401)
- [ ] Transaction can be created and listed
- [ ] OTP is sent to email and can be verified
- [ ] Rate limiter blocks excessive requests (429 returned)
- [ ] Biometric data in DB is encrypted (not plaintext)
- [ ] Device status endpoint returns valid response
- [ ] Full diagnostics run without crashing

### Edge Case Tests

- [ ] Register with duplicate username → error shown
- [ ] Register with duplicate email → error shown
- [ ] Login with wrong password → error shown, no JWT returned
- [ ] Submit empty registration form → all field errors shown
- [ ] Submit invalid email format → validation error shown
- [ ] Biometric scan with no matching user → 404 returned
- [ ] Expired JWT on protected endpoint → 401 returned
- [ ] Contact form submitted with all fields → success message shown
- [ ] Navigate to non-existent route → 404 page or redirect
- [ ] Google login for unregistered user → informative error returned

### Regression Tests (After Each Deployment)

- [ ] Landing page loads in < 3 seconds
- [ ] No console errors on page load
- [ ] Registration flow completes end-to-end
- [ ] Password login flow completes end-to-end
- [ ] Biometric login flow completes end-to-end (simulation)
- [ ] Database tables intact after restart

---

## 11. Common Bugs & What to Look For

| Bug / Issue                         | Symptoms                                           | Where to Check                          |
|-------------------------------------|----------------------------------------------------|-----------------------------------------|
| CORS error on API call              | `Access-Control` error in browser console          | `demo_app.py` CORS config               |
| JWT not attached in frontend        | 401 on protected routes despite being logged in    | `AuthContext.jsx` — check token storage |
| Bio template not passed to register | 400/422 on `/api/register_user`                    | Frontend `Register.jsx` — `bio_id` field |
| Socket.IO not connecting            | `WebSocket connection failed` in console           | Backend running? Nginx config correct?  |
| Rate limit hitting normal traffic   | 429 errors without high request volume             | Flask-Limiter config in `demo_app.py`   |
| OTP email not received              | Timeout on OTP verification                        | SMTP credentials; check spam folder     |
| Biometric match always fails        | Login always returns 404 even for registered user  | `SIMULATE` mode mismatch between reg/login |
| DB schema missing tables            | `no such table` or `relation does not exist` error | Run `init_db()` manually                |

---

## 12. Reporting Issues

When reporting a bug, include:

1. **Steps to reproduce** — exact sequence of actions
2. **Expected result** — what should happen
3. **Actual result** — what actually happened
4. **Environment** — OS, Python version, Node version, browser
5. **Backend logs** — terminal output from `python main.py`
6. **Browser console errors** — screenshot or copy-paste
7. **Network tab** — failed HTTP requests (status codes, request/response bodies)
8. **Database state** — if relevant (e.g., user count, transaction IDs)

### Log Collection

```bash
# Backend logs — redirect to file
python main.py 2>&1 | tee biopay_backend.log

# Frontend build warnings
npm run build 2>&1 | tee biopay_frontend_build.log
```

---

> 📬 Report bugs to the **BioPay QA Channel** with logs attached. Tag `[CRITICAL]` for auth failures, `[HIGH]` for data integrity issues, and `[LOW]` for UI/UX issues.
