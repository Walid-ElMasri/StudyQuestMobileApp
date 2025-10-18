# ⚙️ StudyQuest Backend

Backend for the **StudyQuest – Gamified Productivity App**, built with **FastAPI** and **SQLModel**.

---

##  Tech Stack
- FastAPI + Uvicorn application server
- SQLModel (SQLAlchemy + Pydantic) data layer
- SQLite for local development (with optional `DATABASE_URL` for production)

---

##  Quickstart (Local)

```bash
# Activate virtual environment
python3 -m venv venv
source venv/bin/activate       # (Windows: venv\Scripts\activate)

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload
```

The interactive API explorer is available at `http://127.0.0.1:8000/docs`.

Set `DATABASE_URL` to point to a production-ready database (e.g. Postgres) when deploying; the app will fall back to `sqlite:///studyquest.db` if the variable is not set.

---

## 🗃️ Data Model Overview
| Model | Purpose | Key Fields |
|-------|---------|------------|
| `User` | Global user profile | `username`, `email`, `total_xp`, `join_date` |
| `Progress` | Study sessions & reflections | `user`, `duration_minutes`, `xp_gained`, `reflection` |
| `Quest` / `Level` | Gamified quests & leveling system | `difficulty`, `xp_reward`, `current_level`, `xp_to_next` |
| `Avatar` / `Badge` | Cosmetics & rewards | `hairstyle`, `outfit`, `xp_required`, `icon_url` |
| `TextAIReflection` | AI mentor reflections | `reflection_text`, `ai_feedback`, `summary`, `xp_reward` |
| `BossBattle` | Daily boss battle quiz stats | `score`, `total_questions`, `difficulty`, `xp_reward` |
| `Friend` / `Leaderboard` | Social features | `friend_username`, `status`, `total_xp`, `current_streak` |

---

## 📚 API Overview

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/users/` | Register a new StudyQuest user |
| `GET` | `/users/` | List all registered users |
| `GET` | `/users/{username}` | Retrieve a single user |
| `GET` | `/home/dashboard` | Aggregated dashboard stats for a user |
| `POST` | `/progress/` | Log a study session (XP + streaks) |
| `GET` | `/progress/?user=` | List study sessions for a user |
| `GET` | `/progress/stats?user=` | Progress statistics summary |
| `POST` | `/quests/` | Create quests (admin/script use) |
| `PUT` | `/quests/{quest_id}/complete` | Mark quest complete and update level |
| `GET` | `/quests/level/{username}` | Fetch a user’s level data |
| `POST` | `/cosmetics/avatar` | Create/update avatar for a user |
| `GET` | `/cosmetics/avatar/{username}` | Fetch avatar |
| `POST` | `/cosmetics/badge` | Create badge definition |
| `GET` | `/cosmetics/badges` | List badges / `<= xp` variants |
| `POST` | `/text-ai/` | Submit reflection → AI feedback |
| `GET` | `/text-ai/?user=` | List reflections for a user |
| `POST` | `/boss/start` | Start boss battle session |
| `POST` | `/boss/answer` | Submit answer and update score |
| `GET` | `/boss/status?user=` | Session status / time remaining |
| `POST` | `/social/friends/add` | Send friend request |
| `PATCH` | `/social/friends/respond` | Accept/decline/block friend request |
| `GET` | `/social/leaderboard` | XP leaderboard snapshot |

> Tip: Every router group includes a root `GET` endpoint with a short explainer (e.g. `/boss`, `/social`, `/cosmetics`).

---

##  Example Requests

Register a user:

```http
POST /users/
Content-Type: application/json

{
  "username": "lynn",
  "email": "lynn@example.com"
}
```

Log a progress session:

```http
POST /progress/
Content-Type: application/json

{
  "user": "lynn",
  "date": "2024-05-01T18:30:00Z",
  "duration_minutes": 55,
  "reflection": "Deep work on calculus."
}
```

Start a boss battle:

```http
POST /boss/start
Content-Type: application/json

{
  "user": "lynn",
  "difficulty": "hard",
  "total_questions": 5
}
```

---

##  Deployment Notes
1. Set `DATABASE_URL` in the deployment environment (Postgres/MySQL managed service recommended).  
2. Provide the environment variable to the runtime before booting the app.  
3. The included `vercel.json` + `api/index.py` entrypoint support Vercel serverless deployment (see repository docs once configured).  

After deployment, smoke-test:
- `GET /` to verify health
- `GET /docs` to load the OpenAPI explorer
- Run a sample flow (register user → log progress → fetch dashboard)

---

##  Our presentation steps:
- Demonstrate local usage (`uvicorn app.main:app --reload`) and a quick walk-through of `/docs`.
- Show live API interaction against the deployed URL.
- Highlight each feature area owned by teammate and how the backend routes support them.
