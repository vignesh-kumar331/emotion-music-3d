"""
Emotion Engine per spec sections 3-12, 36, 37
- Continuous valence/arousal + discrete taxonomy
- Text analysis (keyword + sentiment + intensity + negation + mixed emotions)
- Voice/Face/Biometric stubs (uncertain signals)
- Signal fusion with priority weighting
- Confidence handling & ambiguity detection
"""
import re
from typing import List, Dict, Any, Tuple

# Spec 4 taxonomy
PRIMARY_EMOTIONS = ["joy","sadness","anger","fear","surprise","disgust"]
EXTENDED = ["calm","anxiety","excitement","contentment","loneliness","nostalgia","melancholy","hope","frustration","restlessness","boredom","gratitude","anticipation","confidence","tenderness","relief","motivation","peacefulness"]
TAXONOMY = set(PRIMARY_EMOTIONS + EXTENDED)

# Reference VA per spec 3.1 examples
VA_MAP = {
    "sadness": (-0.7, 0.3),
    "melancholy": (-0.6, 0.25),
    "loneliness": (-0.6, 0.3),
    "excitement": (0.8, 0.9),
    "joy": (0.8, 0.7),
    "calm": (0.5, 0.2),
    "peacefulness": (0.6, 0.15),
    "contentment": (0.6, 0.3),
    "anger": (-0.7, 0.9),
    "frustration": (-0.5, 0.75),
    "fear": (-0.6, 0.85),
    "anxiety": (-0.5, 0.75),
    "restlessness": (-0.25, 0.72),
    "boredom": (-0.3, 0.2),
    "nostalgia": (-0.1, 0.35),
    "hope": (0.4, 0.5),
    "gratitude": (0.7, 0.4),
    "anticipation": (0.5, 0.65),
    "confidence": (0.6, 0.6),
    "tenderness": (0.5, 0.3),
    "relief": (0.6, 0.35),
    "motivation": (0.65, 0.85),
    "surprise": (0.2, 0.8),
    "disgust": (-0.6, 0.6),
}

INTENSITY_MODIFIERS = {"very":1.2,"really":1.2,"extremely":1.3,"so":1.15,"quite":1.1,"a bit":0.85,"slightly":0.7,"somewhat":0.85,"kinda":0.85,"kind of":0.85}
NEGATIONS = {"not","no","never","n't","dont","don't","isn't","arent","aren't","wasn't","weren't"}

SAFETY_PATTERNS = [
    r"kill myself", r"suicide", r"self.?harm", r"hurt myself", r"want to die", r"end my life", r"can't stay safe", r"better off dead", r"plan to (hurt|kill)",
    r"immediate danger", r"harm (someone|another|others)", r"intent to harm"
]

KEYWORD_TO_EMOTION = {
    "sad": "sadness", "down": "sadness", "depressed": "sadness", "exhausted": "sadness", "lonely": "loneliness", "alone": "loneliness",
    "angry": "anger", "mad": "anger", "furious": "anger", "irritated": "frustration", "frustrated": "frustration",
    "anxious": "anxiety", "anxiety": "anxiety", "nervous": "anxiety", "worried": "anxiety", "restless": "restlessness",
    "bored": "boredom", "calm": "calm", "peaceful": "peacefulness", "content": "contentment",
    "excited": "excitement", "exciting": "excitement", "joyful": "joy", "happy": "joy", "elated": "joy", "grateful": "gratitude",
    "hopeful": "hope", "hope": "hope", "nostalgic": "nostalgia", "nostalgia": "nostalgia", "melancholy": "melancholy",
    "motivated": "motivation", "motivating": "motivation", "confident": "confidence", "tender": "tenderness",
    "relieved": "relief", "relief": "relief", "energetic": "excitement", "drained": "sadness", "terrible day":"sadness",
    "fear": "fear", "afraid": "fear", "surprised": "surprise"
}

def detect_safety(text: str) -> Dict[str,Any]:
    low = text.lower()
    for pat in SAFETY_PATTERNS:
        if re.search(pat, low):
            return {"is_crisis": True, "severity":"high", "matched_pattern": pat, "reason":"Safety language detected"}
    # hopelessness without explicit self-harm -> medium
    if re.search(r"hopeless|no point|no reason to live|can't go on", low):
        return {"is_crisis": False, "severity":"medium", "reason":"Hopelessness language"}
    return {"is_crisis": False, "severity":"low", "reason": None}

