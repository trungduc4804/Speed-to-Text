from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, require_role, get_current_user
from app.models.user import User
from app.schemas import User as UserSchema, UserUpdate
from app.core.security import verify_password, hash_password

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Trả về thông tin người dùng đang đăng nhập."""
    return current_user

@router.put("/me", response_model=UserSchema)
def update_current_user_info(user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Cập nhật thông tin và mật khẩu."""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
        
    if user_update.new_password:
        if not user_update.current_password:
            raise HTTPException(status_code=400, detail="Vui lòng nhập mật khẩu hiện tại để đổi mật khẩu mới.")
        if not verify_password(user_update.current_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không chính xác.")
        current_user.password_hash = hash_password(user_update.new_password)
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/", response_model=List[UserSchema], dependencies=[Depends(require_role(["ADMIN"]))])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """API dành riêng cho Admin để lấy danh sách toàn bộ Users."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users
