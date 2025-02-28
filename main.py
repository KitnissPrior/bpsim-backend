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
    allow_origins=["*"],  # Либо конкретные URL-адреса
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

@app.get("/users/")
async def get_users():
    """Возвращает список пользователей"""
    users = db.session.query(ModelUser).all()
    return users

@app.post("/user/", response_model=SchemaUser)
def create_user(user: SchemaUser):
    """
    Добавляет пользователя
    """
    db_user = ModelUser(username=user.username, email=user.email)
    db.session.add(db_user)
    db.session.commit()
    return db_user

@app.get("/nodes/")
async def get_nodes():
    """Возвращает список узлов"""
    nodes = db.session.query(ModelNode).all()
    return nodes

@app.post("/node/", response_model=SchemaNode)
async def add_node(node: SchemaNode):
    """
    Добавляет узел в модель
    """
    db_node = ModelNode(name=node.name, description=node.description, posX = node.posX, posY = node.posY)
    db.session.add(db_node)
    db.session.commit()
    return db_node

@app.get("/")
async def home():
    """ Home endpoint """
    return {"data": "Это бэкенд BPsim Web!"}

# To run locally
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)