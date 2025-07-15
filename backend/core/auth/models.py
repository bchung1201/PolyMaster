from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Wallet configuration
    wallet_address = Column(String, unique=True, nullable=True)
    encrypted_private_key = Column(Text, nullable=True)  # Encrypted with user's password
    clob_api_key = Column(Text, nullable=True)  # Encrypted
    clob_secret = Column(Text, nullable=True)   # Encrypted
    clob_passphrase = Column(Text, nullable=True)  # Encrypted
    
    # Trading preferences
    default_dry_run = Column(Boolean, default=True)
    risk_tolerance = Column(String, default="medium")  # low, medium, high
    max_trade_amount = Column(Integer, default=100)  # in USDC

# Pydantic models for API
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    is_verified: bool
    wallet_address: Optional[str]
    has_wallet_configured: bool

class WalletConfig(BaseModel):
    clob_api_key: str
    clob_secret: str
    clob_passphrase: str
    wallet_private_key: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None