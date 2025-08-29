from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
import models, logging
from schemas.teacher import TeacherCreate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class TeacherService:
    @staticmethod
    def create_teacher(db: Session, teacher_in: TeacherCreate):
        try:
            # Validate input data
            if not teacher_in.name or not teacher_in.name.strip():
                logger.error("Teacher name is required")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Teacher name is required"
                )

            if not teacher_in.email or not teacher_in.email.strip():
                logger.error("Teacher email is required")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Teacher email is required"
                )


            # Check if teacher already exists
            existing_teacher = db.query(models.Teacher).filter(
                models.Teacher.email == teacher_in.email
            ).first()

            if existing_teacher:
                logger.warning(f"Teacher with email {teacher_in.email} already exists")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Teacher with email {teacher_in.email} already exists"
                )

            # Create new teacher
            db_teacher = models.Teacher(
                name=teacher_in.name.strip(),
                email=teacher_in.email.strip().lower()
            )

            db.add(db_teacher)
            db.commit()
            db.refresh(db_teacher)

            logger.info(f"Teacher created successfully: {db_teacher.id}")
            return db_teacher

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database integrity error while creating teacher: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data provided for teacher creation"
            )
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while creating teacher: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create teacher due to database error"
            )
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while creating teacher: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating teacher"
            )

    @staticmethod
    def get_all_teachers(db: Session):
        try:
            teachers = db.query(models.Teacher).all()
            logger.info(f"Retrieved {len(teachers)} teachers")
            return teachers
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving teachers: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve teachers due to database error"
            )
        except Exception as e:
            logger.error(f"Unexpected error while retrieving teachers: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving teachers"
            )

    @staticmethod
    def get_teacher_by_id(db: Session, teacher_id: UUID):
        try:
            teacher = db.query(models.Teacher).filter(
                models.Teacher.id == teacher_id
            ).first()

            if not teacher:
                logger.warning(f"Teacher with ID {teacher_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Teacher with ID {teacher_id} not found"
                )

            return teacher
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving teacher: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve teacher due to database error"
            )
        except Exception as e:
            logger.error(f"Unexpected error while retrieving teacher: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while retrieving teacher"
            )

    @staticmethod
    def update_teacher(db: Session, teacher_id: UUID, teacher_in: TeacherCreate):
        try:
            teacher = db.query(models.Teacher).filter(
                models.Teacher.id == teacher_id
            ).first()

            if not teacher:
                logger.warning(f"Teacher with ID {teacher_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Teacher with ID {teacher_id} not found"
                )


            # Check if email is already taken by another teacher
            if teacher_in.email and teacher_in.email != teacher.email:
                existing_teacher = db.query(models.Teacher).filter(
                    models.Teacher.email == teacher_in.email,
                    models.Teacher.id != teacher_id
                ).first()

                if existing_teacher:
                    logger.warning(f"Email {teacher_in.email} is already taken by another teacher")
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Email {teacher_in.email} is already taken by another teacher"
                    )

            # Update teacher fields
            if teacher_in.name:
                teacher.name = teacher_in.name.strip()
            if teacher_in.email:
                teacher.email = teacher_in.email.strip().lower()

            db.commit()
            db.refresh(teacher)

            logger.info(f"Teacher updated successfully: {teacher_id}")
            return teacher

        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while updating teacher: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update teacher due to database error"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while updating teacher: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating teacher"
            )

    @staticmethod
    def delete_teacher(db: Session, teacher_id: UUID):
        try:
            teacher = db.query(models.Teacher).filter(
                models.Teacher.id == teacher_id
            ).first()

            if not teacher:
                logger.warning(f"Teacher with ID {teacher_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Teacher with ID {teacher_id} not found"
                )

            db.delete(teacher)
            db.commit()

            logger.info(f"Teacher deleted successfully: {teacher_id}")
            return {"message": f"Teacher with ID {teacher_id} deleted successfully"}

        except HTTPException:
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while deleting teacher: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete teacher due to database error"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while deleting teacher: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting teacher"
            )


teacher_service = TeacherService()