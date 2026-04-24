"""
Agent API routes - AI conversation handling.
"""

import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from core import get_supabase_client, set_agency_context, get_llm_client
from models import User, MessageRole
from .auth import get_current_user
from agent.orchestrator import AgentOrchestrator

router = APIRouter()

# Active orchestrators by conversation_id
_active_orchestrators: Dict[str, AgentOrchestrator] = {}


class ChatRequest(BaseModel):
    message: str
    conversation_id: str


class ToolResultRequest(BaseModel):
    tool_call_id: str
    result: Any
    error: str = None


@router.post("/chat", response_model=dict)
async def chat(
    request: ChatRequest,
    user: User = Depends(get_current_user)
):
    """
    Send a message to the agent and get response.
    Synchronous request-response for simple queries.
    """
    supabase = get_supabase_client()
    await set_agency_context(supabase, str(user.agency_id))

    # Verify conversation exists and belongs to agency
    conv_result = supabase.table("conversations")\
        .select("*")\
        .eq("id", request.conversation_id)\
        .eq("agency_id", str(user.agency_id))\
        .single()\
        .execute()

    if not conv_result.data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Save user message
    supabase.table("messages").insert({
        "conversation_id": request.conversation_id,
        "role": MessageRole.USER.value,
        "content": request.message
    }).execute()

    # Initialize orchestrator
    orchestrator = AgentOrchestrator(
        agency_id=str(user.agency_id),
        conversation_id=request.conversation_id
    )

    # Load conversation history
    messages_result = supabase.table("messages")\
        .select("*")\
        .eq("conversation_id", request.conversation_id)\
        .order("created_at")\
        .execute()

    messages = messages_result.data or []

    # Run agent
    response = await orchestrator.run(
        user_message=request.message,
        conversation_history=messages,
        user_id=str(user.id)
    )

    # Save assistant message
    assistant_message = {
        "conversation_id": request.conversation_id,
        "role": MessageRole.ASSISTANT.value,
        "content": response.content,
        "model": response.model,
        "tokens_used": response.tokens_used,
        "latency_ms": int(response.latency_ms) if response.latency_ms else None
    }

    if response.tool_calls:
        assistant_message["tool_calls"] = [
            {
                "id": tc.id,
                "function": {
                    "name": tc.name,
                    "arguments": json.dumps(tc.arguments)
                }
            }
            for tc in response.tool_calls
        ]

    supabase.table("messages").insert(assistant_message).execute()

    # Execute tools if present
    tool_results = []
    if response.tool_calls:
        for tool_call in response.tool_calls:
            try:
                result = await orchestrator.execute_tool(tool_call)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "name": tool_call.name,
                    "result": result
                })

                # Save tool result message
                supabase.table("messages").insert({
                    "conversation_id": request.conversation_id,
                    "role": MessageRole.TOOL.value,
                    "content": json.dumps(result) if isinstance(result, dict) else str(result),
                    "tool_results": [{"tool_call_id": tool_call.id, "output": str(result)}]
                }).execute()

            except Exception as e:
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "name": tool_call.name,
                    "error": str(e)
                })

    return {
        "message": response.content,
        "tool_calls": [
            {
                "id": tc.id,
                "name": tc.name,
                "arguments": tc.arguments
            }
            for tc in (response.tool_calls or [])
        ],
        "tool_results": tool_results,
        "model": response.model,
        "tokens_used": response.tokens_used,
        "latency_ms": response.latency_ms
    }


