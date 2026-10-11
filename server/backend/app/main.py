from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.response import AppException, fail, ok
from app.routers import (
    admin,
    auth,
    banners,
    dining_groups,
    dinner_plans,
    eat_records,
    feeding_values,
    food_categories,
    foods,
)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    app.include_router(health_router(), prefix="/api")
    app.include_router(auth.router, prefix="/api")
    app.include_router(food_categories.router, prefix="/api")
    app.include_router(foods.router, prefix="/api")
    app.include_router(banners.router, prefix="/api")
    app.include_router(eat_records.router, prefix="/api")
    app.include_router(dining_groups.router, prefix="/api")
    app.include_router(dinner_plans.router, prefix="/api")
    app.include_router(feeding_values.router, prefix="/api")
    app.include_router(admin.router)

    static_root = Path(settings.upload_dir).parent
    static_root.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_root)), name="static")

    register_exception_handlers(app)
    return app


def health_router() -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict[str, Any]:
        settings = get_settings()
        return ok({"status": "ok", "app_name": settings.app_name, "env": settings.app_env})

    return router


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(status_code=200, content=fail(exc.code, exc.message))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        content = fail(40001, "参数错误", {"errors": jsonable_encoder(exc.errors())})
        return JSONResponse(status_code=200, content=content)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if request.url.path.startswith("/admin") and exc.status_code in {401, 403}:
            return JSONResponse(
                status_code=exc.status_code,
                content=fail(40300, str(exc.detail)),
                headers=exc.headers,
            )
        code = 40004 if exc.status_code == 404 else 40001
        return JSONResponse(status_code=200, content=fail(code, str(exc.detail)))

    @app.exception_handler(Exception)
    async def unknown_exception_handler(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(status_code=200, content=fail(50000, "服务器内部错误"))


app = create_app()
