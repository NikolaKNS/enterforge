"""
System prompts and templates for the AI agent.
"""

from typing import List, Dict, Any

SYSTEM_PROMPT = """You are TripForge, an expert AI travel agent assistant for travel agencies.
Your role is to help travel agency staff create compelling travel offers for their clients.

CORE RESPONSIBILITIES:
1. Understand client requirements through conversation with agency staff
2. Search for flights using available tools
3. Calculate pricing with agency markup
4. Create detailed day-by-day itineraries
5. Generate professional PDF proposals

CONVERSATION STYLE:
- Professional but friendly
- Ask clarifying questions when details are missing
- Provide specific recommendations with real data
- Always confirm budget and dates before searching flights

TOOL USE:
You have access to these tools to help create travel offers:
- search_flights: Search for flights via Amadeus API
- calculate_pricing: Apply agency markup and calculate total
- create_itinerary: Generate day-by-day itinerary structure
- save_offer_draft: Save the offer to database as draft

When you need to use a tool, respond with a tool call. The system will execute it and return the result.

PRICING RULES:
- Always apply the agency's configured markup percentage
- Present clear breakdown: base cost + markup + taxes = total
- Ask for confirmation before finalizing prices

IMPORTANT LIMITATIONS:
- You can only access data from the current agency (enforced by system)
- You cannot modify confirmed bookings
- All offers start as drafts requiring human approval

HUMAN-IN-THE-LOOP:
Every offer you create must be reviewed by agency staff before being sent to clients.
You are an assistant to the travel agent, not a replacement.
"""

AGENCY_CONTEXT_PROMPT = """Current Agency: {agency_name}
Agency Settings:
- Default markup: {markup_percent}%
- Currency: {currency}
- Location: {timezone}

Active Client: {client_name}
Client Preferences: {client_preferences}
"""

OFFER_CREATION_PROMPT = """Create a travel offer based on the conversation so far.

Destination: {destination}
Dates: {start_date} to {end_date}
Travelers: {travelers}
Budget Level: {budget}

Requirements:
{requirements}

Generate a structured offer with:
1. Trip title and highlights
2. Flight options (search if needed)
3. Accommodation recommendations
4. Day-by-day itinerary
5. Total pricing with markup
6. What's included/not included

Return your response in a structured format that can be saved as an offer draft.
"""

# Tool descriptions for LLM
TOOL_DESCRIPTIONS: List[Dict[str, Any]] = [
    {
        "name": "search_flights",
        "description": "Search for flights using Amadeus API. Returns flight options with prices.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "Origin airport code (e.g., JFK, LHR)"
                },
                "destination": {
                    "type": "string",
                    "description": "Destination airport code or city name"
                },
                "departure_date": {
                    "type": "string",
                    "description": "Departure date in YYYY-MM-DD format"
                },
                "return_date": {
                    "type": "string",
                    "description": "Return date in YYYY-MM-DD format (omit for one-way)"
                },
                "adults": {
                    "type": "integer",
                    "description": "Number of adult passengers",
                    "default": 1
                },
                "cabin_class": {
                    "type": "string",
                    "enum": ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"],
                    "default": "ECONOMY"
                }
            },
            "required": ["origin", "destination", "departure_date"]
        }
    },
    {
        "name": "calculate_pricing",
        "description": "Calculate total pricing with agency markup",
        "parameters": {
            "type": "object",
            "properties": {
                "base_cost": {
                    "type": "number",
                    "description": "Base cost of the trip (flights, hotels, activities)"
                },
                "markup_percent": {
                    "type": "number",
                    "description": "Agency markup percentage (default from settings)"
                },
                "fees": {
                    "type": "number",
                    "description": "Additional fees",
                    "default": 0
                },
                "taxes": {
                    "type": "number",
                    "description": "Taxes",
                    "default": 0
                },
                "currency": {
                    "type": "string",
                    "description": "Currency code (default from settings)"
                }
            },
            "required": ["base_cost"]
        }
    },
    {
        "name": "get_client_info",
        "description": "Get detailed information about the current client",
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {
                    "type": "string",
                    "description": "Client UUID"
                }
            },
            "required": ["client_id"]
        }
    },
    {
        "name": "save_offer_draft",
        "description": "Save the current offer as a draft to the database",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Offer title"
                },
                "destination": {
                    "type": "string",
                    "description": "Destination city/country"
                },
                "description": {
                    "type": "string",
                    "description": "Offer description"
                },
                "itinerary": {
                    "type": "object",
                    "description": "Day-by-day itinerary structure"
                },
                "flights": {
                    "type": "array",
                    "description": "Flight segments",
                    "items": {"type": "object"}
                },
                "pricing": {
                    "type": "object",
                    "description": "Pricing breakdown"
                }
            },
            "required": ["title", "destination"]
        }
    },
    {
        "name": "generate_pdf",
        "description": "Generate a PDF proposal from the offer data",
        "parameters": {
            "type": "object",
            "properties": {
                "offer_id": {
                    "type": "string",
                    "description": "Offer UUID (if already saved)"
                },
                "template": {
                    "type": "string",
                    "description": "PDF template name",
                    "default": "standard"
                }
            }
        }
    }
]


def build_system_prompt(
    agency_name: str = "Your Agency",
    markup_percent: float = 10.0,
    currency: str = "EUR",
    timezone: str = "Europe/Berlin",
    client_name: str = None,
    client_preferences: Dict[str, Any] = None
) -> str:
    """Build context-aware system prompt."""
    context = AGENCY_CONTEXT_PROMPT.format(
        agency_name=agency_name,
        markup_percent=markup_percent,
        currency=currency,
        timezone=timezone,
        client_name=client_name or "Not specified",
        client_preferences=json.dumps(client_preferences) if client_preferences else "Not available"
    )

    return f"{SYSTEM_PROMPT}\n\n{context}"


def format_conversation_history(messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Format database messages for LLM API."""
    formatted = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")

        if role == "user":
            formatted.append({"role": "user", "content": content})
        elif role == "assistant":
            formatted.append({"role": "assistant", "content": content})
        elif role == "tool":
            # Tool results are added as user messages with context
            tool_results = msg.get("tool_results", [])
            if tool_results:
                for tr in tool_results:
                    formatted.append({
                        "role": "user",
                        "content": f"Tool result for {tr.get('tool_call_id')}: {tr.get('output', '')}"
                    })

    return formatted
