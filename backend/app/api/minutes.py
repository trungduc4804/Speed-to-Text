import shutil
import os
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.deps import get_db, get_current_user, require_role
from app.models.user import User
from app.models.meeting import Meeting, MeetingStatus
from app.schemas import MeetingCreate, MeetingResponse, MeetingUpdate, MeetingStatusUpdate, MeetingAdminResponse
from app.core.config import settings
from app.services import stt_service
from app.services.ai_service import analyze_transcript
from app.services.minute_service import MinuteService
import json


router = APIRouter()

@router.post("/", response_model=MeetingResponse)
def create_meeting(
    file: UploadFile = File(...),
    title: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["CHAIRMAN", "SECRETARY"]))
):
    # Validate file extension
    if not file.filename.lower().endswith(('.mp3', '.wav')):
        raise HTTPException(status_code=400, detail="Only .mp3 and .wav files are allowed")

    # Save file
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.AUDIO_DIR, filename)
    
    # Create directory if not exists (redundant if already done, but safe)
    os.makedirs(settings.AUDIO_DIR, exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Transcribe (Simulated for now, would be async task in production)
    transcript = stt_service.transcribe_audio(file_path)

    # Analyze with AI
    ai_result = analyze_transcript(transcript)
    action_items_str = json.dumps(ai_result["action_items"], ensure_ascii=False)

    # Normalize path for web storage (forward slashes)
    web_audio_path = file_path.replace(os.sep, "/")

    # Create DB record
    meeting = Meeting(
        title=title,
        user_id=current_user.id,
        audio_path=web_audio_path,
        transcript=transcript,
        final_content=transcript, # Default to transcript
        summary=ai_result["summary"],
        action_items=action_items_str,
        status=MeetingStatus.DRAFT.value
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting

@router.get("/", response_model=List[MeetingResponse])
def read_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Meeting).filter(Meeting.user_id == current_user.id)

    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                Meeting.title.ilike(search_fmt),
                Meeting.final_content.ilike(search_fmt)
            )
        )
    
    if status and status != 'ALL':
        query = query.filter(Meeting.status == status)
        
    if from_date:
        query = query.filter(Meeting.created_at >= from_date)
        
    if to_date:
        query = query.filter(Meeting.created_at <= to_date)

    meetings = query.order_by(Meeting.created_at.desc()).offset(skip).limit(limit).all()
    return meetings

@router.get("/admin/all", response_model=List[MeetingAdminResponse])
def read_all_meetings_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"]))
):
    query = db.query(Meeting)
    
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                Meeting.title.ilike(search_fmt),
                Meeting.final_content.ilike(search_fmt)
            )
        )
        
    if status and status != 'ALL':
        query = query.filter(Meeting.status == status)
        
    if from_date:
        query = query.filter(Meeting.created_at >= from_date)
        
    if to_date:
        query = query.filter(Meeting.created_at <= to_date)
        
    meetings = query.order_by(Meeting.created_at.desc()).offset(skip).limit(limit).all()
    
    # Map the owner info to the response
    result = []
    for m in meetings:
        # Create a dictionary from the meeting model
        m_dict = {
            "id": m.id,
            "title": m.title,
            "user_id": m.user_id,
            "audio_path": m.audio_path,
            "transcript": m.transcript,
            "final_content": m.final_content,
            "pdf_path": m.pdf_path,
            "status": m.status,
            "created_at": m.created_at,
            "owner_username": m.owner.username if m.owner else "Unknown",
            "owner_fullname": m.owner.full_name if m.owner else None
        }
        result.append(MeetingAdminResponse(**m_dict))
        
    return result


@router.get("/{minute_id}", response_model=MeetingResponse)
def read_meeting(minute_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    roles = [r.name for r in current_user.roles]
    if "ADMIN" in roles:
        meeting = db.query(Meeting).filter(Meeting.id == minute_id).first()
    else:
        meeting = db.query(Meeting).filter(Meeting.id == minute_id, Meeting.user_id == current_user.id).first()
        
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.put("/{minute_id}", response_model=MeetingResponse)
def update_meeting(minute_id: int, meeting_in: MeetingUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meeting = db.query(Meeting).filter(Meeting.id == minute_id, Meeting.user_id == current_user.id).first()
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    MinuteService.check_can_edit(meeting)
    
    meeting.final_content = meeting_in.final_content
    db.commit()
    db.refresh(meeting)
    return meeting

@router.put("/{minute_id}/status", response_model=MeetingResponse)
def update_meeting_status(minute_id: int, status_update: MeetingStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meeting = db.query(Meeting).filter(Meeting.id == minute_id).first()
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    # Anyone who is chairman or secretary can try to change status, permission is checked in the service
    return MinuteService.change_status(db, meeting, status_update.status, current_user)


@router.delete("/{minute_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(minute_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    meeting = db.query(Meeting).filter(Meeting.id == minute_id, Meeting.user_id == current_user.id).first()
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Optional: Delete files (audio.wav.txt, audio.wav, audio.mp3)
    # Be careful with paths. For now, we just delete the DB record.
    # In a real app we would cleanup storage here.
    
    db.delete(meeting)
    db.commit()
    return None

@router.post("/{minute_id}/analyze", response_model=MeetingResponse)
def analyze_meeting_content(minute_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Manually triggers AI summary and action item extraction based on the current `final_content`.
    """
    meeting = db.query(Meeting).filter(Meeting.id == minute_id, Meeting.user_id == current_user.id).first()
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    MinuteService.check_can_edit(meeting)
    
    text_to_analyze = meeting.final_content or meeting.transcript
    if not text_to_analyze:
        raise HTTPException(status_code=400, detail="Không có nội dung để phân tích.")
        
    ai_result = analyze_transcript(text_to_analyze)
    action_items_str = json.dumps(ai_result["action_items"], ensure_ascii=False)
    
    meeting.summary = ai_result["summary"]
    meeting.action_items = action_items_str
    
    db.commit()
    db.refresh(meeting)
    return meeting
