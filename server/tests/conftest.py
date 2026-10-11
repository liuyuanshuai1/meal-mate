from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from app import models  # noqa: F401
from app.core.admin_auth import require_admin_basic
from app.core.config import get_settings
from app.core.database import Base, get_db
from app.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

ADMIN_TOKEN = "test-admin-token"


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture()
def override_db(db_session: AsyncSession) -> Generator[None, None, None]:
    async def _get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[require_admin_basic] = lambda: None
    yield
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_headers() -> dict[str, str]:
    return {"X-Admin-Token": ADMIN_TOKEN}


@pytest_asyncio.fixture()
async def client(override_db: None, monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator[AsyncClient, None]:
    monkeypatch.setattr(get_settings(), "admin_token", ADMIN_TOKEN)
    monkeypatch.setattr("app.routers.auth.exchange_code_for_openid", lambda code: f"test:{code}")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
