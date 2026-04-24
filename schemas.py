from pydantic import BaseModel
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class Task(TaskCreate):
    id: int
    completed: bool

    class Config:
        from_attributes = True