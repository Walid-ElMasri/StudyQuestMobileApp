# ⚙️ StudyQuest Backend

Backend for the **StudyQuest – Gamified Productivity App**, built with **FastAPI** and **SQLModel**.

---

## 🚀 Run Locally

```bash
# Activate virtual environment
python3 -m venv venv
source venv/bin/activate       # (Windows: venv\Scripts\activate)

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload
