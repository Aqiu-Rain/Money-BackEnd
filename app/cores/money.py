from datetime import datetime
from loguru import logger

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.models import Result
from app.schemas.money import SearchSchema
from app.responses import ResponseException


def getMoneyPages(skip: int, limit: int, db: Session):
    data = db.query(Result).offset(skip).limit(limit).all()
    count = db.query(Result).count()

    return {"data": data, "total": count}


def deleteMoney(id: int, db: Session):
    item = db.query(Result).filter_by(id=id).first()
    if not item:
        raise ResponseException.HTTP_404_NOT_FOUND

    db.delete(item)
    db.commit()

    return {'detail': '删除成功'}


def searchMoney(data: SearchSchema, db: Session):
    import time
    start_time = time.time()
    print(start_time)
    if not data.date_range:
        # 查找Result.sno包含data.q 的所有结果
        items = db.query(Result).filter(func.lower(Result.sno).like(f'%{data.q}%')).all()

        end_time = time.time()
        print(end_time)
        print(f'cost: {int(end_time) - int(start_time)}')

        return {"data": items, "total": len(items)}
    else:
        logger.debug(data.date_range)
        start_date = datetime.strptime(data.date_range[0], '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(data.date_range[1], '%Y-%m-%d %H:%M:%S')
        logger.debug(start_date)
        logger.debug(end_date)

        items = db.query(Result).filter(
            and_(Result.sno.like(f'%{data.q}%'), Result.create_at.between(start_date, end_date))
        ).order_by(Result.id.desc()).all()

        end_time = time.time()

        logger.debug(f'cost: {int(end_time) - int(start_time)}')

        return {"data": items, "total": len(items)}


def deleteAllMoney(db: Session):
    db.query(Result).delete()

    db.commit()

    return {'detail': '删除成功'}