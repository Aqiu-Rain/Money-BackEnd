# 导入系统库

# 导入第三方库
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 导入自定义库
from app.services.websocket.websocket_manager import WebSocketManager
from app.settings import load_app_settings

# 定义全局变量
config = load_app_settings()
engine = create_engine(config.DB.DATABASE_URL)
SessionLocal = sessionmaker(autoflush=config.DB.AUTO_FLASH, bind=engine)
Base = declarative_base()

# 获取websocket manager实例
def get_ws_manager():
    return WebSocketManager()
        


def get_rdbms():
    rdbms = SessionLocal()
    try:
        yield rdbms
    finally:
        rdbms.close()


def get_rdbms_sync():
    rdbms = SessionLocal()
    return rdbms


def generate_tables():
    Base.metadata.create_all(bind=engine)