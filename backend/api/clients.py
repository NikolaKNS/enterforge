"""
Client management API routes.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr

from core import get_supabase_client, set_agency_context
from models import User, Client, ClientCreate, ClientUpdate, ClientPreferences
from .auth import get_current_user

router = APIRouter()


class ClientCreateRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    preferences: Optional[ClientPreferences] = None
    notes: Optional[str] = None


class ClientUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    preferences: Optional[ClientPreferences] = None
    notes: Optional[str] = None


@router.get("", response_model=List[dict])
async def list_clients(
    search: Optional[str] = Query(None, description="Search by name or email"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user)
):
    """List all clients for the agency."""
    supabase = get_supabase_client()
    await set_agency_context(supabase, str(user.agency_id))

    query = supabase.table("clients").select("*")

    if search:
        query = query.or_(f"name.ilike.%{search}%,email.ilike.%{search}%")

    result = query.range(offset, offset + limit - 1)\
        .order("created_at", desc=True)\
        .execute()

    return result.data or []


@router.post("", response_model=dict, status_code=201)
async def create_client(
    request: ClientCreateRequest,
    user: User = Depends(get_current_user)
):
    """Create a new client."""
    supabase = get_supabase_client()

    data = {
        "agency_id": str(user.agency_id),
        "name": request.name,
        "email": request.email,
        "phone": request.phone,
        "preferences": request.preferences.model_dump() if request.preferences else {},
        "notes": request.notes,
        "created_by": str(user.id)
    }

    try:
        result = supabase.table("clients").insert(data).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create client: {str(e)}")


@router.get("/{client_id}", response_model=dict)
async def get_client(
    client_id: str,
    user: User = Depends(get_current_user)
):
    """Get a specific client."""
    supabase = get_supabase_client()
    await set_agency_context(supabase, str(user.agency_id))

    result = supabase.table("clients")\
        .select("*")\
        .eq("id", client_id)\
        .single()\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Client not found")

    return result.data


@router.put("/{client_id}", response_model=dict)
async def update_client(
    client_id: str,
    request: ClientUpdateRequest,
    user: User = Depends(get_current_user)
):
    """Update a client."""
    supabase = get_supabase_client()

    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.email is not None:
        update_data["email"] = request.email
    if request.phone is not None:
        update_data["phone"] = request.phone
    if request.preferences is not None:
        update_data["preferences"] = request.preferences.model_dump()
    if request.notes is not None:
        update_data["notes"] = request.notes

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        result = supabase.table("clients")\
            .update(update_data)\
            .eq("id", client_id)\
            .eq("agency_id", str(user.agency_id))\
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Client not found")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")


@router.delete("/{client_id}")
async def delete_client(
    client_id: str,
    user: User = Depends(get_current_user)
):
    """Delete a client."""
    supabase = get_supabase_client()

    try:
        result = supabase.table("clients")\
            .delete()\
            .eq("id", client_id)\
            .eq("agency_id", str(user.agency_id))\
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Client not found")

        return {"message": "Client deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Delete failed: {str(e)}")


@router.get("/{client_id}/offers", response_model=List[dict])
async def get_client_offers(
    client_id: str,
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user)
):
    """Get all offers for a client."""
    supabase = get_supabase_client()
    await set_agency_context(supabase, str(user.agency_id))

    result = supabase.table("offers")\
        .select("*")\
        .eq("client_id", client_id)\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute()

    return result.data or []
