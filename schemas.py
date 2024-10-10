from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    id: int
    name: str
    email: str

class UserCreate(UserBase):
    created_at: datetime

class UserResponse(UserBase):
    pass

    class Config:
        orm_mode = True
