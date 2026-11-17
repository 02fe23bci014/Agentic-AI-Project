import uuid
from fastapi import APIRouter, HTTPException

from backend.database.connection import get_connection
from backend.models.user import User, UserLoginRequest, UserRegisterRequest, UserUpdateRequest
from backend.services.auth_service import hash_password, verify_password


router = APIRouter()


@router.post("/login")
def login(request: UserLoginRequest):
    """Authenticate a student or faculty user."""
    username = request.username.strip().lower()
    expected_role = request.role.strip().lower()

    with get_connection() as connection:
        user_row = connection.execute(
            """
            SELECT id, username, password_hash, role, full_name, email
            FROM users
            WHERE LOWER(username) = ?
            """,
            (username,),
        ).fetchone()

    if not user_row:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    # Verify password
    if not verify_password(request.password, user_row["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    # Verify requested role matches the account role
    if user_row["role"] != expected_role:
        role_label = user_row["role"].title()
        raise HTTPException(
            status_code=400,
            detail=f"This account is registered as a {role_label} account. Please select {role_label} to sign in.",
        )

    user = User(
        id=user_row["id"],
        username=user_row["username"],
        role=user_row["role"],
        full_name=user_row["full_name"],
        email=user_row["email"],
    )

    # Return user with a session token
    token = f"token_{user.id}_{uuid.uuid4().hex[:12]}"

    return {
        "status": "success",
        "user": user,
        "token": token,
        "message": f"Welcome back, @{user.username}!",
    }


@router.post("/register", status_code=201)
def register(request: UserRegisterRequest):
    """Register a new student or faculty account."""
    username = request.username.strip().lower()
    role = request.role.strip().lower()

    if role not in ("student", "faculty"):
        raise HTTPException(
            status_code=400,
            detail="Role must be either 'student' or 'faculty'.",
        )

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM users WHERE LOWER(username) = ?",
            (username,),
        ).fetchone()

        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Username '{username}' is already taken.",
            )

        user_id = f"{role}-{uuid.uuid4().hex[:8]}"
        p_hash = hash_password(request.password)

        connection.execute(
            """
            INSERT INTO users (id, username, password_hash, role, full_name, email)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                username,
                p_hash,
                role,
                request.full_name.strip(),
                request.email.strip() if request.email else None,
            ),
        )

    user = User(
        id=user_id,
        username=username,
        role=role,
        full_name=request.full_name.strip(),
        email=request.email,
    )

    return {
        "status": "success",
        "user": user,
        "token": f"token_{user_id}_{uuid.uuid4().hex[:12]}",
        "message": f"Account created successfully for @{user.username}!",
    }


@router.put("/profile", response_model=User)
def update_profile(request: UserUpdateRequest):
    """Update profile details (name, email, or password)."""
    with get_connection() as connection:
        user_row = connection.execute(
            "SELECT id, username, password_hash, role, full_name, email FROM users WHERE id = ?",
            (request.user_id,),
        ).fetchone()

        if not user_row:
            raise HTTPException(status_code=404, detail="User not found.")

        new_full_name = request.full_name.strip() if request.full_name is not None and request.full_name.strip() else user_row["full_name"]
        new_email = request.email.strip() if request.email is not None else user_row["email"]
        new_password_hash = hash_password(request.password) if request.password and request.password.strip() else user_row["password_hash"]

        connection.execute(
            """
            UPDATE users
            SET full_name = ?, email = ?, password_hash = ?
            WHERE id = ?
            """,
            (new_full_name, new_email, new_password_hash, request.user_id),
        )

    return User(
        id=user_row["id"],
        username=user_row["username"],
        role=user_row["role"],
        full_name=new_full_name,
        email=new_email,
    )


@router.get("/users", response_model=list[User])
def list_users(role: str | None = None):
    """Retrieve users list (optional filter by role)."""
    query = "SELECT id, username, role, full_name, email FROM users"
    params = []
    if role:
        query += " WHERE role = ?"
        params.append(role.strip().lower())
    query += " ORDER BY role, username"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    return [
        User(
            id=row["id"],
            username=row["username"],
            role=row["role"],
            full_name=row["full_name"],
            email=row["email"],
        )
        for row in rows
    ]
