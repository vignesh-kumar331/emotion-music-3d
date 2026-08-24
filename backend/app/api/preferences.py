from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.schemas import PreferencesUpdate, PreferencesOut, ConsentUpdate
from app.models.models import UserPreferences, ConsentRecord
import uuid, datetime

router = APIRouter(prefix="/preferences", tags=["preferences"])

@router.get("", response_model=PreferencesOut)
def get_prefs(db: Session = Depends(get_db), user = Depends(get_current_user)):
    p=db.query(UserPreferences).filter(UserPreferences.user_id==user.id).first()
    if not p:
        p=UserPreferences(user_id=user.id); db.add(p); db.commit(); db.refresh(p)
    return PreferencesOut(user_id=user.id, favorite_genres=p.favorite_genres or [], favorite_artists=p.favorite_artists or [], emotion_detection_enabled=p.emotion_detection_enabled, camera_analysis_enabled=p.camera_analysis_enabled, voice_analysis_enabled=p.voice_analysis_enabled, biometric_enabled=p.biometric_enabled, mood_history_enabled=p.mood_history_enabled, personalized_recommendations=p.personalized_recommendations, contextual_personalization=p.contextual_personalization, journal_analysis_enabled=p.journal_analysis_enabled, cultural_prefs=p.cultural_prefs or {})

@router.put("", response_model=PreferencesOut)
def update_prefs(data: PreferencesUpdate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    p=db.query(UserPreferences).filter(UserPreferences.user_id==user.id).first()
    for k,v in data.dict(exclude_unset=True).items():
        setattr(p,k,v)
    p.updated_at=datetime.datetime.utcnow()
    db.commit(); db.refresh(p)
    return PreferencesOut(user_id=user.id, favorite_genres=p.favorite_genres or [], favorite_artists=p.favorite_artists or [], emotion_detection_enabled=p.emotion_detection_enabled, camera_analysis_enabled=p.camera_analysis_enabled, voice_analysis_enabled=p.voice_analysis_enabled, biometric_enabled=p.biometric_enabled, mood_history_enabled=p.mood_history_enabled, personalized_recommendations=p.personalized_recommendations, contextual_personalization=p.contextual_personalization, journal_analysis_enabled=p.journal_analysis_enabled, cultural_prefs=p.cultural_prefs or {})

@router.post("/consent")
def set_consent(data: ConsentUpdate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    rec=ConsentRecord(user_id=user.id, signal_type=data.signal_type, granted=data.granted)
    db.add(rec)
    # also toggle preference flags
    p=db.query(UserPreferences).filter(UserPreferences.user_id==user.id).first()
    mapping={"camera":"camera_analysis_enabled","voice":"voice_analysis_enabled","biometric":"biometric_enabled","journal":"journal_analysis_enabled"}
    field=mapping.get(data.signal_type)
    if field:
        setattr(p, field, data.granted)
    db.commit()
    return {"status":"ok", "signal_type":data.signal_type, "granted":data.granted}

@router.delete("/reset")
def reset_profile(db: Session = Depends(get_db), user = Depends(get_current_user)):
    # per spec 30: reset personalization profile + delete emotion history
    from app.models.models import EmotionEvent, ListeningEvent, RecommendationFeedback
    db.query(EmotionEvent).filter(EmotionEvent.user_id==user.id).delete()
    db.query(ListeningEvent).filter(ListeningEvent.user_id==user.id).delete()
    db.query(RecommendationFeedback).filter(RecommendationFeedback.user_id==user.id).delete()
    p=db.query(UserPreferences).filter(UserPreferences.user_id==user.id).first()
    if p:
        p.favorite_genres=[]; p.favorite_artists=[]; p.cultural_prefs={}
    db.commit()
    return {"status":"reset complete", "message":"Emotional history and personalization reset."}

@router.get("/transparency")
def transparency(db: Session = Depends(get_db), user = Depends(get_current_user)):
    p=db.query(UserPreferences).filter(UserPreferences.user_id==user.id).first()
    return {
        "why_you_see_recommendations": [
            "Your selected mood" if p.emotion_detection_enabled else "Mood disabled",
            "Your listening preferences",
            "Your recent feedback",
            "Your selected activity" if p.contextual_personalization else "Context disabled",
        ],
        "data_controls": "You can disable emotion-based personalization, delete history, and export data at any time.",
        "note": "Emotion inference is probabilistic, not a diagnosis."
    }
