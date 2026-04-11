# � Ghi Chú Dự Án — Hệ Thống Biên Bản Cuộc Họp (Speech-to-Text)

> Đồ án tốt nghiệp — Ứng dụng chuyển giọng nói thành văn bản, quản lý biên bản cuộc họp, phân tích AI và ký số điện tử.

---

## 🏗️ Kiến Trúc Hệ Thống

```
Do-An-TN/
├── backend/
│   ├── app/
│   │   ├── main.py              # Entry point, đăng ký tất cả router
│   │   ├── db.py                # Kết nối SQLAlchemy
│   │   ├── deps.py              # Dependency injection (auth, role guard)
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── api/                 # Các router API
│   │   │   ├── auth.py          # Đăng ký / Đăng nhập
│   │   │   ├── minutes.py       # CRUD biên bản cuộc họp
│   │   │   ├── roles.py         # Quản lý vai trò (ADMIN only)
│   │   │   ├── users.py         # Xem danh sách user
│   │   │   ├── pdf.py           # Xuất PDF
│   │   │   ├── signature.py     # Ký số & xác thực chữ ký
│   │   │   ├── stt.py           # Speech-to-Text endpoint
│   │   │   └── files.py         # Phục vụ file tĩnh
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── user.py          # Bảng users
│   │   │   ├── meeting.py       # Bảng meetings
│   │   │   └── role.py          # Bảng roles + user_roles
│   │   ├── services/            # Business logic
│   │   │   ├── stt_service.py   # Whisper.cpp transcription
│   │   │   ├── ai_service.py    # Gemini AI phân tích nội dung
│   │   │   ├── pdf_service.py   # Tạo file PDF (ReportLab)
│   │   │   ├── signature_service.py  # RSA ký số
│   │   │   ├── role_service.py  # Gán / thu hồi role
│   │   │   └── minute_service.py # Workflow trạng thái biên bản
│   │   └── core/
│   │       ├── config.py        # Cấu hình từ .env
│   │       └── security.py      # JWT + bcrypt
│   ├── uploads/                 # Lưu file audio upload
│   ├── whisper/                 # Whisper.cpp binary + model
│   └── ffmpeg/                  # FFmpeg binary
└── frontend/
    ├── templates/               # Jinja2 HTML templates
    │   ├── index.html           # Trang chính (danh sách biên bản)
    │   ├── login.html           # Đăng nhập
    │   ├── register.html        # Đăng ký
    │   ├── meeting_detail.html  # Chi tiết biên bản
    │   └── admin.html           # Trang quản trị
    └── static/
        ├── js/
        │   ├── main.js          # Logic trang chính (upload, list, filter)
        │   ├── auth.js          # Xử lý login/register
        │   ├── admin.js         # Logic trang admin
        │   └── api.js           # Axios/fetch helper
        └── css/
```

---

## 🔌 API Endpoints Đầy Đủ

### Auth — `/api/v1/auth`
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| POST | `/register` | Public | Đăng ký tài khoản mới |
| POST | `/login` | Public | Đăng nhập → trả JWT Bearer token |

### Biên Bản (Minutes) — `/api/v1/minutes`
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| POST | `/` | CHAIRMAN, SECRETARY | Tạo biên bản mới (upload audio .mp3/.wav) |
| GET | `/` | Đã đăng nhập | Lấy danh sách biên bản của mình (có tìm kiếm, lọc, phân trang) |
| GET | `/admin/all` | ADMIN | Lấy toàn bộ biên bản của tất cả user |
| GET | `/{id}` | Đã đăng nhập | Xem chi tiết biên bản |
| PUT | `/{id}` | Owner | Cập nhật nội dung biên bản |
| PUT | `/{id}/status` | Owner | Đổi trạng thái biên bản |
| DELETE | `/{id}` | Owner | Xoá biên bản |
| POST | `/{id}/analyze` | Owner | Kích hoạt AI phân tích lại nội dung |

### Vai Trò (Roles) — `/api/v1/roles`
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| POST | `/` | ADMIN | Tạo role mới |
| POST | `/{user_id}/assign/{role_id}` | ADMIN | Gán role cho user |
| DELETE | `/{user_id}/remove/{role_id}` | ADMIN | Thu hồi role |
| GET | `/{user_id}/roles` | Đã đăng nhập | Xem roles của user |

### Ký Số (Signature) — `/api/v1/signature`
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| POST | `/sign/{minute_id}` | Owner | Ký số PDF bằng RSA → trả về signature + public key |
| POST | `/verify` | Public | Xác thực chữ ký (upload PDF + public key + signature) |

