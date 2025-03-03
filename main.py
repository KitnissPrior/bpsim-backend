import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db.database import engine
from db.models import User as ModelUser
from db.models import Node as ModelNode
from db.models import SubjectArea as ModelSubjectArea
from db.models import Model as ModelBpsimModel

from db.schemas import User as SchemaUser
from db.schemas import Node as SchemaNode
from db.schemas import SubjectArea as SchemaSubjectArea
from db.schemas import Model as SchemaBpsimModel
from db.database import Base
from fastapi_sqlalchemy import DBSessionMiddleware, db

import os
from dotenv import load_dotenv

load_dotenv('.env')

app = FastAPI(
    title="API для работы с BPsim.MAS",
    version="1.0.0",
    openapi_tags=[

        {
            "name": "Subject Areas",
            "description": "Операции для работы с ПО"
        },
        {
            "name": "Models",
            "description": "Операции для работы с моделями"
        },
        {
            "name": "Nodes",
            "description": "Операции для работы с узлами"
        },
        {
            "name": "Users",
            "description": "Операции для работы с пользователями"
        },
        {
            "name": "Connections",
            "description": "Проверка соединения"
        }
    ]
)

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

@app.get("/users/", tags=["Users"])
async def get_users():
    """Возвращает список пользователей"""
    users = db.session.query(ModelUser).all()
    return users

@app.post("/user/", response_model=SchemaUser, tags=["Users"])
def create_user(user: SchemaUser):
    """
    Добавляет пользователя
    """
    db_user = ModelUser(username=user.username, email=user.email)
    db.session.add(db_user)
    db.session.commit()
    return db_user

@app.get("/subjectAreas/", tags=["Subject Areas"])
async def get_subject_areas():
    """Возвращает список ПО"""
    subject_areas = db.session.query(ModelSubjectArea).all()
    return subject_areas

@app.post("/subjectArea/", tags=["Subject Areas"])
async def create_subject_area(area: SchemaSubjectArea):
    """Добавляет ПО"""
    db_sub_area = ModelSubjectArea(name=area.name, description=area.description)
    db.session.add(db_sub_area)
    db.session.commit()
    db.session.refresh(db_sub_area)
    return db_sub_area

@app.get("/models/", tags=["Models"])
async def get_models():
    """Возвращает список моделей"""
    models = db.session.query(ModelBpsimModel).all()
    return models

@app.post("/model/", tags=["Models"])
async def create_model(model: SchemaBpsimModel):
    """Добавляет модель"""
    model = ModelBpsimModel(name=model.name, description=model.description, sub_area_id = model.sub_area_id)
    db.session.add(model)
    db.session.commit()
    db.session.refresh(model)
    return model

@app.delete("/model/{id}", tags=["Models"])
async def delete_model(id: int):
    """Удаляет модель по id"""
    db_model = db.session.query(ModelBpsimModel).get(id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    db.session.delete(db_model)
    db.session.commit()

    return {"status": "success", "message": "Модель успешно удалена"}

@app.get("/nodes/", tags=["Nodes"])
async def get_nodes():
    """Возвращает список узлов"""
    nodes = db.session.query(ModelNode).all()
    return nodes

@app.get("/node/{id}", tags=["Nodes"])
async def get_node(id: int):
    """Возвращает узел по id"""
    node = db.session.get(ModelNode, id)
    return node

initialX = 50
initialY = 200
deltaX = 40
deltaY = 20
@app.post("/node/", tags=["Nodes"])
async def create_node(node: SchemaNode):
    """Добавляет узел"""
    global initialX, deltaX, initialY, deltaY
    initialY += deltaY
    initialX += deltaX
    db_node = ModelNode(name=f"Новый узел", description=node.description,
                        posX=node.posX + initialX, posY=node.posY + initialY)
    db.session.add(db_node)
    db.session.commit()
    db.session.refresh(db_node)
    return db_node

@app.put("/node/{id}", tags=["Nodes"])
async def update_node(id: int, node_update: SchemaNode):
    """Обновляет данные узла по id

    P.S.Чтобы поле осталось без изменений, надо передать в него null
    """
    db_node = db.session.query(ModelNode).get(id)

    if not db_node:
        raise HTTPException(status_code=404, detail="Узел не найден")

    # Обновляем только те поля, которые были переданы
    for key, value in node_update.dict(exclude_none=True).items():
        setattr(db_node, key, value)

    db.session.add(db_node)
    db.session.commit()
    new_node = db.session.query(ModelNode).get(id)

    return {"status": "success", "data": new_node}

@app.delete("/node/{id}", tags=["Nodes"])
async def delete_node(id: int):
    """Удаляет узел по id"""
    db_node = db.session.query(ModelNode).get(id)

    if not db_node:
        raise HTTPException(status_code=404, detail="Узел не найден")

    db.session.delete(db_node)
    db.session.commit()

    return {"status": "success", "message": "Узел успешно удалён"}

@app.get("/", tags=["Connections"])
async def ping():
    """Home endpoint"""
    return {"data": "Это бэкенд BPsim Web!"}

# To run locally
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)