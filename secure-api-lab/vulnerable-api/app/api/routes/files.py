from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/files", tags=["Files"])


@router.post("/upload")
def upload_file():
    """File upload endpoint.

    Not yet implemented — will be added in a future milestone
    to demonstrate insecure file upload vulnerabilities.
    """
    return {"detail": "File upload not yet implemented"}

