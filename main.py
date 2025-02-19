from fastapi import FastAPI, Depends

from pydantic import BaseModel, ConfigDict

app = FastAPI()


class NodeAdd(BaseModel):
   name: str
   description: str | None = None

class Node(NodeAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)

@app.post("/")
async def add_node(node: NodeAdd = Depends()):
   return {"data": node}


@app.get("/")
async def home():
    return {"data": "Это бэкенд BPsim Web!"}