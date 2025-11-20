import csv
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import (
    IntegrityError, 
    DataError, 
    OperationalError, 
    ProgrammingError, 
    InvalidRequestError
)
from sqlalchemy import select
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Session
from typing import NoReturn, List
from models import *
from base import *

async def get_db() -> AsyncGenerator[AsyncSession | None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise ValueError("Запись нарушает уникальность или целостность") from e

        except DataError as e:
            await session.rollback()
            raise ValueError("Неверные данные для полей модели") from e

        except OperationalError as e:
            raise ConnectionError("Ошибка подключения к базе данных") from e

        except InvalidRequestError as e:
            await session.rollback()
            raise RuntimeError("Ошибка SQLAlchemy: неправильное использование сессии") from e

        except Exception as e:
            await session.rollback()
            raise RuntimeError(f"Неизвестная ошибка базы данных: {e}") from e
        finally:
            await session.close()

class DataBaseManager:

    async def insert_users(self, users: List[User]) -> NoReturn:
        async with async_session_maker() as session:
            async with session.begin():
                session.add_all(users)
                await session.flush()

    async def insert_user(self, user: User) -> NoReturn:
        async with async_session_maker() as session:
            async with session.begin():
                session.add(user)
                await session.flush()

    async def insert_from_file(self, name_file: str = "students.csv") -> NoReturn:
        async with async_session_maker() as session:
            async with session.begin():
                with open(name_file, encoding="UTF-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            estimation = float(row["Оценка"])
                        except ValueError:
                            estimation = 0.0
                            
                            # # Проверяем, есть ли студент в базе ()
                            # exists = session.query(User).filter_by(
                            #     last_name=row["Фамилия"],
                            #     first_name=row["Имя"],
                            #     faculty=row["Факультет"],
                            #     course=row["Курс"]
                            # ).first()
                            
                            
                        user = User(
                                last_name=row["Фамилия"],
                                first_name=row["Имя"],
                                faculty=row["Факультет"],
                                course=row["Курс"],
                                estimation=estimation
                            )
                        session.add(user)
                        

    async def get__users_by_faculty(self, faculty: str) -> List[User]:
        async with async_session_maker() as session:
            stmt = await session.execute(select(User).where(User.faculty == faculty))
            return stmt.scalars().all()

    async def get_users_by_course(self, course: str) -> List[User]:
        async with async_session_maker() as session:
            stmt = await session.execute(select(User).where(User.course == course))
            return stmt.scalars().all()

    async def get__users_by_id(self, uuid: UUID) -> List[User]:
        async with async_session_maker() as session:
            stmt = await session.execute(select(User).where(User.id == uuid))
            return stmt.scalars().all()

    async def get_average_score(self, faculty: str) -> float:
        async with async_session_maker() as session:
            stmt = await session.execute(select(User.estimation).where(User.faculty == faculty))
            scores = stmt.scalars().all()
            return sum(scores) / len(scores) if scores else 0.0

    async def get_min_esmition(self, course: str, threshold: float = 30) -> float:
        async with async_session_maker() as session:
            stmt = await session.execute(select(User).where((User.course == course) & (User.estimation < threshold)))
            return stmt.scalars().all()

    async def get_last_10_users(limit: int = 10) -> List[User]:
        async with async_session_maker() as session:
            result = await session.execute(select(User).order_by(desc(User.id)).limit(limit))
            return result.scalars().all()

def get_manager():
    return DataBaseManager()