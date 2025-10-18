from app.main import app  # type: ignore


@app.get("/__health")
def vercel_healthcheck():
    """Lightweight healthcheck for Vercel."""
    return {"status": "ok"}
