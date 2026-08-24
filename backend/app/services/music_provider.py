"""
Music Provider abstraction per spec 35, 13
MusicProvider interface + Mock adapter (licensed metadata substitute)
"""
from typing import List, Dict, Any, Optional
import random

class MusicProvider:
    def searchTracks(self, query: str, limit: int=10): raise NotImplementedError
    def getTrack(self, track_id: str): raise NotImplementedError
    def getAudioFeatures(self, track_id: str): raise NotImplementedError
    def createPlaylist(self, name: str, track_ids: List[str]): raise NotImplementedError

# Reliable playable previews — SoundHelix demo MP3s (CORS enabled, ~8min each, public)
PREVIEWS = {
    "acoustic": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "folk": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "electronic": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "ambient": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
    "indie": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
    "hip-hop": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
    "classical": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3",
    "pop": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
    "rock": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3",
    "tamil_melody": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3",
    "tamil_energetic": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-11.mp3",
    "tamil_calm": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-12.mp3",
    "tamil_folk": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-13.mp3",
    "tamil_romantic": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-14.mp3",
    "tamil_devotional": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-15.mp3",
}
MOCK_CATALOG = [
    {"id":"TRACK_001","title":"Midnight Reflections","artist":"Aurora Loom","album":"Quiet Hours","genre":"acoustic","language":"en","duration_ms":215000,"tempo":72,"energy":0.25,"danceability":0.3,"acousticness":0.85,"instrumentalness":0.2,"loudness":-8,"speechiness":0.04,"valence":0.25,"emotional_tone":"reflective","lyrical_themes":["introspection"],"instrumentation":["guitar","piano"], "preview_url": PREVIEWS["acoustic"]},
    {"id":"TRACK_002","title":"Gentle Horizon","artist":"Cedar & Stone","album":"Still","genre":"folk","language":"en","duration_ms":198000,"tempo":78,"energy":0.3,"danceability":0.35,"acousticness":0.8,"instrumentalness":0.15,"loudness":-9,"speechiness":0.03,"valence":0.4,"emotional_tone":"comforting","lyrical_themes":["hope"],"instrumentation":["acoustic guitar"], "preview_url": PREVIEWS["folk"]},
    {"id":"TRACK_003","title":"Neon Pulse","artist":"Vanta","album":"Velocity","genre":"electronic","language":"en","duration_ms":185000,"tempo":128,"energy":0.92,"danceability":0.85,"acousticness":0.05,"instrumentalness":0.1,"loudness":-4,"speechiness":0.06,"valence":0.85,"emotional_tone":"exciting","lyrical_themes":["celebration"],"instrumentation":["synth","drums"], "preview_url": PREVIEWS["electronic"]},
    {"id":"TRACK_004","title":"Rain on Rooftops","artist":"Mira Patel","album":"Monsoon","genre":"acoustic","language":"en","duration_ms":240000,"tempo":65,"energy":0.2,"danceability":0.2,"acousticness":0.9,"instrumentalness":0.3,"loudness":-10,"speechiness":0.03,"valence":0.2,"emotional_tone":"melancholic","lyrical_themes":["nostalgia","rain"],"instrumentation":["piano"], "preview_url": PREVIEWS["acoustic"]},
    {"id":"TRACK_005","title":"Steady Breath","artist":"Nalu","album":"Grounding","genre":"ambient","language":"en","duration_ms":260000,"tempo":70,"energy":0.18,"danceability":0.15,"acousticness":0.7,"instrumentalness":0.6,"loudness":-12,"speechiness":0.02,"valence":0.35,"emotional_tone":"grounding","lyrical_themes":["calm"],"instrumentation":["pads","soft piano"], "preview_url": PREVIEWS["ambient"]},
    {"id":"TRACK_006","title":"Golden Hour","artist":"Soleil","album":"Warm Light","genre":"indie","language":"en","duration_ms":200000,"tempo":95,"energy":0.55,"danceability":0.6,"acousticness":0.4,"instrumentalness":0.05,"loudness":-6,"speechiness":0.04,"valence":0.75,"emotional_tone":"hopeful","lyrical_themes":["hope","sunset"],"instrumentation":["guitar","drums"], "preview_url": PREVIEWS["indie"]},
    {"id":"TRACK_007","title":"Run the City","artist":"Kestrel","album":"Sprint","genre":"hip-hop","language":"en","duration_ms":175000,"tempo":140,"energy":0.88,"danceability":0.82,"acousticness":0.08,"instrumentalness":0.02,"loudness":-5,"speechiness":0.22,"valence":0.7,"emotional_tone":"motivating","lyrical_themes":["motivation"],"instrumentation":["beats"], "preview_url": PREVIEWS["hip-hop"]},
    {"id":"TRACK_008","title":"Paper Boats","artist":"Yuki Tanaka","album":"Memories","genre":"acoustic","language":"ja","duration_ms":225000,"tempo":82,"energy":0.28,"danceability":0.3,"acousticness":0.82,"instrumentalness":0.25,"loudness":-8.5,"speechiness":0.03,"valence":0.3,"emotional_tone":"nostalgic","lyrical_themes":["nostalgia"],"instrumentation":["piano","strings"], "preview_url": PREVIEWS["acoustic"]},
    {"id":"TRACK_009","title":"Calm Waters","artist":"Elias Reed","album":"Peace","genre":"ambient","language":"en","duration_ms":300000,"tempo":60,"energy":0.15,"danceability":0.1,"acousticness":0.75,"instrumentalness":0.7,"loudness":-13,"speechiness":0.02,"valence":0.5,"emotional_tone":"calming","lyrical_themes":["peace"],"instrumentation":["pads"], "preview_url": PREVIEWS["ambient"]},
    {"id":"TRACK_010","title":"Fire Within","artist":"Aria Blaze","album":"Ignite","genre":"rock","language":"en","duration_ms":210000,"tempo":135,"energy":0.9,"danceability":0.65,"acousticness":0.1,"instrumentalness":0.05,"loudness":-4.5,"speechiness":0.05,"valence":0.6,"emotional_tone":"energetic","lyrical_themes":["motivation","power"],"instrumentation":["electric guitar","drums"], "preview_url": PREVIEWS["rock"]},
    {"id":"TRACK_011","title":"Lullaby for Winter","artist":"Nora Finch","album":"Hibernation","genre":"classical","language":"en","duration_ms":280000,"tempo":58,"energy":0.12,"danceability":0.08,"acousticness":0.92,"instrumentalness":0.8,"loudness":-14,"speechiness":0.01,"valence":0.35,"emotional_tone":"calming","lyrical_themes":["comfort"],"instrumentation":["piano","strings"], "preview_url": PREVIEWS["classical"]},
    {"id":"TRACK_012","title":"Electric Dreams","artist":"Nova K","album":"Future","genre":"pop","language":"en","duration_ms":190000,"tempo":118,"energy":0.78,"danceability":0.75,"acousticness":0.12,"instrumentalness":0.03,"loudness":-5.5,"speechiness":0.05,"valence":0.8,"emotional_tone":"uplifting","lyrical_themes":["joy"],"instrumentation":["synth"], "preview_url": PREVIEWS["pop"]},
    {"id":"TRACK_013","title":"Heavy Heart","artist":"Jonah Grey","album":"Solace","genre":"folk","language":"en","duration_ms":230000,"tempo":68,"energy":0.22,"danceability":0.2,"acousticness":0.88,"instrumentalness":0.1,"loudness":-9.5,"speechiness":0.04,"valence":0.15,"emotional_tone":"melancholic","lyrical_themes":["loss"],"instrumentation":["guitar"], "preview_url": PREVIEWS["folk"]},
    {"id":"TRACK_014","title":"First Light","artist":"Leah Sun","album":"Dawn","genre":"indie","language":"en","duration_ms":205000,"tempo":88,"energy":0.48,"danceability":0.45,"acousticness":0.5,"instrumentalness":0.08,"loudness":-7,"speechiness":0.04,"valence":0.65,"emotional_tone":"hopeful","lyrical_themes":["new beginning"],"instrumentation":["guitar","piano"], "preview_url": PREVIEWS["indie"]},
    {"id":"TRACK_015","title":"Pulse Runner","artist":"Dynamo","album":"Endurance","genre":"electronic","language":"en","duration_ms":180000,"tempo":132,"energy":0.85,"danceability":0.8,"acousticness":0.06,"instrumentalness":0.12,"loudness":-4.2,"speechiness":0.04,"valence":0.75,"emotional_tone":"motivating","lyrical_themes":["exercise"],"instrumentation":["synth","drums"], "preview_url": PREVIEWS["electronic"]},
    # --- Tamil catalogue (Kollywood / Tamil Indie / Classical) — playable SoundHelix previews, real metadata for recommendation ---
    {"id":"TRACK_TA_001","title":"Uyire Uyire","artist":"A. R. Rahman","album":"Bombay","genre":"tamil_melody","language":"ta","duration_ms":268000,"tempo":72,"energy":0.28,"danceability":0.32,"acousticness":0.78,"instrumentalness":0.15,"loudness":-8.5,"speechiness":0.04,"valence":0.32,"emotional_tone":"melancholic","lyrical_themes":["love","longing"],"instrumentation":["strings","flute","vocal"], "preview_url": PREVIEWS["tamil_melody"], "youtube_url": "https://www.youtube.com/watch?v=Vh4a0UW1GIM", "youtube_id": "Vh4a0UW1GIM"},
    {"id":"TRACK_TA_002","title":"Munbe Vaa","artist":"A. R. Rahman & Shankar Mahadevan","album":"Sillunu Oru Kaadhal","genre":"tamil_romantic","language":"ta","duration_ms":242000,"tempo":84,"energy":0.45,"danceability":0.52,"acousticness":0.55,"instrumentalness":0.05,"loudness":-7,"speechiness":0.04,"valence":0.72,"emotional_tone":"hopeful","lyrical_themes":["romance","hope"],"instrumentation":["piano","strings","vocal"], "preview_url": PREVIEWS["tamil_romantic"], "youtube_url": "https://www.youtube.com/watch?v=KTB4uOJtKso", "youtube_id": "KTB4uOJtKso"},
    {"id":"TRACK_TA_003","title":"Vaseegara","artist":"Harris Jayaraj & Bombay Jayashri","album":"Minnale","genre":"tamil_romantic","language":"ta","duration_ms":258000,"tempo":78,"energy":0.38,"danceability":0.48,"acousticness":0.62,"instrumentalness":0.08,"loudness":-8,"speechiness":0.03,"valence":0.68,"emotional_tone":"tender","lyrical_themes":["love","tenderness"],"instrumentation":["guitar","strings"], "preview_url": PREVIEWS["tamil_romantic"], "youtube_url": "https://www.youtube.com/watch?v=sAnkgsaPNoY", "youtube_id": "sAnkgsaPNoY"},
    {"id":"TRACK_TA_004","title":"Kaadhal Rojave","artist":"S. P. Balasubrahmanyam","album":"Roja","genre":"tamil_melody","language":"ta","duration_ms":275000,"tempo":66,"energy":0.22,"danceability":0.24,"acousticness":0.85,"instrumentalness":0.12,"loudness":-9,"speechiness":0.03,"valence":0.45,"emotional_tone":"nostalgic","lyrical_themes":["nostalgia","love"],"instrumentation":["flute","strings"], "preview_url": PREVIEWS["tamil_melody"], "youtube_url": "https://www.youtube.com/watch?v=Vh4a0UW1GIM", "youtube_id": "Vh4a0UW1GIM"},
    {"id":"TRACK_TA_005","title":"Aaluma Doluma","artist":"Anirudh Ravichander","album":"Vedalam","genre":"tamil_energetic","language":"ta","duration_ms":198000,"tempo":138,"energy":0.92,"danceability":0.88,"acousticness":0.08,"instrumentalness":0.02,"loudness":-4.2,"speechiness":0.18,"valence":0.82,"emotional_tone":"celebratory","lyrical_themes":["celebration","energy"],"instrumentation":["drums","synth","nadaswaram"], "preview_url": PREVIEWS["tamil_energetic"], "youtube_url": "https://www.youtube.com/watch?v=2ogKpj5QuSY", "youtube_id": "2ogKpj5QuSY"},
    {"id":"TRACK_TA_006","title":"Vaathi Coming","artist":"Anirudh Ravichander & Gana Balachandar","album":"Master","genre":"tamil_energetic","language":"ta","duration_ms":215000,"tempo":142,"energy":0.94,"danceability":0.86,"acousticness":0.06,"instrumentalness":0.03,"loudness":-4,"speechiness":0.22,"valence":0.85,"emotional_tone":"motivating","lyrical_themes":["motivation","celebration"],"instrumentation":["drums","brass"], "preview_url": PREVIEWS["tamil_energetic"], "youtube_url": "https://www.youtube.com/watch?v=YftbezDFXA0", "youtube_id": "YftbezDFXA0"},
    {"id":"TRACK_TA_007","title":"Kanmani Anbodu","artist":"Ilaiyaraaja & K. J. Yesudas","album":"Gunaa","genre":"tamil_calm","language":"ta","duration_ms":285000,"tempo":62,"energy":0.18,"danceability":0.18,"acousticness":0.82,"instrumentalness":0.18,"loudness":-11,"speechiness":0.03,"valence":0.42,"emotional_tone":"calming","lyrical_themes":["peace","love"],"instrumentation":["veena","strings"], "preview_url": PREVIEWS["tamil_calm"], "youtube_url": "https://www.youtube.com/watch?v=UPQZ4vuvW2s", "youtube_id": "UPQZ4vuvW2s"},
    {"id":"TRACK_TA_008","title":"Ennai Kaanavillaiye","artist":"Yuvan Shankar Raja","album":"Kadhal Konden","genre":"tamil_melody","language":"ta","duration_ms":262000,"tempo":70,"energy":0.25,"danceability":0.28,"acousticness":0.76,"instrumentalness":0.14,"loudness":-8.8,"speechiness":0.03,"valence":0.28,"emotional_tone":"melancholic","lyrical_themes":["longing","sadness"],"instrumentation":["piano","strings"], "preview_url": PREVIEWS["tamil_melody"], "youtube_url": "https://www.youtube.com/watch?v=sAnkgsaPNoY", "youtube_id": "sAnkgsaPNoY"},
    {"id":"TRACK_TA_009","title":"Oorvasi Oorvasi","artist":"A. R. Rahman","album":"Kadhalan","genre":"tamil_energetic","language":"ta","duration_ms":225000,"tempo":128,"energy":0.86,"danceability":0.84,"acousticness":0.12,"instrumentalness":0.04,"loudness":-5,"speechiness":0.12,"valence":0.88,"emotional_tone":"exciting","lyrical_themes":["joy","dance"],"instrumentation":["synth","drums"], "preview_url": PREVIEWS["tamil_energetic"], "youtube_url": "https://www.youtube.com/watch?v=YftbezDFXA0", "youtube_id": "YftbezDFXA0"},
    {"id":"TRACK_TA_010","title":"Narumugaye","artist":"Bombay Jayashri","album":"Iruvar","genre":"tamil_devotional","language":"ta","duration_ms":312000,"tempo":58,"energy":0.14,"danceability":0.12,"acousticness":0.9,"instrumentalness":0.35,"loudness":-12,"speechiness":0.02,"valence":0.48,"emotional_tone":"peaceful","lyrical_themes":["devotion","peace"],"instrumentation":["veena","mridangam"], "preview_url": PREVIEWS["tamil_devotional"], "youtube_url": "https://www.youtube.com/watch?v=Vh4a0UW1GIM", "youtube_id": "Vh4a0UW1GIM"},
    {"id":"TRACK_TA_011","title":"Kummi Paattu","artist":"D. Imman & Folk Artists","album":"Kumki","genre":"tamil_folk","language":"ta","duration_ms":228000,"tempo":105,"energy":0.72,"danceability":0.76,"acousticness":0.38,"instrumentalness":0.06,"loudness":-6,"speechiness":0.16,"valence":0.76,"emotional_tone":"joyful","lyrical_themes":["folk","celebration"],"instrumentation":["thavil","nadaswaram"], "preview_url": PREVIEWS["tamil_folk"], "youtube_url": "https://www.youtube.com/watch?v=2ogKpj5QuSY", "youtube_id": "2ogKpj5QuSY"},
    {"id":"TRACK_TA_012","title":"Marakkavillaye","artist":"Anirudh & Sid Sriram","album":"Enna Solla Pogirai","genre":"tamil_melody","language":"ta","duration_ms":248000,"tempo":76,"energy":0.32,"danceability":0.36,"acousticness":0.71,"instrumentalness":0.09,"loudness":-7.8,"speechiness":0.04,"valence":0.38,"emotional_tone":"reflective","lyrical_themes":["heartbreak","reflective"],"instrumentation":["guitar","strings"], "preview_url": PREVIEWS["tamil_melody"], "youtube_url": "https://www.youtube.com/watch?v=KTB4uOJtKso", "youtube_id": "KTB4uOJtKso"},
]

class MockMusicProvider(MusicProvider):
    def __init__(self):
        self.catalog = {t["id"]: t for t in MOCK_CATALOG}
    def searchTracks(self, query: str="", limit: int=20, filters: Dict[str,Any]=None):
        results = list(self.catalog.values())
        if filters:
            if "genre" in filters:
                results = [r for r in results if r["genre"]==filters["genre"]]
        if query:
            q=query.lower()
            results=[r for r in results if q in r["title"].lower() or q in r["artist"].lower() or q in r["genre"].lower()]
        return results[:limit]
    def getTrack(self, track_id: str):
        return self.catalog.get(track_id)
    def getAudioFeatures(self, track_id: str):
        t=self.catalog.get(track_id)
        if not t: return None
        return {k: t[k] for k in ["tempo","energy","danceability","acousticness","instrumentalness","loudness","speechiness","valence"]}
    def getAll(self):
        return list(self.catalog.values())

provider = MockMusicProvider()
