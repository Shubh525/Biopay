"""
Run this ONCE on the production server to:
1. Add the is_phone_verified column to existing users table
2. Mark ALL existing users as verified (they were created by old code that
   committed to DB, so we treat them as legitimate unless proven otherwise)
3. The new code will set is_phone_verified=True only after OTP is confirmed

Usage:
    cd backend
    python migrate_add_verified.py
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_URL")
if not DATABASE_URL:
    raise RuntimeError("POSTGRES_URL not set")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Check if column already exists
    result = conn.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='users' AND column_name='is_phone_verified'
    """))
    already_exists = result.fetchone() is not None

    if already_exists:
        print("Column 'is_phone_verified' already exists — skipping ALTER TABLE.")
    else:
        print("Adding 'is_phone_verified' column...")
        conn.execute(text("""
            ALTER TABLE users
            ADD COLUMN is_phone_verified BOOLEAN NOT NULL DEFAULT FALSE
        """))
        print("Column added.")

    # Mark all EXISTING users as verified (they were created by old code which
    # committed before OTP — we assume they are real users, not ghosts,
    # since we can't distinguish them without the column having existed before).
    updated = conn.execute(text("""
        UPDATE users
        SET is_phone_verified = TRUE
        WHERE is_phone_verified = FALSE
    """))
    conn.commit()
    print(f"Marked {updated.rowcount} existing user(s) as verified.")
    print("Migration complete.")
