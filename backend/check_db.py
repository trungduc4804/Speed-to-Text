import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app.models.user import User
from app.models.role import Role

from app.services.role_service import role_service
db = SessionLocal()
try:
    role_service.assign_first_user_as_admin(db)
    print("Xong, da cap quyen!")
finally:
    db.close()
