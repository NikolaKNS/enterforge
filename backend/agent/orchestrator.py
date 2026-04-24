"""
Agent Orchestrator - Main AI conversation loop with tool use.
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from uuid import UUID

from core import get_llm_client, get_supabase_client, settings
from core.llm_client import ToolCall, LLMResponse, LLMError
from models import MessageRole
from .prompts import (
    SYSTEM_PROMPT,
    TOOL_DESCRIPTIONS,
    format_conversation_history,
    build_system_prompt
)
from tools import (
    search_flights,
    calculate_pricing,
    get_client_info,
    save_offer_draft,
    generate_pdf,
    ToolError
)


class AgentOrchestrator:
    """
    Orchestrates AI agent conversations with tool use.
    Handles the loop: LLM -> tool call -> result -> LLM
    """

    def __init__(
        self,
        agency_id: str,
        conversation_id: str,
        max_turns: int = None
    ):
        self.agency_id = agency_id
        self.conversation_id = conversation_id
        self.max_turns = max_turns or settings.AGENT_MAX_TURNS
        self.llm_client = get_llm_client()
        self.supabase = get_supabase_client()

        # Tool registry
        self.tools = {
            "search_flights": search_flights,
            "calculate_pricing": calculate_pricing,
            "get_client_info": get_client_info,
            "save_offer_draft": save_offer_draft,
            "generate_pdf": generate_pdf,
        }

    async def _get_agency_context(self) -> Dict[str, Any]:
        """Load agency settings for prompt context."""
        try:
            result = self.supabase.table("agencies")\
                .select("*")\
                .eq("id", self.agency_id)\
                .single()\
                .execute()

            if result.data:
                agency = result.data
                settings_data = agency.get("settings", {})
                return {
                    "name": agency.get("name", "Your Agency"),
                    "markup_percent": settings_data.get("default_markup_percent", 10),
                    "currency": settings_data.get("currency", "EUR"),
                    "timezone": settings_data.get("timezone", "Europe/Berlin"),
                }
        except Exception as e:
            print(f"Error loading agency context: {e}")

        return {
            "name": "Your Agency",
            "markup_percent": 10,
            "currency": "EUR",
            "timezone": "Europe/Berlin",
        }

    async def _get_client_context(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Load client info if conversation has a client."""
        try:
            result = self.supabase.table("conversations")\
                .select("client_id,clients(*)")\
                .eq("id", conversation_id)\
                .single()\
                .execute()

            if result.data and result.data.get("clients"):
                client = result.data["clients"]
                return {
                    "id": client.get("id"),
                    "name": client.get("name"),
                    "email": client.get("email"),
                    "preferences": client.get("preferences", {})
                }
        except Exception as e:
            print(f"Error loading client context: {e}")

        return None

    def _build_messages(
        self,
        system_prompt: str,
        conversation_history: List[Dict[str, Any]],
        user_message: str
    ) -> List[Dict[str, str]]:
        """Build message list for LLM API."""
        messages = [{"role": "system", "content": system_prompt}]

        # Add formatted conversation history
        formatted_history = format_conversation_history(conversation_history)
        messages.extend(formatted_history)

        # Add current user message if not already in history
        if not conversation_history or conversation_history[-1].get("role") != "user":
            messages.append({"role": "user", "content": user_message})

        return messages

    async def run(
        self,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        user_id: str
    ) -> LLMResponse:
        """
        Main conversation loop with tool use.

        Args:
            user_message: The current user message
            conversation_history: Previous messages in this conversation
            user_id: ID of the agency staff user

        Returns:
            LLMResponse with content and optional tool calls
        """
        # Build system prompt with context
        agency_ctx = await self._get_agency_context()
        client_ctx = await self._get_client_context(self.conversation_id)

        system_prompt = build_system_prompt(
            agency_name=agency_ctx["name"],
            markup_percent=agency_ctx["markup_percent"],
            currency=agency_ctx["currency"],
            timezone=agency_ctx["timezone"],
            client_name=client_ctx["name"] if client_ctx else None,
            client_preferences=client_ctx["preferences"] if client_ctx else None
        )

        # Build messages
        messages = self._build_messages(system_prompt, conversation_history, user_message)

        # Run LLM with tools
        for turn in range(self.max_turns):
            try:
                response = await self.llm_client.chat(
                    messages=messages,
                    tools=TOOL_DESCRIPTIONS,
                    temperature=settings.AGENT_TEMPERATURE
                )

                # If no tool calls, return final response
                if not response.tool_calls:
                    return response

                # Execute tools and continue loop
                messages.append({
                    "role": "assistant",
                    "content": response.content or ""
                })

                # Add tool calls to messages
                for tool_call in response.tool_calls:
                    messages.append({
                        "role": "assistant",
                        "content": f"Using tool: {tool_call.name}",
                        "tool_calls": [{
                            "id": tool_call.id,
                            "function": {
                                "name": tool_call.name,
                                "arguments": json.dumps(tool_call.arguments)
                            }
                        }]
                    })

                # Execute each tool and get results
                tool_results = []
                for tool_call in response.tool_calls:
                    result = await self.execute_tool(tool_call)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(result) if isinstance(result, dict) else str(result)
                    })

                    # Add tool result to messages
                    messages.append({
                        "role": "user",
                        "content": f"Tool result for {tool_call.name}: {tool_results[-1]['output']}"
                    })

                # Save tool execution results to database
                await self._save_tool_results(response.tool_calls, tool_results)

            except LLMError as e:
                # Return error as response
                return LLMResponse(
                    content=f"I encountered an error: {str(e)}. Please try again or contact support.",
                    model="error",
                    tool_calls=None
                )
            except Exception as e:
                print(f"Unexpected error in agent loop: {e}")
                return LLMResponse(
                    content="An unexpected error occurred. Please try again.",
                    model="error",
                    tool_calls=None
                )

        # Max turns reached
        return LLMResponse(
            content="This conversation has become quite complex. Let me summarize what we've discussed so far, and you can let me know what you'd like to focus on next.",
            model=self.llm_client.default_model,
            tool_calls=None
        )

    async def execute_tool(self, tool_call: ToolCall) -> Any:
        """
        Execute a tool call and return result.

        Args:
            tool_call: Tool call from LLM

        Returns:
            Tool execution result

        Raises:
            ToolError: If tool execution fails
        """
        tool_name = tool_call.name
        tool_args = tool_call.arguments

        # Get tool function
        if tool_name not in self.tools:
            raise ToolError(f"Unknown tool: {tool_name}")

        tool_func = self.tools[tool_name]

        # Add context to arguments
        tool_args["_agency_id"] = self.agency_id
        tool_args["_conversation_id"] = self.conversation_id

        try:
            # Execute tool
            result = await tool_func(**tool_args)
            return result

        except ToolError as e:
            raise e
        except Exception as e:
            raise ToolError(f"Tool execution failed: {str(e)}")

    async def _save_tool_results(
        self,
        tool_calls: List[ToolCall],
        tool_results: List[Dict[str, str]]
    ) -> None:
        """Save tool results to conversation history."""
        try:
            # Create tool role messages for each result
            for tool_result in tool_results:
                message = {
                    "conversation_id": self.conversation_id,
                    "role": MessageRole.TOOL.value,
                    "content": tool_result["output"],
                    "tool_results": [tool_result]
                }

                self.supabase.table("messages").insert(message).execute()

        except Exception as e:
            print(f"Error saving tool results: {e}")

    async def generate_offer_summary(self, offer_data: Dict[str, Any]) -> str:
        """Generate a summary of an offer for the agent to present."""
        prompt = f"""Summarize this travel offer in a compelling way for the agency staff:

Title: {offer_data.get('title')}
Destination: {offer_data.get('destination')}
Price: {offer_data.get('pricing', {}).get('total')} {offer_data.get('pricing', {}).get('currency')}
Duration: {len(offer_data.get('itinerary', []))} days

Create a brief summary highlighting key selling points and value.
"""

        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                system="You are a travel marketing expert. Write concise, compelling summaries.",
                temperature=0.7
            )
            return response
        except Exception as e:
            return f"Offer created: {offer_data.get('title')} to {offer_data.get('destination')}"
