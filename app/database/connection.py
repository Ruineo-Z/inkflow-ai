from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import logging
from app.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建基础模型类
Base = declarative_base()

def create_database_if_not_exists():
    """检查并创建数据库（如果不存在）"""
    try:
        # 对于SQLite，数据库文件会自动创建，无需特殊处理
        if settings.database_url.startswith('sqlite'):
            logger.info("使用SQLite数据库，文件将自动创建")
            return

        # PostgreSQL数据库创建逻辑
        if settings.database_url.startswith('postgresql'):
            # 解析数据库URL获取数据库名
            db_url_parts = settings.database_url.split('/')
            db_name = db_url_parts[-1]
            base_url = '/'.join(db_url_parts[:-1]) + '/postgres'  # 连接到默认postgres数据库

            # 创建临时引擎连接到postgres数据库
            temp_engine = create_engine(base_url, isolation_level='AUTOCOMMIT')

            with temp_engine.connect() as conn:
                # 检查数据库是否存在
                result = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": db_name}
            )
            
            if not result.fetchone():
                # 数据库不存在，创建它
                logger.info(f"数据库 {db_name} 不存在，正在创建...")
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"数据库 {db_name} 创建成功")
            else:
                logger.info(f"数据库 {db_name} 已存在")
                
        temp_engine.dispose()
        
    except Exception as e:
        logger.error(f"创建数据库时出错: {e}")
        raise

def init_database():
    """初始化数据库和数据表"""
    try:
        # 首先确保数据库存在
        create_database_if_not_exists()
        
        # 创建数据库引擎
        engine = create_engine(
            settings.database_url,
            echo=settings.debug,  # 在调试模式下显示SQL语句
            pool_pre_ping=True,   # 连接池预检查
            pool_recycle=300      # 连接回收时间
        )
        
        return engine
        
    except Exception as e:
        logger.error(f"初始化数据库时出错: {e}")
        raise

def create_tables():
    """创建数据表"""
    try:
        # 导入所有模型以确保它们被注册到Base.metadata
        from app.models import Story, Chapter, Choice
        
        # 创建所有表
        logger.info("正在创建数据表...")
        Base.metadata.create_all(bind=engine)
        logger.info("数据表创建完成")
        
    except Exception as e:
        logger.error(f"创建数据表时出错: {e}")
        raise

# 初始化数据库并创建引擎
engine = init_database()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖注入：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()