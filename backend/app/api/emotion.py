from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_user_optional
from app.schemas.schemas import TextAnalyzeRequest, TextAnalyzeResponse, EmotionFusionRequest, EmotionFusionResponse, EmotionState, EmotionScore
from app.services.emotion_engine import analyze_text, fuse_signals, analyze_voice_stub, analyze_face_stub, analyze_biometric_stub
from app.models.models import EmotionEvent, EmotionSignal, ConsentRecord
from typing import Any

router = APIRouter(prefix="/emotion", tags=["emotion"])

def _to_state(fused: dict) -> EmotionState:
    return EmotionState(
        primary_emotion=fused.get("primary_emotion"),
        secondary_emotions=fused.get("secondary_emotions",[]),
        valence=fused.get("valence",0),
        arousal=fused.get("arousal",0.4),
        confidence=fused.get("confidence",0.5),
        emotions=[EmotionScore(label=e["label"], score=e["score"]) for e in fused.get("emotions",[]) if isinstance(e, dict)]
    )

@router.post("/analyze-text", response_model=TextAnalyzeResponse)
def analyze_text_endpoint(req: TextAnalyzeRequest, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    res = analyze_text(req.text)
    emotion = EmotionState(
        primary_emotion=res.get("primary"),
        secondary_emotions=[e["label"] for e in res.get("emotions",[])[1:3]] if res.get("emotions") else [],
        valence=res["valence"], arousal=res["arousal"], confidence=res["confidence"],
        emotions=[EmotionScore(label=e["label"], score=e["score"]) for e in res.get("emotions",[])]
    )
    # persist if user
    if user and user.preferences.mood_history_enabled if hasattr(user, 'preferences') and user.preferences else True:
        try:
            ev = EmotionEvent(user_id=user.id, primary_emotion=res.get("primary"), secondary_emotions=[e["label"] for e in res.get("emotions",[])[1:2]], valence=res["valence"], arousal=res["arousal"], confidence=res["confidence"], source="text", raw_signals={"text":req.text})
            db.add(ev); db.commit()
        except: pass
    return TextAnalyzeResponse(emotion=emotion, intent=res.get("intent","GENERAL_CONVERSATION"), safety=res.get("safety",{}))

@router.post("/analyze-voice")
def analyze_voice(features: dict, user = Depends(get_current_user_optional)):
    # check consent
    if user:
        # if voice not enabled, require consent - for demo allow but flag
        pass
    res = analyze_voice_stub(features)
    return res

@router.post("/analyze-face")
def analyze_face(features: dict, user = Depends(get_current_user_optional)):
    res = analyze_face_stub(features)
    return res

@router.post("/analyze-biometric")
def analyze_biometric(features: dict, user = Depends(get_current_user_optional)):
    res = analyze_biometric_stub(features)
    return res

@router.post("/fuse", response_model=EmotionFusionResponse)
def fuse(req: EmotionFusionRequest, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    signals=[]
    for s in req.signals:
        # consent check stub: if source requires consent and not granted, skip
        if user:
            pref = user.preferences
            if s.source=="voice" and pref and not pref.voice_analysis_enabled:
                continue
            if s.source=="face" and pref and not pref.camera_analysis_enabled:
                continue
            if s.source=="biometric" and pref and not pref.biometric_enabled:
                continue
        # if text provided, run analysis
        if s.source=="text" and s.text:
            r = analyze_text(s.text)
            signals.append({"source":"text","valence":r["valence"],"arousal":r["arousal"],"confidence":r["confidence"],"emotions":r["emotions"]})
        else:
            signals.append({"source": s.source, "valence": s.valence or 0, "arousal": s.arousal or 0.4, "confidence": s.confidence or 0.5, "emotions": [{"label":e.label,"score":e.score} for e in (s.emotions or [])]})
    manual = None
    if req.manual_selection:
        manual = {"primary_emotion": req.manual_selection.primary_emotion, "secondary_emotions": req.manual_selection.secondary_emotions, "valence": req.manual_selection.valence, "arousal": req.manual_selection.arousal, "confidence": req.manual_selection.confidence}
    fused = fuse_signals(signals, manual)
    # persist
    if user:
        try:
            ev = EmotionEvent(user_id=user.id, primary_emotion=fused.get("primary_emotion"), secondary_emotions=fused.get("secondary_emotions",[]), valence=fused["valence"], arousal=fused["arousal"], confidence=fused["confidence"], source="fused", raw_signals={"signals": signals})
            db.add(ev); db.commit()
        except: pass
    return EmotionFusionResponse(fused=_to_state(fused), contributions=fused.get("contributions",{}))
