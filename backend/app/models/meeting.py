from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db import Base

class MeetingStatus(str, enum.Enum):
    DRAFT = "NHAP"
    PENDING_APPROVAL = "CHO_DUYET"
    APPROVED = "DA_DUYET"
    SIGNED = "DA_KY"
    ARCHIVED = "LUU_TRU"


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    audio_path = Column(String)
    transcript = Column(Text)
    final_content = Column(Text)
    summary = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)  # JSON string
    pdf_path = Column(String)
    signature = Column(Text, nullable=True)      # Chữ ký số RSA (base64)
    status = Column(String, default=MeetingStatus.DRAFT.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("app.models.user.User", backref="meetings")

