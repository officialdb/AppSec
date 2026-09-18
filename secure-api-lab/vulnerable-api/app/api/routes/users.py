from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.users import UserResponse, UserUpdate

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's own profile."""
    return current_user


@router.get("/search", response_model=list[UserResponse])
def search_users(
    q: str = "",
    mode: str = "secure",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search users by name or email.

    Supports both the remediated (default) parameterized query and the
    isolated vulnerable query for AppSec training and regression testing.

    - Default (mode="secure"): Parameterized query using bind parameter (:pattern).
    - Lab Mode (mode="vulnerable"): Dynamic string interpolation (VULN-002).
    """
    if not q or not q.strip():
        return []

    if mode == "vulnerable":
        # INTENTIONALLY VULNERABLE — VULN-002 SQL INJECTION LAB
        # Unsafe string interpolation allows SQL injection via the 'q' parameter.
        query_str = f"""
            SELECT id, email, full_name, role, created_at, updated_at
            FROM users
            WHERE email ILIKE '%{q}%'
               OR full_name ILIKE '%{q}%'
        """
        result = db.execute(text(query_str))
        return result.mappings().all()

    # SECURE / REMEDIATED IMPLEMENTATION — VULN-002
    # Parameterized query: user input is safely bound to :pattern.
    query_str = text("""
        SELECT id, email, full_name, role, created_at, updated_at
        FROM users
        WHERE email ILIKE :pattern
           OR full_name ILIKE :pattern
    """)
    result = db.execute(query_str, {"pattern": f"%{q}%"})
    return result.mappings().all()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a user's profile by ID.

    INTENTIONAL VULNERABILITY: Broken Object-Level Authorization (BOLA/IDOR)

    The authenticated user's identity is verified, but
    ownership/authorization of the requested object is not checked.

    A secure implementation would verify::

        if current_user.id != user_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Forbidden")
    """
    # INTENTIONAL VULNERABILITY (IDOR):
    # No check that current_user.id == user_id.
    # Any authenticated user can read any other user's profile.
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a user's profile.

    INTENTIONAL VULNERABILITY: Same BOLA/IDOR flaw as GET —
    any authenticated user can modify any other user's profile.
    """
    # INTENTIONAL VULNERABILITY (IDOR):
    # No ownership check before modifying the resource.
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.email is not None:
        user.email = data.email

    db.commit()
    db.refresh(user)
    return user

