from fastapi import Depends, HTTPException, status

from auth.auth_repository import UserRepository, get_user_reposetory
from auth.auth_schema import UserResponse, UserRegistrate
from pwdlib import PasswordHash
from auth.auth_schema import UserResponse


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo
        self.pwd_passwd = PasswordHash.recommended()

    async def get_password_hash(self, password):
        return self.pwd_passwd.hash(password)

    async def verify_password(self, plain_password, hashed_password):
        return self.pwd_passwd.verify(plain_password, hashed_password)

    async def get_user_by_id(self, user_id: int) -> UserResponse | None:
        user = await self.repo.get_by_id(user_id)
        return user

    async def get_user_by_name(self, username: str) -> UserResponse | None:
        post = await self.repo.get_by_name(username)
        return post

    async def get_user_by_email(self, email: str) -> UserResponse | None:
        post = await self.repo.get_by_email(email)
        return post

    async def create_user(self, user_data: UserRegistrate) -> UserResponse:
        if await self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="The user already exists"
            )
        data_dump = user_data.model_dump()
        data_dump["hashed_password"] = await self.get_password_hash(data_dump["password"])
        data_dump.pop("password")
        user = await self.repo.create(data_dump)
        
        return UserResponse.from_orm(user)

async def get_users_service(repo: UserRepository = Depends(get_user_reposetory)) -> UserService:
    return UserService(repo)