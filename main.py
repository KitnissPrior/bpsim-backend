import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

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

@app.get("/subjectArea/{id}", tags=["Subject Areas"])
async def get_subject_area(id: int):
    """Возвращает ПО по id"""
    db_sub_area = db.session.query(ModelSubjectArea).get(id)
    if not db_sub_area:
        raise HTTPException(status_code=404, detail="Предметная область не найдена")
    return db_sub_area

@app.post("/subjectArea/", tags=["Subject Areas"])
async def create_subject_area(area: SchemaSubjectArea):
    """Добавляет ПО"""
    db_sub_area = ModelSubjectArea(name=area.name, description=area.description)
    db.session.add(db_sub_area)
    db.session.commit()
    db.session.refresh(db_sub_area)
    return db_sub_area

@app.delete("/subjectArea/{id}", tags=["Subject Areas"])
async def delete_subject_area(id: int):
    """Удаляет ПО по id"""
    db_sub_area = db.session.query(ModelSubjectArea).get(id)
    if not db_sub_area:
        raise HTTPException(status_code=404, detail="Предметная область не найдена")

    name = db_sub_area.name
    db.session.delete(db_sub_area)
    db.session.commit()

    return {"status": "success", "message": f"Предметная область '{name}' успешно удалена"}

@app.get("/models/{sub_area_id}", tags=["Models"])
async def get_models(sub_area_id: int):
    """Возвращает список моделей
    """
    models = db.session.query(ModelBpsimModel).filter((ModelBpsimModel.sub_area_id == sub_area_id)).all()
    return models

@app.get("/model/{id}", tags=["Models"])
async def get_model(id: int):
    """Возвращает модель по id"""
    db_model = db.session.query(ModelBpsimModel).get(id)
    if not db_model:
        raise HTTPException(status_code=404, detail="Модель не найдена")
    return db_model

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
    name = db_model.name
    db.session.delete(db_model)
    db.session.commit()

    return {"status": "success", "message": f"Модель '{name}' успешно удалена"}

@app.get("/nodes/{model_id}", tags=["Nodes"])
async def get_nodes(model_id: int):
    """Возвращает список узлов"""
    nodes = db.session.query(ModelNode).filter(ModelNode.model_id == model_id).all()
    return nodes

@app.get("/node/{id}", tags=["Nodes"])
async def get_node(id: int):
    """Возвращает узел по id"""
    node = db.session.get(ModelNode, id)
    if not node:
        raise HTTPException(status_code=404, detail="Узел не найден")
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
    model = db.session.query(ModelBpsimModel).get(node.model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Модели с таким id не существует!")
    name = "Новый узел" if not node.name else node.name
    db_node = ModelNode(name=name, description=node.description, model_id=node.model_id,
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
    name = db_node.name
    db.session.delete(db_node)
    db.session.commit()

    return {"status": "success", "message": f"Узел '{name}' успешно удалён"}

@app.get("/", tags=["Connections"])
async def ping():
    """Home endpoint"""
    return {"data": "Это бэкенд BPsim Web!"}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc: RequestValidationError):
    error_details = []
    for error in exc.errors():
        error_details.append({
            "поле": ".".join(map(str, error["loc"][1:])),
            "ошибка": error["msg"],
            "тип": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": "Ошибка валидации данных",
            "details": error_details,
            "полученные_данные": exc.body
        }
    )

# To run locally
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)