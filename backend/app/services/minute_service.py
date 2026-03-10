from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.meeting import Meeting, MeetingStatus
from app.models.user import User

class MinuteService:
    """Service for handling meeting minutes business logic."""

    @staticmethod
    def change_status(db: Session, meeting: Meeting, new_status: MeetingStatus, user: User) -> Meeting:
        roles = [role.name for role in user.roles]
        
        if new_status == MeetingStatus.PENDING_APPROVAL:
            if "SECRETARY" not in roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ SECRETARY mới có thể chuyển sang trạng thái CHO_DUYET")
            if meeting.status != MeetingStatus.DRAFT.value:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ có thể chuyển sang CHO_DUYET từ trạng thái NHAP")
                
        elif new_status == MeetingStatus.APPROVED:
            if "CHAIRMAN" not in roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ CHAIRMAN mới có thể duyệt (chuyển sang DA_DUYET)")
            if meeting.status != MeetingStatus.PENDING_APPROVAL.value:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cuộc họp phải ở trạng thái CHO_DUYET mới có thể duyệt")
                
        elif new_status == MeetingStatus.SIGNED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Trạng thái DA_KY được tự động cập nhật khi ký tài liệu")
            
        elif new_status == MeetingStatus.ARCHIVED:
            if "CHAIRMAN" not in roles and "SECRETARY" not in roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền chuyển sang trạng thái LUU_TRU")
        
        meeting.status = new_status.value
        db.commit()
        db.refresh(meeting)
        return meeting

    @staticmethod
    def check_can_edit(meeting: Meeting):
        if meeting.status in [MeetingStatus.SIGNED.value, MeetingStatus.ARCHIVED.value]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không được phép sửa nội dung khi đã ký hoặc lưu trữ")
