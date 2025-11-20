from fastapi import APIRouter, Depends, HTTPException, status, Response
from service import *
from models import *
from pathlib import Path

file_path = Path("students.csv")


router = APIRouter(prefix="/db", tags=["Database"])


@router.post("/initbase", response_model=None, status_code=status.HTTP_201_CREATED, description="Создание пустой базы, если в репозитории лежит файл students.csv, то добавит все данные в БД")
async def init_database(db_manager: DataBaseManager = Depends(get_manager)) -> dict:
    await init_db()
    if file_path:
        await db_manager.insert_from_file("students.csv")
    else:
        return {"massage": "File not found"}
    return {"message": "Base created"}

@router.post("/findcourse", response_model=List[UserResponse], status_code=status.HTTP_200_OK, description="Пример получения списка студентов по выбранному курсу")
async def find_by_course(course: str, db_manager: DataBaseManager = Depends(get_manager)) -> List[User]:
    result = await db_manager.get_users_by_course(course)
    return result
    
@router.post("/courseofminesmition", response_model=List[UserResponse], status_code=status.HTTP_200_OK, description="Пример получения списка студентов по выбранному курсу с оценкой ниже 30 баллов")
async def min_esmition_course(course: str, threshold: float = 30, db_manager: DataBaseManager = Depends(get_manager)) -> List[User]:
    result = await db_manager.get_min_esmition(course, threshold)
    return result    
    
@router.post("/findfaculty", response_model=List[UserResponse], status_code=status.HTTP_200_OK, description="Пример получения списка студентов по выбранному факультету")
async def find_by_faculty(faculty: str, db_manager: DataBaseManager = Depends(get_manager)) -> List[User]:
    result = await db_manager.get__users_by_faculty(faculty)
    return result


@router.post("/averagescore", response_model=float, status_code=status.HTTP_200_OK, description="Пример получения среднего балла по факультету")
async def average_score_by_faculty(faculty: str, db_manager: DataBaseManager = Depends(get_manager)) -> List[User]:
    result = await db_manager.get_average_score(faculty)
    return result




    # print("\n\n******************** Пример получения списка уникальных курсов  ***********************\n\n")
    # c = await db_manager.get__users_by_course("Физика")
    # print(c)

    # print("\n\n******************** Пример получения списка студентов по названию факультета ***********************\n\n")
    # d = await db_manager.get__users_by_faculty("РЭФ")
    # print(d)

    # new_stundet = User(
    #     last_name="Встанька", 
    #     first_name="Ванька", 
    #     faculty="СИД", 
    #     course="Теор. Механика", 
    #     estimation=52
    #     )

    # print("\n\n******************** Пример добавление студента ***********************\n\n")

    # await db_manager.insert_user(new_stundet)

    # print("\n\n******************** Пример добавление списка студентов ***********************\n\n")
    # users_list = [
    #     User(last_name="Петров", first_name="Пётр", faculty="ФПМИ", course="Мат. Анализ", estimation=48),
    #     User(last_name="Сидоров", first_name="Сидор", faculty="ФТФ", course="Физика", estimation=37)
    # ]

    # await db_manager.insert_users(users_list)
    
    # e = db_manager.get_last_10_users()
    # print(e)