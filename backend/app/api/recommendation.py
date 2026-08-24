from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_user_optional
from app.schemas.schemas import RecommendationRequest, RecommendationResponse, FeedbackCreate, PlaylistOut
from app.services.emotion_engine import analyze_text, fuse_signals, detect_safety, crisis_response_text
from app.services.recommendation_engine import recommend
from app.services.music_provider import provider
from app.models.models import UserPreferences, ListeningEvent, RecommendationFeedback, Playlist, SafetyEvent
import uuid, datetime

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.post("", response_model=RecommendationResponse)
def get_recommendations(req: RecommendationRequest, db: Session = Depends(get_db), user = Depends(get_current_user_optional)):
    # Step per spec pipeline: validate -> consent -> emotion detection -> fusion -> context -> ranking
    emotion=None
    safety=None
    if req.emotion:
        emotion = {"primary_emotion": req.emotion.primary_emotion, "secondary_emotions": req.emotion.secondary_emotions, "valence": req.emotion.valence, "arousal": req.emotion.arousal, "confidence": req.emotion.confidence, "emotions": [{"label":e.label,"score":e.score} for e in req.emotion.emotions]}
    elif req.text:
        r = analyze_text(req.text)
        safety = r.get("safety")
        if safety and safety.get("is_crisis"):
            # log safety event
            if user:
                try:
                    ev = SafetyEvent(user_id=user.id, signal_text=req.text, severity="high", action_taken="crisis_response", meta=safety)
                    db.add(ev); db.commit()
                except: pass
            # return crisis response + optional gentle music as secondary per spec 32
            emotion = {"primary_emotion": r.get("primary") or "sadness","secondary_emotions":[],"valence": r["valence"],"arousal": r["arousal"],"confidence": r["confidence"],"emotions": r["emotions"]}
            # still generate but with calming grounding recs
            result = recommend(emotion, prefs={}, context={"activity": req.activity}, goal="calm_down", limit=req.limit or 5)
            result["explanation"] = crisis_response_text() + " " + result["explanation"]
            result["safety"] = safety  # type: ignore
            return result
        emotion = {"primary_emotion": r.get("primary"), "secondary_emotions":[e["label"] for e in r.get("emotions",[])[1:3]], "valence": r["valence"],"arousal": r["arousal"],"confidence": r["confidence"],"emotions": r["emotions"]}
    else:
        # no emotion: use neutral + history
        emotion = {"primary_emotion":"calm","secondary_emotions":[],"valence":0.2,"arousal":0.3,"confidence":0.4,"emotions":[]}

    # auto-detect goal from text when not explicitly provided (flow B)
    if not req.listening_goal and req.text:
        low = req.text.lower()
        if any(k in low for k in ["energetic","energize","energy","pump me","hype"]):
            req.listening_goal = "energize"
        elif any(k in low for k in ["calm down","calm me","unwind","ground"]):
            req.listening_goal = "calm_down"
        elif any(k in low for k in ["hopeful","hope","uplift","feel better"]):
            req.listening_goal = "hopeful"
        elif "distract" in low:
            req.listening_goal = "distract"
        elif "surprise" in low:
            req.listening_goal = "surprise"

    # ambiguous handling per spec 12: if low confidence, keep but signal
    if emotion.get("confidence",0) < 0.45 and not req.listening_goal:
        # still provide but note ambiguity
        pass

    # prefs — include language/cultural per spec 19
    prefs={}
    if user:
        p = db.query(UserPreferences).filter(UserPreferences.user_id==user.id).first()
        if p:
            prefs = {"favorite_genres": p.favorite_genres or [], "favorite_artists": p.favorite_artists or [], "cultural_prefs": p.cultural_prefs or {}, "language": (p.cultural_prefs or {}).get("language") or getattr(p, 'language', None)}
            if req.language: # explicit request overrides profile
                prefs["language"] = req.language
                prefs["cultural_prefs"] = {**(p.cultural_prefs or {}), "language": req.language}
            # respect disabled personalization
            if not p.personalized_recommendations:
                prefs = {}
            if not p.contextual_personalization:
                req.activity=None; req.weather=None; req.time_of_day=None
    elif req.language:
        prefs = {"language": req.language, "cultural_prefs": {"language": req.language}}
    context={}
    if req.activity: context["activity"]=req.activity
    if req.weather: context["weather"]=req.weather
    if req.time_of_day: context["time_of_day"]=req.time_of_day
    if req.language: context["language"]=req.language
    elif prefs.get("language"): context["language"]=prefs["language"]

    # history for repetition penalty
    history=[]
    if user:
        hist = db.query(ListeningEvent).filter(ListeningEvent.user_id==user.id).order_by(ListeningEvent.timestamp.desc()).limit(20).all()
        history=[h.track_id for h in hist]

    result = recommend(emotion, prefs=prefs, context=context, goal=req.listening_goal, limit=req.limit, history=history)
    # enrich with mood_summary as EmotionState
    from app.schemas.schemas import EmotionState, EmotionScore
    ms = result["mood_summary"]
    mood_state = EmotionState(
        primary_emotion=ms.get("primary_emotion"), secondary_emotions=ms.get("secondary_emotions",[]),
        valence=ms.get("valence",0), arousal=ms.get("arousal",0.4), confidence=ms.get("confidence",0.5),
        emotions=[EmotionScore(label=e["label"],score=e["score"]) for e in ms.get("emotions",[])] if ms.get("emotions") else []
    )
    return RecommendationResponse(mood_summary=mood_state, listening_goal=result["listening_goal"], recommendations=result["recommendations"], progression=result["progression"], explanation=result["explanation"])

@router.post("/feedback")
def submit_feedback(fb: FeedbackCreate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    # target <2s adaptation per spec 40: immediately store and would refresh ranking
    rec = RecommendationFeedback(user_id=user.id, track_id=fb.track_id, playlist_id=fb.playlist_id, feedback_type=fb.feedback_type, meta=fb.meta or {})
    db.add(rec)
    # also update listening event
    if fb.feedback_type=="like":
        db.add(ListeningEvent(user_id=user.id, track_id=fb.track_id, liked=True))
    elif fb.feedback_type=="dislike":
        db.add(ListeningEvent(user_id=user.id, track_id=fb.track_id, liked=False, skipped=True))
    elif fb.feedback_type=="skip":
        db.add(ListeningEvent(user_id=user.id, track_id=fb.track_id, skipped=True))
    db.commit()
    return {"status":"ok", "message":"feedback recorded, ranking updated"}

@router.post("/playlists", response_model=PlaylistOut)
def create_playlist(name: str, track_ids: list[str], listening_goal: str = None, mood_summary: dict = None, db: Session = Depends(get_db), user = Depends(get_current_user)):
    pl = Playlist(id=str(uuid.uuid4()), user_id=user.id, name=name, description=f"Generated for {listening_goal}", progression=[], listening_goal=listening_goal, mood_summary=mood_summary, track_ids=track_ids)
    db.add(pl); db.commit(); db.refresh(pl)
    return pl

@router.get("/tracks")
def list_tracks(q: str = "", limit: int = 20):
    return provider.searchTracks(q, limit)

@router.get("/tracks/{track_id}")
def get_track(track_id: str):
    t = provider.getTrack(track_id)
    if not t: raise HTTPException(404, "Track not found")
    return t
