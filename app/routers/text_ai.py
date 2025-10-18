from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from app.database import engine
from app.models import TextAIReflection, User
from app.schemas import TextAIReflectionCreate, TextAIReflectionRead


router = APIRouter(prefix="/text-ai", tags=["Text AI Mentor"])


# ------------------------------------------------------------------
# 🧠 Helper — Mock AI Logic
# ------------------------------------------------------------------

def generate_ai_feedback(reflection_text: str) -> dict:
    """
    Temporary placeholder for AI analysis logic.
    You can later replace this with a call to OpenAI, Anthropic, or Bedrock.
    """
    text = reflection_text.lower()

    # Simple sentiment / keyword mock logic
    if any(word in text for word in ["tired", "hard", "struggle", "stuck"]):
        feedback = "It sounds like you faced challenges today — remember, progress is built through persistence."
    elif any(word in text for word in ["happy", "productive", "focused", "good", "great"]):
        feedback = "Fantastic work! Keep maintaining that focused mindset."
    else:
        feedback = "Keep reflecting — awareness is the key to consistent improvement."

    summary = (
        reflection_text[:120] + "..."
        if len(reflection_text) > 120
        else reflection_text
    )

    xp_reward = 10  # default XP for completing a reflection

    return {"feedback": feedback, "summary": summary, "xp_reward": xp_reward}


# ------------------------------------------------------------------
# 📘 ROUTES
# ------------------------------------------------------------------


@router.post("/", response_model=TextAIReflectionRead)
def add_reflection(data: TextAIReflectionCreate):
    """
    Add a new text reflection entry and analyze it using AI feedback logic.
    Returns feedback, summary, and XP reward.
    """
    with Session(engine) as session:
        user_exists = session.exec(select(User).where(User.username == data.user)).first()
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found. Please register first.")
        # Step 1: Generate AI feedback and summary
        ai_result = generate_ai_feedback(data.reflection_text)

        # Step 2: Create and save new record
        reflection = TextAIReflection(
            user=data.user,
            date=data.date,
            reflection_text=data.reflection_text,
            ai_feedback=ai_result["feedback"],
            summary=ai_result["summary"],
            xp_reward=ai_result["xp_reward"],
        )

        session.add(reflection)
        session.commit()
        session.refresh(reflection)

        return reflection


@router.get("/", response_model=list[TextAIReflectionRead])
def list_reflections(user: str):
    """
    Get all text reflections submitted by a specific user.
    """
    with Session(engine) as session:
        user_exists = session.exec(select(User).where(User.username == user)).first()
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found. Please register first.")
        reflections = session.exec(
            select(TextAIReflection).where(TextAIReflection.user == user)
        ).all()
        if not reflections:
            raise HTTPException(status_code=404, detail="No reflections found for this user.")
        return reflections


@router.get("/{reflection_id}", response_model=TextAIReflectionRead)
def get_reflection(reflection_id: int):
    """
    Retrieve a specific reflection by ID.
    """
    with Session(engine) as session:
        reflection = session.get(TextAIReflection, reflection_id)
        if not reflection:
            raise HTTPException(status_code=404, detail="Reflection not found.")
        return reflection


@router.delete("/{reflection_id}")
def delete_reflection(reflection_id: int):
    """
    Delete a specific text reflection entry.
    """
    with Session(engine) as session:
        reflection = session.get(TextAIReflection, reflection_id)
        if not reflection:
            raise HTTPException(status_code=404, detail="Reflection not found.")
        session.delete(reflection)
        session.commit()
        return {"message": f"Reflection {reflection_id} deleted successfully."}
