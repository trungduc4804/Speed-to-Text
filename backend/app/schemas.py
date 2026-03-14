from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.meeting import MeetingStatus

class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    created_at: datetime
    roles: list[RoleResponse] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class MeetingBase(BaseModel):
    title: str

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(BaseModel):
    final_content: str

class MeetingStatusUpdate(BaseModel):
    status: MeetingStatus

# Schema nhận chữ ký từ client (ký phía client bằng Web Crypto API)
class SignRequest(BaseModel):
    signature: str  # base64-encoded RSA-PSS signature

class MeetingResponse(MeetingBase):
    id: int
    user_id: int
    audio_path: Optional[str] = None
    transcript: Optional[str] = None
    final_content: Optional[str] = None
    summary: Optional[str] = None
    action_items: Optional[str] = None
    pdf_path: Optional[str] = None
    signature: Optional[str] = None  # Chữ ký số RSA (base64)
    status: MeetingStatus
    created_at: datetime

    class Config:
        from_attributes = True

class MeetingAdminResponse(MeetingResponse):
    owner_username: str
    owner_fullname: Optional[str] = None
