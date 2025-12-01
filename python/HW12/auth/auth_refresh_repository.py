from datetime import datetime, timedelta, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from auth.auth_model import RefreshToken as RefreshTokenModel
from base import get_session
from fastapi import Depends
from config import REFRESH_TOKEN_EXPIRE_DAYS


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, token_hash: str, plain: str, user_id: int, expires_days: int = REFRESH_TOKEN_EXPIRE_DAYS) -> RefreshTokenModel:
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)
        rt = RefreshTokenModel(token_hash=token_hash, plain=plain, user_id=user_id, expires_at=expires_at)
        self.db.add(rt)
        await self.db.commit()
        await self.db.refresh(rt)
        return rt.id
    
    async def get_by_hash(self, token_hash: str) -> RefreshTokenModel | None:
        res = await self.db.execute(select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash))
        return res.scalar_one_or_none()
    
    async def get_by_id(self, id: int) -> RefreshTokenModel | None:
        res = await self.db.execute(select(RefreshTokenModel).where(RefreshTokenModel.id == id))
        return res.scalar_one_or_none()
    
    async def revoke(self, token_id: int) -> bool:
        res = await self.db.execute(select(RefreshTokenModel).where(RefreshTokenModel.id == token_id))
        obj = res.scalar_one_or_none()
        if obj:
            obj.revoked = True
            await self.db.commit()
            return True
        return False
    
    async def revoke_all_for_user(self, user_id: int):
        res = await self.db.execute(select(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id))
        rows = res.scalars().all()
        for r in rows:
            r.revoked = True
        await self.db.commit()
    



async def get_refresh_reposetory(db: AsyncSession = Depends(get_session)) -> RefreshTokenModel:
    return RefreshTokenRepository(db)