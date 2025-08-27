from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from database import get_db
from schemas.student import StudentCreate, StudentOut
from services.student import student_service

student_router = APIRouter(prefix="/student", tags=["student"])

@student_router.post("/", response_model=StudentOut)
def register_student( student_in: StudentCreate, db:Session = Depends(get_db)):
    student_data = student_service.create_student(db, student_in)
    return student_data

@student_router.get("/", response_model=List[StudentOut])
def get_all_student(db: Session = Depends(get_db)):
    return db.query(models.Student).all()