### PDF — `/api/v1/pdf`
| Method | Endpoint | Quyền | Mô tả |
|--------|----------|-------|-------|
| POST | `/{minute_id}/generate` | Owner | Xuất biên bản ra file PDF |

---

## 🗄️ Database Models

### Bảng `users`
| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| id | Integer PK | |
| username | String UNIQUE | |
| password_hash | String | bcrypt |
| full_name | String | |
| created_at | DateTime | |

### Bảng `meetings`
| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| id | Integer PK | |
| user_id | FK → users | |
| title | String | |
| audio_path | String | Đường dẫn file audio |
| transcript | Text | Kết quả Whisper.cpp |
| final_content | Text | Nội dung đã chỉnh sửa |
| summary | Text | Tóm tắt từ Gemini AI |
| action_items | Text | JSON string danh sách công việc |
| pdf_path | String | Đường dẫn file PDF |
| status | String | Enum trạng thái |
| created_at | DateTime | |

### Trạng Thái Biên Bản (MeetingStatus)
```
NHAP → CHO_DUYET → DA_DUYET → DA_KY → LUU_TRU
(DRAFT)  (PENDING)  (APPROVED) (SIGNED) (ARCHIVED)
```

---

## 👥 Hệ Thống Phân Quyền (RBAC)

| Role | Quyền hạn |
|------|-----------|
| **ADMIN** | Quản lý user/role, xem tất cả biên bản |
| **CHAIRMAN** | Tạo biên bản, phê duyệt, ký số |
| **SECRETARY** | Tạo biên bản, chỉnh sửa nội dung |
| **MEMBER** | Xem biên bản của mình |
| **VIEWER** | Chỉ xem |

> 💡 User đầu tiên đăng ký sẽ được tự động gán ADMIN.

---

## ⚙️ Pipeline Xử Lý Biên Bản

```
Upload audio (.mp3/.wav)
    ↓
FFmpeg chuyển đổi → WAV 16kHz mono
    ↓
Whisper.cpp nhận dạng tiếng Việt → transcript
    ↓
Gemini 2.5 Flash phân tích → summary + action_items
    ↓
Lưu DB (DRAFT)
    ↓
User chỉnh sửa → Xuất PDF (ReportLab)
    ↓
RSA ký số PDF → DA_KY
```

---

## 🛠️ Tech Stack & Dependencies

| Thư viện | Phiên bản | Mục đích |
|----------|-----------|----------|
| `fastapi` | 0.109.0 | Web framework |
| `uvicorn` | 0.27.0 | ASGI server |
| `sqlalchemy` | 2.0.25 | ORM |
| `pydantic` | 2.5.3 | Data validation |
| `python-jose` | 3.3.0 | JWT |
| `passlib[bcrypt]` | 1.7.4 | Mã hoá mật khẩu |
| `reportlab` | 4.0.9 | Xuất PDF |
| `google-genai` | latest | Gemini AI API |
| `psycopg2-binary` | 2.9.9 | PostgreSQL driver |
| `cryptography` | latest | RSA encrypt/decrypt |
| Whisper.cpp | binary | STT (offline) |
| FFmpeg | binary | Audio conversion |

---

## ⚙️ Cài Đặt & Chạy

### 1. Cài dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Cấu hình `.env`
```env
DATABASE_URL=postgresql://user:pass@host/dbname
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_jwt_secret
ACCESS_TOKEN_EXPIRE_MINUTES=30
WHISPER_BINARY_PATH=./whisper/main.exe
WHISPER_MODEL_PATH=./models/ggml-base.bin
FFMPEG_BINARY_PATH=./ffmpeg/ffmpeg.exe
AUDIO_DIR=./uploads
```

### 3. Chạy server
```bash
uvicorn backend.app.main:app --reload
```

Truy cập: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### 4. Deploy Render
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

---

## 📄 Các Trang Frontend

| URL | Template | Mô tả |
|-----|----------|-------|
| `/` | `index.html` | Trang chính — danh sách, upload biên bản |
| `/login` | `login.html` | Đăng nhập |
| `/register` | `register.html` | Đăng ký |
| `/meeting/{id}` | `meeting_detail.html` | Chi tiết, chỉnh sửa, ký số |
| `/admin` | `admin.html` | Quản lý user & role (ADMIN only) |

---

## 📝 TODO

- [ ] Cải thiện tốc độ nhận dạng Whisper.cpp (dùng model lớn hơn / GPU)
- [ ] Tối ưu workflow phê duyệt nhiều người ký
- [ ] Thêm email thông báo khi biên bản thay đổi trạng thái
- [ ] Unit test cho các service chính

---

*Cập nhật: 14/03/2026*
