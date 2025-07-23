import redis
import logging
from typing import Optional
from app.config import settings

# 配置日志
logger = logging.getLogger(__name__)

class RedisConnection:
    """Redis连接管理类"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.connect()
    
    def connect(self):
        """连接到Redis"""
        try:
            # 解析Redis URL
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis连接成功")
            
        except redis.ConnectionError as e:
            logger.error(f"Redis连接失败: {e}")
            self.redis_client = None
        except Exception as e:
            logger.error(f"Redis连接异常: {e}")
            self.redis_client = None
    
    def get_client(self) -> Optional[redis.Redis]:
        """获取Redis客户端"""
        if self.redis_client is None:
            self.connect()
        return self.redis_client
    
    def is_connected(self) -> bool:
        """检查Redis连接状态"""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except:
            pass
        return False
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """设置键值对"""
        try:
            client = self.get_client()
            if client:
                client.set(key, value, ex=ex)
                return True
        except Exception as e:
            logger.error(f"Redis设置失败: {e}")
        return False
    
    def get(self, key: str) -> Optional[str]:
        """获取值"""
        try:
            client = self.get_client()
            if client:
                return client.get(key)
        except Exception as e:
            logger.error(f"Redis获取失败: {e}")
        return None
    
    def delete(self, key: str) -> bool:
        """删除键"""
        try:
            client = self.get_client()
            if client:
                client.delete(key)
                return True
        except Exception as e:
            logger.error(f"Redis删除失败: {e}")
        return False
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            client = self.get_client()
            if client:
                return bool(client.exists(key))
        except Exception as e:
            logger.error(f"Redis检查失败: {e}")
        return False

# 创建全局Redis连接实例
redis_connection = RedisConnection()

# 便捷函数
def get_redis_client() -> Optional[redis.Redis]:
    """获取Redis客户端"""
    return redis_connection.get_client()

def redis_set(key: str, value: str, ex: Optional[int] = None) -> bool:
    """设置Redis键值对"""
    return redis_connection.set(key, value, ex)

def redis_get(key: str) -> Optional[str]:
    """获取Redis值"""
    return redis_connection.get(key)

def redis_delete(key: str) -> bool:
    """删除Redis键"""
    return redis_connection.delete(key)

def redis_exists(key: str) -> bool:
    """检查Redis键是否存在"""
    return redis_connection.exists(key)

def is_redis_connected() -> bool:
    """检查Redis连接状态"""
    return redis_connection.is_connected()