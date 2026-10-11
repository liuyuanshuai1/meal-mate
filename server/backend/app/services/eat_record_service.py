from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.response import AppException
from app.models.eat_record import EatRecord


class EatRecordService:
    @staticmethod
    async def list_records(db: AsyncSession, user_id: int, page: int, page_size: int) -> tuple[list[EatRecord], int]:
        if user_id <= 0:
            raise AppException(40001, "user_id 必须大于 0")
        if page < 1 or page_size < 1 or page_size > 100:
            raise AppException(40001, "分页参数错误")
        total = await db.scalar(select(func.count()).select_from(EatRecord).where(EatRecord.user_id == user_id))
        stmt = (
            select(EatRecord)
            .options(selectinload(EatRecord.items))
            .where(EatRecord.user_id == user_id)
            .order_by(EatRecord.eaten_at.desc(), EatRecord.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await db.scalars(stmt)).all()
        return list(rows), total or 0

    @staticmethod
    async def get_record(db: AsyncSession, record_id: int, user_id: int) -> EatRecord:
        if user_id <= 0:
            raise AppException(40001, "user_id 必须大于 0")
        stmt = (
            select(EatRecord)
            .options(selectinload(EatRecord.items))
            .where(EatRecord.id == record_id, EatRecord.user_id == user_id)
        )
        record = await db.scalar(stmt)
        if record is None:
            raise AppException(40004, "一起吃过记录不存在")
        return record

    @staticmethod
    async def delete_record(db: AsyncSession, record_id: int, user_id: int) -> None:
        record = await EatRecordService.get_record(db, record_id, user_id)
        await db.delete(record)
        await db.commit()
