import urllib.request, urllib.parse, json, ssl
ssl._create_default_https_context = ssl._create_unverified_context

ITUNES_CACHE = {}

def _itunes_search(term: str, limit: int = 8, country: str = "IN"):
    """Call iTunes Search API - free, no key, returns original 30s previews"""
    key = f"{term}:{limit}:{country}"
    if key in ITUNES_CACHE:
        return ITUNES_CACHE[key]
    try:
        q = urllib.parse.quote(term)
        url = f"https://itunes.apple.com/search?term={q}&media=music&entity=song&limit={limit}&country={country}"
        # also try US fallback if IN gives few results
        req = urllib.request.Request(url, headers={"User-Agent":"EmotionMusic/1.0"})
        with urllib.request.urlopen(req, timeout=6) as r:
            data = json.loads(r.read().decode())
            results = data.get("results", [])
            ITUNES_CACHE[key] = results
            return results
    except Exception as e:
        print(f"iTunes search failed {term}: {e}")
        return []

def itunes_to_track(item: dict, idx: int) -> dict:
    """Convert iTunes result to our Track dict"""
    # Estimate emotion features from track metadata — simple heuristic
    # Use trackName/artist for valence/energy hints
    title = item.get("trackName","")
    artist = item.get("artistName","")
    album = item.get("collectionName","")
    genre = item.get("primaryGenreName","Tamil") or "Tamil"
    duration = item.get("trackTimeMillis", 200000)
    preview = item.get("previewUrl","")
    artwork = item.get("artworkUrl100","")
    # Infer language: if artist/genre contains Tamil keywords or country IN
    lang = "ta" if any(k in (title+artist+genre).lower() for k in ["tamil","uyire","munbe","vas","kollywood"]) else "en"
    # Simple valence/energy based on genre keywords
    lower = genre.lower()
    if "hip-hop" in lower or "kuthu" in lower:
        energy, valence, tempo = 0.88, 0.78, 135
        tone = "energetic"
    elif "romantic" in lower or "melody" in lower:
        energy, valence, tempo = 0.42, 0.68, 80
        tone = "romantic"
    else:
        energy, valence, tempo = 0.5, 0.6, 95
        tone = "reflective"
    return {
        "id": f"ITUNES_{item.get('trackId', idx)}",
        "title": title,
        "artist": artist,
        "album": album,
        "genre": genre.lower().replace(" ", "_"),
        "language": "ta" if "tamil" in term_hint(title) else lang,
        "duration_ms": duration,
        "tempo": tempo,
        "energy": energy,
        "danceability": 0.6 if energy>0.6 else 0.35,
        "acousticness": 0.4,
        "instrumentalness": 0.05,
        "loudness": -6,
        "speechiness": 0.04,
        "valence": valence,
        "emotional_tone": tone,
        "lyrical_themes": [genre],
        "instrumentation": ["vocal","strings"],
        "preview_url": preview,
        "artwork_url": artwork,
        "youtube_url": "",
        "youtube_id": "",
        "source": "itunes"
    }

def term_hint(title: str) -> str:
    return title.lower()

