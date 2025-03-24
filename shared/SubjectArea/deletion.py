from fastapi_sqlalchemy import db
from db.models import Model as ModelBpsimModel
from shared.Model.deletion import delete_model_by_id
def delete_subject_area_models(sub_area_id: int):
    """Удаляет все модели предметной области"""
    models = db.session.query(ModelBpsimModel).filter(ModelBpsimModel.sub_area_id == sub_area_id)
    for model in models:
        delete_model_by_id(model.id)