from sqlalchemy import Column, Float, String, Integer
from database import Base
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, unique=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    description = Column(String)
    posX = Column(Float)
    posY = Column(Float)