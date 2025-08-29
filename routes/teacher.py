from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from database import get_db
from schemas.teacher import TeacherCreate, TeacherOut
from services.teacher import teacher_service


logger = logging.getLogger(__name__)

teacher_router = APIRouter(prefix="/teacher", tags=["teacher"])

@teacher_router.post("/", status_code=status.HTTP_201_CREATED, response_model=TeacherOut)
def register_teacher(teacher_in: TeacherCreate, db: Session = Depends(get_db)):
    try:
        teacher_data = teacher_service.create_teacher(db, teacher_in)
        return teacher_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in register_teacher endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while registering teacher"
        )

@teacher_router.get("/", status_code=status.HTTP_200_OK, response_model=List[TeacherOut])
def get_all_teachers(db: Session = Depends(get_db)):
    try:
        return teacher_service.get_all_teachers(db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_all_teachers endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving teachers"
        )

@teacher_router.get("/{teacher_id}", status_code=status.HTTP_200_OK, response_model=TeacherOut)
def get_teacher(teacher_id: UUID, db: Session = Depends(get_db)):
    try:
        return teacher_service.get_teacher_by_id(db, teacher_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_teacher endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving teacher"
        )


@teacher_router.put("/{teacher_id}", status_code=status.HTTP_200_OK, response_model=TeacherOut)
def update_teacher(teacher_id: UUID, teacher_in: TeacherCreate, db: Session = Depends(get_db)):
    try:
        return teacher_service.update_teacher(db, teacher_id, teacher_in)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_teacher endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating teacher"
        )

@teacher_router.delete("/{teacher_id}", status_code=status.HTTP_200_OK)
def delete_teacher(teacher_id: UUID, db: Session = Depends(get_db)):
    try:
        return teacher_service.delete_teacher(db, teacher_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_teacher endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting teacher"
        )