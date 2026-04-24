"""
Authentication API routes.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta

from core import get_supabase_client, verify_jwt_token, get_user_by_auth_id
from models import User

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    agency_id: str


# Authentication dependency
async def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    """Verify JWT and return user."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    # Extract token from "Bearer <token>"
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization

    try:
        # Verify token with Supabase
        auth_data = await verify_jwt_token(token)
        auth_user_id = auth_data["id"]

        # Get user from our database
        user_data = await get_user_by_auth_id(auth_user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        return User(**user_data)

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login with email and password."""
    supabase = get_supabase_client()

    try:
        # Sign in with Supabase Auth
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Get agency user data
        user_data = await get_user_by_auth_id(response.user.id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not registered in agency")

        return LoginResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user=user_data
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token."""
    supabase = get_supabase_client()

    try:
        response = supabase.auth.refresh_session(refresh_token)

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token refresh failed: {str(e)}")


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """Logout and invalidate token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = authorization[7:] if authorization.startswith("Bearer ") else authorization

    supabase = get_supabase_client()

    try:
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        # Even if sign out fails locally, we consider it done
        return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user info."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role,
        agency_id=str(user.agency_id)
    )
