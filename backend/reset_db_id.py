from app.db import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # Reset ID sequence in PostgreSQL cho bằng 1
    # PostgreSQL sử dụng tên sequence mặc định là "tablename_id_seq"
    db.execute(text("TRUNCATE TABLE users CASCADE;")) 
    db.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1;"))
    db.commit()
    print("Success: Truncated users and reset sequence to 1")
except Exception as e:
    db.rollback()
    print("Error:", e)
finally:
    db.close()
