# db.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from palm_secure.models import Base

load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "POSTGRES_URL environment variable is not set. "
        "Example: postgresql://user:password@localhost:5432/biopay"
    )

# Connection pool config — prevents exhaustion under load
# NOTE: pool_pre_ping=True is critical for RDS which drops idle connections
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # max persistent connections
    max_overflow=20,       # extra connections allowed during bursts
    pool_timeout=30,       # seconds to wait for a connection from the pool
    pool_recycle=1800,     # recycle connections after 30 min (avoids stale)
    pool_pre_ping=True,    # test connection health before using it — essential for RDS
)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Create all tables that don't yet exist (dev convenience — use Alembic in prod)."""
    Base.metadata.create_all(engine)
