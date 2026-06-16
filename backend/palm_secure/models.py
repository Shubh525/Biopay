# models.py

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _utcnow():
    """Timezone-aware UTC timestamp (replaces deprecated datetime.utcnow)."""
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = 'users'

    id               = Column(String, primary_key=True)
    username         = Column(String, unique=True, nullable=False)
    email            = Column(String, unique=True, nullable=False)
    phone            = Column(String)
    password_hash    = Column(Text, nullable=False)
    bio_id_hash      = Column(Text)
    bio_id_encrypted = Column(Text)


class ContactMessage(Base):
    __tablename__ = 'contact_messages'

    id        = Column(String, primary_key=True)
    email     = Column(String)
    phone     = Column(String)
    message   = Column(Text)
    timestamp = Column(DateTime, default=_utcnow)


class Transaction(Base):
    __tablename__ = 'transactions'

    id          = Column(String, primary_key=True)
    user_id     = Column(String, ForeignKey('users.id'), nullable=False)
    amount      = Column(Float, nullable=False)
    description = Column(Text)
    timestamp   = Column(DateTime, default=_utcnow)
    status      = Column(String, default='pending')