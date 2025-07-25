"""
日志配置模块
使用loguru进行日志管理，按天保存，保留最近三天的日志
"""

import os
import sys
from loguru import logger
from pathlib import Path


def setup_logger():
    """
    配置loguru日志系统
    - 按天保存日志文件
    - 保留最近3天的日志
    - 控制台输出彩色日志
    - 文件输出详细日志
    """
    # 移除默认的控制台处理器
    logger.remove()
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 控制台日志配置 - 生产环境简化输出
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 文件日志配置 - 详细输出
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level="INFO",
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # 添加文件处理器 - 按天轮转，保留3天
    logger.add(
        log_dir / "inkflow_{time:YYYY-MM-DD}.log",
        format=file_format,
        level="DEBUG",
        rotation="00:00",  # 每天午夜轮转
        retention="3 days",  # 保留3天
        compression="zip",  # 压缩旧日志
        encoding="utf-8",
        backtrace=True,
        diagnose=True
    )
    
    # 添加错误日志文件 - 只记录ERROR及以上级别
    logger.add(
        log_dir / "inkflow_error_{time:YYYY-MM-DD}.log",
        format=file_format,
        level="ERROR",
        rotation="00:00",
        retention="7 days",  # 错误日志保留7天
        compression="zip",
        encoding="utf-8",
        backtrace=True,
        diagnose=True
    )
    
    logger.info("日志系统初始化完成")
    logger.info(f"日志目录: {log_dir.absolute()}")
    
    return logger


# 全局日志实例
app_logger = setup_logger()


def get_logger(name: str = None):
    """
    获取日志实例
    
    Args:
        name: 日志名称，通常使用模块名
        
    Returns:
        logger实例
    """
    if name:
        return logger.bind(name=name)
    return logger
