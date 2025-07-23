from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Optional
import logging

from ..models import User
from ..database import get_db
from ..utils.jwt_utils import JWTUtils

logger = logging.getLogger(__name__)
security = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["authentication"])

# Pydantic模型
class UserRegister(BaseModel):
    username: str

class UserLogin(BaseModel):
    user_id: str

class UserResponse(BaseModel):
    username: str
    user_id: str
    created_at: str

class AuthResponse(BaseModel):
    message: str
    user: UserResponse
    token: str

class TokenVerifyResponse(BaseModel):
    valid: bool
    user: Optional[dict] = None
    error: Optional[str] = None

# 依赖函数
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    获取当前认证用户
    """
    token = credentials.credentials
    payload = JWTUtils.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == payload['user_id'], User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册
    """
    try:
        username = user_data.username.strip()
        if not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username cannot be empty"
            )
        
        if len(username) < 2 or len(username) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be between 2 and 50 characters"
            )
        
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        
        # 创建新用户
        new_user = User(username=username)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 生成JWT令牌
        token = JWTUtils.generate_token(new_user.id, new_user.username)
        
        logger.info(f"New user registered: {new_user.username} (ID: {new_user.user_id})")
        
        return AuthResponse(
            message="User registered successfully",
            user=UserResponse(
                username=new_user.username,
                user_id=new_user.user_id,
                created_at=new_user.created_at.isoformat()
            ),
            token=token
        )
    
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration failed due to data conflict"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error during user registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/login", response_model=AuthResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录
    """
    try:
        user_id = login_data.user_id.strip().upper()
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID cannot be empty"
            )
        
        # 查找用户
        user = db.query(User).filter(User.user_id == user_id, User.is_active == True).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID"
            )
        
        # 生成JWT令牌
        token = JWTUtils.generate_token(user.id, user.username)
        
        logger.info(f"User logged in: {user.username} (ID: {user.user_id})")
        
        return AuthResponse(
            message="Login successful",
            user=UserResponse(
                username=user.username,
                user_id=user.user_id,
                created_at=user.created_at.isoformat()
            ),
            token=token
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error during user login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    return UserResponse(
        username=current_user.username,
        user_id=current_user.user_id,
        created_at=current_user.created_at.isoformat()
    )

@router.post("/verify", response_model=TokenVerifyResponse)
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    验证JWT令牌
    """
    try:
        token = credentials.credentials
        payload = JWTUtils.verify_token(token)
        
        if not payload:
            return TokenVerifyResponse(
                valid=False,
                error="Invalid or expired token"
            )
        
        return TokenVerifyResponse(
            valid=True,
            user={
                "user_id": payload['user_id'],
                "username": payload['username']
            }
        )
    
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return TokenVerifyResponse(
            valid=False,
            error="Internal server error"
        )