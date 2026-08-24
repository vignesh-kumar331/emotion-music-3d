from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.schemas import JournalCreate, JournalOut
from app.models.models import MoodJournal
from app.services.emotion_engine import analyze_text
import uuid, datetime

router = APIRouter(prefix="/journal", tags=["journal"])

@router.post("", response_model=JournalOut)
def create_entry(data: JournalCreate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    # per spec 26: only analyze if user enabled and requested
    valence=arousal=None
    mood=data.mood
    if data.analyze and user.preferences and user.preferences.journal_analysis_enabled:
        res=analyze_text(data.text)
        valence=res["valence"]; arousal=res["arousal"]
        if not mood:
            mood=res.get("primary")
    entry = MoodJournal(id=str(uuid.uuid4()), user_id=user.id, text=data.text, mood=mood, intensity=data.intensity, valence=valence, arousal=arousal, tags=data.tags)
    db.add(entry); db.commit(); db.refresh(entry)
    return entry

@router.get("", response_model=list[JournalOut])
def list_entries(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return db.query(MoodJournal).filter(MoodJournal.user_id==user.id).order_by(MoodJournal.timestamp.desc()).all()

@router.get("/insights")
def insights(db: Session = Depends(get_db), user = Depends(get_current_user)):
    # per spec 27: correlation without causal claims
    journals = db.query(MoodJournal).filter(MoodJournal.user_id==user.id).all()
    if not journals:
        return {"message":"Not enough data for insights yet. Journal more to see patterns."}
    # simple aggregation: mood frequency
    from collections import Counter
    moods=[j.mood for j in journals if j.mood]
    cnt=Counter(moods)
    return {
        "total_entries": len(journals),
        "mood_distribution": dict(cnt),
        "note": "Your listening history shows a pattern; this is correlation, not causation."
    }

@router.delete("/{entry_id}")
def delete_entry(entry_id: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    j=db.query(MoodJournal).filter(MoodJournal.id==entry_id, MoodJournal.user_id==user.id).first()
    if not j: raise HTTPException(404,"Not found")
    db.delete(j); db.commit()
    return {"status":"deleted"}

@router.get("/export")
def export_data(db: Session = Depends(get_db), user = Depends(get_current_user)):
    # per spec 28: export for professional sharing, requires explicit call
    journals=db.query(MoodJournal).filter(MoodJournal.user_id==user.id).all()
    return {"user_id": user.id, "exported_at": datetime.datetime.utcnow().isoformat(), "journals":[{"date":j.timestamp.isoformat(),"mood":j.mood,"intensity":j.intensity,"text":j.text,"tags":j.tags} for j in journals], "disclaimer":"Shared only with your explicit consent. This is not a medical diagnosis."}
