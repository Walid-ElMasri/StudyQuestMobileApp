from fastapi import FastAPI
from app.database import init_db

#  Import all router modules
from app.routers import (
    home,
    progress,
    quests,
    cosmetics,
    text_ai,
    bossbattle,
    social
)

#  Create the FastAPI application
app = FastAPI(
    title="StudyQuest Backend API",
    description=(
        "Gamified productivity app backend built with FastAPI + SQLModel.\n\n"
        "Each teammate owns one feature area — all integrated into one backend:\n"
        "- Walid: Progress Tracking + Home\n"
        "- Nour: Quests & Levels\n"
        "- Aya: Cosmetics & Rewards\n"
        "- All Team: Text AI Mentor\n"
        "- Lynn: Boss Battle\n"
        "- Mohamad: Social Features"
    ),
    version="1.0.0",
)


#  Include all routers
app.include_router(home.router)
app.include_router(progress.router)
app.include_router(quests.router)
app.include_router(cosmetics.router)
app.include_router(text_ai.router)
app.include_router(bossbattle.router)
app.include_router(social.router)


#  Initialize the database when the app starts
@app.on_event("startup")
def on_startup():
    init_db()


#  Root route (API homepage)
@app.get("/", tags=["Root"])
def root():
    """
    StudyQuest API landing page — shows available endpoints and docs link.
    """
    return {
        "message": "Welcome to the StudyQuest Backend API 🎯",
        "status": "running",
        "main_endpoints": {
            "Home Dashboard": "/home/dashboard?user=<username>",
            "Progress Tracking": "/progress",
            "Quests & Levels": "/quests",
            "Cosmetics & Rewards": "/cosmetics",
            "AI Text Mentor": "/text-ai",
            "Daily Boss Battle": "/boss",
            "Social Features": "/social"
        },
        "docs": "/docs",
    }

