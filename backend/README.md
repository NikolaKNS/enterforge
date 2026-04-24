# TripForge Backend

FastAPI backend for TripForge Enterprise - AI Travel Agent SaaS.

## Features

- **Multi-tenant Architecture**: Complete data isolation between travel agencies
- **AI Agent with Tool Use**: Ollama-powered agent that can:
  - Search flights (Amadeus API or mock data)
  - Calculate pricing with agency markup
  - Generate professional PDF proposals
  - Manage offers through approval workflow
- **Human-in-the-Loop**: All AI-generated offers require staff approval
- **Real-time WebSocket**: Live agent conversations

## Tech Stack

- **Framework**: FastAPI + Python 3.10+
- **Database**: Supabase (PostgreSQL) with Row-Level Security
- **AI**: Ollama (local LLMs with tool use support)
- **PDF**: WeasyPrint + Jinja2 templates
- **Auth**: Supabase Auth (JWT)

## Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

```bash
cp .env.example .env
# Edit .env with your values
```

Required:
- `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` - Your Supabase project
- `OLLAMA_BASE_URL` - Usually `http://localhost:11434`

Optional:
- `AMADEUS_CLIENT_ID` and `AMADEUS_CLIENT_SECRET` - For live flight search
- `SENDGRID_API_KEY` - For email delivery

### 3. Setup Ollama

```bash
# Install Ollama: https://ollama.com/download

# Pull a tool-capable model
ollama pull qwen2.5:14b
# or
ollama pull llama3.1:8b
```

### 4. Database Setup

Run the migration in Supabase SQL Editor:

```sql
-- Copy contents of migrations/001_initial.sql
-- and run in Supabase Dashboard → SQL Editor
```

### 5. Run Development Server

```bash
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Endpoints

### Authentication
- `POST /api/auth/login` - Login with email/password
- `GET /api/auth/me` - Get current user

### Clients
- `GET /api/clients` - List clients
- `POST /api/clients` - Create client
- `GET /api/clients/{id}` - Get client details

### Conversations
- `GET /api/conversations` - List conversations
- `POST /api/conversations` - Create conversation
- `GET /api/conversations/{id}` - Get conversation with messages

### Agent
- `POST /api/agent/chat` - Send message, get AI response
- `WS /ws/agent/{conversation_id}` - Real-time WebSocket chat

### Offers
- `GET /api/offers` - List offers
- `POST /api/offers` - Create offer (manual or from conversation)
- `POST /api/offers/{id}/submit` - Submit for approval
- `POST /api/offers/{id}/approve` - Approve offer
- `POST /api/offers/{id}/reject` - Reject with reason
- `POST /api/offers/{id}/send` - Send to client

## Architecture

```
backend/
├── main.py              # FastAPI app entry point
├── core/                # Core utilities
│   ├── config.py        # Pydantic settings
│   ├── supabase.py      # Database client
│   └── llm_client.py    # Ollama integration
├── api/                 # API routes
│   ├── auth.py
│   ├── clients.py
│   ├── conversations.py
│   ├── offers.py
│   └── agent.py         # WebSocket + chat endpoints
├── agent/               # AI agent orchestration
│   ├── orchestrator.py  # Main conversation loop
│   └── prompts.py       # System prompts + tool descriptions
├── tools/               # Agent tool implementations
│   ├── flight_search.py # Amadeus API
│   ├── pricing.py       # Agency markup calc
│   ├── offer_tools.py   # Save/update offers
│   └── pdf_tools.py     # PDF generation
├── models/              # Pydantic models
│   ├── agency.py
│   ├── user.py
│   ├── client.py
│   ├── conversation.py
│   ├── message.py
│   └── offer.py
└── migrations/          # SQL migrations
    └── 001_initial.sql
```

## Tool Use Architecture

The AI agent uses Ollama's tool calling capability:

1. **User sends message** → Stored in database
2. **Orchestrator loads context** → Agency settings, client info, conversation history
3. **LLM generates response** → May include tool calls
4. **Tools execute** → Flight search, pricing calc, etc.
5. **Results stored** → Tool results saved as messages
6. **Final response returned** → Sent to user

Available tools:
- `search_flights` - Search Amadeus/GDS
- `calculate_pricing` - Apply agency markup
- `get_client_info` - Load client preferences
- `save_offer_draft` - Save offer to database
- `generate_pdf` - Create PDF proposal

## Human-in-the-Loop Workflow

```
Agent Chat → AI Generates Offer → Draft Saved
                                      ↓
Staff Reviews ← Pending Approval ← Submit
     ↓
Approve/Reject → Sent to Client (if approved)
```

## Development

### Adding a New Tool

1. Define tool in `tools/` (e.g., `tools/hotels.py`)
2. Add to `tools/__init__.py` exports
3. Add to `agent/prompts.py` TOOL_DESCRIPTIONS
4. Import in `agent/orchestrator.py` and add to `self.tools`

### Testing

```bash
# Run tests
pytest

# Run specific test
pytest tests/test_offers.py -v
```

### Code Style

```bash
# Format with black
black .

# Type check
mypy .
```

## Production Deployment

### Environment

Set `APP_ENV=production` and configure proper CORS origins.

### Recommended Hosting

- **Backend**: Railway, Render, or Fly.io
- **Database**: Supabase Cloud
- **AI**: Self-hosted Ollama or run locally

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Ollama not responding

- Check Ollama is running: `ollama list`
- Verify model is pulled: `ollama pull qwen2.5:14b`
- Test API: `curl http://localhost:11434/api/tags`

### Database RLS errors

- Ensure `set_config` RPC is created (in migration)
- Check agency_id is being set correctly

### PDF generation fails

- Install system dependencies for WeasyPrint:
  ```bash
  # Ubuntu/Debian
  apt-get install -y libpango-1.0-0 libpangoft2-1.0-0
  ```

## License

Proprietary - TripForge Enterprise
