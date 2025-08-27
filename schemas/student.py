from uuid import UUID
from pydantic import BaseModel, EmailStr


class StudentBase(BaseModel):
    name: str
    email: EmailStr

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: UUID

class StudentOut(BaseModel):
    name: str
    email: EmailStr


    model_config = {
        "from_attributes": True
    }


