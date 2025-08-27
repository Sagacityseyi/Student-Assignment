from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from database import get_db
from schemas.teacher import TeacherCreate, TeacherOut
from services.teacher import teacher_service

teacher_router = APIRouter(prefix="/teacher", tags=["teacher"])

@teacher_router.post("/", response_model=TeacherOut)
def register_teacher( teacher_in: TeacherCreate, db:Session = Depends(get_db)):
    teacher_data = teacher_service.create_teacher(db, teacher_in)
    return teacher_data

@teacher_router.get("/", response_model=List[TeacherOut])
def get_all_teacher(db:Session = Depends(get_db)):
    return db.query(models.Teacher).all()