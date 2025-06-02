import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from sqlalchemy import and_, or_

from db.database import engine
from db.models import User as ModelUser
from db.models import Node as ModelNode
from db.models import SubjectArea as ModelSubjectArea
from db.models import Model as ModelBpsimModel
from db.models import Relation as ModelRelation
from db.models import NodeDetail as ModelNodeDetail
from db.models import Resource as ModelResource
from db.models import ResourceType as ModelResourceType
from db.models import NodeRes as ModelNodeRes
from db.models import Measure as ModelMeasure
from db.models import Chart as ModelChart
from db.models import ModelControl as ModelBpsimModelControl

from db.schemas import User as SchemaUser
from db.schemas import Node as SchemaNode
from db.schemas import SubjectArea as SchemaSubjectArea
from db.schemas import Model as SchemaBpsimModel
from db.schemas import Relation as SchemaRelation
from db.schemas import NodeDetail as SchemaNodeDetail
from db.schemas import Resource as SchemaResource
from db.schemas import NodeRes as SchemaNodeRes
from db.schemas import Chart as SchemaChart
from db.schemas import ModelControl as SchemaModelControl
from db.database import Base

from fastapi_sqlalchemy import DBSessionMiddleware, db

from shared.enums.control_types import ControlType
from shared.validation import (check_existance, check_sub_area_name_unique, check_model_name_unique,
                               check_resource_name_unique, check_node_name_unique)

from simulation.sim import get_events_list, get_report
from simulation.types import SimulationNodedata

import os
from dotenv import load_dotenv

load_dotenv('.env')

app = FastAPI(
    title="API для работы с BPsim.MAS",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Simulation",
            "description": "Запуск симуляции"
        },
        {
            "name": "Subject Areas",
            "description": "Операции для работы с ПО"
        },
        {
            "name": "Models",
            "description": "Операции для работы с моделями"
        },
        {
            "name": "Model Controls",
            "description": "Операции для работы с компонентами управления моделью"
        },
        {
            "name": "Nodes",
            "description": "Операции для работы с узлами"
        },
        {
            "name": "Relations",
            "description": "Операции для работы со связями"
        },
        {
            "name": "Node Details",
            "description": "Операции для работы со свойствами узла"
        },
        {
            "name": "Node Resources",
            "description": "Операции для работы с ресурсами узла"
        },
        {
            "name": "Resources",
            "description": "Операции для работы с ресурсами"
        },
        {
            "name": "Measures",
            "description": "Операции для работы с единицами измерения"
        },
        {
            "name": "Charts",
            "description": "Операции для работы с диаграммами"
        },
        {
            "name": "Users",
            "description": "Операции для работы с пользователями"
        },
        {
            "name": "Connections",
            "description": "Проверка соединения"
        },
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

def delete_model_control_by_id(control_id: int):
    """Удаляет компоненты модели по id"""
    control = db.session.query(ModelBpsimModelControl).get(control_id)
    if control:
        db.session.delete(control)
        db.session.commit()

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

@app.get("/subjectArea/{id}/", tags=["Subject Areas"])
async def get_subject_area(id: int):
    """Возвращает ПО по id"""
    db_sub_area = db.session.query(ModelSubjectArea).get(id)
    check_existance(db_sub_area, "Предметная область не найдена")
    return db_sub_area

@app.post("/subjectArea/", tags=["Subject Areas"])
async def create_subject_area(area: SchemaSubjectArea):
    """Добавляет ПО"""
    check_sub_area_name_unique(area.name)

    db_sub_area = ModelSubjectArea(name=area.name, description=area.description)
    db.session.add(db_sub_area)
    db.session.commit()
    db.session.refresh(db_sub_area)
    return db_sub_area

@app.delete("/subjectArea/{id}/", tags=["Subject Areas"])
async def delete_subject_area(id: int):
    """Удаляет ПО по id"""
    db_sub_area = db.session.query(ModelSubjectArea).get(id)
    check_existance(db_sub_area, "Предметная область не найдена")
    name = db_sub_area.name

    db.session.delete(db_sub_area)
    db.session.commit()

    return {"status": "success", "message": f"Предметная область '{name}' успешно удалена"}

