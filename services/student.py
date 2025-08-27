from sqlalchemy.orm import Session
import models
from schemas.student import StudentCreate

class StudentService:
    @staticmethod
    def create_student( db: Session, student_in: StudentCreate):
      db_student = models.Student(
        name = student_in.name,
        email = student_in.email
    )

      db.add(db_student)
      db.commit()
      db.refresh(db_student)
      return db_student

student_service = StudentService()