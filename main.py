from fastapi import FastAPI, Depends

from pydantic import BaseModel, ConfigDict

app = FastAPI()
class STaskAdd(BaseModel):
   name: str
   description: str | None = None

class STask(STaskAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)

@app.post("/")
async def add_task(task: STaskAdd = Depends()):
   return {"data": task}


@app.get("/")
async def home():
    return {"data": "Hi there!"}