@app.get("/models/{sub_area_id}/", tags=["Models"])
async def get_models(sub_area_id: int):
    """Возвращает список моделей"""
    models = db.session.query(ModelBpsimModel).filter((ModelBpsimModel.sub_area_id == sub_area_id)).all()
    return models

@app.get("/model/{id}/", tags=["Models"])
async def get_model(id: int):
    """Возвращает модель по id"""
    db_model = db.session.query(ModelBpsimModel).get(id)
    check_existance(db_model, "Модель не найдена")
    return db_model

@app.post("/model/", tags=["Models"])
async def create_model(model: SchemaBpsimModel):
    """Добавляет модель"""
    check_model_name_unique(model.name, model.sub_area_id)

    model = ModelBpsimModel(name=model.name, description=model.description, sub_area_id = model.sub_area_id)
    db.session.add(model)
    db.session.commit()
    db.session.refresh(model)
    return model

@app.delete("/model/{id}/", tags=["Models"])
async def delete_model(id: int):
    """Удаляет модель по id"""
    db_model = db.session.query(ModelBpsimModel).get(id)
    check_existance(db_model,"Модель не найдена")
    name = db_model.name

    db.session.delete(db_model)
    db.session.commit()

    return {"status": "success", "message": f"Модель '{name}' успешно удалена"}

@app.get("/nodes/{model_id}/", tags=["Nodes"])
async def get_nodes(model_id: int):
    """Возвращает список узлов"""
    nodes = db.session.query(ModelNode).filter(ModelNode.model_id == model_id).all()
    return nodes

@app.get("/node/{id}/", tags=["Nodes"])
async def get_node(id: int):
    """Возвращает узел по id"""
    node = db.session.get(ModelNode, id)
    check_existance(node, "Узел не найден")
    return node

initialX = 50
initialY = 100
deltaX = 0
deltaY = 0
@app.post("/node/", tags=["Nodes"])
async def create_node(node: SchemaNode):
    """Добавляет узел"""
    global initialX, deltaX, initialY, deltaY
    initialY += deltaY
    initialX += deltaX
    model = db.session.query(ModelBpsimModel).get(node.model_id)
    check_existance(model, "Модели с таким id не существует!")

    name = "Новый узел" if not node.name else node.name
    db_node = ModelNode(name=name, description=node.description, model_id=node.model_id,
                        posX=node.posX + initialX, posY=node.posY + initialY)
    db.session.add(db_node)
    db.session.commit()
    db.session.refresh(db_node)

    db_node_details = ModelNodeDetail(node_id=db_node.id, cost=0.0, duration="0")
    db.session.add(db_node_details)
    db.session.commit()

    return db_node

@app.put("/node/{id}/", tags=["Nodes"])
async def update_node(id: int, node_update: SchemaNode):
    """Обновляет данные узла по id

    P.S.Чтобы поле осталось без изменений, надо передать в него null
    """
    db_node = db.session.query(ModelNode).get(id)
    check_existance(db_node, "Узел не найден")

    check_node_name_unique(node_update, id)

    # Обновляем только те поля, которые были переданы
    for key, value in node_update.dict(exclude_none=True).items():
        setattr(db_node, key, value)

    db.session.add(db_node)
    db.session.commit()
    new_node = db.session.query(ModelNode).get(id)

    return {"status": "success", "data": new_node}

@app.delete("/node/{id}/", tags=["Nodes"])
async def delete_node(id: int):
    """Удаляет узел по id"""
    db_node = db.session.query(ModelNode).get(id)
    check_existance(db_node, "Узел не найден")

    name = db_node.name
    relation = (db.session.query(ModelRelation)
                .filter(or_(ModelRelation.target_id == id, ModelRelation.source_id == id))
                .first())

    db.session.delete(db_node)
    db.session.commit()

    if relation:
        db.session.delete(relation)
        db.session.commit()

    return {"status": "success", "message": f"Узел '{name}' успешно удалён"}


@app.get("/relations/{model_id}/", tags=["Relations"])
async def get_relations(model_id: int):
    """Возвращает связи по id модели"""
    relations = db.session.query(ModelRelation).filter_by(model_id=model_id).all()
    return relations