def search_original_songs(emotion: str, language: str, limit: int = 8, goal: str = ""):
    """Build search terms for original songs via iTunes - ALL 24 emotions mapped to original Tamil/English masters"""
    # Comprehensive mapping per spec 4 - every emotion has original studio query
    ta_map = {
        "joy": ["Tamil happy Anirudh", "Kummi Paattu Kumki D Imman"],
        "sadness": ["Uyire Bombay A R Rahman", "Munbe Vaa Sillunu Oru Kadhal", "Ennai Kaanavillaiye Kadhal Konden"],
        "anger": ["Aaluma Doluma Vedalam Anirudh", "Vaathi Coming Master"],
        "fear": ["Tamil thriller Anirudh", "Tamil intense BGM"],
        "surprise": ["Tamil surprise hit", "Tamil festival song"],
        "disgust": ["Tamil intense Anirudh", "Tamil mass"],
        "calm": ["Kanmani Anbodu Guna Ilaiyaraaja", "Narumugaye Iruvar"],
        "anxiety": ["Kanmani Anbodu Guna", "Tamil calm Ilaiyaraaja"],
        "excitement": ["Aaluma Doluma Vedalam", "Oorvasi Oorvasi Kadhalan A R Rahman", "Vaathi Coming"],
        "contentment": ["Vaseegara Minnale Harris Jayaraj", "Munbe Vaa"],
        "loneliness": ["Uyire Uyire Bombay", "Marakkavillaye Enna Solla Pogirai"],
        "nostalgia": ["Kaadhal Rojave Roja S P Balasubrahmanyam", "Poongatrile Uyire"],
        "melancholy": ["Ennai Kaanavillaiye Kadhal Konden Yuvan", "Uyire Bombay"],
        "hope": ["Munbe Vaa Sillunu Oru Kadhal", "Vaseegara Minnale"],
        "frustration": ["Aaluma Doluma Vedalam", "Tamil mass beat"],
        "restlessness": ["Vaathi Coming Master", "Oorvasi Oorvasi"],
        "boredom": ["Kummi Paattu Kumki", "Tamil folk D Imman"],
        "gratitude": ["Narumugaye Iruvar Bombay Jayashri", "Tamil devotional"],
        "anticipation": ["Tamil energetic Anirudh", "Tamil festival"],
        "confidence": ["Vaathi Coming Master Anirudh", "Tamil mass"],
        "tenderness": ["Vaseegara Minnale", "Munbe Vaa"],
        "relief": ["Kanmani Anbodu Guna", "Narumugaye"],
        "motivation": ["Vaathi Coming Master", "Aaluma Doluma Vedalam", "Kummi Paattu"],
        "peacefulness": ["Narumugaye Iruvar", "Kanmani Anbodu Guna Ilaiyaraaja"],
    }
    en_map = {
        "joy": ["happy pop", "joyful upbeat"],
        "sadness": ["sad acoustic", "melancholy piano"],
        "anger": ["angry rock energetic", "intense"],
        "fear": ["dark ambient thriller", "suspense"],
        "surprise": ["surprise pop", "upbeat surprise"],
        "disgust": ["intense rock"],
        "calm": ["calm ambient", "peaceful acoustic"],
        "anxiety": ["calm anxiety relief", "grounding ambient"],
        "excitement": ["exciting dance energetic", "party"],
        "contentment": ["content acoustic", "warm folk"],
        "loneliness": ["lonely sad", "introspective"],
        "nostalgia": ["nostalgic 80s", "retro"],
        "melancholy": ["melancholic indie", "sad reflective"],
        "hope": ["hopeful uplifting", "inspiring"],
        "frustration": ["intense frustration rock"],
        "restlessness": ["restless energetic"],
        "boredom": ["fun energetic pop"],
        "gratitude": ["grateful warm", "thankful"],
        "anticipation": ["anticipation energetic", "exciting"],
        "confidence": ["confident powerful", "motivational"],
        "tenderness": ["tender romantic", "soft love"],
        "relief": ["relief calm", "peaceful"],
        "motivation": ["motivational energetic", "workout"],
        "peacefulness": ["peaceful ambient", "calm meditation"],
    }
    terms = []
    if language == "ta":
        terms = ta_map.get(emotion, [f"Tamil {emotion} A R Rahman", "Tamil hit"])
        # goal can further refine
        if goal == "energize" and emotion in ["sadness","melancholy"]:
            terms = ["Aaluma Doluma Vedalam", "Vaathi Coming Master"]
        elif goal == "calm_down":
            terms = ["Kanmani Anbodu Guna", "Narumugaye Iruvar"]
    else:
        # English or auto - use en map, also consider goal
        base = en_map.get(emotion, [f"{emotion} song"])
        terms = base
        if goal == "energize":
            terms = ["energetic workout", "motivational"]
        elif goal == "calm_down":
            terms = ["calm peaceful", "ambient"]
    # Also try US store if IN fails - will be handled by caller retry

    results = []
    for term in terms[:2]:
        items = _itunes_search(term, limit=limit)
        for idx, it in enumerate(items):
            # Filter only Tamil for ta requests when possible
            if language == "ta":
                # iTunes IN store mostly returns Tamil for Tamil queries; keep all
                pass
            track = itunes_to_track(it, idx)
            # Force language to requested if we asked Tamil
            if language == "ta" and track["language"] != "ta":
                # Check if artist contains tamil-ish or keep but mark ta for ranking boost
                track["language"] = "ta"
            results.append(track)
            if len(results) >= limit:
                break
        if len(results) >= limit:
            break
    # dedupe by title+artist
    seen = set()
    deduped = []
    for r in results:
        key = (r["title"], r["artist"])
        if key not in seen:
            seen.add(key)
            deduped.append(r)
    return deduped[:limit]
