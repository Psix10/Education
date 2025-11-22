from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import uuid4
from jose import JWTError, jwt
from pwdlib import PasswordHash

from auth.auth_repository import UserRepository, get_user_reposetory
from auth.auth_schema import TokenData, UserResponse
from config import *
from auth.auth_refresh_repository import RefreshTokenRepository, get_refresh_reposetory


security = HTTPBearer()

class AuthService:
    def __init__(
        self, repo: UserRepository,
        refresh_repo: RefreshTokenRepository | None = None,
        credentials: HTTPAuthorizationCredentials | None = None,
        
    ):
        self.repo = repo
        self.credentials = credentials
        self.refresh_repo = refresh_repo
        self.pwd_context = PasswordHash.recommended()
        
    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
    
    async def authenticate_user(self, email: str, password: str) -> UserResponse | bool:
        user = await self.repo.get_by_email(email)
        print("User from DB:", user)

        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user
    
    async def get_current_user(self):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                self.credentials.credentials,
                SECRET_KEY,
                ALGORITHM,
            )
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception

        user = await self.repo.get_by_email(email)
        if user.status is False:
            raise HTTPException(status_code=400, detail="Inactive user")
        if user is None:
            raise credentials_exception
        return user
    
    async def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
            
        to_encode.update({"exp" : expire})
        
        encode_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM,)
        
        return encode_jwt

    async def create_refresh_token(self, user_id: int) -> str:
        plain = str(uuid4())
        h = PasswordHash.recommended()
        hash = h.hash(plain)
        if not self.refresh_repo:
            raise RuntimeError("Refresh repo not configured")
        await self.refresh_repo.create(hash, user_id, expires_days=REFRESH_TOKEN_EXPIRE_DAYS)
        return hash

    async def verify_refresh_token(self, refresh_plain: str):
        if not self.refresh_repo:
            raise RuntimeError()
        rt = await self.refresh_repo.get_by_hash(refresh_plain)
        if not rt:
            return None
        if rt.revoked:
            return None
        if rt.expires_at < datetime.utcnow():
            return None
        user = await self.repo.get_by_id(rt.user_id)
        return {"refresh": rt, "user": user}


async def get_req_service(repo: UserRepository = Depends(get_user_reposetory), refresh_repo: RefreshTokenRepository = Depends(get_refresh_reposetory)) -> AuthService:
    return AuthService(repo, refresh_repo)

async def get_auth_service(
    repo: UserResponse = Depends(get_user_reposetory),
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_reposetory),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthService:
    return AuthService(repo, refresh_repo, credentials)