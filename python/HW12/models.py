
from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from pydantic import BaseModel
from typing import Optional

Base = declarative_base()

class User(Base):
    __tablename__ = "Students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    faculty: Mapped[str] = mapped_column(String(100))
    course: Mapped[str] = mapped_column(String(100))
    estimation: Mapped[float] = mapped_column(Float)

    def __repr__(self):
        return (f"User(id={self.id!r}, last_name={self.last_name!r}, "
                f"first_name={self.first_name!r}, faculty={self.faculty!r}, "
                f"course={self.course!r}, estimation={self.estimation!r})")

class UserCreate(BaseModel):
    last_name: str
    first_name: str
    faculty: str
    course: str
    estimation: float
    
class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    faculty: str
    course: str
    estimation: float

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    last_name: Optional[str]
    first_name: Optional[str]
    faculty: Optional[str]
    course: Optional[str]
    estimation: Optional[float]
    
    class Config:
        orm_mode = True