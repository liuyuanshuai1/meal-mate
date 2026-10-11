from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.response import ok
from app.models.user import User
from app.schemas.common import PageResult
from app.schemas.eat_record import EatRecordItemOut, EatRecordOut
from app.services.eat_record_service import EatRecordService

router = APIRouter(prefix="/eat-records", tags=["eat-records"])


@router.get("")
async def list_eat_records(
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    records, total = await EatRecordService.list_records(db, user.id, page, page_size)
    items = [
        EatRecordOut(
            id=record.id,
            user_id=record.user_id,
            person=record.person,
            feeding_total=sum(item.feeding_value * item.quantity for item in record.items),
            eaten_at=record.eaten_at,
            items=[EatRecordItemOut.model_validate(item) for item in record.items],
            created_at=record.created_at,
            updated_at=record.updated_at,
        ).model_dump(mode="json")
        for record in records
    ]
    data = PageResult(items=items, total=total, page=page, page_size=page_size)
    return ok(data.model_dump(mode="json"))


@router.get("/{record_id}")
async def get_eat_record(
    record_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    record = await EatRecordService.get_record(db, record_id, user.id)
    return ok(
        EatRecordOut(
            id=record.id,
            user_id=record.user_id,
            person=record.person,
            feeding_total=sum(item.feeding_value * item.quantity for item in record.items),
            eaten_at=record.eaten_at,
            items=[EatRecordItemOut.model_validate(item) for item in record.items],
            created_at=record.created_at,
            updated_at=record.updated_at,
        ).model_dump(mode="json")
    )


@router.delete("/{record_id}")
async def delete_eat_record(
    record_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    await EatRecordService.delete_record(db, record_id, user.id)
    return ok()
