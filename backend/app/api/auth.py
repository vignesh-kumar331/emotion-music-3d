from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.models import User, UserPreferences
from app.schemas.schemas import UserCreate, UserLogin, Token, UserOut
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email==data.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(email=data.email, hashed_password=hash_password(data.password), display_name=data.display_name)
    db.add(user); db.commit(); db.refresh(user)
    prefs = UserPreferences(user_id=user.id)
    db.add(prefs); db.commit()
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type":"bearer", "user": user}

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email==data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type":"bearer", "user": user}

@router.get("/me", response_model=UserOut)
def me(current = Depends(get_current_user)):
    return current
