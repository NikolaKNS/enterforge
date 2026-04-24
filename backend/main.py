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

# CORS middleware - Allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Next.js dev server
        "http://localhost:3001",
        "https://tripforge.app",       # Production
        "https://*.tripforge.app",     # Subdomains
    ],
    allow_credentials=True,
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

@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Send a message to the TripForge AI agent.
    Creates or continues a conversation and returns the agent's response.
    """
    from agent.agent import TripForgeAgent, create_agent
    from core.supabase import get_supabase_client

    supabase = get_supabase_client()

    # Get agency info
    agency_result = supabase.table("agencies")\
        .select("name")\
        .eq("id", request.agency_id)\
        .single()\
        .execute()

    if not agency_result.data:
        raise HTTPException(status_code=404, detail="Agency not found")

    agency_name = agency_result.data["name"]

    # Create or load conversation
    if request.conversation_id:
        # Load existing conversation
        agent = await create_agent(request.agency_id, agency_name)
        await agent.load_conversation(request.conversation_id)
    else:
        # Create new conversation
        agent = await create_agent(request.agency_id, agency_name)
        conversation_id = await agent.start_conversation(
            user_id=request.user_id or "anonymous",
            client_id=request.client_info.get("client_id") if request.client_info else None
        )
        logger.info(f"Created new conversation: {conversation_id}")

    # Send message to agent
    response = await agent.send_message(request.message)

    # Check if offer was created (conversation status would be pending_approval)
    conv_check = supabase.table("conversations")\
        .select("status")\
        .eq("id", agent.conversation_id)\
        .single()\
        .execute()

    requires_approval = False
    if conv_check.data and conv_check.data.get("status") == "pending_approval":
        requires_approval = True

    return ChatResponse(
        conversation_id=agent.conversation_id,
        message=response.get("message", ""),
        requires_approval=requires_approval,
        tool_calls=response.get("tool_calls")
    )


# ==========================================
# Conversation Endpoints
# ==========================================

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
    from core.supabase import get_supabase_client

    supabase = get_supabase_client()

    query = supabase.table("conversations")\
        .select("*")\
        .eq("agency_id", agency_id)

    if status:
        query = query.eq("status", status)

    result = query.order("updated_at", desc=True).execute()

    return {
        "conversations": result.data or [],
        "count": len(result.data) if result.data else 0
    }


@app.get("/api/conversation/{conversation_id}/messages", tags=["Conversations"])
async def get_conversation_messages(
    conversation_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get full message history for a conversation.
    """
    from core.supabase import get_supabase_client

    supabase = get_supabase_client()

    # Get conversation details
    conv_result = supabase.table("conversations")\
        .select("*")\
        .eq("id", conversation_id)\
        .single()\
        .execute()

    if not conv_result.data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages
    messages_result = supabase.table("messages")\
        .select("*")\
        .eq("conversation_id", conversation_id)\
        .order("created_at")\
        .execute()

    return {
        "conversation": conv_result.data,
        "messages": messages_result.data or []
    }


@app.post("/api/conversation/{conversation_id}/close", tags=["Conversations"])
async def close_conversation(
    conversation_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Close/archived a conversation."""
    from core.supabase import get_supabase_client

    supabase = get_supabase_client()

    result = supabase.table("conversations")\
        .update({"status": "closed"})\
        .eq("id", conversation_id)\
        .execute()

    if not result.data:
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
    from core.supabase import get_supabase_client

    supabase = get_supabase_client()

    query = supabase.table("offers")\
        .select("*")\
        .eq("agency_id", agency_id)

    if status:
        query = query.eq("status", status)

    result = query.order("created_at", desc=True).execute()

    return {
        "offers": result.data or [],
        "count": len(result.data) if result.data else 0
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
    from core.supabase import get_supabase_client

    supabase = get_supabase_client()

    result = supabase.table("agencies")\
        .select("name, slug, branding_config, settings")\
        .eq("slug", slug)\
        .single()\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Agency not found")

    agency = result.data

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
    from core.supabase import get_supabase_client

    supabase = get_supabase_client()

    result = supabase.table("agencies")\
        .select("id, name, slug")\
        .eq("slug", slug)\
        .execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Agency not found")

    return {
        "exists": True,
        "agency": result.data[0]
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
    from core.supabase import get_supabase_client

    supabase = get_supabase_client()

    query = supabase.table("clients")\
        .select("*")\
        .eq("agency_id", agency_id)

    if search:
        query = query.or_(f"name.ilike.%{search}%,email.ilike.%{search}%")

    result = query.order("created_at", desc=True).execute()

    return {
        "clients": result.data or [],
        "count": len(result.data) if result.data else 0
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
