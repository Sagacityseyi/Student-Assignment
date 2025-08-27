from sqlalchemy.orm import Session
import models
from schemas.teacher import TeacherCreate

class TeacherService:
    @staticmethod
    def create_teacher(db: Session, teacher_in: TeacherCreate ):
     db_teacher = models.Teacher(
        name = teacher_in.name,
        email = teacher_in.email
    )

     db.add(db_teacher)
     db.commit()
     db.refresh(db_teacher)
     return db_teacher

teacher_service = TeacherService()