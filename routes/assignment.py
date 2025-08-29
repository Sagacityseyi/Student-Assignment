from uuid import UUID
from fastapi import APIRouter, Depends, Form, File, UploadFile, status, HTTPException
from sqlalchemy.orm import Session
import models
from database import get_db
from schemas.assignment import AssignmentOut
from services.assignment import AssignmentService
import logging

logger = logging.getLogger(__name__)

assignment_router = APIRouter(prefix="/assignment", tags=["assignment"])

@assignment_router.post("/", status_code=status.HTTP_201_CREATED, response_model=AssignmentOut)
async def submit_assignment(
    name: str = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        return await AssignmentService.submit_assignment(
            student_name=name,
            subject=subject,
            description=description,
            file=file,
            db=db,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in submit_assignment endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@assignment_router.get("/", status_code=status.HTTP_200_OK, response_model=list[AssignmentOut])
def get_all_assignments(db: Session = Depends(get_db)):
    try:
        assignments = db.query(models.Assignment).join(models.Student).all()

        results = []
        for a in assignments:
            results.append({
                "id": a.id,
                "student_name": a.student.name if a.student else "Unknown",
                "subject": a.subject,
                "description": a.description,
                "filename": a.filename,
                "comments": a.comments,
            })
        return results
    except Exception as e:
        logger.error(f"Error retrieving all assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve assignments"
        )

@assignment_router.get("/student/{student_name}", status_code=status.HTTP_200_OK, response_model=list[AssignmentOut])
def get_assignments_by_student_name(student_name: str, db: Session = Depends(get_db)):
    try:
        assignments = AssignmentService.get_assignments_by_student_name(db, student_name)
        return assignments
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_assignments_by_student_name endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@assignment_router.patch("/{assignment_id}/comment", response_model=AssignmentOut)
def add_comment(assignment_id: UUID, comment: str, db: Session = Depends(get_db)):
    try:
        result = AssignmentService.add_teacher_comment(db, assignment_id, comment)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in add_comment endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )