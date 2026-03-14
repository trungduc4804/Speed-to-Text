from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.models.meeting import Meeting, MeetingStatus
from app.schemas import SignRequest, MeetingResponse
from app.services.signature_service import SignatureService

router = APIRouter()
signature_service = SignatureService()


@router.post("/save-public-key")
def save_public_key(
    public_key: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    User upload public key PEM của họ để lưu vào hệ thống.
    Chỉ cần làm 1 lần (hoặc khi đổi cặp khóa).
    """
    content = public_key.file.read().decode("utf-8")
    # Kiểm tra định dạng cơ bản
    if "BEGIN PUBLIC KEY" not in content:
        raise HTTPException(status_code=400, detail="File không hợp lệ. Phải là RSA Public Key PEM.")

    current_user.public_key = content
    db.commit()
    return {"message": "Đã lưu public key thành công."}


@router.post("/sign/{minute_id}", response_model=MeetingResponse)
def sign_pdf(
    minute_id: int,
    sign_data: SignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Nhận chữ ký số từ client (đã ký bằng private key ở phía trình duyệt).
    Server xác thực chữ ký bằng public key của user, rồi lưu vào DB.
    """
    meeting = db.query(Meeting).filter(
        Meeting.id == minute_id,
        Meeting.user_id == current_user.id
    ).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Không tìm thấy biên bản.")

    if not meeting.pdf_path:
        raise HTTPException(
            status_code=400,
            detail="Chưa có file PDF. Vui lòng xuất PDF trước khi ký số."
        )

    if not current_user.public_key:
        raise HTTPException(
            status_code=400,
            detail="Bạn chưa đăng ký public key. Hãy tạo cặp khóa và lưu public key trước."
        )

    # Xác thực chữ ký bằng public key đang lưu trong DB
    try:
        is_valid = signature_service.verify_signature_from_file(
            pdf_path=meeting.pdf_path,
            signature_b64=sign_data.signature,
            public_key_pem=current_user.public_key.encode("utf-8")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi xác thực chữ ký: {str(e)}")

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Chữ ký không hợp lệ. Vui lòng kiểm tra lại private key."
        )

    # Lưu chữ ký và cập nhật trạng thái
    meeting.signature = sign_data.signature
    meeting.status = MeetingStatus.SIGNED.value
    db.commit()
    db.refresh(meeting)

    return meeting


@router.get("/public-key/me")
def get_my_public_key(current_user: User = Depends(get_current_user)):
    """Kiểm tra xem user đã lưu public key chưa."""
    return {
        "has_public_key": current_user.public_key is not None,
        "public_key": current_user.public_key
    }


@router.post("/verify")
def verify_signature(
    public_key: UploadFile = File(...),
    pdf_file: UploadFile = File(...),
    signature: str = Form(...)
):
    """
    Xác thực chữ ký: upload PDF + public key PEM + signature base64.
    Trả về { valid: true/false }.
    """
    try:
        public_key_content = public_key.file.read()

        import tempfile, os, shutil
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(pdf_file.file, tmp)
            tmp_path = tmp.name

        is_valid = signature_service.verify_signature_from_file(
            pdf_path=tmp_path,
            signature_b64=signature,
            public_key_pem=public_key_content
        )
        os.unlink(tmp_path)

        return {"valid": is_valid}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
