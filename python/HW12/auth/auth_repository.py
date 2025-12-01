from typing import Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth.auth_model import UserAuth
from base import get_session


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
    
    async def create(self, user_data: dict) -> UserAuth:
        user = UserAuth(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_by_id(self, id: int) -> Optional[UserAuth]:
        res = await self.db.execute(select(UserAuth).where(UserAuth.id == id))
        return res.scalar_one_or_none()
    
    async def get_by_name(self, name: int) -> Optional[UserAuth]:
        res = await self.db.execute(select(UserAuth).where(UserAuth.username == name))
        return res.scalar_one_or_none()
    
    async def get_by_email(self, email: int) -> Optional[UserAuth]:
        res = await self.db.execute(select(UserAuth).where(UserAuth.email == email))
        return res.scalar_one_or_none()




async def get_user_reposetory(db: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(db)