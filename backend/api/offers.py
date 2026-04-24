"""
Offer management API routes.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field

from core import get_supabase_client, set_agency_context, settings
from models import (
    User, OfferStatus, OfferPricing, OfferContent,
    ItineraryDay, FlightSegment
)
from .auth import get_current_user

router = APIRouter()


class OfferCreateRequest(BaseModel):
    conversation_id: Optional[str] = None
    client_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=500)
    destination: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content_json: OfferContent
    pricing: OfferPricing
    itinerary: Optional[List[ItineraryDay]] = None
    flights: Optional[List[FlightSegment]] = None
    valid_until: Optional[str] = None  # ISO date


class OfferUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_json: Optional[OfferContent] = None
    pricing: Optional[OfferPricing] = None
    itinerary: Optional[List[ItineraryDay]] = None
    flights: Optional[List[FlightSegment]] = None
    valid_until: Optional[str] = None


class OfferApprovalRequest(BaseModel):
    notes: Optional[str] = None


class OfferRejectionRequest(BaseModel):
    reason: str = Field(..., min_length=1)


class OfferSendRequest(BaseModel):
    method: str = Field(default="email", pattern=r"^(email|link|manual)$")
    email_subject: Optional[str] = None
    email_body: Optional[str] = None


@router.get("", response_model=List[dict])
async def list_offers(
    status: Optional[OfferStatus] = Query(None),
    client_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user)
):
    """List offers for the agency."""
    supabase = get_supabase_client()
    await set_agency_context(supabase, str(user.agency_id))

    query = supabase.table("offers").select("*")

    if status:
        query = query.eq("status", status.value)
    if client_id:
        query = query.eq("client_id", client_id)

    result = query.order("created_at", desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()

    return result.data or []


@router.post("", response_model=dict, status_code=201)
async def create_offer(
    request: OfferCreateRequest,
    user: User = Depends(get_current_user)
):
    """Create a new offer (from AI or manual)."""
    supabase = get_supabase_client()

    data = {
        "agency_id": str(user.agency_id),
        "conversation_id": request.conversation_id,
        "client_id": request.client_id,
        "created_by": str(user.id),
        "title": request.title,
        "destination": request.destination,
        "description": request.description,
        "content_json": request.content_json.model_dump(),
        "pricing": request.pricing.model_dump(),
        "itinerary": [day.model_dump() for day in request.itinerary] if request.itinerary else None,
        "flights": [flight.model_dump() for flight in request.flights] if request.flights else None,
        "status": "draft",
        "valid_until": request.valid_until
    }

    try:
        result = supabase.table("offers").insert(data).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create offer: {str(e)}")


@router.get("/{offer_id}", response_model=dict)
async def get_offer(
    offer_id: str,
    user: User = Depends(get_current_user)
):
    """Get offer details."""
    supabase = get_supabase_client()
    await set_agency_context(supabase, str(user.agency_id))

    result = supabase.table("offers")\
        .select("*")\
        .eq("id", offer_id)\
        .single()\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Offer not found")

    return result.data


@router.put("/{offer_id}", response_model=dict)
async def update_offer(
    offer_id: str,
    request: OfferUpdateRequest,
    user: User = Depends(get_current_user)
):
    """Update an offer (only when in draft or rejected)."""
    supabase = get_supabase_client()

    # Get current offer to check status
    current = supabase.table("offers")\
        .select("status")\
        .eq("id", offer_id)\
        .eq("agency_id", str(user.agency_id))\
        .single()\
        .execute()

    if not current.data:
        raise HTTPException(status_code=404, detail="Offer not found")

    if current.data["status"] not in ["draft", "rejected"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot edit offer in status: {current.data['status']}"
        )

    update_data = {}
    if request.title is not None:
        update_data["title"] = request.title
    if request.description is not None:
        update_data["description"] = request.description
    if request.content_json is not None:
        update_data["content_json"] = request.content_json.model_dump()
    if request.pricing is not None:
        update_data["pricing"] = request.pricing.model_dump()
    if request.itinerary is not None:
        update_data["itinerary"] = [day.model_dump() for day in request.itinerary]
    if request.flights is not None:
        update_data["flights"] = [flight.model_dump() for flight in request.flights]
    if request.valid_until is not None:
        update_data["valid_until"] = request.valid_until

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        result = supabase.table("offers")\
            .update(update_data)\
            .eq("id", offer_id)\
            .eq("agency_id", str(user.agency_id))\
            .execute()

        return result.data[0] if result.data else {}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")


@router.post("/{offer_id}/submit", response_model=dict)
async def submit_for_approval(
    offer_id: str,
    user: User = Depends(get_current_user)
):
    """Submit offer for approval."""
    supabase = get_supabase_client()

    try:
        result = supabase.table("offers")\
            .update({
                "status": "pending_approval",
                "submitted_for_approval_at": "now()"
            })\
            .eq("id", offer_id)\
            .eq("agency_id", str(user.agency_id))\
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Offer not found")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Submit failed: {str(e)}")


@router.post("/{offer_id}/approve", response_model=dict)
async def approve_offer(
    offer_id: str,
    request: OfferApprovalRequest,
    user: User = Depends(get_current_user)
):
    """Approve an offer."""
    supabase = get_supabase_client()

    # Verify user has approval permission (admin can always approve)
    if user.role.value != "admin":
        # Get offer creator
        offer = supabase.table("offers")\
            .select("created_by")\
            .eq("id", offer_id)\
            .eq("agency_id", str(user.agency_id))\
            .single()\
            .execute()

        if offer.data and offer.data["created_by"] == str(user.id):
            raise HTTPException(
                status_code=403,
                detail="You cannot approve your own offer"
            )

    try:
        result = supabase.table("offers")\
            .update({
                "status": "approved",
                "approved_by": str(user.id),
                "approved_at": "now()"
            })\
            .eq("id", offer_id)\
            .eq("agency_id", str(user.agency_id))\
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Offer not found")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Approval failed: {str(e)}")


@router.post("/{offer_id}/reject", response_model=dict)
async def reject_offer(
    offer_id: str,
    request: OfferRejectionRequest,
    user: User = Depends(get_current_user)
):
    """Reject an offer with reason."""
    supabase = get_supabase_client()

    try:
        result = supabase.table("offers")\
            .update({
                "status": "rejected",
                "rejection_reason": request.reason
            })\
            .eq("id", offer_id)\
            .eq("agency_id", str(user.agency_id))\
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Offer not found")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Rejection failed: {str(e)}")


@router.post("/{offer_id}/send", response_model=dict)
async def send_offer(
    offer_id: str,
    request: OfferSendRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
):
    """Send approved offer to client."""
    supabase = get_supabase_client()
    await set_agency_context(supabase, str(user.agency_id))

    # Get offer and verify it's approved
    offer = supabase.table("offers")\
        .select("*,clients(email,name)")\
        .eq("id", offer_id)\
        .eq("agency_id", str(user.agency_id))\
        .single()\
        .execute()

    if not offer.data:
        raise HTTPException(status_code=404, detail="Offer not found")

    if offer.data["status"] not in ["approved", "sent"]:
        raise HTTPException(
            status_code=400,
            detail="Offer must be approved before sending"
        )

    # Update status to sent
    update_data = {
        "status": "sent",
        "sent_at": "now()",
        "sent_method": request.method
    }

    result = supabase.table("offers")\
        .update(update_data)\
        .eq("id", offer_id)\
        .execute()

    # TODO: Background task for email sending
    # if request.method == "email":
    #     background_tasks.add_task(send_offer_email, offer.data, request.email_subject, request.email_body)

    return {
        "message": f"Offer sent via {request.method}",
        "offer": result.data[0] if result.data else None
    }


@router.post("/{offer_id}/pdf")
async def generate_pdf(
    offer_id: str,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
):
    """Generate PDF for offer (triggers async generation)."""
    # TODO: Implement PDF generation with WeasyPrint
    # This would:
    # 1. Get offer data
    # 2. Render HTML template with agency branding
    # 3. Generate PDF with WeasyPrint
    # 4. Upload to Supabase Storage
    # 5. Update offer.pdf_url

    return {
        "message": "PDF generation started",
        "offer_id": offer_id
    }


@router.delete("/{offer_id}")
async def delete_offer(
    offer_id: str,
    user: User = Depends(get_current_user)
):
    """Delete an offer (only draft or rejected)."""
    supabase = get_supabase_client()

    # Get current status
    current = supabase.table("offers")\
        .select("status")\
        .eq("id", offer_id)\
        .eq("agency_id", str(user.agency_id))\
        .single()\
        .execute()

    if not current.data:
        raise HTTPException(status_code=404, detail="Offer not found")

    if current.data["status"] not in ["draft", "rejected"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete offer in status: {current.data['status']}"
        )

    try:
        result = supabase.table("offers")\
            .delete()\
            .eq("id", offer_id)\
            .eq("agency_id", str(user.agency_id))\
            .execute()

        return {"message": "Offer deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Delete failed: {str(e)}")
