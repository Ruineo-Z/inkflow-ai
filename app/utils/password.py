"""
密码哈希和验证工具
使用bcrypt进行安全的密码哈希
"""

import bcrypt


class PasswordUtils:
    """密码工具类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        对密码进行哈希处理
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码字符串
        """
        # 生成盐值并哈希密码
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        验证密码是否正确
        
        Args:
            password: 明文密码
            hashed_password: 哈希后的密码
            
        Returns:
            密码是否匹配
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    @staticmethod
    def is_strong_password(password: str) -> tuple[bool, str]:
        """
        检查密码强度
        
        Args:
            password: 密码
            
        Returns:
            (是否强密码, 错误信息)
        """
        if len(password) < 8:
            return False, "密码长度至少8位"
        
        if len(password) > 128:
            return False, "密码长度不能超过128位"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "密码必须包含大写字母、小写字母和数字"
        
        return True, ""
