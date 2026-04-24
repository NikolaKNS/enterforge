"""
Message (conversation history) models.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class MessageRole(str, Enum):
    """Message role types."""
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SYSTEM = "system"


class ToolCall(BaseModel):
    """Tool call from assistant."""
    id: str
    type: str = "function"
    function: Dict[str, Any]  # {name: str, arguments: str}


class ToolResult(BaseModel):
    """Tool execution result."""
    tool_call_id: str
    output: str
    error: Optional[str] = None


class MessageBase(BaseModel):
    """Base message model."""
    role: MessageRole
    content: str


class MessageCreate(MessageBase):
    """Create message request."""
    conversation_id: UUID
    tool_calls: Optional[List[ToolCall]] = None
    tool_results: Optional[List[ToolResult]] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None


class Message(MessageBase):
    """Complete message model (from database)."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None
    created_at: datetime


class MessageForAPI(BaseModel):
    """Message formatted for Anthropic API."""
    role: str
    content: str


class MessageWithMetrics(Message):
    """Message with additional metrics."""
    conversation_title: Optional[str] = None
    user_name: Optional[str] = None


# Anthropic API formatted message utilities
def to_anthropic_messages(messages: List[Message]) -> List[Dict[str, str]]:
    """Convert internal messages to Anthropic API format."""
    result = []
    for msg in messages:
        if msg.role == MessageRole.USER:
            result.append({"role": "user", "content": msg.content})
        elif msg.role == MessageRole.ASSISTANT:
            result.append({"role": "assistant", "content": msg.content})
        # Tool messages handled separately via tool_result blocks
    return result
