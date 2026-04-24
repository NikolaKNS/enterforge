"""
Client information tool.
"""

from typing import Dict, Any, Optional

from core import get_supabase_client
from .base import ToolError


async def get_client_info(
    client_id: str,
    _agency_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get detailed information about a client.

    Args:
        client_id: Client UUID
        _agency_id: Injected agency ID (for security)

    Returns:
        Client information

    Raises:
        ToolError: If client not found or not in agency
    """
    if not client_id:
        raise ToolError("Client ID is required")

    if not _agency_id:
        raise ToolError("Agency context required")

    try:
        supabase = get_supabase_client()

        # Query with agency check
        result = supabase.table("clients")\
            .select("*")\
            .eq("id", client_id)\
            .eq("agency_id", _agency_id)\
            .single()\
            .execute()

        if not result.data:
            raise ToolError(f"Client not found: {client_id}")

        client = result.data

        # Get client's offer history
        offers_result = supabase.table("offers")\
            .select("id,title,status,created_at,total_cost:pricing->total")\
            .eq("client_id", client_id)\
            .eq("agency_id", _agency_id)\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()

        # Format response
        preferences = client.get("preferences", {})

        return {
            "id": client.get("id"),
            "name": client.get("name"),
            "email": client.get("email"),
            "phone": client.get("phone"),
            "preferences": {
                "budget_range": preferences.get("budget_range", "Not specified"),
                "travel_style": preferences.get("travel_style", "Not specified"),
                "dietary_restrictions": preferences.get("dietary_restrictions", []),
                "accessibility_needs": preferences.get("accessibility_needs"),
                "preferred_airlines": preferences.get("preferred_airlines", []),
                "seat_preference": preferences.get("seat_preference"),
                "room_preference": preferences.get("room_preference"),
                "activity_level": preferences.get("activity_level", "Not specified")
            },
            "notes": client.get("notes", ""),
            "created_at": client.get("created_at"),
            "offer_history": offers_result.data or [],
            "total_offers": len(offers_result.data) if offers_result.data else 0
        }

    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Failed to get client info: {str(e)}")


async def search_clients(
    query: str,
    _agency_id: str = None,
    limit: int = 10,
    **kwargs
) -> list:
    """
    Search for clients by name or email.

    Args:
        query: Search query string
        _agency_id: Injected agency ID
        limit: Max results

    Returns:
        List of matching clients
    """
    if not query or len(query) < 2:
        raise ToolError("Search query must be at least 2 characters")

    if not _agency_id:
        raise ToolError("Agency context required")

    try:
        supabase = get_supabase_client()

        result = supabase.table("clients")\
            .select("id,name,email,phone")\
            .eq("agency_id", _agency_id)\
            .or_(f"name.ilike.%{query}%,email.ilike.%{query}%")\
            .limit(limit)\
            .execute()

        return result.data or []

    except Exception as e:
        raise ToolError(f"Client search failed: {str(e)}")
