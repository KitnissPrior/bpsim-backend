from pydantic import BaseModel
from typing import Optional, Any

class User(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True

class SubjectArea(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True

class Model(BaseModel):
    name: str
    description: Optional[str] = None
    sub_area_id: int

    class Config:
        orm_mode = True

class Node(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    posX: Optional[float] = None
    posY: Optional[float] = None
    model_id: int

    class Config:
        orm_mode = True

class Relation(BaseModel):
    source_id: int
    target_id: int
    model_id: int

    class Config:
        orm_mode = True

class NodeDetail(BaseModel):
    node_id: int
    duration: Optional[str] = None
    cost: Optional[float] = None

    class Config:
        orm_mode = True

class NodeRes(BaseModel):
    node_id: int
    value: str
    res_in_out: float
    res_id: int
    model_id: int

    class Config:
        orm_mode = True

class ResourceType(BaseModel):
    name: str
    prefix: str

    class Config:
        orm_mode = True

class Resource(BaseModel):
    name: str
    type_id: int
    sub_area_id: int
    current_value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    measure_id: Optional[int] = None

    class Config:
        orm_mode = True

class Measure(BaseModel):
    name: str

    class Config:
        orm_mode = True

class Chart(BaseModel):
    name: str
    model_id: int
    object_id: int
    x_legend: Optional[str] = None
    y_legend: str
    pos_x: float
    pos_y: float
    width: Optional[float] = None
    height: Optional[float] = None

    class Config:
        orm_mode = True

class ModelControl(BaseModel):
    model_id: int
    type_id: int
    control_name: str
    pos_x: float
    pos_y: float
    width: Optional[float] = None
    height: Optional[float] = None

    class Config:
        orm_mode = True