def analyze_text(text: str) -> Dict[str,Any]:
    """
    Returns EmotionState dict + intent + safety per spec 6.1, 37
    Prioritize explicit statements.
    """
    safety = detect_safety(text)
    low = text.lower().strip()
    if not low:
        return {"valence":0.0,"arousal":0.3,"confidence":0.2,"emotions":[],"primary":None,"intent":"GENERAL_CONVERSATION","safety":safety}

    # Intent classification per 37
    intent = "MOOD_REPORT"
    if any(x in low for x in ["play", "recommend", "playlist", "song", "music"]):
        if "playlist" in low: intent="PLAYLIST_REQUEST"
        else: intent="MUSIC_REQUEST"
    if re.search(r"journal|today i", low): intent="JOURNAL_ENTRY"
    if any(x in low for x in ["like","dislike","skip","more like","less like","doesn't match","matches my mood"]): intent="FEEDBACK"
    if safety["is_crisis"]: intent="SAFETY_SIGNAL"
    if re.search(r"i (feel|am|m feeling)", low): intent="MOOD_REPORT"

    # Negation + intensity windows
    tokens = re.findall(r"\w+|\S", low)
    scores: Dict[str,float] = {}
    # explicit label priority: if user says "I'm happy" prioritize joy
    explicit = None
    m = re.search(r"i('m| am) (really |very |so |quite |extremely )?(happy|joyful|sad|angry|anxious|excited|calm|lonely|nostalgic|hopeful|frustrated|restless|bored|grateful|confident|motivated|peaceful|content)", low)
    if m:
        label = KEYWORD_TO_EMOTION.get(m.group(3), m.group(3))
        explicit = label
        scores[label] = 0.85

    # scan keywords
    for kw, emo in KEYWORD_TO_EMOTION.items():
        if kw in low:
            # check negation within 3 tokens before
            idx = low.find(kw)
            window = low[max(0, idx-20):idx]
            negated = any(n in window for n in NEGATIONS)
            val = 0.65
            # intensity modifier
            for mod, mult in INTENSITY_MODIFIERS.items():
                if mod in window:
                    val *= mult
                    break
            if negated:
                val *= 0.25  # heavily reduce
            scores[emo] = max(scores.get(emo,0), min(val, 0.92))

    # handle mixed: "sad but also hopeful"
    if "but also" in low or "and also" in low or "while" in low:
        # boost secondary detection already covered; just keep both
        pass
    if "don't know what i'm feeling" in low or "don't know how i feel" in low:
        return {"valence":0.0,"arousal":0.4,"confidence":0.25,"emotions":[],"primary":None,"intent":intent,"safety":safety,"ambiguous":True}

    if not scores:
        # neutral sentiment fallback
        if any(w in low for w in ["terrible","awful","rough","bad","hard"]):
            scores["sadness"]=0.55
        elif any(w in low for w in ["great","wonderful","amazing","good","love"]):
            scores["joy"]=0.60
        else:
            return {"valence":0.0,"arousal":0.4,"confidence":0.35,"emotions":[],"primary":None,"intent":intent,"safety":safety}

    # sort
    sorted_em = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_em[0][0]
    # compute valence/arousal weighted
    vs, ars, wsum = 0,0,0
    for emo, sc in sorted_em:
        v,a = VA_MAP.get(emo, (0,0.5))
        vs += v*sc
        ars += a*sc
        wsum += sc
    valence = max(-1, min(1, vs/wsum if wsum else 0))
    arousal = max(0, min(1, ars/wsum if wsum else 0.4))
    confidence = min(0.95, 0.55 + 0.15*len(sorted_em) + 0.1*(1 if explicit else 0))
    # if mixed emotions with conflicting valence, reduce confidence
    valences = [VA_MAP.get(e,(0,0))[0] for e,_ in sorted_em[:2]]
    if len(valences)==2 and valences[0]*valences[1] < 0:
        confidence *= 0.85
    emotions = [{"label":k,"score":round(v,2)} for k,v in sorted_em]
    return {"valence":round(valence,2),"arousal":round(arousal,2),"confidence":round(confidence,2),"emotions":emotions,"primary":primary,"intent":intent,"safety":safety}

def analyze_voice_stub(features: Dict[str,Any]) -> Dict[str,Any]:
    # Stub: returns uncertain estimate per spec 7
    energy = features.get("energy", 0.5)
    pitch_var = features.get("pitch_variation", 0.5)
    # map to arousal via energy
    return {"valence":0.0,"arousal":round(max(0,min(1,energy*0.8+ pitch_var*0.2)),2),"confidence":0.45,"emotions":[],"source":"voice"}

def analyze_face_stub(features: Dict[str,Any]) -> Dict[str,Any]:
    smile = features.get("smile", 0.5)
    brow = features.get("brow_movement", 0.5)
    valence = (smile - 0.5)*0.6
    return {"valence":round(valence,2),"arousal":0.4,"confidence":0.4,"emotions":[],"source":"face"}

