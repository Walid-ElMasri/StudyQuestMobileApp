from sqlmodel import SQLModel, create_engine

# Use SQLite (simple for local dev + Vercel)
sqlite_file_name = "studyquest.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Engine connects SQLModel to the database
engine = create_engine(sqlite_url, echo=False)

def init_db():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)