@router.websocket("/ws/{conversation_id}")
async def agent_websocket(websocket: WebSocket, conversation_id: str):
    """
    WebSocket endpoint for real-time agent conversations.
    More responsive for interactive sessions.
    """
    await websocket.accept()

    try:
        # Expect auth token in first message
        auth_msg = await websocket.receive_text()
        auth_data = json.loads(auth_msg)
        token = auth_data.get("token")

        if not token:
            await websocket.send_json({"error": "Authentication required"})
            await websocket.close(code=1008)
            return

        # Verify token and get user
        from core import verify_jwt_token, get_user_by_auth_id

        try:
            auth_payload = await verify_jwt_token(token)
            user_data = await get_user_by_auth_id(auth_payload["id"])

            if not user_data:
                await websocket.send_json({"error": "User not found"})
                await websocket.close(code=1008)
                return

            user = User(**user_data)

        except Exception as e:
            await websocket.send_json({"error": f"Authentication failed: {str(e)}"})
            await websocket.close(code=1008)
            return

        # Verify conversation access
        supabase = get_supabase_client()
        await set_agency_context(supabase, str(user.agency_id))

        conv_result = supabase.table("conversations")\
            .select("*")\
            .eq("id", conversation_id)\
            .eq("agency_id", str(user.agency_id))\
            .single()\
            .execute()

        if not conv_result.data:
            await websocket.send_json({"error": "Conversation not found"})
            await websocket.close(code=1008)
            return

        # Initialize or get existing orchestrator
        if conversation_id not in _active_orchestrators:
            _active_orchestrators[conversation_id] = AgentOrchestrator(
                agency_id=str(user.agency_id),
                conversation_id=conversation_id
            )

        orchestrator = _active_orchestrators[conversation_id]

        await websocket.send_json({
            "type": "connected",
            "message": "Agent connected. Ready for conversation."
        })

        # Main conversation loop
        while True:
            try:
                data = await websocket.receive_text()
                payload = json.loads(data)

                message = payload.get("message", "")
                if not message:
                    continue

                # Save user message
                supabase.table("messages").insert({
                    "conversation_id": conversation_id,
                    "role": MessageRole.USER.value,
                    "content": message
                }).execute()

                # Load history
                messages_result = supabase.table("messages")\
                    .select("*")\
                    .eq("conversation_id", conversation_id)\
                    .order("created_at")\
                    .execute()

                # Send typing indicator
                await websocket.send_json({"type": "typing"})

                # Run agent
                response = await orchestrator.run(
                    user_message=message,
                    conversation_history=messages_result.data or [],
                    user_id=str(user.id)
                )

                # Save assistant message
                assistant_message = {
                    "conversation_id": conversation_id,
                    "role": MessageRole.ASSISTANT.value,
                    "content": response.content,
                    "model": response.model,
                    "tokens_used": response.tokens_used,
                    "latency_ms": int(response.latency_ms) if response.latency_ms else None
                }

                if response.tool_calls:
                    assistant_message["tool_calls"] = [
                        {
                            "id": tc.id,
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments)
                            }
                        }
                        for tc in response.tool_calls
                    ]

                supabase.table("messages").insert(assistant_message).execute()

                # Send response
                await websocket.send_json({
                    "type": "message",
                    "role": "assistant",
                    "content": response.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "name": tc.name,
                            "arguments": tc.arguments
                        }
                        for tc in (response.tool_calls or [])
                    ]
                })

                # Execute tools if present
                if response.tool_calls:
                    await websocket.send_json({"type": "tool_executing"})

                    for tool_call in response.tool_calls:
                        try:
                            result = await orchestrator.execute_tool(tool_call)

                            # Save tool result
                            supabase.table("messages").insert({
                                "conversation_id": conversation_id,
                                "role": MessageRole.TOOL.value,
                                "content": json.dumps(result) if isinstance(result, dict) else str(result),
                                "tool_results": [{"tool_call_id": tool_call.id, "output": str(result)}]
                            }).execute()

                            await websocket.send_json({
                                "type": "tool_result",
                                "tool_call_id": tool_call.id,
                                "name": tool_call.name,
                                "result": result
                            })

                        except Exception as e:
                            await websocket.send_json({
                                "type": "tool_error",
                                "tool_call_id": tool_call.id,
                                "name": tool_call.name,
                                "error": str(e)
                            })

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
            except Exception as e:
                await websocket.send_json({"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        pass
    finally:
        # Cleanup orchestrator if needed
        if conversation_id in _active_orchestrators:
            del _active_orchestrators[conversation_id]


async def handle_agent_websocket(websocket: WebSocket, conversation_id: str):
    """Wrapper for use in main.py WebSocket route."""
    await agent_websocket(websocket, conversation_id)
