from uuid import UUID

from pydantic import BaseModel, EmailStr


class Teacher(BaseModel):
    name: str
    email: EmailStr

class TeacherCreate(Teacher):
    pass

class TeacherOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr

model_config ={
    "from_attributes": True
}