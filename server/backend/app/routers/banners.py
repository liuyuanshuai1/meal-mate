from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_auth import require_admin
from app.core.database import get_db
from app.core.response import AppException, ok
from app.models.banner import Banner
from app.schemas.banner import BannerCreate, BannerOut, BannerUpdate

router = APIRouter(prefix="/banners", tags=["banners"])


@router.get("")
async def list_banners(include_inactive: bool = False, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    stmt = select(Banner)
    if not include_inactive:
        stmt = stmt.where(Banner.is_active.is_(True))
    stmt = stmt.order_by(Banner.sort.asc(), Banner.id.asc())
    rows = (await db.scalars(stmt)).all()
    data = [BannerOut.model_validate(row).model_dump(mode="json") for row in rows]
    return ok(data)


@router.post("")
async def create_banner(
    payload: BannerCreate,
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    banner = Banner(**payload.model_dump())
    db.add(banner)
    await db.commit()
    await db.refresh(banner)
    return ok(BannerOut.model_validate(banner).model_dump(mode="json"))


@router.put("/{banner_id}")
async def update_banner(
    banner_id: int,
    payload: BannerUpdate,
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    banner = await db.get(Banner, banner_id)
    if banner is None:
        raise AppException(40004, "banner 不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(banner, key, value)
    await db.commit()
    await db.refresh(banner)
    return ok(BannerOut.model_validate(banner).model_dump(mode="json"))


@router.delete("/{banner_id}")
async def delete_banner(
    banner_id: int,
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    banner = await db.get(Banner, banner_id)
    if banner is None:
        raise AppException(40004, "banner 不存在")
    banner.is_active = False
    await db.commit()
    await db.refresh(banner)
    return ok(BannerOut.model_validate(banner).model_dump(mode="json"))
