"""
TripForge AI Agent - Core travel agent assistant using Ollama kimi-k2 model.
"""

import json
import httpx
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from uuid import UUID
from dataclasses import dataclass, field

from core import get_supabase_client


# Ollama API configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"


@dataclass
class Tool:
    """Tool definition for the agent."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable


@dataclass
class Message:
    """Agent message structure."""
    role: str  # 'system', 'user', 'assistant', 'tool'
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_results: Optional[List[Dict]] = None
    created_at: datetime = field(default_factory=datetime.now)


class TripForgeAgent:
    """
    TripForge AI Travel Agent using Ollama kimi-k2 model.

    Capabilities:
    - Search flights, hotels, and activities
    - Calculate pricing with agency markup
    - Create and save offers to Supabase
    - Maintain conversation history
    """

    def __init__(self, agency_id: str, agency_name: str = "Your Agency"):
        self.agency_id = agency_id
        self.agency_name = agency_name
        self.conversation_id: Optional[str] = None
        self.client_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.messages: List[Message] = []
        self.http_client = httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=120.0)

        # Initialize tools
        self.tools = self._initialize_tools()
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build the system prompt with agency context."""
        return f"""You are TripForge, an expert travel agent AI assistant working for {self.agency_name}.
You help create detailed, personalized travel offers for clients. Always be professional, thorough, and ask clarifying questions when needed.

You have access to the following tools to help create travel offers:

1. search_flights(origin, destination, date, passengers) - Search for available flights between locations
2. search_hotels(destination, checkin, checkout, guests) - Search for hotel accommodations
3. search_activities(destination, duration, preferences) - Find activities and attractions at the destination
4. create_offer(title, flights, hotels, activities, total_price, notes) - Create and save a complete travel offer to the database
5. calculate_price(components) - Calculate total price with agency markup applied

When you need to use a tool, respond with a JSON object in this format:
{{"tool_calls": [{{"name": "tool_name", "arguments": {{"param1": "value1"}}}}]}}

Important guidelines:
- Always ask clarifying questions if destination, dates, or passenger count are unclear
- Provide realistic estimates and explain your reasoning
- When all details are gathered, create a comprehensive offer with the create_offer tool
- The user (agency staff) will review and approve before sending to clients
"""

    def _initialize_tools(self) -> Dict[str, Tool]:
        """Initialize all available tools."""
        return {
            "search_flights": Tool(
                name="search_flights",
                description="Search for flights between origin and destination",
                parameters={
                    "type": "object",
                    "properties": {
                        "origin": {"type": "string", "description": "Departure airport/city"},
                        "destination": {"type": "string", "description": "Arrival airport/city"},
                        "date": {"type": "string", "description": "Departure date (YYYY-MM-DD)"},
                        "passengers": {"type": "integer", "description": "Number of passengers", "default": 1},
                        "return_date": {"type": "string", "description": "Return date (optional)"}
                    },
                    "required": ["origin", "destination", "date"]
                },
                handler=self._search_flights
            ),
            "search_hotels": Tool(
                name="search_hotels",
                description="Search for hotel accommodations",
                parameters={
                    "type": "object",
                    "properties": {
                        "destination": {"type": "string", "description": "City or location"},
                        "checkin": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                        "checkout": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"},
                        "guests": {"type": "integer", "description": "Number of guests", "default": 2}
                    },
                    "required": ["destination", "checkin", "checkout"]
                },
                handler=self._search_hotels
            ),
            "search_activities": Tool(
                name="search_activities",
                description="Find activities and attractions",
                parameters={
                    "type": "object",
                    "properties": {
                        "destination": {"type": "string", "description": "City or location"},
                        "duration": {"type": "integer", "description": "Number of days"},
                        "preferences": {"type": "array", "items": {"type": "string"}, "description": "Activity preferences"}
                    },
                    "required": ["destination", "duration"]
                },
                handler=self._search_activities
            ),
            "create_offer": Tool(
                name="create_offer",
                description="Create and save a travel offer to the database",
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Offer title"},
                        "destination": {"type": "string", "description": "Main destination"},
                        "description": {"type": "string", "description": "Offer description"},
                        "flights": {"type": "array", "description": "Flight details"},
                        "hotels": {"type": "array", "description": "Hotel details"},
                        "activities": {"type": "array", "description": "Activity details"},
                        "total_price": {"type": "number", "description": "Total price"},
                        "currency": {"type": "string", "default": "EUR"},
                        "notes": {"type": "string", "description": "Additional notes"}
                    },
                    "required": ["title", "destination", "total_price"]
                },
                handler=self._create_offer
            ),
            "calculate_price": Tool(
                name="calculate_price",
                description="Calculate total price with agency markup",
                parameters={
                    "type": "object",
                    "properties": {
                        "components": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["flight", "hotel", "activity", "fee"]},
                                    "description": {"type": "string"},
                                    "cost": {"type": "number"},
                                    "quantity": {"type": "integer", "default": 1}
                                },
                                "required": ["type", "description", "cost"]
                            }
                        },
                        "markup_percent": {"type": "number", "default": 10}
                    },
                    "required": ["components"]
                },
                handler=self._calculate_price
            )
        }

    async def start_conversation(
        self,
        user_id: str,
        client_id: Optional[str] = None,
        title: str = "New Trip Planning"
    ) -> str:
        """Start a new conversation and return conversation ID."""
        supabase = get_supabase_client()

        result = supabase.table("conversations").insert({
            "agency_id": self.agency_id,
            "user_id": user_id,
            "client_id": client_id,
            "title": title,
            "status": "active"
        }).execute()

        if result.data:
            self.conversation_id = result.data[0]["id"]
            self.user_id = user_id
            self.client_id = client_id

            # Add system message
            await self._save_message(
                role="system",
                content=self.system_prompt
            )

            return self.conversation_id

        raise Exception("Failed to create conversation")

    async def load_conversation(self, conversation_id: str) -> None:
        """Load existing conversation history."""
        supabase = get_supabase_client()

        # Load conversation details
        conv_result = supabase.table("conversations")\
            .select("*")\
            .eq("id", conversation_id)\
            .eq("agency_id", self.agency_id)\
            .single()\
            .execute()

        if not conv_result.data:
            raise ValueError(f"Conversation not found: {conversation_id}")

        self.conversation_id = conversation_id
        self.user_id = conv_result.data["user_id"]
        self.client_id = conv_result.data.get("client_id")

        # Load message history
        msg_result = supabase.table("messages")\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("created_at")\
            .execute()

        self.messages = [
            Message(
                role=msg["role"],
                content=msg["content"],
                tool_calls=msg.get("tool_calls"),
                tool_results=msg.get("tool_results"),
                created_at=msg["created_at"]
            )
            for msg in (msg_result.data or [])
        ]

    async def send_message(self, user_message: str) -> Dict[str, Any]:
        """Send a message to the agent and get response."""
        # Save user message
        await self._save_message(role="user", content=user_message)

        # Get response from Ollama
        response = await self._call_ollama(user_message)

        # Check if response contains tool calls
        if "tool_calls" in response:
            tool_calls = response["tool_calls"]

            # Save assistant message with tool calls
            await self._save_message(
                role="assistant",
                content="",
                tool_calls=tool_calls
            )

            # Execute tools
            tool_results = []
            for call in tool_calls:
                result = await self._execute_tool(call)
                tool_results.append({
                    "tool_call_id": call.get("id", "call_1"),
                    "name": call["name"],
                    "result": result
                })

            # Save tool results
            await self._save_message(
                role="tool",
                content=json.dumps([r["result"] for r in tool_results]),
                tool_results=tool_results
            )

            # Get final response from model with tool results
            final_response = await self._call_ollama_with_results(tool_results)

            # Save final assistant message
            await self._save_message(role="assistant", content=final_response)

            return {
                "message": final_response,
                "tool_calls": tool_calls,
                "tool_results": tool_results
            }
        else:
            # Simple text response
            await self._save_message(role="assistant", content=response["content"])

            return {
                "message": response["content"],
                "tool_calls": None,
                "tool_results": None
            }

    async def _call_ollama(self, user_message: str) -> Dict[str, Any]:
        """Call Ollama API with conversation history."""
        # Build messages for Ollama
        messages = []

        # Add system prompt
        messages.append({
            "role": "system",
            "content": self.system_prompt
        })

        # Add conversation history (last 10 messages)
        for msg in self.messages[-10:]:
            if msg.role == "tool":
                # Convert tool results to user role with context
                messages.append({
                    "role": "user",
                    "content": f"Tool result: {msg.content}"
                })
            else:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # Add tools description (simplified - tools can cause issues with some models)
        # Skip tools for simple conversations, only add them when needed
        pass  # Skip tools description for now

        print(f"[DEBUG] Sending {len(messages)} messages to Ollama")
        for i, m in enumerate(messages):
            print(f"[DEBUG] Message {i}: role={m['role']}, content={m['content'][:50]}...")

        # Make API call
        try:
            response = await self.http_client.post(
                "/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 2000
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            print(f"[DEBUG] Ollama full response: {json.dumps(data, indent=2)[:500]}")

            content = data.get("message", {}).get("content", "")
            print(f"[DEBUG] Extracted content: '{content[:200]}...' " if len(content) > 200 else f"[DEBUG] Extracted content: '{content}'")

            # Try to parse tool calls
            try:
                parsed = json.loads(content)
                if "tool_calls" in parsed:
                    return parsed
            except json.JSONDecodeError:
                pass

            return {"content": content}

        except Exception as e:
            return {"content": f"I apologize, but I'm having trouble connecting right now. Error: {str(e)}"}

    async def _call_ollama_with_results(self, tool_results: List[Dict]) -> str:
        """Call Ollama after tool execution to get final response."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "Here are the tool results:"}
        ]

        # Add tool results
        for result in tool_results:
            messages.append({
                "role": "user",
                "content": f"{result['name']}: {json.dumps(result['result'], indent=2)}"
            })

        messages.append({
            "role": "user",
            "content": "Based on these results, provide a helpful response to the user summarizing what was found. Be professional and suggest next steps."
        })

        try:
            response = await self.http_client.post(
                "/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1500
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "I've processed the results. How would you like to proceed?")

        except Exception as e:
            return "I've gathered the information. Would you like me to create an offer based on these results?"

    def _build_tools_description(self) -> str:
        """Build tools description for the prompt."""
        descriptions = []
        for name, tool in self.tools.items():
            desc = f"- {name}: {tool.description}"
            desc += f"\n  Parameters: {json.dumps(tool.parameters.get('properties', {}))}"
            descriptions.append(desc)
        return "\n".join(descriptions)

    async def _execute_tool(self, tool_call: Dict) -> Any:
        """Execute a tool call."""
        tool_name = tool_call.get("name")
        arguments = tool_call.get("arguments", {})

        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}

        tool = self.tools[tool_name]

        try:
            # Inject context
            arguments["_agency_id"] = self.agency_id
            arguments["_conversation_id"] = self.conversation_id
            arguments["_user_id"] = self.user_id

            result = await tool.handler(**arguments)
            return result

        except Exception as e:
            return {"error": str(e)}

    async def _save_message(
        self,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict]] = None,
        tool_results: Optional[List[Dict]] = None
    ) -> None:
        """Save message to Supabase (or skip if unavailable)."""
        if not self.conversation_id:
            return

        # Try to save to Supabase, but silently skip if unavailable
        try:
            supabase = get_supabase_client()
            data = {
                "conversation_id": self.conversation_id,
                "role": role,
                "content": content,
                "tool_calls": tool_calls,
                "tool_results": tool_results
            }
            supabase.table("messages").insert(data).execute()
        except Exception:
            # Supabase not available, continue with local-only storage
            pass

        # Add to local history (always works)
        self.messages.append(Message(
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results
        ))

    # ===============================
    # TOOL HANDLERS (Mock Data)
    # ===============================

    async def _search_flights(
        self,
        origin: str,
        destination: str,
        date: str,
        passengers: int = 1,
        return_date: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Search flights - Mock implementation."""
        # Mock flight results
        flights = [
            {
                "airline": "Lufthansa",
                "flight_number": "LH123",
                "departure": {"airport": origin, "time": f"{date}T10:00:00"},
                "arrival": {"airport": destination, "time": f"{date}T14:30:00"},
                "price": 450 * passengers,
                "class": "Economy"
            },
            {
                "airline": "Air France",
                "flight_number": "AF456",
                "departure": {"airport": origin, "time": f"{date}T14:00:00"},
                "arrival": {"airport": destination, "time": f"{date}T18:45:00"},
                "price": 380 * passengers,
                "class": "Economy"
            }
        ]

        if return_date:
            flights.append({
                "airline": "Lufthansa",
                "flight_number": "LH124",
                "departure": {"airport": destination, "time": f"{return_date}T16:00:00"},
                "arrival": {"airport": origin, "time": f"{return_date}T20:30:00"},
                "price": 450 * passengers,
                "class": "Economy",
                "is_return": True
            })

        return {
            "origin": origin,
            "destination": destination,
            "date": date,
            "passengers": passengers,
            "flights": flights,
            "cheapest_price": min(f["price"] for f in flights if not f.get("is_return"))
        }

    async def _search_hotels(
        self,
        destination: str,
        checkin: str,
        checkout: str,
        guests: int = 2,
        **kwargs
    ) -> Dict[str, Any]:
        """Search hotels - Mock implementation."""
        nights = self._calculate_nights(checkin, checkout)

        hotels = [
            {
                "name": f"{destination} Grand Hotel",
                "stars": 4,
                "location": "City Center",
                "price_per_night": 120,
                "total_price": 120 * nights,
                "amenities": ["WiFi", "Pool", "Gym", "Restaurant"]
            },
            {
                "name": f"{destination} Boutique Inn",
                "stars": 3,
                "location": "Historic District",
                "price_per_night": 85,
                "total_price": 85 * nights,
                "amenities": ["WiFi", "Breakfast", "Garden"]
            },
            {
                "name": f"{destination} Luxury Resort",
                "stars": 5,
                "location": "Beachfront",
                "price_per_night": 280,
                "total_price": 280 * nights,
                "amenities": ["Spa", "Pool", "Beach Access", "Fine Dining"]
            }
        ]

        return {
            "destination": destination,
            "checkin": checkin,
            "checkout": checkout,
            "nights": nights,
            "guests": guests,
            "hotels": hotels,
            "best_value": hotels[0],
            "cheapest": hotels[1]
        }

    async def _search_activities(
        self,
        destination: str,
        duration: int,
        preferences: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Search activities - Mock implementation."""
        all_activities = [
            {"name": f"{destination} City Tour", "type": "sightseeing", "duration": "3 hours", "price": 45},
            {"name": "Museum Pass", "type": "culture", "duration": "full day", "price": 35},
            {"name": "Wine Tasting Experience", "type": "food", "duration": "4 hours", "price": 85},
            {"name": "Cooking Class", "type": "food", "duration": "5 hours", "price": 120},
            {"name": "Adventure Hike", "type": "adventure", "duration": "6 hours", "price": 65},
            {"name": "Boat Cruise", "type": "relaxation", "duration": "2 hours", "price": 55},
            {"name": "Spa Day", "type": "relaxation", "duration": "full day", "price": 180},
            {"name": "Local Market Tour", "type": "shopping", "duration": "2 hours", "price": 0}
        ]

        # Filter by preferences if provided
        if preferences:
            filtered = [a for a in all_activities if any(
                p.lower() in a["type"].lower() or p.lower() in a["name"].lower()
                for p in preferences
            )]
            activities = filtered if filtered else all_activities[:5]
        else:
            activities = all_activities[:5]

        return {
            "destination": destination,
            "duration_days": duration,
            "preferences": preferences or [],
            "activities": activities,
            "total_activities_price": sum(a["price"] for a in activities),
            "suggested_per_day": 1 if duration <= 3 else 2
        }

    async def _calculate_price(
        self,
        components: List[Dict[str, Any]],
        markup_percent: float = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """Calculate price with agency markup."""
        breakdown = []
        total_cost = 0

        for comp in components:
            cost = comp.get("cost", 0) * comp.get("quantity", 1)
            total_cost += cost

            breakdown.append({
                "type": comp.get("type", "other"),
                "description": comp.get("description", ""),
                "base_cost": comp.get("cost", 0),
                "quantity": comp.get("quantity", 1),
                "subtotal": cost
            })

        markup_amount = total_cost * (markup_percent / 100)
        final_price = total_cost + markup_amount

        return {
            "breakdown": breakdown,
            "subtotal": total_cost,
            "markup_percent": markup_percent,
            "markup_amount": round(markup_amount, 2),
            "final_price": round(final_price, 2),
            "currency": "EUR"
        }

    async def _create_offer(
        self,
        title: str,
        destination: str,
        total_price: float,
        description: str = "",
        flights: Optional[List[Dict]] = None,
        hotels: Optional[List[Dict]] = None,
        activities: Optional[List[Dict]] = None,
        notes: str = "",
        currency: str = "EUR",
        **kwargs
    ) -> Dict[str, Any]:
        """Create offer in Supabase."""
        supabase = get_supabase_client()

        # Get agency settings for markup
        agency_result = supabase.table("agencies")\
            .select("settings")\
            .eq("id", self.agency_id)\
            .single()\
            .execute()

        markup = agency_result.data.get("settings", {}).get("default_markup_percent", 10) if agency_result.data else 10

        # Calculate final price with markup
        base_cost = total_price
        markup_amount = base_cost * (markup / 100)
        final_price = base_cost + markup_amount

        offer_data = {
            "agency_id": self.agency_id,
            "conversation_id": self.conversation_id,
            "client_id": self.client_id,
            "created_by": self.user_id,
            "title": title,
            "destination": destination,
            "description": description,
            "content_json": {
                "flights": flights or [],
                "hotels": hotels or [],
                "activities": activities or [],
                "notes": notes
            },
            "pricing": {
                "base_cost": base_cost,
                "markup": markup_amount,
                "total": final_price,
                "currency": currency
            },
            "status": "draft"
        }

        result = supabase.table("offers").insert(offer_data).execute()

        if result.data:
            offer_id = result.data[0]["id"]

            # Update conversation status to pending_approval
            supabase.table("conversations").update({
                "status": "pending_approval"
            }).eq("id", self.conversation_id).execute()

            return {
                "success": True,
                "offer_id": offer_id,
                "title": title,
                "destination": destination,
                "base_cost": base_cost,
                "markup_percent": markup,
                "final_price": final_price,
                "currency": currency,
                "message": f"Offer '{title}' created successfully. It's ready for your review and approval.",
                "url": f"/offers/{offer_id}"
            }

        return {"error": "Failed to create offer"}

    def _calculate_nights(self, checkin: str, checkout: str) -> int:
        """Calculate number of nights between dates."""
        from datetime import datetime

        try:
            d1 = datetime.strptime(checkin, "%Y-%m-%d")
            d2 = datetime.strptime(checkout, "%Y-%m-%d")
            return max(1, (d2 - d1).days)
        except:
            return 1


# Singleton agent instances by conversation
_agents: Dict[str, TripForgeAgent] = {}


async def get_agent(conversation_id: str) -> Optional[TripForgeAgent]:
    """Get or create agent for a conversation."""
    if conversation_id in _agents:
        return _agents[conversation_id]

    # Load conversation and create agent
    agent = TripForgeAgent(agency_id="", agency_name="")
    await agent.load_conversation(conversation_id)

    _agents[conversation_id] = agent
    return agent


async def create_agent(agency_id: str, agency_name: str) -> TripForgeAgent:
    """Create a new agent instance."""
    return TripForgeAgent(agency_id=agency_id, agency_name=agency_name)
