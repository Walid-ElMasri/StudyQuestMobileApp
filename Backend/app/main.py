from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db

from app.Routers import home, progress, bossbattle  
try:
    from app.Routers import quests
except Exception:
    quests = None
try:
    from app.Routers import cosmetics
except Exception:
    cosmetics = None
try:
    from app.Routers import mentor as text_ai
except Exception:
    text_ai = None
try:
    from app.Routers import socialfeatures as social
except Exception:
    social = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

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
    lifespan=lifespan,
)


app.include_router(home.router)
app.include_router(progress.router)
if quests and hasattr(quests, "router"):
    app.include_router(quests.router)
app.include_router(bossbattle.router)
if cosmetics and hasattr(cosmetics, "router"):
    app.include_router(cosmetics.router)
if text_ai and hasattr(text_ai, "router"):
    app.include_router(text_ai.router)
if social and hasattr(social, "router"):
    app.include_router(social.router)



@app.get("/", tags=["Root"])
def root():
    """
    StudyQuest API landing page — shows available endpoints and docs link.
    """
    return {
        "message": "Welcome to the StudyQuest Backend API",
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

