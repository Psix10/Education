import csv
from uuid import UUID, uuid4
from sqlalchemy import String, Select, Float
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import NoReturn, List

Base = declarative_base()

class User(Base):
    __tablename__ = "Students"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    faculty: Mapped[str] = mapped_column(String(100))
    course: Mapped[str] = mapped_column(String(100))
    estimation: Mapped[float] = mapped_column(Float)

    def __repr__(self):
        return (f"User(id={self.id!r}, last_name={self.last_name!r}, "
                f"first_name={self.first_name!r}, faculty={self.faculty!r}, "
                f"course={self.course!r}, estimation={self.estimation!r})")

engine = create_engine("postgresql+psycopg2://user:password@localhost:5432/postgres", echo=True)
Base.metadata.create_all(engine)

class DatabaseManager:
    def __init__(self,  engine: object) -> NoReturn:
        self.engine: object = engine

    def insert_users(self, users: List[User]) -> NoReturn:
        with Session(self.engine) as session:
            session.add_all(users)
            session.commit()

    def insert_user(self, user: User) -> NoReturn:
        with Session(self.engine) as session:
            session.add(user)
            session.commit()

    def insert_from_file(self, name_file: str = "students.csv") -> NoReturn:
        with open(name_file, encoding="UTF-8") as f:
            reader = csv.DictReader(f)
            with Session(self.engine) as session:
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
                session.commit()

    def get__users_by_faculty(self, faculty: str) -> List[User]:
        with Session(self.engine) as session:
            stmt = Select(User).where(User.faculty == faculty)
            return session.scalars(stmt).all()

    def get__users_by_course(self, course: str) -> List[User]:
        with Session(self.engine) as session:
            stmt = Select(User).where(User.course == course)
            return session.scalars(stmt).all()
    
    def get__users_by_id(self, uuid: UUID) -> List[User]:
        with Session(self.engine) as session:
            stmt = Select(User).where(User.id == uuid)
            return session.scalars(stmt).all()
    
    def get_average_score(self, faculty: str) -> float:
        with Session(self.engine) as session:
            stmt = Select(User.estimation).where(User.faculty == faculty)
            
            return (sum(session.scalars(stmt).all())) / len(session.scalars(stmt).all())
    
    def get_min_esmition(self, course: str, threshold: float = 30) -> float:
        with Session(self.engine) as session:
            stmt = Select(User).where((User.course == course) & (User.estimation < threshold))
            result = session.scalars(stmt).all()
            return result

db_manager = DatabaseManager(engine)   

# РАСКОМЕНТИРОВАТЬ ДЛЯ СОЗДАНИЕ БД ИЗ ФАЙЛА
#db_manager.insert_from_file("students.csv")
print("\n\n******************** Пример получения списка студентов по выбранному курсу с оценкой ниже 30 баллов  ***********************\n\n")
a = db_manager.get_min_esmition("История")
print(a)

print("\n\n******************** Пример получения среднего балла по факультету  ***********************\n\n")

b = db_manager.get_average_score("РЭФ")
print(f"Средний балл: {b}")

print("\n\n******************** Пример получения списка уникальных курсов  ***********************\n\n")

print(db_manager.get__users_by_course("Физика"))

print("\n\n******************** Пример получения списка студентов по названию факультета ***********************\n\n")

print(db_manager.get__users_by_faculty("РЭФ"))

new_stundet = User(last_name="Встанька", first_name="Ванька", faculty="СИД", course="Теор. Механика", estimation=52)

db_manager.insert_user(new_stundet)

users_list = [
    User(last_name="Петров", first_name="Пётр", faculty="ФПМИ", course="Мат. Анализ", estimation=48),
    User(last_name="Сидоров", first_name="Сидор", faculty="ФТФ", course="Физика", estimation=37)
]

db_manager.insert_users(users_list)