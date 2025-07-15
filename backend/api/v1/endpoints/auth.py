from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from core.auth.models import UserCreate, UserLogin, UserResponse, Token, WalletConfig, User
from core.auth.service import AuthService
from services.user_trading_service import UserTradingService
from core.dependencies import get_database_session  # You'd need to implement this

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Initialize auth service
auth_service = AuthService()

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_database_session)
):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check username
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        hashed_password = auth_service.hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            username=new_user.username,
            is_active=new_user.is_active,
            is_verified=new_user.is_verified,
            wallet_address=new_user.wallet_address,
            has_wallet_configured=bool(new_user.clob_api_key)
        )
        
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user account"
        )

@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_database_session)
):
    """Login user and return JWT token"""
    try:
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not auth_service.verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Create and return token
        return auth_service.create_user_token(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database_session)
):
    """Get current user information"""
    try:
        # Verify token
        payload = auth_service.verify_token(credentials.credentials)
        user_email = payload.get("sub")
        
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user from database
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
            wallet_address=user.wallet_address,
            has_wallet_configured=bool(user.clob_api_key)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user information"
        )

@router.post("/wallet/configure")
async def configure_wallet(
    wallet_config: WalletConfig,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database_session)
):
    """Configure user's wallet credentials"""
    try:
        # Get current user
        payload = auth_service.verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == payload.get("sub")).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Encrypt and store wallet configuration
        encrypted_config = auth_service.encrypt_wallet_config(wallet_config)
        
        user.clob_api_key = encrypted_config["clob_api_key"]
        user.clob_secret = encrypted_config["clob_secret"]
        user.clob_passphrase = encrypted_config["clob_passphrase"]
        if encrypted_config["wallet_private_key"]:
            user.encrypted_private_key = encrypted_config["wallet_private_key"]
        
        db.commit()
        
        return {"message": "Wallet configuration saved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configuring wallet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving wallet configuration"
        )

@router.get("/wallet/test")
async def test_wallet_connection(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database_session)
):
    """Test user's wallet connection"""
    try:
        # Get current user
        payload = auth_service.verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == payload.get("sub")).first()
        
        if not user or not user.clob_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wallet not configured"
            )
        
        # Create user trading service and test connection
        user_trading_service = UserTradingService(user, auth_service)
        portfolio = await user_trading_service.get_user_portfolio()
        
        return {
            "success": True,
            "message": "Wallet connection successful",
            "balance": portfolio.get("balance")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing wallet connection: {e}")
        return {
            "success": False,
            "message": f"Wallet connection failed: {str(e)}"
        }

# Dependency to get current user from token
async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database_session)
) -> User:
    """Dependency to get current user from JWT token"""
    payload = auth_service.verify_token(credentials.credentials)
    user_email = payload.get("sub")
    
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user