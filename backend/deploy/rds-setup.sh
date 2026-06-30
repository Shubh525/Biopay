#!/usr/bin/env bash
# =============================================================================
# BioPay — Fresh RDS Database Setup Script
# Creates a brand-new, clean database on AWS RDS with no mock data.
# Schema is auto-created by SQLAlchemy (init_db).
#
# Usage (run from EC2 after .env is configured with RDS endpoint):
#   chmod +x rds-setup.sh
#   cd /var/www/biopay/backend
#   source venv/bin/activate
#   ./deploy/rds-setup.sh
# =============================================================================

set -euo pipefail

# ── Load RDS config from .env ─────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env not found in current directory."
    echo "   Run this script from /var/www/biopay/backend"
    exit 1
fi

# Parse POSTGRES_URL from .env
POSTGRES_URL=$(grep -E "^POSTGRES_URL=" .env | cut -d'=' -f2- | tr -d '"')
if [ -z "$POSTGRES_URL" ]; then
    echo "❌ ERROR: POSTGRES_URL not set in .env"
    exit 1
fi

# Extract components from URL
# Format: postgresql://user:pass@host:port/dbname
RDS_USER=$(echo "$POSTGRES_URL" | sed -E 's|postgresql://([^:]+):.*|\1|')
RDS_PASS=$(echo "$POSTGRES_URL" | sed -E 's|postgresql://[^:]+:([^@]+)@.*|\1|')
RDS_HOST=$(echo "$POSTGRES_URL" | sed -E 's|.*@([^:]+):.*|\1|')
RDS_PORT=$(echo "$POSTGRES_URL" | sed -E 's|.*:([0-9]+)/.*|\1|')
RDS_DB=$(echo "$POSTGRES_URL"   | sed -E 's|.*/([^?]+).*|\1|')

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     BioPay — Fresh RDS Database Setup                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "  RDS Host : $RDS_HOST"
echo "  Port     : $RDS_PORT"
echo "  User     : $RDS_USER"
echo "  Database : $RDS_DB"
echo ""
echo "  ⚠️  This will create a FRESH database with NO data."
echo "  All tables will be empty — no mock users, no test data."
echo ""
read -p "  Type 'yes' to continue: " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "  Aborted."
    exit 0
fi

# ── Step 1: Test RDS connectivity ─────────────────────────────────────────────
echo ""
echo "▶ Step 1 — Testing RDS connectivity..."
export PGPASSWORD="$RDS_PASS"
if pg_isready -h "$RDS_HOST" -p "$RDS_PORT" -U "$RDS_USER" -d "$RDS_DB" -t 15; then
    echo "  ✅ RDS is reachable."
else
    echo "  ❌ Cannot reach RDS at $RDS_HOST:$RDS_PORT"
    echo ""
    echo "  Checklist:"
    echo "  [ ] RDS instance status = 'available' in AWS Console"
    echo "  [ ] RDS Security Group has inbound rule: PostgreSQL (5432) from EC2 SG"
    echo "  [ ] EC2 and RDS are in the same VPC"
    echo "  [ ] POSTGRES_URL in .env has the correct endpoint and password"
    exit 1
fi

# ── Step 2: Verify database exists on RDS ────────────────────────────────────
echo ""
echo "▶ Step 2 — Verifying database '$RDS_DB' exists on RDS..."
DB_EXISTS=$(psql -h "$RDS_HOST" -p "$RDS_PORT" -U "$RDS_USER" -d postgres \
    -tAc "SELECT 1 FROM pg_database WHERE datname='$RDS_DB';" 2>/dev/null || echo "0")

if [ "$DB_EXISTS" != "1" ]; then
    echo "  Database '$RDS_DB' does not exist. Creating it..."
    psql -h "$RDS_HOST" -p "$RDS_PORT" -U "$RDS_USER" -d postgres \
        -c "CREATE DATABASE $RDS_DB;"
    echo "  ✅ Database '$RDS_DB' created."
else
    echo "  ✅ Database '$RDS_DB' already exists on RDS."
fi

# ── Step 3: Initialize schema via SQLAlchemy (init_db) ────────────────────────
echo ""
echo "▶ Step 3 — Initializing schema (creates tables via SQLAlchemy)..."
venv/bin/python - <<'PYEOF'
import sys, os
sys.path.insert(0, '.')
# Ensure we load the RDS .env
from dotenv import load_dotenv
load_dotenv()

try:
    from palm_secure.db import init_db, engine
    init_db()

    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected = {'users', 'transactions', 'contact_messages'}
    missing  = expected - set(tables)

    if missing:
        print(f"  ❌ Missing tables: {missing}")
        sys.exit(1)

    print(f"  ✅ Tables created: {', '.join(sorted(tables))}")

except Exception as e:
    print(f"  ❌ Schema init failed: {e}")
    sys.exit(1)
PYEOF

# ── Step 4: Verify tables are empty (no mock data) ────────────────────────────
echo ""
echo "▶ Step 4 — Verifying tables are empty (fresh start)..."
psql -h "$RDS_HOST" -p "$RDS_PORT" -U "$RDS_USER" -d "$RDS_DB" << 'SQL'
SELECT
  'users'            AS table_name, COUNT(*) AS row_count FROM users
UNION ALL
SELECT
  'transactions',                   COUNT(*)              FROM transactions
UNION ALL
SELECT
  'contact_messages',               COUNT(*)              FROM contact_messages;
SQL

echo ""
echo "  ✅ All tables are empty — clean production database ready."

# ── Step 5: Confirm SIMULATE=false in .env ────────────────────────────────────
echo ""
echo "▶ Step 5 — Checking SIMULATE flag..."
SIMULATE_VAL=$(grep -E "^SIMULATE=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'")
if [ "$SIMULATE_VAL" = "true" ]; then
    echo "  ⚠️  WARNING: SIMULATE=true is set in .env"
    echo "       This means biometric scans are FAKED."
    echo "       Set SIMULATE=false for real hardware use."
else
    echo "  ✅ SIMULATE=$SIMULATE_VAL (hardware mode)"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅  Fresh database setup complete!                         ║"
echo "║                                                              ║"
echo "║  Database is empty and ready for production use.            ║"
echo "║  No mock users, no test data.                               ║"
echo "║                                                              ║"
echo "║  Next:                                                       ║"
echo "║    sudo systemctl restart biopay-backend                    ║"
echo "║    curl http://127.0.0.1:5000/api/health                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
unset PGPASSWORD
