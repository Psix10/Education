import logging

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from service import *
from models import *
from pathlib import Path
from typing import List

from auth.depend import require_write_access
from auth.auth_schema import IDList
from redis_m.residconnect import cache_response


file_path = Path("students.csv")


router = APIRouter(prefix="/db", tags=["Database"])

logger = logging.getLogger("delete_users")
logging.basicConfig(level=logging.INFO)

@router.get("/initbase", response_model=None, status_code=status.HTTP_201_CREATED, description="Создание пустой базы, если в репозитории лежит файл students.csv, то добавит все данные в БД")
async def init_database(db_manager: DataBaseManager = Depends(get_manager)) -> dict:
    await init_db()
    # if file_path:
    #     await db_manager.insert_from_file("students.csv")
    # else:
    #     return {"massage": "File not found"}
    return {"message": "Base created"}

"""HW 12 Задание создайте эндпойнт в проекте FastAPI выполняющий эту процедуру как фоновую задачу. В качестве параметров он должен принимать путь к csv файлу:"""
async def add_students_by_file(db_manager: DataBaseManager, file: str) -> NoReturn:
    if file_path:
        await db_manager.insert_from_file(file)

@router.post("/addfromfile", response_model=None, status_code=status.HTTP_200_OK, description="Добавление студентов из файла students.csv")
async def add_users_from_file(background_tasks: BackgroundTasks, db_manager: DataBaseManager = Depends(get_manager)) -> dict:
    print("Starting background task to add students from file...")
    background_tasks.add_task(add_students_by_file, db_manager, "students.csv")
    print("Background task added.")
    return {"message": "Adding students in background"}

"""_________________________________________________________________________________________________________________________________________________________"""

@router.get("/findcourse", response_model=List[UserResponse], status_code=status.HTTP_200_OK, description="Пример получения списка студентов по выбранному курсу")
async def find_by_course(course: str, db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    result = await db_manager.get_users_by_course(course)
    return result
    
@router.get("/courseofminesmition", response_model=List[UserResponse], status_code=status.HTTP_200_OK, description="Пример получения списка студентов по выбранному курсу с оценкой ниже 30 баллов")
@cache_response(expire=120)
async def min_esmition_course(request: Request, course: str, threshold: float = 30, db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    result = await db_manager.get_min_esmition(course, threshold)
    return result    
    
@router.get("/findfaculty", response_model=List[UserResponse], status_code=status.HTTP_200_OK, description="Пример получения списка студентов по выбранному факультету")
@cache_response(expire=120)
async def find_by_faculty(faculty: str, db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    result = await db_manager.get__users_by_faculty(faculty)
    return result


@router.get("/averagescore", response_model=float, status_code=status.HTTP_200_OK, description="Пример получения среднего балла по факультету")
@cache_response(expire=120)
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
async def delete_user(user_id: int, db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> List[User]:
    result = await db_manager.delete_user(user_id)
    return result

"""HW 12 Шаг 2. Так же добавьте эндпойнт позволяющий удалить записи из БД по переданному списку. Выполнение процедуры удаления также следует выполнять как фоновую задачу."""
async def delete_users_by_list(db_manager: DataBaseManager, user_ids: List[int]) -> None:
    try:
        for i in user_ids:
            try:
                deleted = await db_manager.delete_user(i)
                if deleted:
                    logger.info("Successfully deleted user with id: %s", i)
                else:
                    logger.warning("User with id %s not found", i)
            except Exception as e:
                logger.info("Background task finished successfully for ids: %s", i)
    except asyncio.CancelledError:
        logger.warning("Background task cancelled for ids: %s", i)
    except Exception as e:
        logger.exception("Error while deleting users in background for ids %s: %s", i, e)
        
        
@router.delete("/deleteuserbylist", response_model=dict, status_code=status.HTTP_200_OK, description="Удалить студентов по списку id")
async def delete_user_by_list(user_ids: IDList, background_tasks: BackgroundTasks, db_manager: DataBaseManager = Depends(get_manager), user = Depends(require_write_access)) -> dict:
    print("Starting background task to delete students by list...")
    user_ids = user_ids.user_ids
    if not user_ids:
        raise HTTPException(status_code=400, detail="No user IDs provided") 
    
    background_tasks.add_task(delete_users_by_list, db_manager, user_ids)
    print("Background task added.")
    return {"message": "Deleting students in background"}