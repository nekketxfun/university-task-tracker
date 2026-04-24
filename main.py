from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

import models, schemas, database

# Создаем таблицы при запуске
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Task Manager")
templates = Jinja2Templates(directory="templates")

# Зависимость для получения сессии БД
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Эндпоинты (для JSON) ---
@app.post("/api/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/api/tasks", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Task).offset(skip).limit(limit).all()

@app.put("/api/tasks/{task_id}")
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.completed = not task.completed
    db.commit()
    return {"message": "Task updated", "id": task_id}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}

# --- Веб-интерфейс (HTML) ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})

@app.post("/add")
async def add_task_web(title: str = Form(...), description: str = Form(None), db: Session = Depends(get_db)):
    new_task = models.Task(title=title, description=description)
    db.add(new_task)
    db.commit()
    return templates.TemplateResponse("index.html", {"request": request, "tasks": db.query(models.Task).all()})

@app.post("/toggle/{task_id}")
async def toggle_task_web(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        task.completed = not task.completed
        db.commit()
    return templates.TemplateResponse("index.html", {"request": request, "tasks": db.query(models.Task).all()})

@app.post("/delete/{task_id}")
async def delete_task_web(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
    return templates.TemplateResponse("index.html", {"request": request, "tasks": db.query(models.Task).all()})