from fastapi import Depends, HTTPException, status
from auth.auth_service import get_auth_service

async def require_write_access(current_user = Depends(get_auth_service)):
    user = await current_user.get_current_user()
    # user.is_read_only — флаг в модели
    if getattr(user, "is_read_only", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not access")
    return user