import re
from typing import Optional
from pydantic import BaseModel, field_validator, EmailStr, ConfigDict

class UserBase(BaseModel):
    email: EmailStr

class UserResponse(UserBase):
    status: bool
    full_name: str | None = None
    username: str | None  = None

    model_config = ConfigDict(
        from_attributes=True
    )


class UserRegistrate(UserBase):
    username: str
    full_name: str
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, psw: str) -> str:
        errors = []
        
        if len(psw) < 8:
            errors.append('не менее 8 символов')
        
        if re.search(r'[^A-Za-z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', psw):
            errors.append('только латинские буквы, цифры и специальные символы')
        
        if not re.search(r'[A-Z]', psw):
            errors.append('хотя бы одну заглавную латинскую букву')
        
        if not re.search(r'[a-z]', psw):
            errors.append('хотя бы одну строчную латинскую букву')
        
        if not re.search(r'\d', psw):
            errors.append('хотя бы одну цифру')
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', psw):
            errors.append('хотя бы один специальный символ')
        
        if errors:
            raise ValueError(f'Пароль должен содержать: {", ".join(errors)}')
        
        return psw


class UserInDB(UserResponse):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str

class TokenData(BaseModel):
    email: str = None

class Login(BaseModel):
    email: str
    password: str

class IDList(BaseModel):
    user_ids: list[int]
    
    model_config = ConfigDict(
        from_attributes=True
    )