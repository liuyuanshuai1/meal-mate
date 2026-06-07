from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.response import AppException
from app.models.banner import Banner
from app.models.eat_record import EatRecord
from app.models.food import Food
from app.models.food_category import FoodCategory
from app.services.image_upload import save_upload_image

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))

MESSAGE_TEXT = {
    "created": "保存成功",
    "updated": "更新成功",
    "deleted": "删除成功",
}
LINK_TYPES = {"none", "food", "url"}


def success_redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=303)


def message_text(message: str | None) -> str | None:
    if message is None:
        return None
    return MESSAGE_TEXT.get(message)


def clean_optional(value: str | None, max_length: int | None = None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if cleaned == "":
        return None
    if max_length is not None and len(cleaned) > max_length:
        raise ValueError("参数错误")
    return cleaned


def clean_required(value: str, max_length: int) -> str:
    cleaned = value.strip()
    if cleaned == "" or len(cleaned) > max_length:
        raise ValueError("参数错误")
    return cleaned


def parse_int(value: str | None, default: int = 0, positive: bool = False) -> int:
    cleaned = (value or "").strip()
    if cleaned == "":
        parsed = default
    else:
        try:
            parsed = int(cleaned)
        except ValueError as exc:
            raise ValueError("参数错误") from exc
    if positive and parsed <= 0:
        raise ValueError("参数错误")
    return parsed


def parse_optional_int(value: str | None) -> int | None:
    cleaned = (value or "").strip()
    if cleaned == "":
        return None
    try:
        return int(cleaned)
    except ValueError as exc:
        raise ValueError("参数错误") from exc


def parse_decimal(value: str | None) -> Decimal:
    cleaned = (value or "").strip()
    if cleaned == "":
        return Decimal("0")
    try:
        parsed = Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError("参数错误") from exc
    if parsed < 0:
        raise ValueError("参数错误")
    return parsed


def checkbox(value: str | None) -> bool:
    return value is not None


async def list_categories(db: AsyncSession) -> list[FoodCategory]:
    rows = await db.scalars(select(FoodCategory).order_by(FoodCategory.sort.asc(), FoodCategory.id.asc()))
    return list(rows)


async def list_foods_with_category(db: AsyncSession) -> list[Food]:
    rows = await db.scalars(
        select(Food)
        .options(selectinload(Food.category))
        .where(Food.is_active.is_(True))
        .order_by(Food.sort.asc(), Food.id.asc()),
    )
    return list(rows)


async def list_banners(db: AsyncSession) -> list[Banner]:
    rows = await db.scalars(select(Banner).order_by(Banner.sort.asc(), Banner.id.asc()))
    return list(rows)


async def render_categories(
    request: Request,
    db: AsyncSession,
    message: str | None = None,
    error: str | None = None,
    edit_id: int | None = None,
    form: dict[str, object] | None = None,
) -> Response:
    edit_category = await db.get(FoodCategory, edit_id) if edit_id is not None else None
    return templates.TemplateResponse(
        request,
        "admin/categories.html",
        {
            "title": "菜品分类管理",
            "active_nav": "categories",
            "message": message_text(message),
            "error": error,
            "categories": await list_categories(db),
            "edit_category": edit_category,
            "form": form or {},
        },
    )


async def render_foods(
    request: Request,
    db: AsyncSession,
    message: str | None = None,
    error: str | None = None,
    edit_id: int | None = None,
    form: dict[str, object] | None = None,
) -> Response:
    edit_food = await db.get(Food, edit_id) if edit_id is not None else None
    return templates.TemplateResponse(
        request,
        "admin/foods.html",
        {
            "title": "菜品管理",
            "active_nav": "foods",
            "message": message_text(message),
            "error": error,
            "foods": await list_foods_with_category(db),
            "categories": await list_categories(db),
            "edit_food": edit_food,
            "form": form or {},
        },
    )


async def render_banners(
    request: Request,
    db: AsyncSession,
    message: str | None = None,
    error: str | None = None,
    edit_id: int | None = None,
    form: dict[str, object] | None = None,
) -> Response:
    edit_banner = await db.get(Banner, edit_id) if edit_id is not None else None
    return templates.TemplateResponse(
        request,
        "admin/banners.html",
        {
            "title": "Banner 管理",
            "active_nav": "banners",
            "message": message_text(message),
            "error": error,
            "banners": await list_banners(db),
            "edit_banner": edit_banner,
            "form": form or {},
            "link_types": ["none", "food", "url"],
        },
    )


async def parse_uploaded_or_url(file: UploadFile | None, image_url: str | None) -> str | None:
    if file is not None and file.filename:
        return await save_upload_image(file)
    return clean_optional(image_url)


@router.get("")
async def admin_index(request: Request, message: str | None = None) -> Response:
    return templates.TemplateResponse(
        request,
        "admin/index.html",
        {
            "title": "后台首页",
            "active_nav": "index",
            "message": message_text(message),
            "error": None,
        },
    )


@router.get("/categories")
async def admin_categories(
    request: Request,
    message: str | None = None,
    edit_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> Response:
    return await render_categories(request, db, message=message, edit_id=edit_id)


@router.post("/categories")
async def create_category(
    request: Request,
    name: Annotated[str, Form()],
    sort: Annotated[str | None, Form()] = None,
    is_active: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
) -> Response:
    form = {"name": name, "sort": sort or "", "is_active": checkbox(is_active)}
    try:
        category = FoodCategory(name=clean_required(name, 64), sort=parse_int(sort), is_active=checkbox(is_active))
        db.add(category)
        await db.commit()
    except ValueError as exc:
        await db.rollback()
        return await render_categories(request, db, error=str(exc), form=form)
    except SQLAlchemyError:
        await db.rollback()
        return await render_categories(request, db, error="保存失败，请稍后再试", form=form)
    return success_redirect("/admin/categories?message=created")


@router.post("/categories/{category_id}/update")
async def update_category(
    category_id: int,
    request: Request,
    name: Annotated[str, Form()],
    sort: Annotated[str | None, Form()] = None,
    is_active: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
) -> Response:
    form = {"name": name, "sort": sort or "", "is_active": checkbox(is_active)}
    category = await db.get(FoodCategory, category_id)
    if category is None:
        return await render_categories(request, db, error="数据不存在", form=form)
    try:
        category.name = clean_required(name, 64)
        category.sort = parse_int(sort)
        category.is_active = checkbox(is_active)
        await db.commit()
    except ValueError as exc:
        await db.rollback()
        return await render_categories(request, db, error=str(exc), edit_id=category_id, form=form)
    except SQLAlchemyError:
        await db.rollback()
        return await render_categories(request, db, error="保存失败，请稍后再试", edit_id=category_id, form=form)
    return success_redirect("/admin/categories?message=updated")


@router.post("/categories/{category_id}/delete")
async def delete_category(category_id: int, request: Request, db: AsyncSession = Depends(get_db)) -> Response:
    category = await db.get(FoodCategory, category_id)
    if category is None:
        return await render_categories(request, db, error="数据不存在")
    try:
        category.is_active = False
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        return await render_categories(request, db, error="保存失败，请稍后再试")
    return success_redirect("/admin/categories?message=deleted")


@router.get("/foods")
async def admin_foods(
    request: Request,
    message: str | None = None,
    edit_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> Response:
    return await render_foods(request, db, message=message, edit_id=edit_id)


@router.post("/foods")
async def create_food(
    request: Request,
    name: Annotated[str, Form()],
    category_id: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    image_url: Annotated[str | None, Form()] = None,
    image_file: Annotated[UploadFile | None, File()] = None,
    price: Annotated[str | None, Form()] = None,
    is_recommended: Annotated[str | None, Form()] = None,
    is_active: Annotated[str | None, Form()] = None,
    sort: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
) -> Response:
    form = {
        "name": name,
        "category_id": category_id or "",
        "description": description or "",
        "image_url": image_url or "",
        "price": price or "",
        "is_recommended": checkbox(is_recommended),
        "is_active": checkbox(is_active),
        "sort": sort or "",
    }
    try:
        food = Food(
            category_id=parse_optional_int(category_id),
            name=clean_required(name, 128),
            description=clean_optional(description),
            image_url=await parse_uploaded_or_url(image_file, image_url),
            price=parse_decimal(price),
            is_recommended=checkbox(is_recommended),
            is_active=checkbox(is_active),
            sort=parse_int(sort),
        )
        db.add(food)
        await db.commit()
    except (ValueError, AppException) as exc:
        await db.rollback()
        return await render_foods(request, db, error=str(exc), form=form)
    except SQLAlchemyError:
        await db.rollback()
        return await render_foods(request, db, error="保存失败，请稍后再试", form=form)
    return success_redirect("/admin/foods?message=created")


@router.post("/foods/{food_id}/update")
async def update_food(
    food_id: int,
    request: Request,
    name: Annotated[str, Form()],
    category_id: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    image_url: Annotated[str | None, Form()] = None,
    image_file: Annotated[UploadFile | None, File()] = None,
    price: Annotated[str | None, Form()] = None,
    is_recommended: Annotated[str | None, Form()] = None,
    is_active: Annotated[str | None, Form()] = None,
    sort: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
) -> Response:
    form = {
        "name": name,
        "category_id": category_id or "",
        "description": description or "",
        "image_url": image_url or "",
        "price": price or "",
        "is_recommended": checkbox(is_recommended),
        "is_active": checkbox(is_active),
        "sort": sort or "",
    }
    food = await db.get(Food, food_id)
    if food is None:
        return await render_foods(request, db, error="数据不存在", form=form)
    try:
        food.category_id = parse_optional_int(category_id)
        food.name = clean_required(name, 128)
        food.description = clean_optional(description)
        food.image_url = await parse_uploaded_or_url(image_file, image_url)
        food.price = parse_decimal(price)
        food.is_recommended = checkbox(is_recommended)
        food.is_active = checkbox(is_active)
        food.sort = parse_int(sort)
        await db.commit()
    except (ValueError, AppException) as exc:
        await db.rollback()
        return await render_foods(request, db, error=str(exc), edit_id=food_id, form=form)
    except SQLAlchemyError:
        await db.rollback()
        return await render_foods(request, db, error="保存失败，请稍后再试", edit_id=food_id, form=form)
    return success_redirect("/admin/foods?message=updated")


@router.post("/foods/{food_id}/delete")
async def delete_food(food_id: int, request: Request, db: AsyncSession = Depends(get_db)) -> Response:
    food = await db.get(Food, food_id)
    if food is None:
        return await render_foods(request, db, error="数据不存在")
    try:
        food.is_active = False
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        return await render_foods(request, db, error="保存失败，请稍后再试")
    return success_redirect("/admin/foods?message=deleted")


@router.get("/banners")
async def admin_banners(
    request: Request,
    message: str | None = None,
    edit_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> Response:
    return await render_banners(request, db, message=message, edit_id=edit_id)


@router.post("/banners")
async def create_banner(
    request: Request,
    image_url: Annotated[str, Form()],
    title: Annotated[str | None, Form()] = None,
    link_type: Annotated[str | None, Form()] = "none",
    link_target: Annotated[str | None, Form()] = None,
    sort: Annotated[str | None, Form()] = None,
    is_active: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
) -> Response:
    form = {
        "title": title or "",
        "image_url": image_url,
        "link_type": link_type or "none",
        "link_target": link_target or "",
        "sort": sort or "",
        "is_active": checkbox(is_active),
    }
    try:
        banner = Banner(
            title=clean_optional(title, 128),
            image_url=clean_required(image_url, 4096),
            link_type=clean_required(link_type or "none", 32),
            link_target=clean_optional(link_target, 256),
            sort=parse_int(sort),
            is_active=checkbox(is_active),
        )
        if banner.link_type not in LINK_TYPES:
            raise ValueError("参数错误")
        db.add(banner)
        await db.commit()
    except ValueError as exc:
        await db.rollback()
        return await render_banners(request, db, error=str(exc), form=form)
    except SQLAlchemyError:
        await db.rollback()
        return await render_banners(request, db, error="保存失败，请稍后再试", form=form)
    return success_redirect("/admin/banners?message=created")


@router.post("/banners/{banner_id}/update")
async def update_banner(
    banner_id: int,
    request: Request,
    image_url: Annotated[str, Form()],
    title: Annotated[str | None, Form()] = None,
    link_type: Annotated[str | None, Form()] = "none",
    link_target: Annotated[str | None, Form()] = None,
    sort: Annotated[str | None, Form()] = None,
    is_active: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
) -> Response:
    form = {
        "title": title or "",
        "image_url": image_url,
        "link_type": link_type or "none",
        "link_target": link_target or "",
        "sort": sort or "",
        "is_active": checkbox(is_active),
    }
    banner = await db.get(Banner, banner_id)
    if banner is None:
        return await render_banners(request, db, error="数据不存在", form=form)
    try:
        parsed_link_type = clean_required(link_type or "none", 32)
        if parsed_link_type not in LINK_TYPES:
            raise ValueError("参数错误")
        banner.title = clean_optional(title, 128)
        banner.image_url = clean_required(image_url, 4096)
        banner.link_type = parsed_link_type
        banner.link_target = clean_optional(link_target, 256)
        banner.sort = parse_int(sort)
        banner.is_active = checkbox(is_active)
        await db.commit()
    except ValueError as exc:
        await db.rollback()
        return await render_banners(request, db, error=str(exc), edit_id=banner_id, form=form)
    except SQLAlchemyError:
        await db.rollback()
        return await render_banners(request, db, error="保存失败，请稍后再试", edit_id=banner_id, form=form)
    return success_redirect("/admin/banners?message=updated")


@router.post("/banners/{banner_id}/delete")
async def delete_banner(banner_id: int, request: Request, db: AsyncSession = Depends(get_db)) -> Response:
    banner = await db.get(Banner, banner_id)
    if banner is None:
        return await render_banners(request, db, error="数据不存在")
    try:
        banner.is_active = False
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        return await render_banners(request, db, error="保存失败，请稍后再试")
    return success_redirect("/admin/banners?message=deleted")


def parse_user_id(value: str | None) -> int:
    return parse_int(value, default=1, positive=True)


@router.get("/eat-records")
async def admin_eat_records(
    request: Request,
    user_id: str | None = None,
    message: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> Response:
    try:
        parsed_user_id = parse_user_id(user_id)
    except ValueError as exc:
        return templates.TemplateResponse(
            request,
            "admin/eat_records.html",
            {
                "title": "一起吃过记录",
                "active_nav": "eat_records",
                "message": None,
                "error": str(exc),
                "records": [],
                "user_id": user_id or "1",
            },
            status_code=400,
        )
    rows = await db.scalars(
        select(EatRecord)
        .options(selectinload(EatRecord.items))
        .where(EatRecord.user_id == parsed_user_id)
        .order_by(EatRecord.eaten_at.desc(), EatRecord.id.desc()),
    )
    return templates.TemplateResponse(
        request,
        "admin/eat_records.html",
        {
            "title": "一起吃过记录",
            "active_nav": "eat_records",
            "message": message_text(message),
            "error": None,
            "records": list(rows),
            "user_id": parsed_user_id,
        },
    )


@router.get("/eat-records/{record_id}")
async def admin_eat_record_detail(
    record_id: int,
    request: Request,
    user_id: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> Response:
    try:
        parsed_user_id = parse_user_id(user_id)
    except ValueError as exc:
        return templates.TemplateResponse(
            request,
            "admin/eat_record_detail.html",
            {
                "title": "一起吃过记录详情",
                "active_nav": "eat_records",
                "message": None,
                "error": str(exc),
                "record": None,
                "user_id": user_id or "1",
            },
            status_code=400,
        )
    record = await db.scalar(
        select(EatRecord)
        .options(selectinload(EatRecord.items))
        .where(EatRecord.id == record_id, EatRecord.user_id == parsed_user_id),
    )
    return templates.TemplateResponse(
        request,
        "admin/eat_record_detail.html",
        {
            "title": "一起吃过记录详情",
            "active_nav": "eat_records",
            "message": None,
            "error": None if record is not None else "数据不存在",
            "record": record,
            "user_id": parsed_user_id,
        },
        status_code=200 if record is not None else 404,
    )


@router.post("/eat-records/{record_id}/delete")
async def delete_eat_record(
    record_id: int,
    request: Request,
    user_id: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
) -> Response:
    try:
        parsed_user_id = parse_user_id(user_id)
    except ValueError as exc:
        return templates.TemplateResponse(
            request,
            "admin/eat_records.html",
            {
                "title": "一起吃过记录",
                "active_nav": "eat_records",
                "message": None,
                "error": str(exc),
                "records": [],
                "user_id": user_id or "1",
            },
            status_code=400,
        )
    record = await db.scalar(
        select(EatRecord)
        .options(selectinload(EatRecord.items))
        .where(EatRecord.id == record_id, EatRecord.user_id == parsed_user_id),
    )
    if record is None:
        return templates.TemplateResponse(
            request,
            "admin/eat_record_detail.html",
            {
                "title": "一起吃过记录详情",
                "active_nav": "eat_records",
                "message": None,
                "error": "数据不存在",
                "record": None,
                "user_id": parsed_user_id,
            },
            status_code=404,
        )
    try:
        await db.delete(record)
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        return templates.TemplateResponse(
            request,
            "admin/eat_record_detail.html",
            {
                "title": "一起吃过记录详情",
                "active_nav": "eat_records",
                "message": None,
                "error": "保存失败，请稍后再试",
                "record": record,
                "user_id": parsed_user_id,
            },
        )
    return success_redirect(f"/admin/eat-records?user_id={parsed_user_id}&message=deleted")
