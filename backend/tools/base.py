"""
Base classes and utilities for agent tools.
"""

from typing import Any, Dict
from functools import wraps
import asyncio


class ToolError(Exception):
    """Error raised by agent tools."""
    pass


class ToolResult:
    """Standardized tool result format."""

    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error
        }


def tool(name: str, description: str):
    """Decorator to register a tool."""
    def decorator(func):
        func._is_tool = True
        func._tool_name = name
        func._tool_description = description
        return func
    return decorator


def async_retry(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry async functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))
            raise last_exception
        return wrapper
    return decorator
