# db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from palm_secure.models import Base

DATABASE_URL = os.getenv("POSTGRES_URL") or "postgresql://postgres:1234@localhost:5432/palm_vein_auth"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