@app.get("/relation/{id}/", tags=["Relations"])
async def get_relation(id: int):
    """Возвращает узел по id"""
    db_relation = db.session.query(ModelRelation).get(id)
    check_existance(db_relation, "Связь не найдена")
    return db_relation

@app.post("/relation/", tags=["Relations"])
async def create_relation(relation : SchemaRelation):
    """Добавляет связь"""
    db_relation = ModelRelation(source_id=relation.source_id, target_id=relation.target_id, model_id=relation.model_id)
    db.session.add(db_relation)
    db.session.commit()
    db.session.refresh(db_relation)
    return db_relation

@app.put("/relation/{id}/", tags=["Relations"])
async def update_relation(id: int, relation_update: SchemaRelation):
    """Обновляет данные связи по id"""
    db_relation = db.session.query(ModelRelation).get(id)
    check_existance(db_relation, "Связь не найдена")

    for key, value in relation_update.dict(exclude_none=True).items():
        setattr(db_relation, key, value)

    db.session.add(db_relation)
    db.session.commit()
    new_relation = db.session.query(ModelRelation).get(id)

    return {"status": "success", "data": new_relation}

@app.delete("/relation/{id}/", tags=["Relations"])
async def delete_relation(id: int):
    """Удаляет связь"""
    db_relation = db.session.query(ModelRelation).get(id)
    check_existance(db_relation, "Связь не найдена")
    db.session.delete(db_relation)
    db.session.commit()

    return {"status": "success", "message": "Связь успешно удалена"}

@app.get("/nodeDetails/{node_id}/", tags=["Node Details"])
async def get_node_details(node_id: int):
    """Возвращает свойства узла"""
    db_node_details = db.session.query(ModelNodeDetail).filter(ModelNodeDetail.node_id==node_id).first()
    check_existance(db_node_details , "Свойства узла не найдены")
    return db_node_details

@app.post("/nodeDetails/", tags=["Node Details"])
async def create_node_details(details: SchemaNodeDetail):
    """Добавляет свойства узла"""
    new_details = ModelNodeDetail(node_id=details.node_id, duration=details.duration, cost = details.cost)
    db.session.add(new_details)
    db.session.commit()
    db.session.refresh(new_details)
    return new_details

@app.put("/nodeDetails/{id}/", tags=["Node Details"])
async def update_node_details(id: int, details_update: SchemaNodeDetail):
    db_node_details = db.session.query(ModelNodeDetail).get(id)
    check_existance(db_node_details, "Свойства узла не найдены")

    for key, value in details_update.dict(exclude_none=True).items():
        setattr(db_node_details, key, value)

    db.session.add(db_node_details)
    db.session.commit()
    new_details = db.session.query(ModelNodeDetail).get(id)

    return {"status": "success", "data": new_details}

@app.get("/start/{sub_area_id}/{model_id}/", tags=["Simulation"])
async def start_simulation(sub_area_id: int, model_id: int):
    nodes = db.session.query(ModelNode).filter(ModelNode.model_id == model_id).all()
    relations = (db.session.query(ModelRelation).filter(ModelRelation.model_id == model_id).all())
    node_data = []
    for node in nodes:
        details = (db.session.query(ModelNodeDetail).filter(ModelNodeDetail.node_id == node.id).first())
        resources_in = db.session.query(ModelNodeRes).filter(and_(ModelNodeRes.node_id == node.id,
                                                                  ModelNodeRes.res_in_out == 0)).all()
        resources_out = db.session.query(ModelNodeRes).filter(and_(ModelNodeRes.node_id == node.id,
                                                                  ModelNodeRes.res_in_out == 1)).all()
        node_data.append(SimulationNodedata(
            id=node.id, name=node.name,
            duration=int(details.duration), cost = details.cost,
            resources_in=resources_in, resources_out=resources_out))

    sub_area_resources = db.session.query(ModelResource).filter(ModelResource.sub_area_id == sub_area_id).all()
    events = get_events_list(node_data, relations)
    (report, chart_table, export_table) = get_report(events, 500, sub_area_resources)
    return {"report": report, "chart_table": chart_table, "export_table": export_table}

