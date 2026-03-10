# Hệ thống Biên bản Cuộc họp (Meeting Minutes System)

Dự án hỗ trợ ghi biên bản cuộc họp tự động bằng cách chuyển đổi giọng nói thành văn bản (Speech-to-Text), chỉnh sửa văn bản, xuất biên bản thành tệp PDF và hỗ trợ ký số điện tử để xác thực tài liệu.

## ✨ Tính năng chính (Features)

1. **Quản lý Tài khoản (Authentication)**:
   - Đăng ký, Đăng nhập bảo mật (mã hóa mật khẩu bằng `bcrypt`, cấp token JWT).
   - Giao diện thân thiện trực quan với từng người dùng.
2. **Quản lý Cuộc họp (Dashboard)**:
   - Xem danh sách các biên bản cuộc họp đã tạo.
   - Thêm cuộc họp mới.
3. **Chuyển đổi Giọng nói thành Văn bản (Speech to Text - STT)**:
   - Upload file ghi âm (`.mp3`, `.wav`, `.m4a`).
   - Tự động tách lời thoại từ file âm thanh sử dụng mô hình **Whisper** (thông qua `whisper.cpp` để tăng tốc độ xử lý).
   - Tích hợp `FFmpeg` để xử lý và chuyển đổi định dạng âm thanh đầu vào.
4. **Chỉnh sửa Biên bản (Editor)**:
   - Giao diện chỉnh sửa nội dung văn bản sau khi chuyển từ giọng nói.
   - Lưu trữ thay đổi và quản lý thông tin cuộc họp (tiêu đề, địa điểm, thời gian, người chủ trì...).
5. **Xuất file PDF**:
   - Trích xuất nội dung văn bản hoàn chỉnh ra định dạng PDF có hỗ trợ phông chữ tiếng Việt (sử dụng thư viện `ReportLab`).
6. **Ký số Điện tử (Digital Signature)**:
   - Cung cấp tính năng ký điện tử lên biên bản sử dụng thuật toán **RSA**.
   - Lưu trữ thông tin chữ ký chứng thực chống thay đổi nội dung.

## 🛠️ Công nghệ sử dụng (Tech Stack)

### Backend
- **Ngôn ngữ**: Python 3.10+
- **Framework**: FastAPI
- **Cơ sở dữ liệu (Database)**: PostgreSQL
- **ORM**: SQLAlchemy (với `psycopg2-binary`)
- **Xử lý âm thanh**: Whisper (`whisper.cpp`), FFmpeg
- **Tạo PDF**: ReportLab
- **Mã hóa chữ ký**: Cryptography
- **Bảo mật**: passlib, python-jose (JWT)

### Frontend
- **HTML/CSS/JS (Vanilla)**: Giao diện web được thiết kế hiện đại, tùy biến CSS (không dùng framework nặng).
- **Template Engine**: Jinja2 (tích hợp trực tiếp trên FastAPI).
- **Giao tiếp API**: `fetch` API với JSON và Multipart Form-Data.

---

## 🚀 Hướng dẫn Cài đặt & Chạy dự án

### 1. Yêu cầu hệ thống (Prerequisites)
- **Python 3.10** trở lên.
- **PostgreSQL**: Đã được cài đặt và đang chạy trên thiết bị (hoặc dùng Docker).
- Phải có file mô hình **Whisper ggml-model** (hệ thống có script hỗ trợ tự động tải).

### 2. Thiết lập Cơ sở dữ liệu PostgreSQL
Bạn cần tạo một cơ sở dữ liệu (ví dụ tên là `meeting_minutes_db`) trong PostgreSQL.

Tạo file biến môi trường để cấu hình hệ thống:
1. Mở thư mục `backend/`.
2. Tạo file `.env` với nội dung cấu hình cơ sở dữ liệu.
   ```ini
   # File: backend/.env
   SQLALCHEMY_DATABASE_URI=postgresql://<username>:<password>@localhost:5432/meeting_minutes_db
   ```
   *(Thay `<username>` và `<password>` bằng tài khoản PostgreSQL của bạn)*

