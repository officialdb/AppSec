from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    """Public user profile — excludes password and other sensitive fields."""

    id: int
    email: str
    full_name: str
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None

