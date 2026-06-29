#!/usr/bin/env bash
# =============================================================================
# BioPay Backend — Initial EC2 Bootstrap & Deploy Script
# Run this ONCE on a fresh Ubuntu 22.04 EC2 instance to set everything up.
#
# Usage:
#   chmod +x deploy.sh
#   sudo ./deploy.sh
#
# Requirements:
#   - Ubuntu 22.04 LTS
#   - Run as root or with sudo
#   - Git repo already cloned OR will be cloned by this script
# =============================================================================

set -euo pipefail

# ── Config — edit these ───────────────────────────────────────────────────────
APP_DIR="/var/www/biopay"
BACKEND_DIR="$APP_DIR/backend"
LOG_DIR="/var/log/biopay"
REPO_URL="https://github.com/YOUR_ORG/YOUR_REPO.git"   # ← update this
DOMAIN="api.connectbiopay.com"
PYTHON_VERSION="python3.11"
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║     BioPay Backend — EC2 Bootstrap Script    ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── 1. System packages ────────────────────────────────────────────────────────
echo "▶ Installing system packages..."
apt-get update -qq
apt-get install -y -qq \
    python3.11 python3.11-venv python3.11-dev \
    python3-pip \
    nginx \
    certbot python3-certbot-nginx \
    postgresql-client \
    git \
    curl \
    ufw

# ── 2. Firewall ───────────────────────────────────────────────────────────────
echo "▶ Configuring UFW firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable
echo "  Port 5000 (Gunicorn) is NOT exposed — Nginx proxies it internally."

# ── 3. Create log directory ───────────────────────────────────────────────────
echo "▶ Creating log directory at $LOG_DIR..."
mkdir -p "$LOG_DIR"
chown www-data:www-data "$LOG_DIR"

# ── 4. Clone repo ─────────────────────────────────────────────────────────────
echo "▶ Cloning repository to $APP_DIR..."
if [ -d "$APP_DIR/.git" ]; then
    echo "  Repo already exists — pulling latest..."
    git -C "$APP_DIR" pull origin main
else
    git clone "$REPO_URL" "$APP_DIR"
fi
chown -R www-data:www-data "$APP_DIR"

# ── 5. Python virtualenv + dependencies ──────────────────────────────────────
echo "▶ Setting up Python virtualenv..."
if [ ! -d "$BACKEND_DIR/venv" ]; then
    $PYTHON_VERSION -m venv "$BACKEND_DIR/venv"
fi

echo "▶ Installing Python dependencies..."
"$BACKEND_DIR/venv/bin/pip" install --upgrade pip -q
"$BACKEND_DIR/venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt" -q

# ── 6. Environment file ───────────────────────────────────────────────────────
echo ""
echo "▶ Checking for .env file..."
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "  ⚠️  .env not found! Copying .env.example..."
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
    echo ""
    echo "  ❗ IMPORTANT: Edit $BACKEND_DIR/.env and fill in:"
    echo "     - POSTGRES_URL  (your RDS endpoint)"
    echo "     - JWT_SECRET_KEY"
    echo "     - PALM_AUTH_AES_KEY"
    echo "     - SESSION_SECRET"
    echo "     - SMTP_EMAIL / SMTP_PASSWORD"
    echo ""
    read -p "  Press ENTER after editing .env to continue..." _
fi
chown www-data:www-data "$BACKEND_DIR/.env"
chmod 600 "$BACKEND_DIR/.env"

# ── 7. Nginx config ───────────────────────────────────────────────────────────
echo "▶ Installing Nginx config..."
cp "$BACKEND_DIR/deploy/nginx-api.conf" /etc/nginx/sites-available/biopay-api
ln -sf /etc/nginx/sites-available/biopay-api /etc/nginx/sites-enabled/biopay-api
rm -f /etc/nginx/sites-enabled/default   # remove default placeholder

# Test before applying
nginx -t
echo "  Nginx config is valid."

# ── 8. SSL certificate via Let's Encrypt ─────────────────────────────────────
echo "▶ Obtaining SSL certificate for $DOMAIN..."
echo "  Make sure DNS A record for $DOMAIN points to this server's IP first."
read -p "  Press ENTER to run Certbot, or Ctrl+C to skip and do it manually..." _

certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos \
    --email admin@connectbiopay.com --redirect || {
    echo "  ⚠️  Certbot failed. Run manually: sudo certbot --nginx -d $DOMAIN"
}

# ── 9. Systemd service ────────────────────────────────────────────────────────
echo "▶ Installing systemd service..."
cp "$BACKEND_DIR/deploy/biopay-backend.service" /etc/systemd/system/biopay-backend.service
systemctl daemon-reload
systemctl enable biopay-backend
systemctl start biopay-backend

# ── 10. Sudoers rule for CI/CD pipeline (GitHub Actions deploy) ───────────────
echo "▶ Setting up sudoers rule for CI/CD..."
echo "ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart biopay-backend, /bin/systemctl status biopay-backend" \
    > /etc/sudoers.d/biopay-deploy
chmod 440 /etc/sudoers.d/biopay-deploy

# ── 11. Reload Nginx ──────────────────────────────────────────────────────────
systemctl reload nginx

# ── 12. Health check ─────────────────────────────────────────────────────────
echo ""
echo "▶ Running health check..."
sleep 3
if curl -sf http://127.0.0.1:5000/api/health > /dev/null; then
    echo "  ✅ Backend is UP at http://127.0.0.1:5000/api/health"
else
    echo "  ❌ Health check failed. Check logs:"
    echo "     sudo journalctl -u biopay-backend -n 50"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅  Bootstrap complete!                                     ║"
echo "║                                                              ║"
echo "║  API is live at: https://api.connectbiopay.com              ║"
echo "║                                                              ║"
echo "║  Useful commands:                                            ║"
echo "║    sudo systemctl status biopay-backend                     ║"
echo "║    sudo journalctl -u biopay-backend -f                     ║"
echo "║    sudo tail -f /var/log/biopay/gunicorn-error.log          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
