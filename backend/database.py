"""
Supabase database client for TripForge.
Handles multi-tenant queries with automatic agency_id injection.
"""

import os
from typing import Optional, List, Dict, Any
from contextvars import ContextVar
from supabase import create_client, Client
from postgrest.exceptions import APIError

# Context variable for current agency ID (set per-request)
current_agency_id: ContextVar[Optional[str]] = ContextVar('agency_id', default=None)


class DatabaseClient:
    """Supabase client wrapper with multi-tenant support."""

    _instance: Optional['DatabaseClient'] = None
    _client: Optional[Client] = None

    def __new__(cls) -> 'DatabaseClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

            if not supabase_url or not supabase_key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment"
                )

            self._client = create_client(supabase_url, supabase_key)

    @property
    def client(self) -> Client:
        """Get the raw Supabase client."""
        if self._client is None:
            raise RuntimeError("Database client not initialized")
        return self._client

    def set_agency_context(self, agency_id: str) -> None:
        """
        Set the agency context for RLS policies.
        Must be called before any database operations in a request.
        """
        current_agency_id.set(agency_id)
        # Set in Postgres session for RLS policies
        self.client.rpc('set_config', {
            'key': 'app.current_agency_id',
            'value': agency_id
        }).execute()

    def clear_agency_context(self) -> None:
        """Clear the agency context."""
        current_agency_id.set(None)

    # ==========================================
    # Agency Operations
    # ==========================================

    async def create_agency(
        self,
        name: str,
        slug: str,
        branding_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a new agency (tenant)."""
        data = {
            'name': name,
            'slug': slug,
            'branding_config': branding_config or {}
        }

        result = self.client.table('agencies').insert(data).execute()
        return result.data[0] if result.data else None

    async def get_agency_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get agency by slug (for subdomain routing)."""
        result = self.client.table('agencies').select('*').eq('slug', slug).execute()
        return result.data[0] if result.data else None

    async def get_agency(self, agency_id: str) -> Optional[Dict[str, Any]]:
        """Get agency by ID."""
        result = self.client.table('agencies').select('*').eq('id', agency_id).execute()
        return result.data[0] if result.data else None

    # ==========================================
    # User Operations
    # ==========================================

    async def create_user(
        self,
        agency_id: str,
        email: str,
        name: str,
        role: str,
        auth_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new agency user."""
        data = {
            'agency_id': agency_id,
            'email': email,
            'name': name,
            'role': role,
            'auth_user_id': auth_user_id
        }

        result = self.client.table('users').insert(data).execute()
        return result.data[0] if result.data else None

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email (cross-agency - for auth only)."""
        result = self.client.table('users').select('*').eq('email', email).execute()
        return result.data[0] if result.data else None

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID (within current agency context)."""
        result = self.client.table('users').select('*').eq('id', user_id).execute()
        return result.data[0] if result.data else None

    async def list_users(self, agency_id: str) -> List[Dict[str, Any]]:
        """List all users in an agency."""
        self.set_agency_context(agency_id)
        result = self.client.table('users').select('*').execute()
        return result.data or []

    # ==========================================
    # Client Operations
    # ==========================================

    async def create_client(
        self,
        agency_id: str,
        name: str,
        email: str,
        phone: Optional[str] = None,
        preferences: Optional[Dict] = None,
        notes: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new client."""
        self.set_agency_context(agency_id)

        data = {
            'agency_id': agency_id,
            'name': name,
            'email': email,
            'phone': phone,
            'preferences': preferences or {},
            'notes': notes,
            'created_by': created_by
        }

        result = self.client.table('clients').insert(data).execute()
        return result.data[0] if result.data else None

    async def get_client(self, client_id: str, agency_id: str) -> Optional[Dict[str, Any]]:
        """Get client by ID."""
        self.set_agency_context(agency_id)
        result = self.client.table('clients').select('*').eq('id', client_id).execute()
        return result.data[0] if result.data else None

    async def list_clients(
        self,
        agency_id: str,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List clients with optional search."""
        self.set_agency_context(agency_id)

        query = self.client.table('clients').select('*')

        if search:
            query = query.or_(f'name.ilike.%{search}%,email.ilike.%{search}%')

        query = query.range(offset, offset + limit - 1).order('created_at', desc=True)
        result = query.execute()
        return result.data or []

    # ==========================================
    # Conversation Operations
    # ==========================================

    async def create_conversation(
        self,
        agency_id: str,
        user_id: str,
        client_id: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new AI conversation session."""
        self.set_agency_context(agency_id)

        data = {
            'agency_id': agency_id,
            'user_id': user_id,
            'client_id': client_id,
            'title': title or 'New Conversation',
            'status': 'active'
        }

        result = self.client.table('conversations').insert(data).execute()
        return result.data[0] if result.data else None

    async def get_conversation(
        self,
        conversation_id: str,
        agency_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get conversation by ID."""
        self.set_agency_context(agency_id)
        result = self.client.table('conversations').select('*').eq('id', conversation_id).execute()
        return result.data[0] if result.data else None

    async def list_conversations(
        self,
        agency_id: str,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List conversations with filters."""
        self.set_agency_context(agency_id)

        query = self.client.table('conversations').select('*')

        if status:
            query = query.eq('status', status)
        if user_id:
            query = query.eq('user_id', user_id)

        result = query.order('updated_at', desc=True).limit(limit).execute()
        return result.data or []

    async def update_conversation_status(
        self,
        conversation_id: str,
        agency_id: str,
        status: str,
        summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update conversation status."""
        self.set_agency_context(agency_id)

        data = {'status': status}
        if summary:
            data['summary'] = summary

        result = self.client.table('conversations').update(data).eq('id', conversation_id).execute()
        return result.data[0] if result.data else None

    # ==========================================
    # Message Operations
    # ==========================================

    async def create_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict]] = None,
        tool_results: Optional[List[Dict]] = None,
        model: Optional[str] = None,
        tokens_used: Optional[int] = None,
        latency_ms: Optional[int] = None
    ) -> Dict[str, Any]:
        """Add a message to a conversation."""
        data = {
            'conversation_id': conversation_id,
            'role': role,
            'content': content,
            'tool_calls': tool_calls,
            'tool_results': tool_results,
            'model': model,
            'tokens_used': tokens_used,
            'latency_ms': latency_ms
        }

        result = self.client.table('messages').insert(data).execute()
        return result.data[0] if result.data else None

    async def get_conversation_messages(
        self,
        conversation_id: str,
        agency_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all messages for a conversation."""
        self.set_agency_context(agency_id)

        result = self.client.table('messages')\
            .select('*')\
            .eq('conversation_id', conversation_id)\
            .order('created_at', desc=False)\
            .limit(limit)\
            .execute()

        return result.data or []

    # ==========================================
    # Offer Operations
    # ==========================================

    async def create_offer(
        self,
        agency_id: str,
        conversation_id: Optional[str],
        client_id: Optional[str],
        created_by: str,
        title: str,
        destination: str,
        content_json: Dict[str, Any],
        pricing: Dict[str, Any],
        itinerary: Optional[List[Dict]] = None,
        flights: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Create a new offer (draft status)."""
        self.set_agency_context(agency_id)

        data = {
            'agency_id': agency_id,
            'conversation_id': conversation_id,
            'client_id': client_id,
            'created_by': created_by,
            'title': title,
            'destination': destination,
            'content_json': content_json,
            'pricing': pricing,
            'itinerary': itinerary,
            'flights': flights,
            'status': 'draft'
        }

        result = self.client.table('offers').insert(data).execute()
        return result.data[0] if result.data else None

    async def get_offer(
        self,
        offer_id: str,
        agency_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get offer by ID."""
        self.set_agency_context(agency_id)
        result = self.client.table('offers').select('*').eq('id', offer_id).execute()
        return result.data[0] if result.data else None

    async def list_offers(
        self,
        agency_id: str,
        status: Optional[str] = None,
        client_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List offers with filters."""
        self.set_agency_context(agency_id)

        query = self.client.table('offers').select('*')

        if status:
            query = query.eq('status', status)
        if client_id:
            query = query.eq('client_id', client_id)

        result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        return result.data or []

    async def submit_offer_for_approval(
        self,
        offer_id: str,
        agency_id: str
    ) -> Dict[str, Any]:
        """Submit offer for approval."""
        self.set_agency_context(agency_id)

        data = {
            'status': 'pending_approval',
            'submitted_for_approval_at': 'now()'
        }

        result = self.client.table('offers').update(data).eq('id', offer_id).execute()
        return result.data[0] if result.data else None

    async def approve_offer(
        self,
        offer_id: str,
        agency_id: str,
        approved_by: str
    ) -> Dict[str, Any]:
        """Approve an offer."""
        self.set_agency_context(agency_id)

        data = {
            'status': 'approved',
            'approved_by': approved_by,
            'approved_at': 'now()'
        }

        result = self.client.table('offers').update(data).eq('id', offer_id).execute()
        return result.data[0] if result.data else None

    async def reject_offer(
        self,
        offer_id: str,
        agency_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """Reject an offer with reason."""
        self.set_agency_context(agency_id)

        data = {
            'status': 'rejected',
            'rejection_reason': reason
        }

        result = self.client.table('offers').update(data).eq('id', offer_id).execute()
        return result.data[0] if result.data else None

    async def mark_offer_sent(
        self,
        offer_id: str,
        agency_id: str,
        method: str = 'email'
    ) -> Dict[str, Any]:
        """Mark offer as sent to client."""
        self.set_agency_context(agency_id)

        data = {
            'status': 'sent',
            'sent_at': 'now()',
            'sent_method': method
        }

        result = self.client.table('offers').update(data).eq('id', offer_id).execute()
        return result.data[0] if result.data else None

    async def update_offer_pdf(
        self,
        offer_id: str,
        agency_id: str,
        pdf_url: str
    ) -> Dict[str, Any]:
        """Update offer with generated PDF URL."""
        self.set_agency_context(agency_id)

        data = {
            'pdf_url': pdf_url,
            'pdf_generated_at': 'now()'
        }

        result = self.client.table('offers').update(data).eq('id', offer_id).execute()
        return result.data[0] if result.data else None


# Global database client instance
db = DatabaseClient()
