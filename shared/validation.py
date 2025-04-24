from fastapi import HTTPException
from db.database import Base
from db.models import SubjectArea as SubjectArea
from db.models import Model
from db.models import Node
from db.models import Resource as ModelRes
from db.schemas import Resource as SchemaRes
from db.schemas import Node as SchemaNode

from fastapi_sqlalchemy import db
from sqlalchemy import and_

def check_existance(item: Base, details: str):
    if not item:
        raise HTTPException(status_code=404, detail=details)

def check_sub_area_name_unique(name: str):
    another_item = db.session.query(SubjectArea).filter(SubjectArea.name == name).first()
    if another_item:
        raise HTTPException(status_code=409, detail='Предметная область с таким именем уже есть')

def check_model_name_unique(name: str, sub_area_id: int):
    another_item = db.session.query(Model).filter(and_(Model.sub_area_id == sub_area_id, Model.name == name)).first()
    if another_item:
        raise HTTPException(status_code=409, detail='Модель с таким именем уже есть')

def check_resource_name_unique(res: SchemaRes):
    another_item = db.session.query(ModelRes).filter(
        and_(ModelRes.sub_area_id == res.sub_area_id,
             ModelRes.name == res.name)).first()
    if another_item:
        raise HTTPException(status_code=409, detail='Ресурс с таким именем уже есть')

def check_node_name_unique(node: SchemaNode, id: int):
    another_items = db.session.query(Node).filter(
        and_(Node.model_id == node.model_id, Node.name == node.name,
             Node.id != id)).first()
    if another_items:
        raise HTTPException(status_code=409, detail='Узел с таким именем уже есть')