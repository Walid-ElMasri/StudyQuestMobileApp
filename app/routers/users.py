from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from app.database import engine
from app.models import User
from app.schemas import UserCreate, UserRead


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserRead, status_code=201)
def register_user(payload: UserCreate):
    """Create a new StudyQuest user."""
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.username == payload.username)).first()
        if existing:
            raise HTTPException(status_code=409, detail="Username already exists.")

        user = User(username=payload.username, email=payload.email, total_xp=payload.total_xp)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@router.get("/", response_model=list[UserRead])
def list_users():
    """List all registered users."""
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return users


@router.get("/{username}", response_model=UserRead)
def get_user(username: str):
    """Retrieve a specific user by username."""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return user
