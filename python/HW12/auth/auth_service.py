from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import uuid4
from jose import JWTError, jwt
from pwdlib import PasswordHash

from auth.auth_repository import UserRepository, get_user_reposetory
from auth.auth_schema import TokenData, UserResponse
from config import *
from auth.auth_refresh_repository import RefreshTokenRepository, get_refresh_reposetory
from auth.utils import make_token_plain


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
    
    def hash_refresh_token(self, token: str):
        return self.pwd_context.hash(token)
    
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
                algorithms=ALGORITHM,
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
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
            
        to_encode.update({"exp" : int(expire.timestamp())})
        
        encode_jwt = jwt.encode(
            to_encode, 
            SECRET_KEY, 
            algorithm=ALGORITHM,
        )
        
        return encode_jwt

    async def create_refresh_token(self, user_id: int) -> tuple[int, str]:
        if not self.refresh_repo:
            raise RuntimeError("Refresh repo not configured")
        plain = make_token_plain()
        hashed = self.pwd_context.hash(plain)
        token_id = await self.refresh_repo.create(token_hash=hashed, plain=plain, user_id=user_id, expires_days=REFRESH_TOKEN_EXPIRE_DAYS)
        return token_id, plain

    async def verify_refresh_token(self, cookie_value: str):
        try:
            id_str, plain = cookie_value.split(".", 1)
            token_id = int(id_str)
        except Exception as e:
            print("Failed to split cookie:", cookie_value, e)
            return None

        rt = await self.refresh_repo.get_by_id(token_id)
        print("Token from DB:", rt)

        if not rt or rt.revoked or rt.expires_at < datetime.now(timezone.utc):
            print("Token invalid due to revoked/expired or missing")
            return None

        if rt.plain != plain:
            print("Plain does not match! DB:", rt.plain, "Cookie:", plain)
            return None

        user = await self.repo.get_by_id(rt.user_id)
        if not user:
            print("User not found for token!")
            return None

        print("Token and user verified successfully")
        return {"refresh": rt, "user": user}


async def get_req_service(repo: UserRepository = Depends(get_user_reposetory), refresh_repo: RefreshTokenRepository = Depends(get_refresh_reposetory)) -> AuthService:
    return AuthService(repo, refresh_repo)

async def get_auth_service(
    repo: UserRepository = Depends(get_user_reposetory),
    refresh_repo: RefreshTokenRepository = Depends(get_refresh_reposetory),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthService:
    return AuthService(repo, refresh_repo, credentials)