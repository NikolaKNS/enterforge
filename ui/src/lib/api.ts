// TripForge API Client
import { config } from './config';

const API_BASE = config.API_URL;
const API_KEY = config.API_KEY;
const AGENCY_ID = config.AGENCY_ID;

// Debug logging
console.log('[API] Configuration loaded:');
console.log('[API] API_URL:', API_BASE);
console.log('[API] AGENCY_ID:', AGENCY_ID);
console.log('[API] API_KEY exists:', !!API_KEY);

// Generic fetch wrapper
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  console.log('[API] Fetching:', url);

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': API_KEY,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: { message: 'Unknown error' } }));
      throw new Error(error.error?.message || `HTTP ${response.status}`);
    }

    return response.json();
  } catch (err) {
    console.error('[API] Fetch failed:', url, err);
    throw err;
  }
}

// Chat API
export async function sendChatMessage(
  message: string,
  conversationId: string,
  clientInfo?: Record<string, unknown>
) {
  if (!AGENCY_ID) {
    throw new Error('AGENCY_ID is undefined - check environment variables');
  }
  return fetchApi<{
    message: string;
    requires_approval: boolean;
    tool_calls?: unknown[];
  }>('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      agency_id: AGENCY_ID,
      conversation_id: conversationId,
      message,
    }),
  });
}

// Conversations API
export async function getConversations(status?: string) {
  if (!AGENCY_ID) {
    console.warn('[API] AGENCY_ID is undefined, returning empty conversations');
    return { conversations: [], count: 0 };
  }
  const params = status ? `?status=${status}` : '';
  return fetchApi<{ conversations: Conversation[]; count: number }>(
    `/api/conversations/${AGENCY_ID}${params}`
  );
}

export async function createConversation(title?: string, clientId?: string) {
  return fetchApi<Conversation>('/api/conversations', {
    method: 'POST',
    body: JSON.stringify({ title, client_id: clientId }),
  });
}

export async function getConversationMessages(conversationId: string) {
  return fetchApi<{ conversation: Conversation; messages: Message[] }>(
    `/api/conversation/${conversationId}/messages`
  );
}

export async function closeConversation(conversationId: string) {
  return fetchApi<{ message: string; conversation_id: string }>(
    `/api/conversation/${conversationId}/close`,
    { method: 'POST' }
  );
}

// Offers API
export async function getOffers(status?: string) {
  if (!AGENCY_ID) {
    console.warn('[API] AGENCY_ID is undefined, returning empty offers');
    return { offers: [], count: 0 };
  }
  const params = status ? `?status=${status}` : '';
  return fetchApi<{ offers: Offer[]; count: number }>(
    `/api/offers/${AGENCY_ID}${params}`
  );
}

export async function getOffer(offerId: string) {
  return fetchApi<Offer>(`/api/offer/${offerId}`);
}

export async function approveOffer(offerId: string, approvedBy: string, notes?: string) {
  return fetchApi<{ message: string; offer_id: string; status: string }>(
    `/api/offer/${offerId}/approve`,
    {
      method: 'POST',
      body: JSON.stringify({ approved_by: approvedBy, notes }),
    }
  );
}

export async function rejectOffer(offerId: string, reason: string) {
  return fetchApi<{ message: string; offer_id: string; reason: string }>(
    `/api/offer/${offerId}/reject`,
    {
      method: 'POST',
      body: JSON.stringify({ reason }),
    }
  );
}

export async function sendOffer(offerId: string, method: 'email' | 'link' | 'manual' = 'email') {
  return fetchApi<{ message: string; offer_id: string; status: string; method: string }>(
    `/api/offer/${offerId}/send`,
    {
      method: 'POST',
      body: JSON.stringify({ method }),
    }
  );
}

// Clients API
export async function getClients(search?: string) {
  if (!AGENCY_ID) {
    console.warn('[API] AGENCY_ID is undefined, returning empty clients');
    return { clients: [], count: 0 };
  }
  const params = search ? `?search=${encodeURIComponent(search)}` : '';
  return fetchApi<{ clients: Client[]; count: number }>(
    `/api/clients/${AGENCY_ID}${params}`
  );
}

export async function createClient(client: CreateClientRequest) {
  if (!AGENCY_ID) {
    throw new Error('AGENCY_ID is undefined');
  }
  return fetchApi<{ message: string; client: Client }>(
    `/api/clients/${AGENCY_ID}`,
    {
      method: 'POST',
      body: JSON.stringify(client),
    }
  );
}

// Agency Config API
export async function getAgencyConfig(slug: string) {
  return fetchApi<{
    name: string;
    slug: string;
    branding_config: Record<string, unknown>;
    settings: Record<string, unknown>;
  }>(`/api/agency/${slug}/config`);
}

// Health Check
export async function healthCheck() {
  return fetch<{ status: string; timestamp: string; version: string }>('/health');
}

// Types
export interface Conversation {
  id: string;
  agency_id: string;
  client_id?: string;
  user_id: string;
  title: string;
  status: 'active' | 'pending_approval' | 'closed' | 'archived';
  destination?: string;
  travel_dates?: Record<string, unknown>;
  summary?: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'tool' | 'system';
  content: string;
  tool_calls?: unknown[];
  tool_results?: unknown[];
  model?: string;
  tokens_used?: number;
  latency_ms?: number;
  created_at: string;
}

export interface Offer {
  id: string;
  agency_id: string;
  conversation_id?: string;
  client_id?: string;
  created_by: string;
  title: string;
  destination: string;
  description?: string;
  content_json: Record<string, unknown>;
  pricing: {
    base_cost: string;
    markup: string;
    total: string;
    currency: string;
  };
  itinerary?: unknown[];
  flights?: unknown[];
  pdf_url?: string;
  status: 'draft' | 'pending_approval' | 'approved' | 'rejected' | 'sent' | 'converted' | 'expired';
  submitted_for_approval_at?: string;
  approved_by?: string;
  approved_at?: string;
  rejection_reason?: string;
  sent_at?: string;
  sent_method?: string;
  valid_until?: string;
  created_at: string;
  updated_at: string;
}

export interface Client {
  id: string;
  agency_id: string;
  name: string;
  email: string;
  phone?: string;
  preferences?: Record<string, unknown>;
  notes?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateClientRequest {
  name: string;
  email: string;
  phone?: string;
  preferences?: Record<string, unknown>;
  notes?: string;
  created_by?: string;
}
