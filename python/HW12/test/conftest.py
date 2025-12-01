import os
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from main import app
from base import get_session as real_get_session
from models import Base

# Тестовая БД — возьми из env если установлен, иначе fallback
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5431/postgres"
)

# test engine и фабрика сессий
test_engine = create_async_engine(
    TEST_DATABASE_URL, 
    echo=False, 
    future=True,
    poolclass=NullPool,
    )
TestingSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False, class_=AsyncSession)

# создаём/дропаем таблицы один раз за тестовую сессию
@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

# фикстура, если нужен доступ к сессии напрямую в тестах
@pytest_asyncio.fixture()
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

# клиент: переопределяем только get_session, чтобы каждый запрос получал новую сессию
@pytest_asyncio.fixture()
async def client():
    async def _override_get_session():
        async with TestingSessionLocal() as session:
            yield session

    # ПЕРЕОПРЕДЕЛЯЕМ только get_session — не трогаем фабрики репозиториев
    app.dependency_overrides[real_get_session] = _override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac