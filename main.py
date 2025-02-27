from fastapi import FastAPI, Depends
from pydantic import BaseModel, ConfigDict
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_db
from models import Base
from schemas import User
from sqlalchemy import select
from typing import List

import os
from dotenv import load_dotenv

load_dotenv('.env')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Либо конкретные URL-адреса
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    db_url=os.environ['DATABASE_URL']
)

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

@app.get("/users/", response_model=List[User])
async def read_users(db: SessionLocal = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

@app.post("/user/")
def create_user(user: User, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user

class NodeCreation(BaseModel):
    name: str
    description: str | None = None

class Node(NodeCreation):
    id: int
    model_config = ConfigDict(from_attributes=True)

@app.post("/node/")
async def add_node(node: NodeCreation):
    """
    Добавить узел в модель
    """
    return node

@app.get("/")
async def home():
    """ Home endpoint """
    return {"data": "Это бэкенд BPsim Web!"}
