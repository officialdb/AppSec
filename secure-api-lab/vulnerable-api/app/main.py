from fastapi import FastAPI
from sqlalchemy import text

from app.api.routes import auth, documents, files, import_url, users
from app.db.database import engine

app = FastAPI(
    title="Vulnerable API",
    description=(
        "Intentionally vulnerable Document Management API for AppSec training. "
        "Do **not** deploy to production."
    ),
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(files.router)
app.include_router(import_url.router)


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
def health():
    """Basic liveness probe."""
    return {"status": "ok", "application": "vulnerable-api"}


@app.get("/health/db", tags=["Health"])
def health_db():
    """Database connectivity check."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        return {"status": "error", "database": str(exc)}
