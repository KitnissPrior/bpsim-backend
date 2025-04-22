from sqlalchemy import Column, Float, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)

class SubjectArea(Base):
    __tablename__ = "subject_areas"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    description = Column(String, nullable=True)
    # relations
    #models = relationship("Model", cascade="all, delete-orphan")
    #resources = relationship("Resource", cascade="all, delete-orphan")

class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    description = Column(String)
    sub_area_id = Column(Integer, ForeignKey('subject_areas.id'))
    #relations
    #nodes = relationship("Node", cascade="all, delete-orphan")
    #relations = relationship("Relation", cascade="all, delete-orphan")
    #node_resources = relationship("NodeRes", cascade="all, delete-orphan")

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    description = Column(String)
    posX = Column(Float)
    posY = Column(Float)
    # FK
    model_id = Column(Integer, ForeignKey('models.id'), nullable=True)
    control_id = Column(Integer, ForeignKey('model_controls.id'), nullable=True)
    # relations
    # для связей, где текущий узел является источником
    outgoing_relations = relationship(
        "Relation",
        foreign_keys="[Relation.source_id]",
    )

    # для связей, где текущий узел является целевым
    incoming_relations = relationship(
        "Relation",
        foreign_keys="[Relation.target_id]",
    )

class Relation(Base):
    __tablename__ = "relations"

    id = Column(Integer, primary_key=True, unique=True)
    source_id = Column(Integer, ForeignKey('nodes.id'))
    target_id = Column(Integer, ForeignKey('nodes.id'))
    model_id = Column(Integer, ForeignKey('models.id'))

    source_node = relationship(
        "Node",
        foreign_keys="[Relation.source_id]",
        back_populates="outgoing_relations"
    )
    target_node = relationship(
        "Node",
        foreign_keys="[Relation.target_id]",
        back_populates="incoming_relations"
    )

class NodeDetail(Base):
    __tablename__ = "node_details"

    id = Column(Integer, primary_key=True, unique=True)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    duration = Column(String, nullable=True)
    cost = Column(Float, nullable=True)

class NodeRes(Base):
    __tablename__ = "node_resources"

    id = Column(Integer, primary_key=True, unique=True)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    res_id = Column(Integer, ForeignKey('resources.id'))
    model_id = Column(Integer, ForeignKey('models.id'))
    res_in_out = Column(Integer) # 0 - входное условие, 1 - выходное
    value = Column(String)

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, unique=True)
    sub_area_id = Column(Integer, ForeignKey('subject_areas.id'))
    type_id = Column(Integer, ForeignKey('resource_types.id'))
    name = Column(String)
    sys_name = Column(String)
    current_value = Column(Float, nullable=True)
    max_value = Column(Float)
    min_value = Column(Float)
    measure_id = Column(Integer, ForeignKey('measures.id'), nullable=True)

class ResourceType(Base):
    __tablename__ = "resource_types"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    prefix = Column(String)
    # relations
    resource = relationship("Resource", cascade="all, delete-orphan")

class Measure(Base):
    __tablename__ = "measures"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, nullable=True)
    #relations
    #resource = relationship("Resource", cascade="all, delete-orphan")

class Chart(Base):
    __tablename__ = "charts"

    id = Column(Integer, primary_key=True, unique=True)
    model_id = Column(Integer, ForeignKey('models.id'))
    control_id = Column(Integer, ForeignKey('model_controls.id'))
    name = Column(String)
    object_id = Column(Integer, ForeignKey('resources.id'))
    x_legend = Column(String)
    y_legend = Column(String)

class ModelControl(Base):
    __tablename__ = "model_controls"

    id = Column(Integer, primary_key=True, unique=True)
    model_id = Column(Integer, ForeignKey('models.id'))
    type = Column(Integer)
    control_name = Column(String)
    pos_x = Column(Float)
    pos_y = Column(Float)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
