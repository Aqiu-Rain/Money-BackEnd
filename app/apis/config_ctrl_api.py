# 导入第三方库
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query

# 导入自定义库
from app.extensions import get_rdbms
from app.settings import load_app_settings
from app.schemas.config import UpdateSchema
from app.cores.config import getSetting, updateSetting
from app.services.serial.serial_communication import get_ports

# 定义全局变量
router = APIRouter()
settings = load_app_settings()

# 获取串口列表
@router.get('/serials', status_code=200, description='获取串口列表')
def get_serial_lists():
    return get_ports()


# 获取串口配置
@router.get('/setting', status_code=200, description='获取设置')
def get_setting(db: Session = Depends(get_rdbms)):
    return getSetting(db)


# 更新串口配置
@router.put('/setting', status_code=200, description='更新设置')
def update_setting(data: UpdateSchema, db: Session = Depends(get_rdbms)):
    return updateSetting(data, db)


