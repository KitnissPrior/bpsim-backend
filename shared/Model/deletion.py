from db.models import Model as ModelBpsimModel
from db.models import Node as ModelNode

from shared.Node.deletion import delete_node_by_id
from fastapi_sqlalchemy import db

def delete_model_by_id(model_id: int):
    """Удаляет модель по id"""
    db_model = db.session.query(ModelBpsimModel).get(model_id)
    if db_model:
        delete_model_nodes(model_id)
        db.session.delete(db_model)
        db.session.commit()

def delete_model_nodes(model_id):
    """Удаляет все узлы в модели"""
    model_nodes = db.session.query(ModelNode).filter(ModelNode.model_id == model_id).all()
    for node in model_nodes:
        delete_node_by_id(node.id)
