from db.models import ModelControl as ModelBpsimModelControl
from fastapi_sqlalchemy import db

def delete_model_control_by_id(control_id: int):
    """Удаляет компоненты модели по id"""
    control = db.session.query(ModelBpsimModelControl).get(control_id)
    if control:
        db.session.delete(control)
        db.session.commit()


