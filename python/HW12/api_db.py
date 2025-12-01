from fastapi import APIRouter, Depends, HTTPException, status, Response
from service import *
from models import *
from pathlib import Path

from auth.depend import require_write_access

file_path = Path("students.csv")


router = APIRouter(prefix="/db", tags=["Database"])


@router.get("/initbase", response_model=None, status_code=status.HTTP_201_CREATED, description="Создание пустой базы, если в репозитории лежит файл students.csv, то добавит все данные в БД")
async def init_database(db_manager: DataBaseManager = Depends(get_manager)) -> dict:
    await init_db()
    if file_path:
        await db_manager.insert_from_file("students.csv")
    else:
        return {"massage": "File not found"}
    return {"message": "Base created"}

@router.get("/findcourse", response_model=List[UserResponse], status_code=status.HTTP_200_OK, description="Пример получения списка студентов по выбранному курсу")
async def find_by_course(course: str, db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    result = await db_manager.get_users_by_course(course)
    return result
    
@router.get("/courseofminesmition", response_model=List[UserResponse], status_code=status.HTTP_200_OK, description="Пример получения списка студентов по выбранному курсу с оценкой ниже 30 баллов")
async def min_esmition_course(course: str, threshold: float = 30, db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    result = await db_manager.get_min_esmition(course, threshold)
    return result    
    
@router.get("/findfaculty", response_model=List[UserResponse], status_code=status.HTTP_200_OK, description="Пример получения списка студентов по выбранному факультету")
async def find_by_faculty(faculty: str, db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    result = await db_manager.get__users_by_faculty(faculty)
    return result


@router.get("/averagescore", response_model=float, status_code=status.HTTP_200_OK, description="Пример получения среднего балла по факультету")
async def average_score_by_faculty(faculty: str, db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    result = await db_manager.get_average_score(faculty)
    return result



@router.put("/changedata", response_model=UserResponse, status_code=status.HTTP_200_OK, description="Обновить данные студента")
async def average_score_by_faculty(user_id: UUID, user_data: UserUpdate, db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    try:
        result = await db_manager.update_user(user_id, user_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/deleteuser", response_model=bool, status_code=status.HTTP_200_OK, description="Обновить данные студента")
async def delete_user(user_id: UUID, db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    result = await db_manager.delete_user(user_id)
    return result
