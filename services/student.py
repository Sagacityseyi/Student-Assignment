from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
import models,logging
from schemas.student import StudentCreate


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StudentService:
    @staticmethod
    def create_student(db: Session, student_in: StudentCreate):
        try:
            # Validate input data
            if not student_in.name or not student_in.name.strip():
                logger.error("Student name is required")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Student name is required"
                )

            if not student_in.email or not student_in.email.strip():
                logger.error("Student email is required")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Student email is required"
                )

            # Check if student already exists
            existing_student = db.query(models.Student).filter(
                models.Student.email == student_in.email
            ).first()

            if existing_student:
                logger.warning(f"Student with email {student_in.email} already exists")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Student with email {student_in.email} already exists"
                )

            # Create new student
            db_student = models.Student(
                name=student_in.name.strip(),
                email=student_in.email.strip()
            )

            db.add(db_student)
            db.commit()
            db.refresh(db_student)

            logger.info(f"Student created successfully: {db_student.id}")
            return db_student

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error while creating student: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data provided for student creation"
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while creating student: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create student due to database error"
            )
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while creating student: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating student"
            )

    @staticmethod
    def get_all_students(db: Session):
        try:
            students = db.query(models.Student).all()
            logger.info(f"Retrieved {len(students)} students")
            return students
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving students: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve students due to database error"
            )
        except Exception as e:
            logger.error(f"Unexpected error while retrieving students: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving students"
            )

    @staticmethod
    def get_student_by_id(db: Session, student_id: UUID):
        try:
            student = db.query(models.Student).filter(
                models.Student.id == student_id
            ).first()

            if not student:
                logger.warning(f"Student with ID {student_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Student with ID {student_id} not found"
                )

            return student
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving student: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve student due to database error"
            )
        except Exception as e:
            logger.error(f"Unexpected error while retrieving student: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving student"
            )

    @staticmethod
    def delete_student(db: Session, student_id: UUID):
        try:
            student = db.query(models.Student).filter(
                models.Student.id == student_id
            ).first()

            if not student:
                logger.warning(f"Student with ID {student_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Student with ID {student_id} not found"
                )

            db.delete(student)
            db.commit()

            logger.info(f"Student deleted successfully: {student_id}")
            return {"message": f"Student with ID {student_id} deleted successfully"}

        except HTTPException:
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while deleting student: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete student due to database error"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while deleting student: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting student"
            )


student_service = StudentService()