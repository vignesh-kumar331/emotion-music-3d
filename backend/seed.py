from app.core.database import SessionLocal, engine, Base
from app.models.models import Track, TrackFeatures
from app.services.music_provider import MOCK_CATALOG
Base.metadata.create_all(bind=engine)
db=SessionLocal()
count=db.query(Track).count()
if count==0:
    for t in MOCK_CATALOG:
        tr=Track(id=t["id"], title=t["title"], artist=t["artist"], album=t["album"], genre=t["genre"], language=t["language"], duration_ms=t["duration_ms"])
        db.add(tr)
        db.commit()
        feat=TrackFeatures(track_id=t["id"], tempo=t["tempo"], energy=t["energy"], danceability=t["danceability"], acousticness=t["acousticness"], instrumentalness=t["instrumentalness"], loudness=t["loudness"], speechiness=t["speechiness"], valence=t["valence"], lyrical_themes=t["lyrical_themes"], emotional_tone=t["emotional_tone"], instrumentation=t["instrumentation"])
        db.add(feat)
    db.commit()
    print(f"Seeded {len(MOCK_CATALOG)} tracks")
else:
    print(f"Already {count} tracks")
db.close()
