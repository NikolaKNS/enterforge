# TripForge Enterprise - AI Travel Agent SaaS

## Project Overview
TripForge Enterprise is an AI-powered travel agent SaaS platform designed specifically for travel agencies. It leverages Claude's tool use capabilities to automate travel offer creation, flight searches, and document generation while maintaining human oversight for quality control.

**Tagline:** "AI-Powered Travel Operations for Modern Agencies"

---

## Architecture

### Core Concept
- **Multi-tenant SaaS**: Each travel agency is completely isolated with row-level security
- **AI Agent with Tool Use**: Claude acts as an intelligent agent that can:
  - Create personalized travel offers with real pricing
  - Search and compare flights via GDS/Amadeus APIs
  - Generate professional PDF proposals
  - Manage client communications and follow-ups
- **Human-in-the-Loop**: All AI-generated content requires agency staff approval before being sent to clients

### Technology Stack

**Backend (FastAPI + Python)**
- `main.py` - Application entry point with FastAPI app factory
- `agent/` - Claude agent orchestration and conversation management
  - `orchestrator.py` - Main agent loop and conversation state
  - `prompts.py` - System prompts and templates
- `tools/` - Tool definitions for Claude tool use
  - `flight_search.py` - Amadeus/GDS flight search
  - `pdf_generator.py` - PDF proposal generation
  - `pricing.py` - Agency pricing calculations
  - `database.py` - Supabase data access tools
- `models/` - Pydantic models for validation
  - `agency.py`, `client.py`, `offer.py`, `booking.py`
- `api/` - REST API endpoints
  - `auth.py` - Authentication routes
  - `offers.py` - Offer CRUD and approval workflow
  - `clients.py` - Client management
  - `agent.py` - Agent conversation endpoints
- `core/` - Shared utilities
  - `config.py` - Settings management
  - `supabase.py` - Supabase client
  - `anthropic_client.py` - Claude API client

**Frontend (Next.js 14 + Tailwind CSS)**
- App Router structure with React Server Components
- TypeScript throughout
- Real-time updates via Supabase subscriptions
- Role-based UI (admin, agent, viewer)

**Database (Supabase / PostgreSQL)**
- Multi-tenant with Row-Level Security (RLS)
- Real-time subscriptions for live offer updates
- Tables:
  - `agencies` - Agency accounts and settings
  - `users` - Staff members with roles
  - `clients` - Traveler profiles
  - `offers` - AI-generated offers with approval status
  - `bookings` - Confirmed reservations
  - `flights` - Flight search results
  - `templates` - Agency PDF templates

**AI (Anthropic Claude API)**
- Model: `claude-sonnet-4-20250514`
- Tool use for: flight search, pricing, PDF generation, database operations
- Streaming responses for real-time agent interaction

---

## Project Structure
```
tripforge/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic settings
│   │   ├── supabase.py         # Supabase client setup
│   │   └── anthropic_client.py # Claude client with retries
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # Agent loop + conversation state
│   │   └── prompts.py          # System prompts
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── flight_search.py    # Amadeus API integration
│   │   ├── pdf_generator.py    # WeasyPrint/pdfkit for proposals
│   │   ├── pricing.py          # Agency markup calculations
│   │   └── database.py         # Supabase query tools
│   ├── models/
│   │   ├── __init__.py
│   │   ├── agency.py
│   │   ├── client.py
│   │   ├── offer.py
│   │   └── booking.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py             # JWT + Supabase auth
│   │   ├── offers.py           # Offer CRUD + approval
│   │   ├── clients.py          # Client management
│   │   └── agent.py            # Agent WebSocket/SSE
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx            # Dashboard
│   │   ├── offers/
│   │   │   ├── page.tsx        # Offer list
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx    # Offer detail + approval
│   │   │   └── new/
│   │   │       └── page.tsx    # Create with agent
│   │   ├── clients/
│   │   │   └── page.tsx
│   │   └── settings/
│   │       └── page.tsx
│   ├── components/
│   │   ├── AgentChat.tsx       # Claude conversation UI
│   │   ├── OfferCard.tsx
│   │   ├── ApprovalWorkflow.tsx
│   │   └── PDFPreview.tsx
│   ├── lib/
│   │   ├── supabase.ts         # Supabase client
│   │   └── api.ts              # API helpers
│   ├── types/
│   │   └── index.ts
│   ├── tailwind.config.ts
│   ├── next.config.js
│   └── package.json
├── CLAUDE.md
└── README.md
```

---

## Environment Variables

