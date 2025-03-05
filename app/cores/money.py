from sqlalchemy.orm import Session

from app.models import Result
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


def deleteAllMoney(db: Session):
    db.query(Result).delete()

    db.commit()

    return {'detail': '删除成功'}