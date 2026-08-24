from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import enum

# Auth
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str]=None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: str
    display_name: Optional[str]
    created_at: datetime
    class Config: from_attributes=True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# Emotion representation per spec 3,4,5
class EmotionScore(BaseModel):
    label: str
    score: float = Field(ge=0, le=1)

class EmotionState(BaseModel):
    primary_emotion: Optional[str]=None
    secondary_emotions: List[str]=[]
    valence: float = Field(ge=-1, le=1)
    arousal: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    emotions: List[EmotionScore]=[]

class EmotionSignalIn(BaseModel):
    source: str # text, voice, face, biometric, manual
    text: Optional[str]=None
    valence: Optional[float]=None
    arousal: Optional[float]=None
    emotions: Optional[List[EmotionScore]]=None
    confidence: Optional[float]=None
    # for voice/face raw features optional
    raw: Optional[Dict[str,Any]]=None

class EmotionFusionRequest(BaseModel):
    signals: List[EmotionSignalIn]
    manual_selection: Optional[EmotionState]=None
    context: Optional[Dict[str,Any]]=None # time, weather, activity

class EmotionFusionResponse(BaseModel):
    fused: EmotionState
    contributions: Dict[str,float]

class TextAnalyzeRequest(BaseModel):
    text: str
    include_safety: bool = True

class TextAnalyzeResponse(BaseModel):
    emotion: EmotionState
    intent: str
    safety: Dict[str,Any]

# Music
class TrackOut(BaseModel):
    track_id: str
    title: str
    artist: str
    album: Optional[str]
    genre: Optional[str]
    duration_ms: Optional[int]
    features: Optional[Dict[str,Any]]=None
    class Config: from_attributes=True

class RecommendationRequest(BaseModel):
    emotion: Optional[EmotionState]=None
    text: Optional[str]=None # alternative to emotion: free text
    listening_goal: Optional[str]=None # stay, feel_understood, calm_down, hopeful, energize, distract, surprise, progression
    activity: Optional[str]=None
    weather: Optional[Dict[str,Any]]=None
    time_of_day: Optional[str]=None
    language: Optional[str]=None # en, ta, ja etc — respects cultural_prefs per spec 19
    limit: int = 10
    include_explanation: bool = True

class RecommendationItem(BaseModel):
    track_id: str
    title: str
    artist: str
    album: Optional[str]=None
    preview_url: Optional[str]=None
    artwork_url: Optional[str]=None
    youtube_url: Optional[str]=None
    youtube_id: Optional[str]=None
    duration_ms: Optional[int]=None
    language: Optional[str]=None
    source: Optional[str]=None
    match_score: float
    reason: str
    emotional_role: str
    features: Optional[Dict[str,Any]]=None

class RecommendationResponse(BaseModel):
    mood_summary: EmotionState
    listening_goal: str
    recommendations: List[RecommendationItem]
    progression: List[str]
    explanation: str

# Journal
class JournalCreate(BaseModel):
    text: str
    mood: Optional[str]=None
    intensity: Optional[float]=None
    tags: List[str]=[]
    analyze: bool=False

class JournalOut(BaseModel):
    id: str
    timestamp: datetime
    text: str
    mood: Optional[str]
    intensity: Optional[float]
    valence: Optional[float]
    arousal: Optional[float]
    tags: List[str]
    class Config: from_attributes=True

# Preferences & Consent
class PreferencesUpdate(BaseModel):
    favorite_genres: Optional[List[str]]=None
    favorite_artists: Optional[List[str]]=None
    emotion_detection_enabled: Optional[bool]=None
    camera_analysis_enabled: Optional[bool]=None
    voice_analysis_enabled: Optional[bool]=None
    biometric_enabled: Optional[bool]=None
    mood_history_enabled: Optional[bool]=None
    personalized_recommendations: Optional[bool]=None
    contextual_personalization: Optional[bool]=None
    journal_analysis_enabled: Optional[bool]=None
    cultural_prefs: Optional[Dict[str,Any]]=None

class PreferencesOut(BaseModel):
    user_id: str
    favorite_genres: List[str]
    favorite_artists: List[str]
    emotion_detection_enabled: bool
    camera_analysis_enabled: bool
    voice_analysis_enabled: bool
    biometric_enabled: bool
    mood_history_enabled: bool
    personalized_recommendations: bool
    contextual_personalization: bool
    journal_analysis_enabled: bool
    cultural_prefs: Dict[str,Any]
    class Config: from_attributes=True

class ConsentUpdate(BaseModel):
    signal_type: str
    granted: bool

# Feedback
class FeedbackCreate(BaseModel):
    track_id: str
    playlist_id: Optional[str]=None
    feedback_type: str
    meta: Optional[Dict[str,Any]]=None

# Playlist
class PlaylistOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    progression: List[str]
    listening_goal: Optional[str]
    mood_summary: Optional[Dict[str,Any]]
    track_ids: List[str]
    created_at: datetime
    class Config: from_attributes=True
