from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from database import get_db
from schemas.student import StudentCreate, StudentOut
from services.student import student_service


logger = logging.getLogger(__name__)

student_router = APIRouter(prefix="/student", tags=["student"])

@student_router.post("/", status_code=status.HTTP_201_CREATED, response_model=StudentOut)
def register_student(student_in: StudentCreate, db: Session = Depends(get_db)):
    try:
        student_data = student_service.create_student(db, student_in)
        return student_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in register_student endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while registering student"
        )

@student_router.get("/", status_code=status.HTTP_200_OK, response_model=List[StudentOut])
def get_all_students(db: Session = Depends(get_db)):
    try:
        return student_service.get_all_students(db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_all_students endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving students"
        )

@student_router.get("/{student_id}", status_code=status.HTTP_200_OK, response_model=StudentOut)
def get_student(student_id: UUID, db: Session = Depends(get_db)):
    try:
        return student_service.get_student_by_id(db, student_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_student endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving student"
        )

@student_router.delete("/{student_id}", status_code=status.HTTP_200_OK)
def delete_student(student_id: UUID, db: Session = Depends(get_db)):
    try:
        return student_service.delete_student(db, student_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_student endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting student"
        )