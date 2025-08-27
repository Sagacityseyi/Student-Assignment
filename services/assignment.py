import os
import uuid
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
import models

UPLOAD_DIR = "assignments"
MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_FILE_TYPES = {".pdf", ".doc", ".docx", ".txt", ".zip"}


class AssignmentService:
    @staticmethod
    async def submit_assignment(
        student_name: str,
        subject: str,
        description: str,
        file: UploadFile,
        db,
    ):
        student = db.query(models.Student).filter(models.Student.name == student_name).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student '{student_name}' not found"
            )
        if not file.filename:
            raise HTTPException(status_code=400, detail="File is required")

        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_FILE_TYPES)}"
            )

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File exceeds {MAX_FILE_SIZE // (1024 * 1024)}MB"
            )

        await file.seek(0)

        filename = f"{student.name}-{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)

        new_assignment = models.Assignment(
            student_id=student.id,
            subject=subject,
            description=description,
            filename=filename,
        )

        db.add(new_assignment)
        db.commit()
        db.refresh(new_assignment)

        return {
            "id": new_assignment.id,
            "student_name": student.name,
            "subject": new_assignment.subject,
            "description": new_assignment.description,
            "filename": new_assignment.filename,
            "comments": new_assignment.comments,
        }

    @staticmethod
    def get_assignment_by_name(db: Session, student_name: str):
        student = db.query(models.Student).filter (models.Student.name == student_name).first()
        if not student:
            raise HTTPException(
                status_code=404,
                detail=f"Student '{student_name}' not found"
            )
        assignments = db.query(models.Assignment).filter(models.Assignment.student_id == student.id).all()

        return [
            {
                "id": a.id,
                "student_name": student.name,
                "subject": a.subject,
                "description": a.description,
                "filename": a.filename,
                "comments": a.comments,
            }
            for a in assignments
        ]

    @staticmethod
    def add_teacher_comment(db: Session, assignment_id: uuid.UUID, comment:str):
        assignment = db.query(models.Assignment).filter (models.Assignment.id == assignment_id).first()
        if not assignment:
            raise  HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )

        assignment.comments = comment
        db.commit()
        db.refresh(assignment)
        return assignment
