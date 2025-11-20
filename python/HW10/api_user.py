from fastapi import APIRouter, Depends, HTTPException, status, Response
from service import *
from models import *



router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/adduser", response_model=None, status_code=status.HTTP_200_OK)
async def add_user(user: UserCreate, db_manager: DataBaseManager = Depends(get_manager)) -> dict:
    new_user = User(
        last_name=user.last_name,
        first_name=user.first_name,
        faculty=user.faculty,
        course=user.course,
        estimation=user.estimation
    )
    await db_manager.insert_user(new_user)
    return {"message": "User added successfully"}

@router.post("/uniqcourse", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def users_by_course(course: str, db_manager: DataBaseManager = Depends(get_manager)) -> List[User]:
    result = await db_manager.get__users_by_course(course)
    return result


    
    print("\n\n******************** Пример получения списка уникальных курсов  ***********************\n\n")
    c = await db_manager.get__users_by_course("Физика")
    print(c)

    print("\n\n******************** Пример получения списка студентов по названию факультета ***********************\n\n")
    d = await db_manager.get__users_by_faculty("РЭФ")
    print(d)

    new_stundet = User(
        last_name="Встанька", 
        first_name="Ванька", 
        faculty="СИД", 
        course="Теор. Механика", 
        estimation=52
        )

    print("\n\n******************** Пример добавление студента ***********************\n\n")

    await db_manager.insert_user(new_stundet)

    print("\n\n******************** Пример добавление списка студентов ***********************\n\n")
    users_list = [
        User(last_name="Петров", first_name="Пётр", faculty="ФПМИ", course="Мат. Анализ", estimation=48),
        User(last_name="Сидоров", first_name="Сидор", faculty="ФТФ", course="Физика", estimation=37)
    ]

    await db_manager.insert_users(users_list)
    
    e = db_manager.get_last_10_users()
    print(e)