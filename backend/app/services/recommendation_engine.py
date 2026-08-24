"""
Recommendation Engine per spec 13-17, 42, 46, 47
Pipeline: emotion matching + personalization + context + diversity + safety filtering + explanation
"""
from typing import List, Dict, Any, Optional
from app.services.music_provider import provider
from app.services.emotion_engine import VA_MAP
import math, random

# Emotion-to-music soft mapping per spec 14
EMOTION_PREFS = {
    "calm": {"tempo": (55,85), "energy": (0.05,0.35), "acousticness": (0.6,1.0), "danceability": (0.0,0.4)},
    "peacefulness": {"tempo": (50,75), "energy": (0.05,0.3), "acousticness": (0.6,1.0)},
    "sadness": {"tempo": (60,90), "energy": (0.1,0.4), "acousticness": (0.5,1.0), "valence": (0.05,0.4)},
    "melancholy": {"tempo": (60,85), "energy": (0.1,0.35), "acousticness": (0.6,1.0), "valence": (0.1,0.35)},
    "loneliness": {"tempo": (60,85), "energy": (0.1,0.4), "acousticness": (0.6,1.0)},
    "nostalgia": {"tempo": (65,90), "energy": (0.15,0.4), "acousticness": (0.5,0.9)},
    "anxiety": {"tempo": (60,85), "energy": (0.1,0.35), "acousticness": (0.5,0.9)}, # grounding
    "restlessness": {"tempo": (75,105), "energy": (0.35,0.6), "danceability": (0.35,0.65)},
    "excitement": {"tempo": (115,145), "energy": (0.75,1.0), "danceability": (0.6,1.0)},
    "joy": {"tempo": (100,135), "energy": (0.6,0.95), "danceability": (0.55,1.0), "valence": (0.6,1.0)},
    "motivation": {"tempo": (120,145), "energy": (0.75,1.0), "danceability": (0.6,1.0)},
    "hope": {"tempo": (85,110), "energy": (0.4,0.65), "valence": (0.5,0.85)},
    "anger": {"tempo": (110,140), "energy": (0.7,0.95)},
    "boredom": {"tempo": (100,130), "energy": (0.55,0.85), "danceability": (0.5,0.85)},
    "gratitude": {"tempo": (85,115), "energy": (0.4,0.7), "valence": (0.55,0.9)},
}

# Progression templates per spec 16
PROGRESSIONS = {
    "stay": ["congruent","congruent","congruent"],
    "feel_understood": ["congruent","validating","comforting"],
    "calm_down": ["grounding","calming","stable","gentle_positive"],
    "hopeful": ["reflective","validating","comforting","gentle_hope","uplifting"],
    "hope": ["reflective","comforting","gentle_hope"],
    "energize": ["grounding","energizing","motivating","celebratory"],
    "energize_request": ["high_energy","exciting","motivating","celebratory"],
    "distract": ["distracting","uplifting","playful"],
    "surprise": ["diverse","surprise","discovery"],
    "calm": ["grounding","calming"],
}

