#!/usr/bin/env python3
"""
InkFlow AI - 启动脚本
使用uv环境启动应用
"""

import subprocess
import sys
import os

def main():
    """启动应用"""
    print("🚀 启动 InkFlow AI 后端服务...")
    
    # 确保在项目根目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # 使用uv运行应用
        subprocess.run([
            "uv", "run", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "20001",
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
        sys.exit(0)

if __name__ == "__main__":
    main()
