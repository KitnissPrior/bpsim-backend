from fastapi import FastAPI, Depends
from pydantic import BaseModel, ConfigDict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Либо конкретные URL-адреса
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NodeCreation(BaseModel):
    name: str
    description: str | None = None

class Node(NodeCreation):
    id: int
    model_config = ConfigDict(from_attributes=True)

@app.post("/node/")
async def add_node(node: NodeCreation):
    """
    Добавить узел в модель
    """
    return {"data": node}

@app.get("/")
async def home():
    """ Home endpoint """
    return {"data": "Это бэкенд BPsim Web!"}