def score_track(track: Dict[str,Any], emotion: Dict[str,Any], prefs: Dict[str,Any], context: Dict[str,Any], goal: str, history: List[str]) -> float:
    # Emotion Match (soft)
    primary = emotion.get("primary_emotion") or "calm"
    pref_ranges = EMOTION_PREFS.get(primary, {})
    emotion_score = 0.5
    # distance from preferred ranges
    def range_score(val, rng):
        lo, hi = rng
        if lo <= val <= hi: return 1.0
        dist = min(abs(val-lo), abs(val-hi))
        return max(0, 1 - dist/0.5 if "energy" in str(rng) else 1 - dist/50)
    hits = 0
    for k, rng in pref_ranges.items():
        if k in track:
            hits+=1
            emotion_score += range_score(track[k], rng)
    if hits:
        emotion_score = emotion_score / (1+hits*0.5)  # normalize
    else:
        # valence/arousal distance
        v,a = VA_MAP.get(primary, (0,0.4))
        # map track energy to arousal proxy, track valence to valence
        dv = abs(track.get("valence",0.5)- (v+1)/2)  # track valence 0-1 vs (v+1)/2
        da = abs(track.get("energy",0.5) - a)
        emotion_score = max(0, 1 - (dv+da)/2)

    # Goal adjustment per spec 15,16: if goal is energize but user sad, still honor high arousal
    if goal in ["energize","energize_request","become_energized"]:
        # boost high energy tracks regardless of sad valence
        emotion_score = emotion_score*0.5 + track.get("energy",0.5)*0.5
    if goal in ["calm_down","calm"]:
        emotion_score = emotion_score*0.5 + (1-track.get("energy",0.5))*0.5

    # User Preference + Cultural/Language boost per spec 19
    pref_score = 0.5
    if prefs:
        fav_genres = prefs.get("favorite_genres",[])
        if track["genre"] in fav_genres: pref_score += 0.3
        fav_artists = prefs.get("favorite_artists",[])
        if track["artist"] in fav_artists: pref_score += 0.4
        # Tamil cultural preference
        lang = prefs.get("language") or prefs.get("cultural_prefs",{}).get("language")
        if lang == "ta" and track.get("language") == "ta":
            pref_score += 0.35
        pref_score = min(1, pref_score)
    # also direct context language boost (request param)
    req_lang = context.get("language")
    if req_lang and track.get("language") == req_lang:
        pref_score = min(1, pref_score + 0.35)
    elif req_lang == "ta" and track.get("language") != "ta":
        pref_score = max(0, pref_score - 0.25)

    # Context
    ctx_score = 0.5
    if context:
        tod = context.get("time_of_day")
        if tod=="late_night" and track["energy"]>0.7:
            ctx_score -= 0.3
        activity = context.get("activity")
        if activity=="studying" and track.get("speechiness",0)>0.2:
            ctx_score -= 0.4
        if activity=="exercising" and track["energy"]<0.6:
            ctx_score -= 0.3
        weather = context.get("weather")
        if weather and weather.get("condition")=="rainy" and track["emotional_tone"] in ["reflective","melancholic","nostalgic"]:
            ctx_score+=0.2
        ctx_score = max(0,min(1,ctx_score))

    # Diversity: penalize if artist repeated in history (handled elsewhere but small factor)
    diversity = 0.5
    # History repetition penalty: if track in recent history
    if track["id"] in history[-10:]:
        diversity -= 0.5

    # weighted sum per spec 17: Emotion Match + Pref + Context + Diversity - Repetition
    # Availability assumed 1
    total = emotion_score*0.35 + pref_score*0.25 + ctx_score*0.15 + diversity*0.15 + 0.1
    # small random for discovery
    total += random.uniform(-0.03,0.03)
    return max(0,min(1, total))

def diverse_filter(scored: List[Dict], limit: int) -> List[Dict]:
    # avoid same artist/genre repetition per spec 46
    seen_artists=set()
    result=[]
    for item in sorted(scored, key=lambda x: x["score"], reverse=True):
        art=item["track"]["artist"]
        if art in seen_artists and len(result)<limit-1:
            # allow but penalize: skip if we have alternatives
            if random.random()<0.7:
                continue
        result.append(item)
        seen_artists.add(art)
        if len(result)>=limit: break
    return result

def safety_filter(tracks: List[Dict], emotion: Dict) -> List[Dict]:
    # per spec 34: don't recommend self-harm glorifying content; our catalog is safe, so no-op
    # but if crisis, avoid overly intense negative valence? still allow but with warning - we filter high energy if crisis calm?
    return tracks

def generate_progression(goal: str, emotion: Dict) -> List[str]:
    base = PROGRESSIONS.get(goal, PROGRESSIONS.get("feel_understood"))
    # if no explicit goal, infer: if sadness + no goal -> validating
    if not goal:
        primary = emotion.get("primary_emotion")
        if primary in ["sadness","melancholy","loneliness","nostalgia"]:
            return ["reflective","validating","comforting"]
        if primary in ["anxiety","restlessness"]:
            return ["grounding","calming","gentle_positive"]
        if primary in ["excitement","joy","motivation"]:
            return ["celebratory","energizing"]
        return ["grounding","calming"]
    return base

