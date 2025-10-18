from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from app.database import engine
from app.models import Quest, Level
from app.schemas import QuestCreate, QuestRead, LevelRead

router = APIRouter(prefix="/quests", tags=["Quests & Levels"])


# ------------------------------------------------------------------
# 🎯 QUEST ROUTES
# ------------------------------------------------------------------

@router.post("/", response_model=QuestRead)
def create_quest(data: QuestCreate):
    """Create a new quest (admin or team use)."""
    with Session(engine) as session:
        quest = Quest(**data.dict())
        session.add(quest)
        session.commit()
        session.refresh(quest)
        return quest


@router.get("/", response_model=list[QuestRead])
def list_quests(user: str = None):
    """List all quests (or user-specific if ?user=username is provided)."""
    with Session(engine) as session:
        if user:
            quests = session.exec(select(Quest).where(Quest.assigned_to == user)).all()
        else:
            quests = session.exec(select(Quest)).all()
        return quests


@router.put("/{quest_id}/complete", response_model=QuestRead)
def complete_quest(quest_id: int):
    """Mark a quest as completed and reward XP."""
    with Session(engine) as session:
        quest = session.get(Quest, quest_id)
        if not quest:
            raise HTTPException(status_code=404, detail="Quest not found.")
        if quest.completed:
            raise HTTPException(status_code=400, detail="Quest already completed.")

        quest.completed = True
        session.add(quest)

        # Update user's XP level
        level = session.exec(select(Level).where(Level.user == quest.assigned_to)).first()
        if not level:
            level = Level(user=quest.assigned_to, total_xp=quest.xp_reward)
            session.add(level)
        else:
            level.total_xp += quest.xp_reward

            # Handle level-up logic
            if level.total_xp >= level.xp_to_next:
                level.current_level += 1
                level.total_xp -= level.xp_to_next
                level.xp_to_next += 50  # progressively harder

        session.commit()
        session.refresh(quest)
        return quest


# ------------------------------------------------------------------
# 🧱 LEVEL ROUTES
# ------------------------------------------------------------------

@router.get("/level/{username}", response_model=LevelRead)
def get_user_level(username: str):
    """Get the user's level and XP stats."""
    with Session(engine) as session:
        level = session.exec(select(Level).where(Level.user == username)).first()
        if not level:
            raise HTTPException(status_code=404, detail="No level data found for this user.")
        return level