@app.get("/resources/{sub_area_id}/", tags=["Resources"])
async def get_resources(sub_area_id: int):
    """Выгружает список ресурсов в выбранной ПО"""
    resources = db.session.query(ModelResource).filter(ModelResource.sub_area_id == sub_area_id).all()
    return resources

@app.post("/resource/", tags=["Resources"])
async def create_resource(resource: SchemaResource):
    """Создает ресурс"""
    check_resource_name_unique(resource)

    sys_names = db.session.query(ModelResource).filter(ModelResource.sub_area_id==resource.sub_area_id).all()
    prefix = db.session.query(ModelResourceType).get(resource.type_id).prefix
    sys_name = f"{prefix}Res{len(sys_names)+1}"
    new_resource = ModelResource(sub_area_id=resource.sub_area_id, name=resource.name,
                                 type_id=resource.type_id, measure_id=resource.measure_id,
                                 min_value=resource.min_value, max_value=resource.max_value,
                                 current_value=resource.current_value, sys_name=sys_name)
    db.session.add(new_resource)
    db.session.commit()
    db.session.refresh(new_resource)
    return new_resource

@app.delete("/resource/{id}", tags=["Resources"])
async def delete_resource(id: int):
    res = db.session.query(ModelResource).get(id)
    check_existance(res, "Такой ресурс не найден")
    db.session.delete(res)
    db.session.commit()
    return {"status": "success", "message": "Ресурс успешно удален"}

@app.get("/measures/", tags=["Measures"])
async def get_measures():
    """Возвращает список единиц измерения"""
    measures = db.session.query(ModelMeasure).all()
    return measures

@app.get("/resourceTypes/", tags=["Resources"])
async def get_resource_types():
    """Возвращает список типов ресурсов"""
    resource_types = db.session.query(ModelResourceType).all()
    return resource_types

@app.post("/nodeRes/", tags=["Node Resources"])
async def create_node_resource(res: SchemaNodeRes):
    new_node_res = ModelNodeRes(value=res.value, node_id=res.node_id,
                                res_in_out=res.res_in_out,
                                res_id=res.res_id, model_id=res.model_id)
    db.session.add(new_node_res)
    db.session.commit()
    db.session.refresh(new_node_res)
    return new_node_res

@app.get("/nodeResources/{node_id}/", tags=["Node Resources"])
async def get_node_resources(node_id: int):
    resources = db.session.query(ModelNodeRes).filter(ModelNodeRes.node_id==node_id).all()
    return resources

@app.get('/modelControls/{model_id}', tags=["Model Controls"])
async def get_model_controls(model_id: int):
    controls = db.session.query(ModelBpsimModelControl).filter(ModelBpsimModelControl.model_id == model_id).all()
    return controls

@app.get('/chart/{chart_id}/', tags=["Charts"])
async def get_chart(id: int):
    chart = db.session.query(ModelChart).get(id)
    check_existance(chart, 'Диаграмма с таким id не найдена')
    return chart

@app.get('/charts/{model_id}', tags=["Charts"])
async def get_charts(model_id: int):
    charts = db.session.query(ModelChart).filter(ModelChart.model_id == model_id).all()
    return charts

@app.post('/chart/', tags=["Charts"])
async def create_chart(chart: SchemaChart):
    new_control = ModelBpsimModelControl(model_id=chart.model_id, type = ControlType.CHART,
                                         control_name = chart.name, pos_x = chart.pos_x, pos_y = chart.pos_y,
                                         width = chart.width, height = chart.height)
    db.session.add(new_control)
    db.session.commit()
    db.session.refresh(new_control)
    new_chart = ModelChart(name=chart.name, model_id=chart.model_id, object_id = chart.object_id,
                           x_legend = chart.x_legend, y_legend = chart.y_legend, control_id = new_control.id)
    db.session.add(new_chart)
    db.session.commit()
    db.session.refresh(new_chart)
    return new_chart

@app.delete("/chart/{chart_id}/", tags=["Charts"])
async def delete_chart(id: int):
    chart = db.session.query(ModelChart).get(id)
    check_existance(chart, 'Диаграмма с таким id не найдена')
    name = chart.name
    delete_model_control_by_id(chart.control_id)
    return {"status": "success", "message": f"Диаграмма '{name}' успешно удалена"}

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