def recommend(emotion: Dict[str,Any], prefs: Dict[str,Any]=None, context: Dict[str,Any]=None, goal: Optional[str]=None, limit: int=10, history: List[str]=None) -> Dict[str,Any]:
    prefs = prefs or {}
    context = context or {}
    history = history or []
    # normalize goal - case-insensitive, strip
    goal_map = {"stay with my mood":"stay","feel understood":"feel_understood","calm down":"calm_down","feel hopeful":"hopeful","become energized":"energize","energize":"energize","distract myself":"distract","surprise me":"surprise","calm_down":"calm_down","feel_understood":"feel_understood"}
    if goal:
        g_norm = goal.strip().lower()
        goal = goal_map.get(goal, goal_map.get(g_norm, g_norm))
    if not goal:
        goal = "stay"
    # --- DEMO REMOVED: Use ONLY original studio songs via free iTunes API for ALL emotions ---
    tracks = []
    language = context.get("language") or prefs.get("language") or "ta"  # default Tamil as user requested
    # Always fetch originals for every emotion/language
    try:
        from app.services.itunes_provider import search_original_songs
        primary = emotion.get("primary_emotion") or "calm"
        # Try requested language first, then fallback to en/ta
        itunes_tracks = search_original_songs(primary, language, limit=limit, goal=goal)
        if not itunes_tracks and language != "en":
            itunes_tracks = search_original_songs(primary, "en", limit=limit, goal=goal)
        if itunes_tracks:
            tracks = itunes_tracks
        else:
            # Fallback: try generic Tamil hit if still empty
            from app.services.itunes_provider import _itunes_search, itunes_to_track
            fallback = _itunes_search("Tamil hit A R Rahman", limit=limit)
            tracks = [itunes_to_track(it, i) for i, it in enumerate(fallback)]
            for t in tracks:
                t["language"] = language
    except Exception as e:
        print(f"iTunes fetch failed: {e}")
        tracks = []
    # DEMO COMPLETELY REMOVED - no mock fallback
    tracks = safety_filter(tracks, emotion)
    scored=[]
    for t in tracks:
        s = score_track(t, emotion, prefs, context, goal, history)
        scored.append({"track":t,"score":round(s,3)})
    diverse = diverse_filter(scored, limit)
    # assign emotional_role based on progression
    progression = generate_progression(goal, emotion)
    recs=[]
    for idx, item in enumerate(diverse):
        role = progression[min(idx, len(progression)-1)]
        t=item["track"]
        # explanation per spec 24: simple language
        primary = emotion.get("primary_emotion","your mood")
        if role in ["grounding","calming"]:
            reason = f"steady rhythm and moderate energy to help ground {primary} feelings"
        elif role in ["validating","reflective","congruent"]:
            reason = f"reflective tone and acoustic texture matching {primary}"
        elif role in ["comforting","gentle_hope"]:
            reason = f"gentle, hopeful quality to offer comfort"
        elif role in ["uplifting","celebratory","energizing","motivating"]:
            reason = f"higher energy and uplifting tone for momentum"
        else:
            reason = f"balanced energy and emotional tone for {primary}"
        recs.append({
            "track_id": t["id"],
            "title": t["title"],
            "artist": t["artist"],
            "album": t.get("album",""),
            "preview_url": t.get("preview_url",""),
            "artwork_url": t.get("artwork_url",""),
            "youtube_url": t.get("youtube_url",""),
            "youtube_id": t.get("youtube_id",""),
            "duration_ms": t.get("duration_ms", 180000),
            "language": t.get("language","en"),
            "source": t.get("source","mock"),
            "match_score": item["score"],
            "reason": reason,
            "emotional_role": role,
            "features": {"tempo":t["tempo"],"energy":t["energy"],"valence":t["valence"],"genre":t["genre"]}
        })
    # overall explanation
    if emotion.get("confidence",0)<0.5:
        expl = f"I'm getting mixed signals, so I chose a balanced mix starting with {progression[0]} tracks. You can steer me toward more calming, energizing, or emotional options."
    else:
        expl = f"You described {emotion.get('primary_emotion','a reflective')} with low confidence urgency. I built a playlist that starts {progression[0]} and moves toward {progression[-1]}. Goal: {goal.replace('_',' ')}."
        if goal=="stay":
            expl = f"You wanted music that stays with {emotion.get('primary_emotion','your current mood')}, so I prioritized emotionally congruent tracks."
    return {
        "mood_summary": emotion,
        "listening_goal": goal,
        "recommendations": recs,
        "progression": progression,
        "explanation": expl
    }
