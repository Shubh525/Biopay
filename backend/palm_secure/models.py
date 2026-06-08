# models.py

from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey,Text
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    phone = Column(String)
    password_hash = Column(Text)
    bio_id_hash = Column(Text)
    bio_id_encrypted = Column(Text)

class ContactMessage(Base):
    __tablename__ = 'contact_messages'
    id = Column(String, primary_key=True)
    email = Column(String)
    phone = Column(String)
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(String, primary_key=True)
    user_id = Column(String)
    amount = Column(Float)
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String)