from fastapi import HTTPException
from db.database import Base

def check_existance(item: Base, details: str):
    if not item:
        raise HTTPException(status_code=404, detail=details)