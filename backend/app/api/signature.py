from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.models.meeting import Meeting, MeetingStatus
from app.services.signature_service import SignatureService

router = APIRouter()
signature_service = SignatureService()

@router.post("/sign/{minute_id}")
def sign_pdf(minute_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Signs the PDF of the meeting.
    Returns:
    - signature (base64)
    - public_key (pem)
    - private_key (pem) - In real app, user should provide this or manage it securely.
    """
    meeting = db.query(Meeting).filter(Meeting.id == minute_id, Meeting.user_id == current_user.id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if not meeting.pdf_path:
        raise HTTPException(status_code=400, detail="PDF not generated yet. Please export PDF first.")
    
    # Generate keys (Simulation for the project)
    private_pem, public_pem = signature_service.generate_keys()
    
    # Sign
    signature = signature_service.sign_pdf(meeting.pdf_path, private_pem)
    
    # Update status
    meeting.status = MeetingStatus.SIGNED.value
    db.commit()
    
    return {
        "minute_id": minute_id,
        "signature": signature,
        "public_key": public_pem.decode('utf-8'),
        "private_key": private_pem.decode('utf-8')
    }

@router.post("/verify")
def verify_signature(
    public_key: UploadFile = File(...),
    pdf_file: UploadFile = File(...),
    signature: str = Form(...)
):
    """
    Verify upload PDF against Signature and Public Key.
    """
    try:
        public_key_content = public_key.file.read()
        
        # Save PDF to temp to read (or read in memory if service supports bytes)
        # Service takes path. Let's save temp.
        import tempfile
        import os
        import shutil
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            shutil.copyfileobj(pdf_file.file, tmp)
            tmp_path = tmp.name
            
        is_valid = signature_service.verify_signature(tmp_path, signature, public_key_content)
        
        os.unlink(tmp_path)
        
        return {"valid": is_valid}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

