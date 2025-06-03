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
    if not data.date_range:
        # 查找Result.sno包含data.q 的所有结果

        if data.code == "all":
            items = db.query(Result).filter(Result.sno.like(f'%{data.q}%')).all()
        else:
            items = db.query(Result).filter(Result.sno.like(f'%{data.q}%'), Result.tf_flag==data.code).all()

        pdf_data = [
            {
                'create_at': item.create_at,
                'money_flag': item.money_flag,
                'tf_flag': item.tf_flag,
                'ver': item.ver,
                'valuta': item.valuta,
                'machine_number': item.machine_number,
                'sno': item.sno,
                'image_data': item.image_data,
            } for item in items
        ]

        excel_data = [
            {
                'Data&Time': datetime.fromisoformat(str(item.create_at)).strftime('%Y-%m-%d %H:%M:%S'),
                'Currency.': item.money_flag,
                'Denom.': item.tf_flag,
                'Version': item.ver,
                'Code': item.valuta,
                'Machine No.': item.machine_number,
                'S.N.': item.sno,
                'S.N. Image': item.image_data,
            } for item in items
        ]

        return {"data": pdf_data, "excel_data": excel_data, "total": len(pdf_data)}
    else:
        logger.debug(data.date_range)
        start_date = datetime.strptime(data.date_range[0], '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(data.date_range[1], '%Y-%m-%d %H:%M:%S')
        logger.debug(start_date)
        logger.debug(end_date)

        if data.code == "all":
            items = db.query(Result).filter(
                and_(Result.sno.like(f'%{data.q}%'), Result.create_at.between(start_date, end_date))
            ).order_by(Result.id.desc()).all()
        else:
            items = db.query(Result).filter(
                and_(Result.sno.like(f'%{data.q}%'), Result.create_at.between(start_date, end_date), Result.tf_flag==data.code)
            ).order_by(Result.id.desc()).all()

        end_time = time.time()

        logger.debug(f'cost: {int(end_time) - int(start_time)}')
        pdf_data = [
            {
                'create_at': item.create_at,
                'money_flag': item.money_flag,
                'tf_flag': item.tf_flag,
                'ver': item.ver,
                'valuta': item.valuta,
                'machine_number': item.machine_number,
                'sno': item.sno,
                'image_data': item.image_data,
            } for item in items
        ]
        excel_data = [
            {
                'Data&Time': datetime.fromisoformat(str(item.create_at)).strftime('%Y-%m-%d %H:%M:%S'),
                'Currency.': item.money_flag,
                'Denom.': item.tf_flag,
                'Version': item.ver,
                'Code': item.valuta,
                'Machine No.': item.machine_number,
                'S.N.': item.sno,
                'S.N. Image': item.image_data,
            } for item in items
        ]

        return {"data": pdf_data, "excel_data":excel_data, "total": len(pdf_data)}


def deleteAllMoney(db: Session):
    db.query(Result).delete()

    db.commit()

    return {'detail': '删除成功'}