from fastapi import APIRouter, Depends, HTTPException, status, Response
from service import *
from models import *

from auth.depend import require_write_access


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/addlistuser", response_model=None, status_code=status.HTTP_200_OK, description="Добавление студента списком")
async def add_user(users: List[UserCreate], db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> dict:
    users_list = [
        User(
        last_name=user.last_name,
        first_name=user.first_name,
        faculty=user.faculty,
        course=user.course,
        estimation=user.estimation
        )
        for user in users
    ]
    await db_manager.insert_users(users_list)
    return {"message": "User added successfully"}

@router.post("/adduser", response_model=None, status_code=status.HTTP_200_OK, description="Добавление студента")
async def add_user(user: UserCreate, db_manager: DataBaseManager = Depends(get_manager), users = Depends(require_write_access)) -> dict:
    new_user = User(
        last_name=user.last_name,
        first_name=user.first_name,
        faculty=user.faculty,
        course=user.course,
        estimation=user.estimation
    )
    await db_manager.insert_user(new_user)
    return {"message": "User added successfully"}

@router.get("/uniqcourse", response_model=list[str], status_code=status.HTTP_200_OK, description="Пример получения списка уникальных курсов")
async def users_by_course(db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    result = await db_manager.get_unique_course()
    return result

@router.get("/facultystudents", response_model=List[UserResponse], status_code=status.HTTP_200_OK, description="Пример получения списка студентов по названию факультета")
async def users_by_faculty(faculty: str, db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    result = await db_manager.get__users_by_faculty(faculty)
    return result


@router.get("/allusers", response_model=List[UserResponse], status_code=status.HTTP_200_OK, description="Пример получения списка студентов по названию факультета")
async def users_by_faculty(db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    result = await db_manager.get_all_users()
    return result

@router.get("/findidbyuserfaculty", response_model=List[UserResponse], status_code=status.HTTP_200_OK, description="Пример получения id (uuid) студента(-ов) по ФИ и факультету")
async def find_id_by_users_by_faculty(last_name: str, first_name: str, faculty: str, db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    result = await db_manager.get__users_by_first_name_last_name_faculty(last_name, first_name, faculty)
    return result

