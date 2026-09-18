from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/import", tags=["Import"])


@router.post("/url")
def import_from_url():
    """Import content from a URL.

    Not yet implemented — will be added in a future milestone
    to demonstrate SSRF vulnerabilities.
    """
    return {"detail": "URL import not yet implemented"}

