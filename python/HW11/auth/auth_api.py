from fastapi import APIRouter, Depends, HTTPException, status, Body
from datetime import timedelta
from uuid import uuid4

from auth.auth_schema import UserResponse, UserRegistrate, Token, Login
from auth.user_service import UserService, get_users_service
from auth.auth_service import get_auth_service, AuthService, get_req_service
from auth.auth_refresh_repository import get_refresh_reposetory
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from auth.depend import require_write_access

router = APIRouter()


@router.post("/registrate", response_model=UserResponse)
async def registrate(form_data: UserRegistrate, service: UserService = Depends(get_users_service)):
    res = await service.create_user(form_data)
    return res

@router.get("/users/me/", response_model=UserResponse)
async def read_users_me(service: AuthService = Depends(get_auth_service)):
    current_user = await service.get_current_user()
    return current_user

@router.post("/token", response_model=Token)
async def login_for_access_token(from_data: Login, service: AuthService = Depends(get_req_service)):
    user = await service.authenticate_user(from_data.email, from_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate" : "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await service.create_access_token(data={"sub" : user.email}, expires_delta=access_token_expires)
    refresh_plain = await service.create_refresh_token(user.id)
    return {"access_token" : access_token, "refresh_token": refresh_plain, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str = Body(...), service: AuthService = Depends(get_req_service), 
                        refresh_repo = Depends(get_refresh_reposetory)):
    verified = await service.verify_refersh_token(refresh_token)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    rt = verified["refresh"]
    user = verified["user"]
    
    await refresh_repo.revoke(rt.id)
    
    new_refresh_plain = str(uuid4())
    await refresh_repo.create(new_refresh_plain, user.id)
    access_token = service.create_access_token({"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "refresh_token": new_refresh_plain, "token_type": "bearer"}

@router.post("/logout")
async def logout(refresh_token: str = Body(...), auth_service: AuthService = Depends(get_req_service), 
                refresh_repo = Depends(get_refresh_reposetory)):
    rt = await refresh_repo.get_by_hash(refresh_token)
    if not rt:
        raise HTTPException(status_code=404, detail="Refresh token not found")
    await refresh_repo.revoke(rt.id)
    return {"detail": "Logged out"}

@router.post("/items/isthereaccessforrecording", description="Проверка прав доступа")
async def is_there_access_for_recording(user = Depends(require_write_access)):
    # только пользователи с правом записи попадут сюда
    return {"message": "ok"}