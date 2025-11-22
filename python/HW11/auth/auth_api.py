from fastapi import APIRouter, Depends, HTTPException, status, Body, Response, Cookie
from datetime import timedelta
from uuid import uuid4
from fastapi.responses import JSONResponse

from auth.auth_schema import UserResponse, UserRegistrate, Token, Login
from auth.user_service import UserService, get_users_service
from auth.auth_service import get_auth_service, AuthService, get_req_service
from auth.auth_refresh_repository import get_refresh_reposetory
from config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
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
async def login_for_access_token(from_data: Login, service: AuthService = Depends(get_req_service), refresh_repo = Depends(get_refresh_reposetory)):
    user = await service.authenticate_user(from_data.email, from_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate" : "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await service.create_access_token(data={"sub" : user.email}, expires_delta=access_token_expires)

    await refresh_repo.revoke(user.id)
    token_id, plain = await service.create_refresh_token(user.id)
    print("token_id:", token_id)
    print("plain:", plain)
    response = JSONResponse(
        content={
            "access_token": access_token,
            "toke_type": "bearer",
        },
        media_type="application/json"
    )
    response.set_cookie(
        key = "refresh_token",
        value = f"{token_id}.{plain}",
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60
    )
    return response

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str = Cookie(None), service: AuthService = Depends(get_auth_service), 
                        refresh_repo = Depends(get_refresh_reposetory)):
    if not refresh_token:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )
    refresh_token = refresh_token.strip('"')
    verified = await service.verify_refresh_token(refresh_token)
    
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    rt = verified["refresh"]
    user = verified["user"]
    
    print("RT:", rt)
    print("USER:", user)
    
    await refresh_repo.revoke(rt.id)
    await refresh_repo.revoke(user.id)
    
    access_token = await service.create_access_token({"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    token_id, plain = await service.create_refresh_token(user.id)
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"},
        media_type="application/json",
    )
    response.set_cookie(
        key = "refresh_token",
        value = f"{token_id}.{plain}",
        httponly = True,
        secure = False,
        samesite = "lax",
        max_age = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    
    return response

@router.post("/logout")
async def logout(refresh_token: str = Body(...), auth_service: AuthService = Depends(get_req_service), 
                refresh_repo = Depends(get_refresh_reposetory), user = Depends(require_write_access)):
    rt = await refresh_repo.get_by_hash(refresh_token)
    if not rt:
        raise HTTPException(status_code=404, detail="Refresh token not found")
    await refresh_repo.revoke(rt.id)
    return {"detail": "Logged out"}

@router.post("/items/isthereaccessforrecording", description="Проверка прав доступа")
async def is_there_access_for_recording(user = Depends(require_write_access)):
    # только пользователи с правом записи попадут сюда
    return {"message": "ok"}