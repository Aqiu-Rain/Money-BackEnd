from fastapi import APIRouter

from app.apis.data_ctrl_api import router as money_router
from app.apis.config_ctrl_api import router as config_router

router = APIRouter()

router.include_router(money_router, prefix='/money', tags=['钱币'])
router.include_router(config_router, prefix='/config', tags=['config'])

