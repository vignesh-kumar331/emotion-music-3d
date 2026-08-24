import uuid, datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # relationships
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all,delete-orphan")
    consents = relationship("ConsentRecord", back_populates="user", cascade="all,delete-orphan")
    emotion_events = relationship("EmotionEvent", back_populates="user", cascade="all,delete-orphan")
    journals = relationship("MoodJournal", back_populates="user", cascade="all,delete-orphan")
    playlists = relationship("Playlist", back_populates="user", cascade="all,delete-orphan")

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    favorite_genres = Column(JSON, default=list)
    favorite_artists = Column(JSON, default=list)
    language = Column(String, default="en")
    cultural_prefs = Column(JSON, default=dict)
    # toggles per spec section 30
    emotion_detection_enabled = Column(Boolean, default=True)
    camera_analysis_enabled = Column(Boolean, default=False)
    voice_analysis_enabled = Column(Boolean, default=False)
    biometric_enabled = Column(Boolean, default=False)
    mood_history_enabled = Column(Boolean, default=True)
    personalized_recommendations = Column(Boolean, default=True)
    contextual_personalization = Column(Boolean, default=True)
    journal_analysis_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user = relationship("User", back_populates="preferences")

class ConsentRecord(Base):
    __tablename__ = "consent_records"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    signal_type = Column(String) # camera, voice, biometric, weather, journal
    granted = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="consents")

class EmotionEvent(Base):
    __tablename__ = "emotion_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    primary_emotion = Column(String)
    secondary_emotions = Column(JSON, default=list)
    valence = Column(Float)
    arousal = Column(Float)
    confidence = Column(Float)
    source = Column(String) # manual, text, voice, face, biometric, fused
    raw_signals = Column(JSON, default=dict)
    user = relationship("User", back_populates="emotion_events")
    signals = relationship("EmotionSignal", back_populates="event", cascade="all,delete-orphan")

class EmotionSignal(Base):
    __tablename__ = "emotion_signals"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey("emotion_events.id"))
    source = Column(String)
    valence = Column(Float)
    arousal = Column(Float)
    confidence = Column(Float)
    emotions = Column(JSON, default=list)
    event = relationship("EmotionEvent", back_populates="signals")

class Track(Base):
    __tablename__ = "tracks"
    id = Column(String, primary_key=True) # TRACK_001 style
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String)
    genre = Column(String)
    language = Column(String, default="en")
    duration_ms = Column(Integer)
    preview_url = Column(String, nullable=True)
    external_url = Column(String, nullable=True)
    features = relationship("TrackFeatures", back_populates="track", uselist=False, cascade="all,delete-orphan")

class TrackFeatures(Base):
    __tablename__ = "track_features"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    track_id = Column(String, ForeignKey("tracks.id"), unique=True)
    tempo = Column(Float) # BPM
    key = Column(Integer, nullable=True)
    mode = Column(Integer, nullable=True) # 0 minor 1 major
    energy = Column(Float)
    danceability = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    loudness = Column(Float)
    speechiness = Column(Float)
    valence = Column(Float) # musical valence
    arousal_proxy = Column(Float) # mapped from energy
    liveness = Column(Float, default=0.1)
    lyrical_themes = Column(JSON, default=list)
    emotional_tone = Column(String)
    instrumentation = Column(JSON, default=list)
    track = relationship("Track", back_populates="features")

class MoodJournal(Base):
    __tablename__ = "mood_journals"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    text = Column(Text)
    mood = Column(String, nullable=True)
    intensity = Column(Float, nullable=True)
    valence = Column(Float, nullable=True)
    arousal = Column(Float, nullable=True)
    tags = Column(JSON, default=list)
    playlist_id = Column(String, ForeignKey("playlists.id"), nullable=True)
    user = relationship("User", back_populates="journals")

class Playlist(Base):
    __tablename__ = "playlists"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    progression = Column(JSON, default=list)
    listening_goal = Column(String, nullable=True)
    mood_summary = Column(JSON, nullable=True)
    track_ids = Column(JSON, default=list) # ordered list
    user = relationship("User", back_populates="playlists")

class ListeningEvent(Base):
    __tablename__ = "listening_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    track_id = Column(String, ForeignKey("tracks.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    duration_played = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    skipped = Column(Boolean, default=False)
    liked = Column(Boolean, nullable=True)

class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    track_id = Column(String, ForeignKey("tracks.id"))
    playlist_id = Column(String, ForeignKey("playlists.id"), nullable=True)
    feedback_type = Column(String) # like, dislike, skip, save, replay, mood_match, mood_mismatch, etc
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    meta = Column(JSON, default=dict)

class SafetyEvent(Base):
    __tablename__ = "safety_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    signal_text = Column(Text)
    severity = Column(String) # low, medium, high, crisis
    action_taken = Column(String)
    meta = Column(JSON, default=dict)
