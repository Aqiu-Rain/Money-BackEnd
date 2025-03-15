# 导入系统库
import os
import sys
from typing import List

# 定义全局变量
USER_HOME = os.path.expanduser("~")
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'ui')
DATA_STORE_DIR = os.path.join(USER_HOME, 'money_data')


# 定义所有配置数据
class Settings:
    class APP:
        APP_TITLE: str = 'Cash Management SW_GRACETEK'
        APP_VERSION: str = '1.0.0'
        APP_DESCRIPTION: str = '[Money] 点钞数据记录.'
        BACKEND_SERVER: str = 'http://127.0.0.1:8000'

        GLOBAL_API_PREFIX: str = ''

    class DB:
        AUTO_FLASH: bool = True
        PREFIX: str = 'sqlite:///' if sys.platform.startswith('win') else 'sqlite:////'
        DATABASE_URL: str = PREFIX + os.path.join(DATA_STORE_DIR, 'data.db')

    class CORS_MIDDLEWARE:
        ALLOW_METHODS: List[str] = ["*"]
        ALLOW_HEADERS: List[str] = ["*"]
        ALLOW_ORIGINS: List[str] = ["*", ""]
        ALLOW_CREDENTIALS: bool = True

    class LOGGING:
        LEVEL: str = 'DEBUG'
        FORMAT: str = '{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{file}:{function}():{line} -> {message}'
        ENQUEUE: bool = True
        DIAGNOSE: bool = True
        TRACEBACK: bool = True
        LOG_NAME: str = os.path.join(DATA_STORE_DIR, 'money.log')
        RETENTION: int = 5

    class DATA_SOURCE:
        REAL_OR_TEST: str = 'real' # real代表数据是真实数据，test代表数据是从文件中读取的测试数据

def load_app_settings() -> Settings:
    settings = Settings()
    return settings
