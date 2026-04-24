"""
Offer creation and management tools.
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime, date, timedelta
from uuid import uuid4

from core import get_supabase_client
from models import OfferStatus
from .base import ToolError


async def save_offer_draft(
    title: str,
    destination: str,
    _agency_id: str = None,
    _conversation_id: str = None,
    description: Optional[str] = None,
    itinerary: Optional[List[Dict]] = None,
    flights: Optional[List[Dict]] = None,
    pricing: Optional[Dict[str, Any]] = None,
    content_json: Optional[Dict] = None,
    client_id: Optional[str] = None,
    valid_days: int = 7,
    **kwargs
) -> Dict[str, Any]:
    """
    Save an offer as a draft to the database.

    Args:
        title: Offer title
        destination: Destination city/country
        description: Offer description
        itinerary: Day-by-day itinerary structure
        flights: Flight segments
        pricing: Pricing breakdown
        content_json: Full structured offer content
        client_id: Optional client ID to associate
        valid_days: Number of days offer is valid (default 7)
        _agency_id: Injected agency ID
        _conversation_id: Injected conversation ID

    Returns:
        Created offer data

    Raises:
        ToolError: If save fails
    """
    if not _agency_id:
        raise ToolError("Agency context required")

    if not title or not destination:
        raise ToolError("Title and destination are required")

    # Calculate valid until date
    valid_until = (datetime.now() + timedelta(days=valid_days)).strftime("%Y-%m-%d")

    # Build content_json if not provided
    if content_json is None:
        content_json = {
            "trip_title": title,
            "destination": destination,
            "description": description or "",
            "highlights": [],
            "included": [],
            "excluded": [],
            "notes": ""
        }

    # Ensure pricing has required structure
    if pricing is None:
        pricing = {
            "base_cost": "0",
            "markup": "0",
            "fees": "0",
            "taxes": "0",
            "total": "0",
            "currency": "EUR"
        }

    offer_data = {
        "agency_id": _agency_id,
        "conversation_id": _conversation_id,
        "client_id": client_id,
        "created_by": kwargs.get("_user_id"),  # Should be injected
        "title": title,
        "destination": destination,
        "description": description,
        "content_json": content_json,
        "pricing": pricing,
        "itinerary": itinerary or [],
        "flights": flights or [],
        "status": OfferStatus.DRAFT.value,
        "valid_until": valid_until
    }

    try:
        supabase = get_supabase_client()

        result = supabase.table("offers").insert(offer_data).execute()

        if not result.data:
            raise ToolError("Failed to save offer")

        created_offer = result.data[0]

        return {
            "success": True,
            "offer_id": created_offer.get("id"),
            "status": created_offer.get("status"),
            "title": created_offer.get("title"),
            "destination": created_offer.get("destination"),
            "valid_until": valid_until,
            "message": f"Offer '{title}' saved as draft. Review and approve before sending to client.",
            "url": f"/offers/{created_offer.get('id')}"
        }

    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Failed to save offer: {str(e)}")


async def update_offer(
    offer_id: str,
    updates: Dict[str, Any],
    _agency_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update an existing offer.

    Args:
        offer_id: Offer UUID
        updates: Fields to update
        _agency_id: Injected agency ID

    Returns:
        Updated offer
    """
    if not _agency_id:
        raise ToolError("Agency context required")

    try:
        supabase = get_supabase_client()

        # Check offer exists and is editable
        existing = supabase.table("offers")\
            .select("status")\
            .eq("id", offer_id)\
            .eq("agency_id", _agency_id)\
            .single()\
            .execute()

        if not existing.data:
            raise ToolError("Offer not found")

        if existing.data["status"] not in ["draft", "rejected"]:
            raise ToolError(f"Cannot edit offer in status: {existing.data['status']}")

        # Apply updates
        update_data = {}
        for key, value in updates.items():
            if key in ["title", "destination", "description", "content_json",
                       "pricing", "itinerary", "flights", "valid_until"]:
                update_data[key] = value

        if not update_data:
            raise ToolError("No valid fields to update")

        result = supabase.table("offers")\
            .update(update_data)\
            .eq("id", offer_id)\
            .eq("agency_id", _agency_id)\
            .execute()

        if not result.data:
            raise ToolError("Update failed")

        return {
            "success": True,
            "offer": result.data[0],
            "message": "Offer updated successfully"
        }

    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Failed to update offer: {str(e)}")


async def submit_for_approval(
    offer_id: str,
    _agency_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Submit an offer for approval.

    Args:
        offer_id: Offer UUID
        _agency_id: Injected agency ID

    Returns:
        Updated offer
    """
    if not _agency_id:
        raise ToolError("Agency context required")

    try:
        supabase = get_supabase_client()

        result = supabase.table("offers")\
            .update({
                "status": OfferStatus.PENDING_APPROVAL.value,
                "submitted_for_approval_at": "now()"
            })\
            .eq("id", offer_id)\
            .eq("agency_id", _agency_id)\
            .eq("status", OfferStatus.DRAFT.value)\
            .execute()

        if not result.data:
            raise ToolError("Offer not found or already submitted")

        return {
            "success": True,
            "offer_id": offer_id,
            "status": OfferStatus.PENDING_APPROVAL.value,
            "message": "Offer submitted for approval"
        }

    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Failed to submit offer: {str(e)}")