### Backend (.env)
```env
# Supabase
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_JWT_SECRET=...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Amadeus (Flight Search)
AMADEUS_CLIENT_ID=...
AMADEUS_CLIENT_SECRET=...

# App
APP_ENV=development
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

---

## Database Schema (Supabase)

### Row-Level Security (RLS)
Every table has `agency_id` column. RLS policies ensure:
```sql
-- Example RLS policy
CREATE POLICY "agency_isolation" ON offers
  USING (agency_id = current_setting('app.current_agency')::uuid);
```

### Key Tables
```sql
-- Agencies (tenants)
create table agencies (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text unique not null,
  settings jsonb default '{}',
  created_at timestamptz default now()
);

-- Users (agency staff)
create table users (
  id uuid primary key references auth.users(id),
  agency_id uuid references agencies(id),
  email text not null,
  role text check (role in ('admin', 'agent', 'viewer')),
  created_at timestamptz default now()
);

-- Clients
create table clients (
  id uuid primary key default gen_random_uuid(),
  agency_id uuid references agencies(id),
  email text not null,
  name text not null,
  preferences jsonb default '{}',
  created_at timestamptz default now()
);

-- Offers (AI-generated, pending approval)
create table offers (
  id uuid primary key default gen_random_uuid(),
  agency_id uuid references agencies(id),
  client_id uuid references clients(id),
  status text check (status in ('draft', 'pending_approval', 'approved', 'rejected', 'sent')),
  title text not null,
  destination text not null,
  description text,
  itinerary jsonb,
  flights jsonb,
  pricing jsonb,
  pdf_url text,
  ai_conversation jsonb,  -- Store agent interaction
  created_by uuid references users(id),
  approved_by uuid references users(id),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

---

## Claude Tool Use

### Available Tools
```python
TOOLS = [
    {
        "name": "search_flights",
        "description": "Search flights via Amadeus API",
        "input_schema": {...}
    },
    {
        "name": "calculate_pricing",
        "description": "Calculate total with agency markup",
        "input_schema": {...}
    },
    {
        "name": "generate_pdf",
        "description": "Generate PDF proposal from offer data",
        "input_schema": {...}
    },
    {
        "name": "save_offer_draft",
        "description": "Save offer to database as draft",
        "input_schema": {...}
    }
]
```

### Agent Orchestrator Flow
```python
async def run_agent(conversation_id: str, user_message: str):
    # 1. Load conversation history
    # 2. Build messages for Claude
    # 3. Call Claude with tools
    # 4. If tool_use → execute tool → loop
    # 5. If stop → return final response
    # 6. Save to database
```

---

## API Endpoints

### Authentication
- `POST /api/auth/login` - Supabase auth
- `POST /api/auth/refresh` - Refresh JWT

### Agent (WebSocket)
- `WS /api/agent/chat` - Real-time agent conversation

### Offers
- `GET /api/offers` - List (with filters)
- `POST /api/offers` - Create via agent
- `GET /api/offers/{id}` - Get details
- `POST /api/offers/{id}/approve` - Staff approval
- `POST /api/offers/{id}/reject` - Rejection with feedback
- `POST /api/offers/{id}/send` - Send to client

### Clients
- `GET /api/clients`
- `POST /api/clients`
- `GET /api/clients/{id}/offers`

---

## Human-in-the-Loop Workflow

```
1. Agent Chat
   Staff describes client needs → AI asks clarifying questions

2. AI Generation
   AI uses tools to:
   - Search flights
   - Calculate pricing
   - Draft itinerary
   → Saves as DRAFT

3. Review Screen
   Staff sees:
   - Generated offer with full details
   - AI reasoning (which tools used, why)
   - PDF preview
   → Approve / Request Changes / Reject

4. Client Delivery
   Approved → Email PDF + web link to client
   → Status: SENT
```

---

## Frontend Routes

```
/login              → Auth page
/dashboard          → Overview + recent offers
/offers             → All offers list
/offers/new         → Agent chat to create
/offers/[id]        → Offer detail + approval
/clients            → Client management
/settings           → Agency settings
```

---

## Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Code Style

- **Python**: PEP 8, type hints everywhere, Pydantic models
- **TypeScript**: Strict mode, interfaces for all data
- **Imports**: Absolute within each project
- **Error handling**: Always return structured errors
- **Security**: Never trust client input, RLS on all queries

---

## Deployment

- **Backend**: Railway / Fly.io / Render
- **Frontend**: Vercel
- **Database**: Supabase Cloud
- **File Storage**: Supabase Storage (PDFs)
