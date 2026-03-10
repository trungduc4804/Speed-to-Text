from sqlalchemy.orm import Session
from app.models.role import Role, UserRole
from app.models.user import User
from app.schemas import RoleCreate
from fastapi import HTTPException

# Danh sách Role mặc định
DEFAULT_ROLES = ["ADMIN", "SECRETARY", "CHAIRMAN", "MEMBER", "VIEWER"]

class RoleService:
    def create_role(self, db: Session, role_in: RoleCreate) -> Role:
        role = db.query(Role).filter(Role.name == role_in.name).first()
        if role:
            raise HTTPException(status_code=400, detail="Role đã tồn tại.")
        new_role = Role(name=role_in.name, description=role_in.description)
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        return new_role

    def assign_role_to_user(self, db: Session, user_id: int, role_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        role = db.query(Role).filter(Role.id == role_id).first()
        if not user or not role:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng hoặc role.")
        
        user_role = db.query(UserRole).filter_by(user_id=user_id, role_id=role_id).first()
        if user_role:
             raise HTTPException(status_code=400, detail="Người dùng đã có role này.")
             
        new_user_role = UserRole(user_id=user_id, role_id=role_id)
        db.add(new_user_role)
        db.commit()
        return {"message": f"Đã gán role {role.name} cho user {user.username}."}

    def remove_role_from_user(self, db: Session, user_id: int, role_id: int):
        user_role = db.query(UserRole).filter_by(user_id=user_id, role_id=role_id).first()
        if not user_role:
             raise HTTPException(status_code=404, detail="Người dùng không có role này.")
        
        db.delete(user_role)
        db.commit()
        return {"message": "Đã thu hồi role thành công."}

    def init_default_roles(self, db: Session):
        for role_name in DEFAULT_ROLES:
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                new_role = Role(name=role_name, description=f"Quyền {role_name}")
                db.add(new_role)
        db.commit()

    def assign_first_user_as_admin(self, db: Session):
        """Tự động kiểm tra: nếu user đầu tiên tạo ra (id=1) chưa có quyền ADMIN thì cấp cho họ."""
        first_user = db.query(User).order_by(User.id.asc()).first()
        if not first_user:
            return # Chưa có user nào trong hệ thống
            
        admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
        if not admin_role:
            return
            
        user_role = db.query(UserRole).filter_by(user_id=first_user.id, role_id=admin_role.id).first()
        if not user_role:
            new_user_role = UserRole(user_id=first_user.id, role_id=admin_role.id)
            db.add(new_user_role)
            db.commit()

role_service = RoleService()
