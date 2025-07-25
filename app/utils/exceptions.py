"""
全局异常处理器
统一处理所有API异常并返回标准错误格式
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Union
import traceback

from app.models.responses import ErrorResponse

logger = logging.getLogger(__name__)


class APIException(Exception):
    """自定义API异常基类"""
    def __init__(self, message: str, error_code: str = "API_ERROR", status_code: int = 500, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(APIException):
    """数据验证异常"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "VALIDATION_ERROR", 422, details)


class AuthenticationException(APIException):
    """认证异常"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, "AUTHENTICATION_ERROR", 401)


class AuthorizationException(APIException):
    """授权异常"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, "AUTHORIZATION_ERROR", 403)


class ResourceNotFoundException(APIException):
    """资源不存在异常"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, "RESOURCE_NOT_FOUND", 404)


class BusinessException(APIException):
    """业务逻辑异常"""
    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR"):
        super().__init__(message, error_code, 400)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """自定义API异常处理器"""
    logger.error(f"API异常: {exc.message}, 错误码: {exc.error_code}, 详情: {exc.details}")
    
    error_response = ErrorResponse(
        error=exc.message,
        error_code=exc.error_code,
        details=exc.details
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    logger.error(f"HTTP异常: {exc.detail}, 状态码: {exc.status_code}")
    
    # 根据状态码确定错误码
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN", 
        404: "NOT_FOUND",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_SERVER_ERROR"
    }
    
    error_response = ErrorResponse(
        error=exc.detail,
        error_code=error_code_map.get(exc.status_code, "HTTP_ERROR")
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """数据验证异常处理器"""
    logger.error(f"数据验证异常: {exc.errors()}")
    
    # 格式化验证错误信息
    validation_errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        validation_errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = ErrorResponse(
        error="数据验证失败",
        error_code="VALIDATION_ERROR",
        details={"validation_errors": validation_errors}
    )
    
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump()
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """数据库异常处理器"""
    logger.error(f"数据库异常: {str(exc)}")
    logger.error(f"异常堆栈: {traceback.format_exc()}")
    
    error_response = ErrorResponse(
        error="数据库操作失败",
        error_code="DATABASE_ERROR",
        details={"db_error": str(exc)} if logger.level <= logging.DEBUG else None
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}")
    logger.error(f"异常堆栈: {traceback.format_exc()}")
    
    error_response = ErrorResponse(
        error="服务器内部错误",
        error_code="INTERNAL_SERVER_ERROR",
        details={"error": str(exc)} if logger.level <= logging.DEBUG else None
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )


def register_exception_handlers(app):
    """注册所有异常处理器"""
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
