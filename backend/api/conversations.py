"""
Conversation API routes.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from core import get_supabase_client, set_agency_context
from models import User, ConversationStatus, TravelDates
from .auth import get_current_user

router = APIRouter()


class ConversationCreateRequest(BaseModel):
    title: Optional[str] = "New Conversation"
    client_id: Optional[str] = None


class ConversationUpdateRequest(BaseModel):
    title: Optional[str] = None
    status: Optional[ConversationStatus] = None
    destination: Optional[str] = None
    travel_dates: Optional[TravelDates] = None
    summary: Optional[str] = None


@router.get("", response_model=List[dict])
async def list_conversations(
    status: Optional[ConversationStatus] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user)
):
    """List conversations for the agency."""
    supabase = get_supabase_client()
    await set_agency_context(supabase, str(user.agency_id))

    query = supabase.table("conversations").select("*")

    if status:
        query = query.eq("status", status.value)

    result = query.order("updated_at", desc=True).limit(limit).execute()
    return result.data or []


@router.post("", response_model=dict, status_code=201)
async def create_conversation(
    request: ConversationCreateRequest,
    user: User = Depends(get_current_user)
):
    """Create a new AI conversation."""
    supabase = get_supabase_client()

    data = {
        "agency_id": str(user.agency_id),
        "user_id": str(user.id),
        "client_id": request.client_id,
        "title": request.title or "New Conversation",
        "status": "active"
    }

    try:
        result = supabase.table("conversations").insert(data).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create conversation: {str(e)}")


@router.get("/{conversation_id}", response_model=dict)
async def get_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user)
):
    """Get conversation details."""
    supabase = get_supabase_client()
    await set_agency_context(supabase, str(user.agency_id))

    # Get conversation
    result = supabase.table("conversations")\
        .select("*")\
        .eq("id", conversation_id)\
        .single()\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation = result.data

    # Get messages
    messages_result = supabase.table("messages")\
        .select("*")\
        .eq("conversation_id", conversation_id)\
        .order("created_at")\
        .execute()

    conversation["messages"] = messages_result.data or []

    return conversation


@router.put("/{conversation_id}", response_model=dict)
async def update_conversation(
    conversation_id: str,
    request: ConversationUpdateRequest,
    user: User = Depends(get_current_user)
):
    """Update conversation."""
    supabase = get_supabase_client()

    update_data = {}
    if request.title is not None:
        update_data["title"] = request.title
    if request.status is not None:
        update_data["status"] = request.status.value
    if request.destination is not None:
        update_data["destination"] = request.destination
    if request.travel_dates is not None:
        update_data["travel_dates"] = request.travel_dates.model_dump()
    if request.summary is not None:
        update_data["summary"] = request.summary

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        result = supabase.table("conversations")\
            .update(update_data)\
            .eq("id", conversation_id)\
            .eq("agency_id", str(user.agency_id))\
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")


@router.get("/{conversation_id}/messages", response_model=List[dict])
async def get_messages(
    conversation_id: str,
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(get_current_user)
):
    """Get messages for a conversation."""
    supabase = get_supabase_client()
    await set_agency_context(supabase, str(user.agency_id))

    result = supabase.table("messages")\
        .select("*")\
        .eq("conversation_id", conversation_id)\
        .order("created_at")\
        .limit(limit)\
        .execute()

    return result.data or []


@router.post("/{conversation_id}/messages", response_model=dict)
async def add_message(
    conversation_id: str,
    content: str,
    user: User = Depends(get_current_user)
):
    """Add a user message to conversation."""
    supabase = get_supabase_client()

    data = {
        "conversation_id": conversation_id,
        "role": "user",
        "content": content
    }

    try:
        result = supabase.table("messages").insert(data).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add message: {str(e)}")


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user)
):
    """Archive a conversation."""
    supabase = get_supabase_client()

    try:
        result = supabase.table("conversations")\
            .update({"status": "archived"})\
            .eq("id", conversation_id)\
            .eq("agency_id", str(user.agency_id))\
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {"message": "Conversation archived"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Archive failed: {str(e)}")
