from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.models.role import Role
from app.schemas import RoleCreate, RoleResponse
from app.services.role_service import role_service

router = APIRouter()

@router.post("/", response_model=RoleResponse, dependencies=[Depends(require_role(["ADMIN"]))])
def create_role(role_in: RoleCreate, db: Session = Depends(get_db)):
    """Chỉ ADMIN mới có quyền tạo Role mới."""
    return role_service.create_role(db=db, role_in=role_in)

@router.post("/{user_id}/assign/{role_id}", dependencies=[Depends(require_role(["ADMIN"]))])
def assign_role(user_id: int, role_id: int, db: Session = Depends(get_db)):
    """Chỉ ADMIN mới có quyền gán Role cho User."""
    return role_service.assign_role_to_user(db=db, user_id=user_id, role_id=role_id)

@router.delete("/{user_id}/remove/{role_id}", dependencies=[Depends(require_role(["ADMIN"]))])
def remove_role(user_id: int, role_id: int, db: Session = Depends(get_db)):
    """Chỉ ADMIN mới có quyền thu hồi Role của User."""
    return role_service.remove_role_from_user(db=db, user_id=user_id, role_id=role_id)

@router.get("/{user_id}/roles", response_model=List[RoleResponse], dependencies=[Depends(require_role(["ADMIN", "SECRETARY", "CHAIRMAN", "MEMBER", "VIEWER"]))])
def get_user_roles(user_id: int, db: Session = Depends(get_db)):
    """Lấy danh sách các role của một user cụ thể."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    return user.roles
