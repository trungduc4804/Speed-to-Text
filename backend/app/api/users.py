from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, require_role, get_current_user
from app.models.user import User
from app.schemas import User as UserSchema

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Trả về thông tin người dùng đang đăng nhập."""
    return current_user

@router.get("/", response_model=List[UserSchema], dependencies=[Depends(require_role(["ADMIN"]))])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """API dành riêng cho Admin để lấy danh sách toàn bộ Users."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users
