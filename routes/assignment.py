from uuid import UUID
from fastapi import APIRouter, Depends, Form, File, UploadFile, status
from sqlalchemy.orm import Session
import models
from database import get_db
from schemas.assignment import AssignmentOut
from services.assignment import AssignmentService

assignment_router = APIRouter(prefix="/assignment", tags=["assignment"])

@assignment_router.post("/",status_code=status.HTTP_201_CREATED, response_model=AssignmentOut)
async def submit_assignment(
    name: str = Form(...), 
    subject: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await AssignmentService.submit_assignment(
        student_name=name,
        subject=subject,
        description=description,
        file=file,
        db=db,
    )

@assignment_router.get("/", status_code=status.HTTP_200_OK, response_model=list[AssignmentOut])
def get_all_assignments(db: Session = Depends(get_db)):
    assignments = db.query(models.Assignment).all()

    results = []
    for a in assignments:
        results.append({
            "id": a.id,
            "student_name": a.student.name if a.student else None,
            "subject": a.subject,
            "description": a.description,
            "filename": a.filename,
            "comments": a.comments,
        })
    return results

@assignment_router.post("/{name}/assignment", status_code=status.HTTP_200_OK, response_model=AssignmentOut)
def get_assignment_by_name(student_name: str, db: Session = Depends(get_db)):
    assignment = AssignmentService.get_assignment_by_name(db, student_name)
    return assignment

@assignment_router.patch("/{assignment_id}/comment")
def add_comment(assignment_id: UUID, comment: str, db: Session = Depends(get_db)):
    comment = AssignmentService.add_teacher_comment(db, assignment_id, comment)
    return comment