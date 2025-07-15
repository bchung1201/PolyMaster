import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from cryptography.fernet import Fernet
import os
from core.auth.models import User, UserCreate, UserLogin, Token, WalletConfig

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 1440  # 24 hours
        
        # For encrypting wallet credentials
        self.encryption_key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
        if isinstance(self.encryption_key, str):
            self.encryption_key = self.encryption_key.encode()
        self.cipher = Fernet(self.encryption_key)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data like API keys"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def create_user_token(self, user: User) -> Token:
        """Create token response for user"""
        token_data = {
            "sub": user.email,
            "user_id": user.id,
            "username": user.username
        }
        access_token = self.create_access_token(token_data)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60
        )
    
    def encrypt_wallet_config(self, wallet_config: WalletConfig) -> dict:
        """Encrypt wallet configuration for storage"""
        return {
            "clob_api_key": self.encrypt_sensitive_data(wallet_config.clob_api_key),
            "clob_secret": self.encrypt_sensitive_data(wallet_config.clob_secret),
            "clob_passphrase": self.encrypt_sensitive_data(wallet_config.clob_passphrase),
            "wallet_private_key": self.encrypt_sensitive_data(wallet_config.wallet_private_key) if wallet_config.wallet_private_key else None
        }
    
    def decrypt_wallet_config(self, user: User) -> WalletConfig:
        """Decrypt wallet configuration for use"""
        if not user.clob_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has not configured wallet credentials"
            )
        
        return WalletConfig(
            clob_api_key=self.decrypt_sensitive_data(user.clob_api_key),
            clob_secret=self.decrypt_sensitive_data(user.clob_secret),
            clob_passphrase=self.decrypt_sensitive_data(user.clob_passphrase),
            wallet_private_key=self.decrypt_sensitive_data(user.encrypted_private_key) if user.encrypted_private_key else None
        )