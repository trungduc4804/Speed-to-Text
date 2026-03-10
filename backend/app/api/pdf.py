import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.models.meeting import Meeting
from app.core.config import settings
from app.services.pdf_service import PDFService

router = APIRouter()
pdf_service = PDFService()

@router.get("/export/{minute_id}")
def export_pdf(minute_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meeting = db.query(Meeting).filter(Meeting.id == minute_id, Meeting.user_id == current_user.id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if not meeting.final_content:
        raise HTTPException(status_code=400, detail="Meeting content is empty")

    output_filename = f"meeting_{minute_id}.pdf"
    output_path = os.path.join(settings.PDF_DIR, output_filename)
    
    # Ensure directory exists
    os.makedirs(settings.PDF_DIR, exist_ok=True)
    
    pdf_service.create_pdf(meeting.final_content, output_path, title=meeting.title)
    
    # Update DB
    meeting.pdf_path = output_path
    db.commit()
    
    return FileResponse(output_path, media_type="application/pdf", filename=output_filename)

