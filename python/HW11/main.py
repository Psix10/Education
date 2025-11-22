import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from base import init_db
from models import User
from service import *
from api_user import router as user_router
from api_db import router as db_router
from auth.auth_api import router as auth_router

app = FastAPI()


app.include_router(user_router, prefix="/users")
app.include_router(db_router, prefix="/users")
app.include_router(auth_router, prefix="/auth")