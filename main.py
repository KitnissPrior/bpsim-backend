import uvicorn
from fastapi import FastAPI, Depends
from pydantic import BaseModel, ConfigDict
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_db
from models import User as ModelUser
from models import Node as ModelNode
from schemas import User as SchemaUser
from schemas import Node as SchemaNode
from sqlalchemy import select
from database import Base
from fastapi_sqlalchemy import DBSessionMiddleware, db

import os
from dotenv import load_dotenv

load_dotenv('.env')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    DBSessionMiddleware,
    allow_origins=["*"],  # Либо конкретные URL-адреса
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    db_url=os.environ['DATABASE_URL']
)

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

@app.get("/users/")
async def get_users():
    users = db.session.query(ModelUser).all()
    return users

@app.post("/user/", response_model=SchemaUser)
def create_user(user: SchemaUser):
    db_user = ModelUser(name=user.name, email=user.email)
    db.session.add(db_user)
    db.session.commit()
    return db_user

# class NodeCreation(BaseModel):
#     name: str
#     description: str | None = None
#
# class Node(NodeCreation):
#     id: int
#     model_config = ConfigDict(from_attributes=True)

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

# To run locally
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)