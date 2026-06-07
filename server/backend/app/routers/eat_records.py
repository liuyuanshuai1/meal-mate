from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import ok
from app.schemas.common import PageResult
from app.schemas.eat_record import EatRecordCreate, EatRecordOut
from app.services.eat_record_service import EatRecordService

router = APIRouter(prefix="/eat-records", tags=["eat-records"])


@router.post("")
async def create_eat_record(payload: EatRecordCreate, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    record = await EatRecordService.create_record(db, payload)
    return ok(EatRecordOut.model_validate(record).model_dump(mode="json"))


@router.get("")
async def list_eat_records(
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    records, total = await EatRecordService.list_records(db, user_id, page, page_size)
    items = [EatRecordOut.model_validate(record).model_dump(mode="json") for record in records]
    data = PageResult(items=items, total=total, page=page, page_size=page_size)
    return ok(data.model_dump(mode="json"))


@router.get("/{record_id}")
async def get_eat_record(record_id: int, user_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    record = await EatRecordService.get_record(db, record_id, user_id)
    return ok(EatRecordOut.model_validate(record).model_dump(mode="json"))


@router.delete("/{record_id}")
async def delete_eat_record(record_id: int, user_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    await EatRecordService.delete_record(db, record_id, user_id)
    return ok()
