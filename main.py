from fastapi import FastAPI
import models
from database import engine
from routes.assignment import assignment_router
from routes.student import student_router
from routes.teacher import teacher_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(student_router)
app.include_router(assignment_router)
app.include_router(teacher_router)

@app.get("/")
def home():
    return {"message": "Welcome to home page"}