### 3. Cài đặt Backend Dependencies

Mở Terminal / Command Prompt tại thư mục dự án:
```bash
cd backend
pip install -r requirements.txt
```

### 4. Tải và thiết lập Whisper (Voice to Text Model) & FFmpeg

Các Model AI Whisper và FFmpeg rất lớn, vì vậy cần phải tải và thiết lập thông qua kịch bản PowerShell có sẵn.

Mở **PowerShell** tại thư mục `backend/` và chạy 2 script sau:
```powershell
# Tắt chính sách giới hạn thực thi tạm thời
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Tải và cấu hình FFMPEG (nếu trong máy chưa có)
.\setup_ffmpeg.ps1

# Tải và cấu hình Whisper (whisper.cpp binary + ggml model)
.\setup_whisper.ps1
```
*(Nếu bạn muốn độ chính xác cao hơn, có thể dùng file script tải mô hình `small`: `.\download_small_model.ps1`)*

### 5. Khởi động Ứng dụng

Sau khi các bước trên thành công, bạn có thể khởi động backend server (Các bảng database sẽ được tự động tạo lần đầu):

```bash
# Đảm bảo bạn đang ở thư mục backend
uvicorn app.main:app --reload
```
Server sẽ chạy trên địa chỉ: [http://localhost:8000](http://localhost:8000)

---

## 📂 Cấu trúc Thư mục Dự án (Project Structure)

```text
Do-An-TN/
│
├── backend/                  # Chứa toàn bộ logic ứng dụng (API, AI, DB)
│   ├── app/                  # Mã nguồn chính của FastAPI
│   │   ├── api/              # Định tuyến API (Auth, Minutes, STT, PDF, Sign)
│   │   ├── core/             # Cấu hình hệ thống (Config, Security)
│   │   ├── models/           # Định nghĩa Models cho Database (SQLAlchemy)
│   │   ├── services/         # Logic xử lý nghiệp vụ (User, File, STT, PDF...)
│   │   ├── utils/            # Các hàm hỗ trợ dùng chung
│   │   ├── db.py             # Cấu hình kết nối Database
│   │   └── main.py           # Điểm khởi đầu (Entrypoint) của ứng dụng FastAPI
│   ├── ffmpeg/               # Thư mục lưu trữ binary của FFmpeg (Tải về qua script)
│   ├── models/               # Thư mục lưu trữ các file mô hình Whisper (.bin)
│   ├── uploads/              # Lưu trữ cục bộ cho (Audio file và PDF output)
│   ├── whisper/              # Chứa các file thực thi engine whisper.cpp
│   ├── requirements.txt      # File chứa các thư viện Python (psycopg2, fastapi,...)
│   └── *.ps1                 # Các Script thao tác hỗ trợ cài đặt cho Windows
│
├── frontend/                 # Giao diện người dùng
│   ├── static/               # Thư mục chứa CSS, JavaScript tĩnh và Hình ảnh
│   └── templates/            # Các trang giao diện HTML (Jinja2 Templates)
│
└── README.md                 # Tài liệu hướng dẫn (File này)
```

## 📝 Quy trình (User Flow)
1. Truy cập `http://localhost:8000`.
2. Tạo tài khoản thông qua `/register` và Đăng nhập.
3. Trong bảng điều khiển (Dashboard), ấn vào "Tạo Biên Bản Mới" và upload file âm thanh ghi âm cuộc họp.
4. Chờ hệ thống AI chuyển đổi thành văn bản.
5. Click vào biên bản vừa hoàn thành để chỉnh sửa các lỗi chính tả (nếu có) và bổ sung định dạng thông tin.
6. Khi hoàn tất, nhấn "Xuất PDF" để tạo file báo cáo bản cứng.
7. Bạn cũng có thể "Ký xác thực" trực tiếp trên hệ thống để nâng cao tính bảo mật cho biên bản.
