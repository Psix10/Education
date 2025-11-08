from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, validator
from datetime import date, datetime
from typing import Any, Literal, List
from pathlib import Path
import re

app = FastAPI(title="Сбор обращения")

data_dir = Path("tickets")
data_dir.mkdir(exist_ok=True)
ticket_counter = 0
reasons = ["нет доступа к сети", "не работает телефон", "не приходят письма"]

class Ticket(BaseModel):
    last_name: str
    first_name: str
    date_born: date
    date_create: datetime
    phone: str
    email: EmailStr
    id: int = 0
    reason: List[Literal["нет доступа к сети", "не работает телефон", "не приходят письма"]]
    
    @validator("last_name", "first_name")
    def name_valid(cls:"Ticket", value: str) -> str:
        if not re.fullmatch(r"^[А-Я][а-яёЁ]+", value):
            raise ValueError("Должно быть слово на кириллице с заглавной буквы")
        return value
    
    @validator("phone")
    def phone_valid(cls: "Ticket", value: str) -> str:
        if not re.fullmatch(r"\+7\d{10}", value):
            raise ValueError("Телефон должен быть в формате +7XXXXXXXXXX")
        
        return value


@app.post("/submit")
async def submit_ticket(data: Ticket) -> dict[str, Any]:
    global ticket_counter
    ticket_counter += 1
    data.id = ticket_counter
    data.date_create = datetime.now()
    
    file_path = data_dir / f"{data.phone}id{data.id}.json"
    
    json_str = data.model_dump_json(indent=4, ensure_ascii=False)
    
    with file_path.open("w", encoding="UTF-8") as f:
        f.write(json_str)
    
    return {"status" : "success", "id": data.id, "saved_to" : str(file_path)}