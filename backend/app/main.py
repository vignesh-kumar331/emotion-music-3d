from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, emotion, recommendation, journal, preferences

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, description="Emotion-aware music companion per Master System Prompt", version=settings.APP_VERSION)

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(emotion.router, prefix=settings.API_V1_PREFIX)
app.include_router(recommendation.router, prefix=settings.API_V1_PREFIX)
app.include_router(journal.router, prefix=settings.API_V1_PREFIX)
app.include_router(preferences.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} v{settings.APP_VERSION}", "docs":"/docs"}

@app.get("/health")
def health():
    return {"status":"healthy"}
