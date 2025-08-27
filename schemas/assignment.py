from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class AssignmentBase(BaseModel):
    student_name: str
    subject: str
    description: str
    filename: str
    comments: Optional[str] = None

class AssignmentCreate(AssignmentBase):
    pass

class Assignment (AssignmentBase):
    id: UUID

class AssignmentOut(BaseModel):
    id: UUID
    student_name: str
    subject: str
    description: str
    filename: str
    comments: Optional[str]



    model_config = {
        "from_attributes": True
    }