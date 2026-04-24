#!/usr/bin/env python3
"""
TripForge Enterprise - FastAPI Application
AI Travel Agent SaaS for Travel Agencies
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Key for simple authentication
API_KEY = os.getenv("TRIPFORGE_API_KEY", "dev-key-change-in-production")


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key from header."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing x-api-key header")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    logger.info("Starting TripForge API")
    logger.info(f"API Key configured: {API_KEY[:8]}...")
    yield
    logger.info("Shutting down TripForge API")


# Create FastAPI application
app = FastAPI(
    title="TripForge Enterprise API",
    description="AI Travel Agent SaaS for Travel Agencies",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware - Allow ALL origins (development only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error"
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "internal_error"
            }
        }
    )


# ==========================================
# Health Check
# ==========================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"])
async def root():
    """API root endpoint."""
    return {
        "name": "TripForge Enterprise API",
        "version": "1.0.0",
        "documentation": "/docs"
    }


# ==========================================
# Pydantic Models
# ==========================================

class ChatRequest(BaseModel):
    agency_id: str
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    client_info: Optional[dict] = None


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    requires_approval: bool = False
    tool_calls: Optional[list] = None


class AgencyConfigResponse(BaseModel):
    name: str
    slug: str
    branding_config: dict
    settings: dict


class OfferApproveRequest(BaseModel):
    approved_by: str
    notes: Optional[str] = None


class OfferSendRequest(BaseModel):
    method: str = "email"  # email, link, manual
    email_subject: Optional[str] = None
    email_body: Optional[str] = None


# ==========================================
# Chat Endpoint
# ==========================================

# Mock data for testing without database
MOCK_AGENCIES = {
    "ba991771-fe20-488f-99bd-b8aea9fb9295": {"name": "Demo Travel Agency", "slug": "demo"}
}


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Send a message to the TripForge AI agent.
    Creates or continues a conversation and returns the agent's response.
    """
    import traceback

    try:
        from agent.agent import TripForgeAgent
        from uuid import uuid4

        # Use mock agency data if database is unavailable
        agency_data = MOCK_AGENCIES.get(request.agency_id)
        agency_name = agency_data["name"] if agency_data else "Travel Agency"

        # Get or create conversation
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = str(uuid4())
            # Create new conversation
            new_conversation = {
                "id": conversation_id,
                "agency_id": request.agency_id,
                "user_id": "user-001",
                "client_id": None,
                "title": request.message[:50] if request.message else "New Conversation",
                "status": "active",
                "destination": None,
                "travel_dates": None,
                "summary": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            MOCK_CONVERSATIONS.append(new_conversation)
            MOCK_MESSAGES[conversation_id] = []

        # Create agent
        agent = TripForgeAgent(agency_id=request.agency_id, agency_name=agency_name)
        agent.conversation_id = conversation_id

        # Store user message
        user_message = {
            "id": str(uuid4()),
            "conversation_id": conversation_id,
            "role": "user",
            "content": request.message,
            "created_at": datetime.now().isoformat()
        }
        if conversation_id not in MOCK_MESSAGES:
            MOCK_MESSAGES[conversation_id] = []
        MOCK_MESSAGES[conversation_id].append(user_message)

        # Send message to agent
        response = await agent.send_message(request.message)
        logger.info(f"Agent response: {response}")

        # Handle both "message" and "content" keys from agent response
        message_text = response.get("message") or response.get("content", "")
        logger.info(f"Extracted message: {message_text[:100] if message_text else 'EMPTY'}")

        # Store assistant message
        assistant_message = {
            "id": str(uuid4()),
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": message_text,
            "model": "claude-sonnet-4-20250514",
            "created_at": datetime.now().isoformat()
        }
        MOCK_MESSAGES[conversation_id].append(assistant_message)

        return ChatResponse(
            conversation_id=conversation_id,
            message=message_text,
            requires_approval=False,
            tool_calls=response.get("tool_calls")
        )
    except Exception as e:
        logger.error(f"Chat error: {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        # Return a mock response if Ollama fails
        return ChatResponse(
            conversation_id=str(uuid4()),
            message="I'd be happy to help you plan a trip! To get started, could you tell me:\n\n1. Your preferred travel dates\n2. How many travelers?\n3. Departure city\n4. Any specific interests (museums, food, nightlife, etc.)?\n\nOnce I have these details, I can search for flights and create a personalized itinerary for you.",
            requires_approval=False,
            tool_calls=None
        )


# ==========================================
# Conversation Endpoints
# ==========================================

# Mock offers for testing
MOCK_OFFERS = [
    {
        "id": "offer-001",
        "agency_id": "ba991771-fe20-488f-99bd-b8aea9fb9295",
        "conversation_id": "conv-001",
        "client_id": None,
        "created_by": "user-001",
        "title": "Paris Luxury Package",
        "destination": "Paris, France",
        "description": "7-day luxury trip to Paris including flights, 5-star hotel, and guided tours",
        "content_json": {"itinerary": ["Day 1: Arrival", "Day 2: Louvre Museum", "Day 3: Eiffel Tower"]},
        "pricing": {"base_cost": "2500.00", "markup": "500.00", "total": "3000.00", "currency": "USD"},
        "status": "pending_approval",
        "created_at": "2024-01-15T14:30:00",
        "updated_at": "2024-01-15T14:30:00"
    },
    {
        "id": "offer-002",
        "agency_id": "ba991771-fe20-488f-99bd-b8aea9fb9295",
        "conversation_id": "conv-002",
        "client_id": None,
        "created_by": "user-001",
        "title": "Tokyo Business Package",
        "destination": "Tokyo, Japan",
        "description": "5-day business trip package with business class flights",
        "content_json": {"itinerary": ["Day 1: Arrival", "Day 2-4: Business meetings", "Day 5: Departure"]},
        "pricing": {"base_cost": "4500.00", "markup": "900.00", "total": "5400.00", "currency": "USD"},
        "status": "approved",
        "approved_by": "manager@agency.com",
        "approved_at": "2024-01-14T10:00:00",
        "created_at": "2024-01-10T16:00:00",
        "updated_at": "2024-01-14T10:00:00"
    }
]

# Mock clients for testing
MOCK_CLIENTS = [
    {
        "id": "client-001",
        "agency_id": "ba991771-fe20-488f-99bd-b8aea9fb9295",
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "+1-555-0123",
        "preferences": {"class": "business", "dietary": "vegetarian"},
        "created_at": "2024-01-01T00:00:00"
    },
    {
        "id": "client-002",
        "agency_id": "ba991771-fe20-488f-99bd-b8aea9fb9295",
        "name": "Sarah Johnson",
        "email": "sarah.j@example.com",
        "phone": "+1-555-0456",
        "preferences": {"class": "economy", "activities": ["museums", "food"]},
        "created_at": "2024-01-05T00:00:00"
    }
]

# Mock conversations for testing
MOCK_CONVERSATIONS = [
    {
        "id": "conv-001",
        "agency_id": "ba991771-fe20-488f-99bd-b8aea9fb9295",
        "client_id": None,
        "user_id": "user-001",
        "title": "Paris Trip Planning",
        "status": "active",
        "destination": "Paris, France",
        "travel_dates": {"start": "2024-06-15", "end": "2024-06-22"},
        "summary": "Planning a week-long trip to Paris with focus on museums and cuisine",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T14:20:00"
    },
    {
        "id": "conv-002",
        "agency_id": "ba991771-fe20-488f-99bd-b8aea9fb9295",
        "client_id": None,
        "user_id": "user-001",
        "title": "Tokyo Business Trip",
        "status": "pending_approval",
        "destination": "Tokyo, Japan",
        "travel_dates": {"start": "2024-03-10", "end": "2024-03-15"},
        "summary": "Business trip to Tokyo with 2 days leisure",
        "created_at": "2024-01-10T09:15:00",
        "updated_at": "2024-01-14T16:45:00"
    }
]

# Mock messages for testing
MOCK_MESSAGES = {
    "conv-001": [
        {
            "id": "msg-001",
            "conversation_id": "conv-001",
            "role": "user",
            "content": "I want to plan a trip to Paris",
            "created_at": "2024-01-15T10:30:00"
        },
        {
            "id": "msg-002",
            "conversation_id": "conv-001",
            "role": "assistant",
            "content": "I'd love to help you plan a trip to Paris! Could you tell me your preferred travel dates and how many travelers?",
            "created_at": "2024-01-15T10:31:00"
        },
        {
            "id": "msg-003",
            "conversation_id": "conv-001",
            "role": "user",
            "content": "June 15-22, 2 travelers",
            "created_at": "2024-01-15T10:35:00"
        },
        {
            "id": "msg-004",
            "conversation_id": "conv-001",
            "role": "assistant",
            "content": "Perfect! I've noted June 15-22 for 2 travelers. Let me search for flights and hotels in Paris for you.",
            "created_at": "2024-01-15T10:36:00"
        }
    ],
    "conv-002": [
        {
            "id": "msg-005",
            "conversation_id": "conv-002",
            "role": "user",
            "content": "Need a business trip to Tokyo in March",
            "created_at": "2024-01-10T09:15:00"
        },
        {
            "id": "msg-006",
            "conversation_id": "conv-002",
            "role": "assistant",
            "content": "I can help with your Tokyo business trip. What dates in March work for you?",
            "created_at": "2024-01-10T09:16:00"
        }
    ]
}


@app.get("/api/conversations/{agency_id}", tags=["Conversations"])
async def get_conversations(
    agency_id: str,
    status: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """
    Get all conversations for an agency.
    Optionally filter by status (active, pending_approval, closed, archived).
    """
    conversations = [c for c in MOCK_CONVERSATIONS if c["agency_id"] == agency_id]

    if status:
        conversations = [c for c in conversations if c["status"] == status]

    return {
        "conversations": conversations,
        "count": len(conversations)
    }


class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Conversation"
    client_id: Optional[str] = None


@app.post("/api/conversations", tags=["Conversations"])
async def create_conversation(
    request: CreateConversationRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new conversation.
    """
    from uuid import uuid4

    new_conversation = {
        "id": str(uuid4()),
        "agency_id": "ba991771-fe20-488f-99bd-b8aea9fb9295",  # Mock agency
        "user_id": "user-001",  # Mock user
        "client_id": request.client_id,
        "title": request.title or "New Conversation",
        "status": "active",
        "destination": None,
        "travel_dates": None,
        "summary": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    MOCK_CONVERSATIONS.append(new_conversation)
    # Initialize empty message list for this conversation
    MOCK_MESSAGES[new_conversation["id"]] = []

    return new_conversation


@app.get("/api/conversation/{conversation_id}/messages", tags=["Conversations"])
async def get_conversation_messages(
    conversation_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get full message history for a conversation.
    """
    # Find conversation in mock data
    conversation = None
    for c in MOCK_CONVERSATIONS:
        if c["id"] == conversation_id:
            conversation = c
            break

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages from mock data
    messages = MOCK_MESSAGES.get(conversation_id, [])

    return {
        "conversation": conversation,
        "messages": messages
    }


@app.post("/api/conversation/{conversation_id}/close", tags=["Conversations"])
async def close_conversation(
    conversation_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Close/archived a conversation."""
    # Find and update in mock data
    conversation = None
    for c in MOCK_CONVERSATIONS:
        if c["id"] == conversation_id:
            c["status"] = "closed"
            c["updated_at"] = datetime.now().isoformat()
            conversation = c
            break

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation closed", "conversation_id": conversation_id}


# ==========================================
# Offer Endpoints
# ==========================================

@app.post("/api/offer/{offer_id}/approve", tags=["Offers"])
async def approve_offer(
    offer_id: str,
    request: OfferApproveRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Approve an offer (agency staff approval).
    Changes status from draft to approved.
    """
    from core.supabase import get_supabase_client

    supabase = get_supabase_client()

    # Get current offer
    offer_result = supabase.table("offers")\
        .select("*")\
        .eq("id", offer_id)\
        .single()\
        .execute()

    if not offer_result.data:
        raise HTTPException(status_code=404, detail="Offer not found")

    offer = offer_result.data

    if offer.get("status") not in ["draft", "pending_approval"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve offer in status: {offer.get('status')}"
        )

    # Update offer
    update_data = {
        "status": "approved",
        "approved_by": request.approved_by,
        "approved_at": datetime.now().isoformat(),
        "notes": request.notes
    }

    result = supabase.table("offers")\
        .update(update_data)\
        .eq("id", offer_id)\
        .execute()

    return {
        "message": "Offer approved successfully",
        "offer_id": offer_id,
        "status": "approved"
    }


@app.post("/api/offer/{offer_id}/send", tags=["Offers"])
async def send_offer(
    offer_id: str,
    request: OfferSendRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Send approved offer to client.
    Changes status from approved to sent.
    """
    from core.supabase import get_supabase_client

    supabase = get_supabase_client()

    # Get current offer
    offer_result = supabase.table("offers")\
        .select("*")\
        .eq("id", offer_id)\
        .single()\
        .execute()

    if not offer_result.data:
        raise HTTPException(status_code=404, detail="Offer not found")

    offer = offer_result.data

    if offer.get("status") != "approved":
        raise HTTPException(
            status_code=400,
            detail=f"Offer must be approved before sending. Current status: {offer.get('status')}"
        )

    # Update offer
    update_data = {
        "status": "sent",
        "sent_at": datetime.now().isoformat(),
        "sent_method": request.method
    }

    result = supabase.table("offers")\
        .update(update_data)\
        .eq("id", offer_id)\
        .execute()

    return {
        "message": f"Offer sent via {request.method}",
        "offer_id": offer_id,
        "status": "sent",
        "method": request.method
    }


@app.get("/api/offer/{offer_id}", tags=["Offers"])
async def get_offer(
    offer_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get offer details."""
    from core.supabase import get_supabase_client

    supabase = get_supabase_client()

    result = supabase.table("offers")\
        .select("*")\
        .eq("id", offer_id)\
        .single()\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Offer not found")

    return result.data


@app.get("/api/offers/{agency_id}", tags=["Offers"])
async def list_offers(
    agency_id: str,
    status: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """List all offers for an agency."""
    offers = [o for o in MOCK_OFFERS if o["agency_id"] == agency_id]

    if status:
        offers = [o for o in offers if o["status"] == status]

    return {
        "offers": offers,
        "count": len(offers)
    }


@app.post("/api/offer/{offer_id}/reject", tags=["Offers"])
async def reject_offer(
    offer_id: str,
    reason: str,
    api_key: str = Depends(verify_api_key)
):
    """Reject an offer with reason."""
    from core.supabase import get_supabase_client

    supabase = get_supabase_client()

    result = supabase.table("offers")\
        .update({
            "status": "rejected",
            "rejection_reason": reason
        })\
        .eq("id", offer_id)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Offer not found")

    return {
        "message": "Offer rejected",
        "offer_id": offer_id,
        "reason": reason
    }


# ==========================================
# Agency Config Endpoint (White-label)
# ==========================================

@app.get("/api/agency/{slug}/config", response_model=AgencyConfigResponse, tags=["Agency"])
async def get_agency_config(
    slug: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get agency branding configuration for white-label frontend.
    Used by Next.js frontend to apply agency branding.
    """
    # Find agency by slug in mock data
    agency = None
    for a in MOCK_AGENCIES.values():
        if a.get("slug") == slug:
            agency = a
            break

    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    return AgencyConfigResponse(
        name=agency["name"],
        slug=agency["slug"],
        branding_config=agency.get("branding_config", {}),
        settings=agency.get("settings", {})
    )


@app.get("/api/agency/{slug}/verify", tags=["Agency"])
async def verify_agency_slug(
    slug: str,
    api_key: str = Depends(verify_api_key)
):
    """Verify if an agency slug exists (for subdomain routing)."""
    # Find agency by slug in mock data
    agency = None
    for a_id, a in MOCK_AGENCIES.items():
        if a.get("slug") == slug:
            agency = {"id": a_id, "name": a["name"], "slug": a["slug"]}
            break

    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")

    return {
        "exists": True,
        "agency": agency
    }


# ==========================================
# Client Endpoints
# ==========================================

@app.get("/api/clients/{agency_id}", tags=["Clients"])
async def list_clients(
    agency_id: str,
    search: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """List all clients for an agency."""
    clients = [c for c in MOCK_CLIENTS if c["agency_id"] == agency_id]

    if search:
        search_lower = search.lower()
        clients = [c for c in clients if search_lower in c["name"].lower() or search_lower in c["email"].lower()]

    return {
        "clients": clients,
        "count": len(clients)
    }


@app.post("/api/clients/{agency_id}", tags=["Clients"])
async def create_client(
    agency_id: str,
    client: dict,
    api_key: str = Depends(verify_api_key)
):
    """Create a new client."""
    from core.supabase import get_supabase_client

    supabase = get_supabase_client()

    client_data = {
        "agency_id": agency_id,
        "name": client.get("name"),
        "email": client.get("email"),
        "phone": client.get("phone"),
        "preferences": client.get("preferences", {}),
        "created_by": client.get("created_by")
    }

    result = supabase.table("clients").insert(client_data).execute()

    return {
        "message": "Client created",
        "client": result.data[0] if result.data else None
    }


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
