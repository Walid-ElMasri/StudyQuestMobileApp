from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from app.database import engine
from app.models import Progress, User


router = APIRouter(prefix="/home", tags=["Home Page"])


# ------------------------------------------------------------------
# 🔹 Helper Functions
# ------------------------------------------------------------------

def calculate_streak(sessions: list[Progress]) -> int:
    """Calculate consecutive study days (streak) for a user."""
    if not sessions:
        return 0
    dates = sorted({s.date.date() for s in sessions})
    streak = 1
    for i in range(len(dates) - 1, 0, -1):
        if (dates[i] - dates[i - 1]).days == 1:
            streak += 1
        else:
            break
    return streak


def get_motivation_message(streak: int) -> str:
    """Generate motivational message based on the user's streak length."""
    if streak == 0:
        return "Every master was once a beginner — start your first quest today!"
    elif streak < 3:
        return "Nice start! Keep your streak alive 🔥"
    elif streak < 7:
        return f"Awesome! {streak}-day streak — consistency is your superpower 💪"
    else:
        return f"Unstoppable! {streak}-day streak — you’re on fire! ⚡"


# ------------------------------------------------------------------
# 🔹 ROUTES
# ------------------------------------------------------------------

@router.get("/")
def home():
    """
    API root for Home — returns basic API info and navigation links.
    This acts as the landing endpoint for your frontend.
    """
    return {
        "message": "Welcome to the StudyQuest Backend API 🎯",
        "status": "running",
        "available_sections": {
            "Home Dashboard": "/home/dashboard?user=<username>",
            "Progress Tracking": "/progress",
            "Quests & Levels": "/quests",
            "Cosmetics & Rewards": "/cosmetics",
            "AI Text Mentor": "/text-ai",
            "Daily Boss Battle": "/boss",
            "Social Features": "/social"
        },
        "docs": "/docs"
    }


@router.get("/dashboard")
def get_dashboard(user: str):
    """
    Returns the user's Home Page data:
    - Total XP, total sessions, current streak
    - Recent study sessions (up to 3)
    - Motivational message
    - Quick links to other pages
    """
    with Session(engine) as session:
        # 1️⃣ Fetch the user if exists
        user_obj = session.exec(select(User).where(User.username == user)).first()
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found. Please register first.")

        # 2️⃣ Fetch progress sessions
        sessions = session.exec(select(Progress).where(Progress.user == user)).all()
        if not sessions:
            return {
                "user": user,
                "summary": {
                    "total_xp": user_obj.total_xp,
                    "total_sessions": 0,
                    "current_streak_days": 0,
                    "motivation": "Start your first study quest and earn XP today!"
                },
                "recent_sessions": [],
                "navigation": get_navigation_links()
            }

        # 3️⃣ Sort and calculate stats
        sessions.sort(key=lambda x: x.date, reverse=True)
        total_xp = user_obj.total_xp or sum(s.xp_gained for s in sessions)
        total_sessions = len(sessions)
        streak = calculate_streak(sessions)
        motivation = get_motivation_message(streak)

        # 4️⃣ Prepare recent sessions
        recent = [
            {
                "date": s.date.strftime("%Y-%m-%d"),
                "duration": s.duration_minutes,
                "xp": s.xp_gained,
                "reflection": s.reflection
            }
            for s in sessions[:3]
        ]

        # 5️⃣ Return structured dashboard data
        return {
            "user": user,
            "summary": {
                "total_xp": total_xp,
                "total_sessions": total_sessions,
                "current_streak_days": streak,
                "motivation": motivation
            },
            "recent_sessions": recent,
            "navigation": get_navigation_links()
        }


# ------------------------------------------------------------------
# 🔹 Utility
# ------------------------------------------------------------------

def get_navigation_links() -> dict:
    """Centralized map of routes for easy navigation from the Home Page."""
    return {
        "Progress Tracking": "/progress",
        "Quests & Levels": "/quests",
        "Cosmetics & Rewards": "/cosmetics",
        "AI Text Mentor": "/text-ai",
        "Daily Boss Battle": "/boss",
        "Social Features": "/social"
    }
