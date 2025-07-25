from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Optional
from ..models import User
from ..models.responses import (
    SuccessResponse, ErrorResponse, AuthResponse,
    UserResponse as UserResponseModel, STANDARD_RESPONSES
)
from ..database import get_db
from ..utils.jwt_utils import JWTUtils
from ..utils.exceptions import (
    AuthenticationException, ValidationException, BusinessException, APIException
)
from ..utils.logger import get_logger
from ..utils.password import PasswordUtils

logger = get_logger(__name__)
security = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["认证"])

# Pydantic模型
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    user_id: str
    created_at: str

# 使用标准响应模型，移除旧的AuthResponse定义

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

@router.post("/register",
            response_model=SuccessResponse,
            status_code=status.HTTP_201_CREATED,
            responses=STANDARD_RESPONSES)
async def register(user_data: UserRegister, db: Session = Depends(get_db)) -> SuccessResponse:
    """
    用户注册
    """
    try:
        username = user_data.username.strip()
        password = user_data.password.strip()

        if not username:
            raise ValidationException("用户名不能为空")

        if len(username) < 2 or len(username) > 50:
            raise ValidationException("用户名长度必须在2-50个字符之间")

        if not password:
            raise ValidationException("密码不能为空")

        # 验证密码强度
        is_strong, error_msg = PasswordUtils.is_strong_password(password)
        if not is_strong:
            raise ValidationException(error_msg)

        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise BusinessException("用户名已存在", "USERNAME_EXISTS")

        # 哈希密码
        password_hash = PasswordUtils.hash_password(password)

        # 创建新用户
        new_user = User(username=username, password_hash=password_hash)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 生成JWT令牌
        token = JWTUtils.generate_token(new_user.id, new_user.username)
        
        logger.info(f"New user registered: {new_user.username} (ID: {new_user.user_id})")
        
        return SuccessResponse(
            data={
                "user": {
                    "username": new_user.username,
                    "user_id": new_user.user_id,
                    "created_at": new_user.created_at.isoformat()
                },
                "token": token
            },
            message="用户注册成功"
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

@router.post("/login",
            response_model=SuccessResponse,
            responses=STANDARD_RESPONSES)
async def login(login_data: UserLogin, db: Session = Depends(get_db)) -> SuccessResponse:
    """
    用户登录 - 使用用户名和密码
    """
    try:
        username = login_data.username.strip()
        password = login_data.password.strip()

        if not username:
            raise ValidationException("用户名不能为空")

        if not password:
            raise ValidationException("密码不能为空")

        # 查找用户
        user = db.query(User).filter(User.username == username, User.is_active == True).first()
        if not user:
            raise AuthenticationException("用户名或密码错误")

        # 验证密码
        if not PasswordUtils.verify_password(password, user.password_hash):
            raise AuthenticationException("用户名或密码错误")
        
        # 生成JWT令牌
        token = JWTUtils.generate_token(user.id, user.username)

        logger.info(f"User logged in: {user.username} (ID: {user.user_id})")

        return SuccessResponse(
            data={
                "user": {
                    "username": user.username,
                    "user_id": user.user_id,
                    "created_at": user.created_at.isoformat()
                },
                "token": token
            },
            message="登录成功"
        )
    
    except (ValidationException, AuthenticationException):
        raise

    except Exception as e:
        logger.error(f"Error during user login: {e}")
        raise APIException("登录过程中发生错误", "LOGIN_ERROR", 500)

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