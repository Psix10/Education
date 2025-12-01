
from typing import AsyncGenerator
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import NoReturn, List
from models import Base

engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost:5431/postgres",
    echo=True, #Потом выключить 
    future=True,
    
)

async_session_maker = async_sessionmaker(
    engine,
    class_ = AsyncSession,
    expire_on_commit = False
)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()