def analyze_biometric_stub(features: Dict[str,Any]) -> Dict[str,Any]:
    hr = features.get("heart_rate", 75)
    # 60-100 normal; >100 high activation
    arousal = max(0,min(1,(hr-60)/40)) if hr else 0.4
    return {"valence":0.0,"arousal":round(arousal,2),"confidence":0.3,"emotions":[],"source":"biometric"}

FUSION_WEIGHTS = {
    "manual": 1.0,
    "text": 0.85,
    "voice": 0.45,
    "face": 0.35,
    "biometric": 0.25,
    "context": 0.3
}

def fuse_signals(signals: List[Dict[str,Any]], manual: Dict[str,Any]|None=None) -> Dict[str,Any]:
    """
    Weighted fusion per spec 11. User explicit manual highest priority.
    Each signal: {source, valence, arousal, confidence, emotions}
    """
    if manual and manual.get("primary_emotion"):
        # manual overrides heavily
        return {
            "valence": manual.get("valence",0),
            "arousal": manual.get("arousal",0.4),
            "confidence": manual.get("confidence",0.9),
            "primary_emotion": manual.get("primary_emotion"),
            "secondary_emotions": manual.get("secondary_emotions",[]),
            "emotions": [{"label": manual.get("primary_emotion"),"score":0.9}],
            "contributions": {"manual":1.0},
            "ambiguous": False
        }
    if not signals:
        return {"valence":0,"arousal":0.3,"confidence":0.3,"primary_emotion":None,"secondary_emotions":[],"emotions":[],"contributions":{},"ambiguous":True}

    # weighted avg valence/arousal
    total_w = 0
    v_sum=a_sum=0
    emotion_agg: Dict[str,float] = {}
    contrib: Dict[str,float]={}
    low_conf = False
    for s in signals:
        src = s.get("source","text")
        w = FUSION_WEIGHTS.get(src, 0.5) * s.get("confidence",0.5)
        # explicit text signal gets boost
        if src=="text" and s.get("emotions"):
            w *= 1.1
        contrib[src]=round(w,2)
        total_w += w
        v_sum += s.get("valence",0)*w
        a_sum += s.get("arousal",0.4)*w
        for e in s.get("emotions",[]):
            label = e["label"] if isinstance(e, dict) else e
            sc = e["score"] if isinstance(e, dict) else 0.5
            emotion_agg[label]= max(emotion_agg.get(label,0), sc * w)
        if s.get("confidence",0) < 0.4:
            low_conf = True
    if total_w==0:
        return {"valence":0,"arousal":0.4,"confidence":0.3,"primary_emotion":None,"secondary_emotions":[],"emotions":[],"contributions":contrib,"ambiguous":True}
    valence = v_sum/total_w
    arousal = a_sum/total_w
    # primary is max aggregated
    sorted_em = sorted(emotion_agg.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_em[0][0] if sorted_em else None
    secondary = [k for k,v in sorted_em[1:3]]
    # confidence: weighted average + penalty if disagree
    avg_conf = sum(s.get("confidence",0.5)*FUSION_WEIGHTS.get(s.get("source","text"),0.5) for s in signals)/sum(FUSION_WEIGHTS.get(s.get("source","text"),0.5) for s in signals) if signals else 0.3
    # if voice and text disagree (valence diff >0.6) reduce confidence
    valences = [s.get("valence",0) for s in signals if s.get("valence") is not None]
    if len(valences)>=2 and max(valences)-min(valences)>0.6:
        avg_conf *= 0.8
        low_conf=True
    if len(sorted_em)>=2 and len(set([VA_MAP.get(e,(0,0))[0]>0 for e,_ in sorted_em[:2]]))>1:
        avg_conf *=0.9
    confidence = max(0.2,min(0.95, avg_conf))
    ambiguous = confidence < 0.5 or low_conf
    return {
        "valence": round(max(-1,min(1,valence)),2),
        "arousal": round(max(0,min(1,arousal)),2),
        "confidence": round(confidence,2),
        "primary_emotion": primary,
        "secondary_emotions": secondary,
        "emotions": [{"label":k,"score":round(min(0.95, v/max(1,total_w)*3),2)} for k,v in sorted_em],
        "contributions": contrib,
        "ambiguous": ambiguous
    }

def crisis_response_text() -> str:
    return ("I hear that you're going through something really difficult. "
            "If you're in immediate danger or thinking about harming yourself, please reach out right now to a trusted person "
            "or a crisis helpline in your area (for example, in the US call or text 988). "
            "If you can, try to move to a safe place and let someone know how you're feeling. "
            "I'm not a medical professional, but I can stay here and help you find gentle music if you'd like — would you like that?")

