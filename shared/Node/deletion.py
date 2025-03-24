from fastapi_sqlalchemy import db
from sqlalchemy import or_

from db.models import Node as ModelNode
from db.models import NodeDetail as ModelNodeDetail
from db.models import Relation as ModelRelation

def delete_node_by_id(id: int):
    """Удаляет узел по id"""
    db_node = db.session.query(ModelNode).get(id)
    if db_node:
        delete_node_details(id)
        delete_node_relation(id)

        db.session.delete(db_node)
        db.session.commit()

def delete_node_details(node_id: int):
    """Удаляет свойства узла"""
    db_node_details = db.session.query(ModelNodeDetail).filter_by(node_id=node_id).first()
    if db_node_details:
        db.session.delete(db_node_details)

def delete_node_relation(node_id: int):
    """Удаляет связь узла"""
    db_relation = db.session.query(ModelRelation).filter(
        or_(ModelRelation.target_id == node_id, ModelRelation.source_id == node_id)).first()
    if db_relation:
        db.session.delete(db_relation)
