"""
Script migration: thêm cột public_key vào bảng users và signature vào bảng meetings.
Chạy từ thư mục backend: python migrate.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS public_key TEXT;
    """))
    conn.execute(text("""
        ALTER TABLE meetings
        ADD COLUMN IF NOT EXISTS signature TEXT;
    """))
    conn.commit()
    print("Migration thanh cong!")
    print("  - Da them cot 'public_key' vao bang 'users'")
    print("  - Da them cot 'signature' vao bang 'meetings'")
