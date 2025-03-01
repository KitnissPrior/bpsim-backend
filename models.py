from sqlalchemy import Column, Float, String, Integer, ForeignKey
from database import Base
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    description = Column(String)
    posX = Column(Float)
    posY = Column(Float)

class Relation(Base):
    __tablename__ = "relation"

    id = Column(Integer, primary_key=True, unique=True)
    source_id = Column(Integer, ForeignKey('nodes.id'))
    target_id = Column(Integer, ForeignKey('nodes.id'))

class SubjectArea(Base):
    __tablename__ = "subject_areas"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    description = Column(String)

class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    description = Column(String)
    #FK
    sub_area_id = Column(Integer, ForeignKey('subject_areas.id'))
    # FK
    model_id = Column(Integer, ForeignKey('models.id'))

