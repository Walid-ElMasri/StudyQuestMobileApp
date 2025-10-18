from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from app.database import engine
from app.models import Avatar, Badge, User
from app.schemas import AvatarCreate, AvatarRead, BadgeCreate, BadgeRead

router = APIRouter(prefix="/cosmetics", tags=["Cosmetics & Rewards"])


# ------------------------------------------------------------------
# 🎨 AVATAR ROUTES
# ------------------------------------------------------------------

def _ensure_user(session: Session, username: str) -> None:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")

@router.post("/avatar", response_model=AvatarRead)
def create_avatar(data: AvatarCreate):
    """Create or update the user's avatar."""
    with Session(engine) as session:
        _ensure_user(session, data.user)
        # Check if user already has an avatar
        existing = session.exec(select(Avatar).where(Avatar.user == data.user)).first()
        if existing:
            # Update existing avatar
            for key, value in data.dict().items():
                setattr(existing, key, value)
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing

        # Create new avatar
        avatar = Avatar(**data.dict())
        session.add(avatar)
        session.commit()
        session.refresh(avatar)
        return avatar


@router.get("/avatar/{username}", response_model=AvatarRead)
def get_avatar(username: str):
    """Retrieve avatar details for a specific user."""
    with Session(engine) as session:
        _ensure_user(session, username)
        avatar = session.exec(select(Avatar).where(Avatar.user == username)).first()
        if not avatar:
            raise HTTPException(status_code=404, detail="Avatar not found.")
        return avatar


# ------------------------------------------------------------------
# 🏅 BADGE ROUTES
# ------------------------------------------------------------------

@router.post("/badge", response_model=BadgeRead)
def create_badge(data: BadgeCreate):
    """Create a new badge (admin use)."""
    with Session(engine) as session:
        badge = Badge(**data.dict())
        session.add(badge)
        session.commit()
        session.refresh(badge)
        return badge


@router.get("/badges", response_model=list[BadgeRead])
def list_badges():
    """List all available badges."""
    with Session(engine) as session:
        badges = session.exec(select(Badge)).all()
        return badges


@router.get("/badges/{xp}", response_model=list[BadgeRead])
def get_unlockable_badges(xp: int):
    """List all badges unlockable given the user's total XP."""
    with Session(engine) as session:
        badges = session.exec(select(Badge).where(Badge.xp_required <= xp)).all()
        return badges
