# 导入系统库
import json
import os.path

# 导入第三方库
from fastapi import FastAPI
from loguru import logger

# 导入自定义库
# from app.apis import router
from app.models import Config
from app.middlewares import add_cors_middleware
from app.settings import Settings, load_app_settings, DATA_STORE_DIR
from app.extensions import generate_tables, SessionLocal


def create_app() -> FastAPI:
    settings = load_app_settings()
    app = FastAPI(
        title=settings.APP.APP_TITLE,
        version=settings.APP.APP_VERSION,
        description=settings.APP.APP_DESCRIPTION
    )

    register_logger(settings)
    register_router(app, settings)
    init_dirs()
    register_middlewares(app, settings)
    register_databases()

    return app


def register_logger(sett: Settings):
    logger.remove()
    logger.add(sink=sett.LOGGING.LOG_NAME, rotation="1 MB", level=sett.LOGGING.LEVEL)

def register_router(app: FastAPI, sett: Settings):
    from app.apis.ws_ctrl_api import router as router_ws
    from app.apis.config_ctrl_api import router as router_config
    from app.apis.data_ctrl_api import router as router_data
    app.include_router(router_ws, prefix=sett.APP.GLOBAL_API_PREFIX)
    app.include_router(router_config, prefix=sett.APP.GLOBAL_API_PREFIX + '/config')
    app.include_router(router_data, prefix=sett.APP.GLOBAL_API_PREFIX + '/money')


def register_middlewares(app: FastAPI, sett: Settings):
    add_cors_middleware(app, sett)


def init_setting():
    base_settings = {
        'port': '',
        'baudrate': 384000,
        'bytesize': 8,
        'parity': 'N',
        'stopbits': 1,
        'timeout': 1.0,
        'xonxoff': False,
        'rtscts': False,
        'dsrdtr': False
    }

    db = SessionLocal()
    check = db.query(Config).filter_by(name='base').first()
    if not check:
        new_setting = Config(
            name='base',
            content=json.dumps(base_settings),
        )
        db.add(new_setting)
        db.commit()

    db.close()


def register_databases():
    generate_tables()
    init_setting()


def init_dirs():
    if not os.path.exists(DATA_STORE_DIR):
        os.makedirs(DATA_STORE_DIR, exist_ok=True)
