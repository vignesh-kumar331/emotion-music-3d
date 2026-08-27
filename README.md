# Emotion Music Companion — AI-Powered Emotion-Based Music Recommendation

**Live:** `https://vignesh-kumar331.github.io/emotion-music-3d/` · **Repo:** `https://github.com/vignesh-kumar331/emotion-music-3d` · **API Docs (local):** `http://127.0.0.1:8001/docs`

Implementation of Master System Prompt v1.0 (56 sections). Engineering choices left to team are resolved as: **FastAPI + SQLAlchemy + SQLite/Postgres + iTunes Search API (free, original studio previews) + React/Vite + Three.js 3D orb**.

> **Update:** Demo SoundHelix removed — **all 24 emotions now use original studio songs** via free iTunes API (30s previews, artwork, Tamil + English) + YouTube fallback. No demo/ringtone.

## Architecture per spec §38

```
Web/Mobile UI → API Gateway (FastAPI + CORS) → NLP Engine + Emotion Engine + User Profile → Fusion & Context → Recommendation Engine → Music API Adapter → Playlist/Feedback
```

## Quick Start

### Backend (port 8001)
```bash
cd emotion-music-app/backend
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload --port 8001
# docs: http://127.0.0.1:8001/docs
```

### Frontend (port 5174)
```bash
cd emotion-music-app/frontend
npm install
npm run dev
# http://localhost:5174
```

Demo account: `demo@emotion.app / demo123` (auto-created on register)

## Core Concepts Implemented

| Spec | Feature | Location |
|------|---------|----------|
| §3,4 | VA [-1,1]/[0,1] + confidence + 24-label taxonomy | `services/emotion_engine.py:VA_MAP` |
| §5 | Multi-emotion `primary + secondary` | `schemas` `EmotionState` |
| §6,37 | Text analysis: keywords, negation, intensity, mixed, explicit-priority | `analyze_text()` |
| §7-9 | Voice/face/biometric stubs (uncertain) | `analyze_*_stub()` |
| §10 | Manual wheel highest priority | `EmotionFusionRequest.manual_selection` |
| §11 | Weighted fusion, priority manual>text>voice>face>bio | `fuse_signals()` |
| §12 | Ambiguity → clarification question | `confidence<0.5` handling |
| §13 | Track features (tempo, energy, valence, etc) | `models.TrackFeatures`, `MOCK_CATALOG` |
| §14,15,16 | Soft emotion→music mapping, congruence vs progression | `recommendation_engine.EMOTION_PREFS`, `PROGRESSIONS` |
| §17 | Ranking: EmotionMatch+Preference+History+Context+Diversity-Repetition | `score_track()` |
| §22,20,21 | Activity/time/weather context, permission-gated | `recommend()` context |
| §23,45 | Like/dislike/skip/more_like, <2s update | `POST /recommendations/feedback` |
| §24 | Natural-language explanations, no model internals | `recommend()` expl |
| §25 | Companion conversational (clarify if needed, avoid diagnosis) | Frontend `Companion.jsx` |
| §26-28 | Journal CRUD + insights (no causal claim) + export | `api/journal.py` |
| §29,30,49 | Toggles for all signals, consent, reset, encryption-ready | `api/preferences.py` |
| §31-34 | Safety detection, crisis response, no instructions, music secondary | `detect_safety()`, `crisis_response_text()` |
| §35,36 | `MusicProvider` adapter, `EmotionEngine` abstraction | `services/*` |
| §42 | Full pipeline validation→consent→fusion→ranking→safety→explanation | `api/recommendation.py` |
| §43,44 | Structured response `mood_summary+recommendations+progression` | `RecommendationResponse` |
| §46,47 | Diversity filter, priority explicit > inferred | `diverse_filter()` |
| §48 | Transparency screen | `GET /preferences/transparency` |
| §50 | Error: low confidence fallback | `recommend()` ambiguous expl |

## API Reference (v1)

- `POST /api/v1/auth/register` `POST /api/v1/auth/login` `GET /api/v1/auth/me`
- `POST /api/v1/emotion/analyze-text` → {emotion, intent, safety}
- `POST /api/v1/emotion/fuse` → fused with contributions
- `POST /api/v1/recommendations` → {mood_summary, listening_goal, recommendations, progression, explanation}
- `POST /api/v1/recommendations/feedback`
- `GET/POST /api/v1/journal`, `GET /journal/insights`, `GET /journal/export`, `DELETE /journal/{id}`
- `GET/PUT /api/v1/preferences`, `POST /preferences/consent`, `DELETE /preferences/reset`, `GET /preferences/transparency`
- `GET /api/v1/recommendations/tracks`

## Example Flows (verified)

**A — Text Mood** `{"text":"I'm feeling lonely tonight."}` → loneliness · low valence · asks goal.

**B — Explicit energize** `{"text":"I'm angry. Give me something energetic."}` → auto goal energize → high-energy tracks (Run the City, Neon Pulse).

**C — Progression** `{"text":"I'm really down. Help me slowly feel better.", "listening_goal":"Feel hopeful"}` → reflective → comforting → gentle_hope → uplifting.

**D — Correction** User says `No, I'm actually excited` → discard anxiety, re-rank via new `/recommendations` call.

**Safety** `{"text":"I want to kill myself"}` → crisis_response + 988 + grounding playlist secondary.

## Frontend Pages

- `/` Companion: text input, manual wheel (18 emotions + intensity), goal chips, activity, analysis preview, recommendations with reason + emotional_role + match_score, feedback buttons.
- `/journal` Journal entries + correlation insights.
- `/settings` 8 toggles + consent + reset + transparency.
- `/login`

## Data Model (`models.py`)

User, UserPreferences, ConsentRecord, EmotionEvent, EmotionSignal, Track, TrackFeatures, MoodJournal, Playlist, ListeningEvent, RecommendationFeedback, SafetyEvent

## Security Notes

- JWT auth, bcrypt, CORS, rate-limit ready.
- Emotional data separate access control (mood_history_enabled).
- No selling data, no auto sharing (export requires explicit call).

## Limitations & Extensibility

- Voice/face/biometric are stubs — swap `analyze_*_stub` with real vendor (Azure, Hume, etc.) behind `EmotionEngine` interface.
- Music provider is mock 15-track catalog — replace `MockMusicProvider` with Spotify/Apple adapter implementing `MusicProvider` interface.
- Offline: frontend caches last recommendations in memory; backend seed covers offline catalog.
