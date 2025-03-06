# 导入第三方库
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query

# 导入自定义库
from app.extensions import get_rdbms
from app.schemas.money import SearchSchema
from app.cores.money import getMoneyPages, deleteMoney, deleteAllMoney, searchMoney

# 定义全局变量
router = APIRouter()


@router.post('/search',status_code=200, description='搜索点钞记录')
def search(data: SearchSchema, db: Session = Depends(get_rdbms)):
    return searchMoney(data, db)


@router.get('/pages', status_code=200, description='分页获取所有点钞记录')
def pages(skip: int = Query(0, ge=0), limit: int = Query(10, gt=0), db: Session = Depends(get_rdbms)):
    return getMoneyPages(skip, limit, db)


@router.delete('/delete/{id}', status_code=200, description='删除点钞记录')
def delete_money(id: int, db: Session = Depends(get_rdbms)):
    return deleteMoney(id, db)


@router.delete('/delete/all', status_code=200, description='删除所有点钞记录')
def delete_money(db: Session = Depends(get_rdbms)):
    return deleteAllMoney(db)