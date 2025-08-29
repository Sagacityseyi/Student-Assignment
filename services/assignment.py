import uuid, logging, os, models
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = "assignments"
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
ALLOWED_FILE_TYPES = {".pdf", ".doc", ".docx", ".txt", ".zip"}


class AssignmentService:
    @staticmethod
    async def submit_assignment(
            student_name: str,
            subject: str,
            description: str,
            file: UploadFile,
            db: Session,
    ):
        try:
            # Validate student exists
            student = db.query(models.Student).filter(models.Student.name == student_name).first()
            if not student:
                logger.warning(f"Student '{student_name}' not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Student '{student_name}' not found"
                )

            # Validate file presence
            if not file or not file.filename:
                logger.error("No file provided in request")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File is required"
                )

            # Validate file type
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in ALLOWED_FILE_TYPES:
                logger.error(f"Invalid file type: {file_extension}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_FILE_TYPES)}"
                )

            # Validate file size
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                logger.error(f"File size exceeds limit: {len(content)} bytes")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File exceeds {MAX_FILE_SIZE // (1024 * 1024)}MB"
                )

            await file.seek(0)

            filename = f"{student.name}-{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, filename)

            try:
                os.makedirs(UPLOAD_DIR, exist_ok=True)
            except OSError as e:
                logger.error(f"Failed to create directory {UPLOAD_DIR}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create upload directory"
                )

            # Save file to disk
            try:
                with open(file_path, "wb") as f:
                    f.write(content)
            except IOError as e:
                logger.error(f"Failed to save file {filename}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save file"
                )

            # Create database record
            try:
                new_assignment = models.Assignment(
                    student_id=student.id,
                    subject=subject,
                    description=description,
                    filename=filename,
                )

                db.add(new_assignment)
                db.commit()
                db.refresh(new_assignment)

                logger.info(f"Assignment submitted successfully: {new_assignment.id}")

                return {
                    "id": new_assignment.id,
                    "student_name": student.name,
                    "subject": new_assignment.subject,
                    "description": new_assignment.description,
                    "filename": new_assignment.filename,
                    "comments": new_assignment.comments,
                }

            except SQLAlchemyError as e:
                db.rollback()
                logger.error(f"Database error while creating assignment: {str(e)}")

                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except OSError as cleanup_error:
                    logger.error(f"Failed to clean up file {file_path}: {str(cleanup_error)}")

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save assignment record"
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in submit_assignment: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while submitting the assignment"
            )

    @staticmethod
    def get_assignments_by_student_name(db: Session, student_name: str):
        try:
            student = db.query(models.Student).filter(models.Student.name == student_name).first()
            if not student:
                logger.warning(f"Student '{student_name}' not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Student '{student_name}' not found"
                )

            assignments = db.query(models.Assignment).filter(
                models.Assignment.student_id == student.id
            ).all()

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

        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching assignments: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve assignments"
            )
        except Exception as e:
            logger.error(f"Unexpected error in get_assignments_by_student_name: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving assignments"
            )

    @staticmethod
    def add_teacher_comment(db: Session, assignment_id: uuid.UUID, comment: str):
        try:
            if not comment or not comment.strip():
                logger.error("Empty comment provided")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Comment cannot be empty"
                )

            assignment = db.query(models.Assignment).filter(
                models.Assignment.id == assignment_id
            ).first()

            if not assignment:
                logger.warning(f"Assignment {assignment_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignment not found"
                )

            assignment.comments = comment.strip()

            try:
                db.commit()
                db.refresh(assignment)
            except SQLAlchemyError as e:
                db.rollback()
                logger.error(f"Database error while updating comment: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update comment"
                )

            # Get student name for the response
            student = db.query(models.Student).filter(
                models.Student.id == assignment.student_id
            ).first()

            logger.info(f"Comment added to assignment: {assignment_id}")

            return {
                "id": assignment.id,
                "student_name": student.name if student else "Unknown",
                "subject": assignment.subject,
                "description": assignment.description,
                "filename": assignment.filename,
                "comments": assignment.comments,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in add_teacher_comment: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while adding comment"
            )