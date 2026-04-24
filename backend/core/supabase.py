"""
Supabase client initialization.
"""

import os
from typing import Optional
from supabase import create_client, Client

# Module-level client instance
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client instance."""
    global _supabase_client

    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

        # Try loading from .env file if not in environment
        if not supabase_url or not supabase_key:
            try:
                from pathlib import Path
                # Handle Windows/git bash path differences
                base_path = Path(__file__).parent.parent
                env_path = base_path / ".env"
                # Also try with explicit C: drive if in git bash
                if not env_path.exists():
                    # Try resolving the path differently for git bash
                    current_file = Path("C:/Users/Nikola/tripforge/backend/core/supabase.py")
                    env_path = current_file.parent.parent / ".env"
                if env_path.exists():
                    with open(env_path) as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("#"):
                                continue
                            if "=" in line:
                                key, value = line.split("=", 1)
                                key = key.strip()
                                value = value.strip().strip('"').strip("'")
                                if key == "SUPABASE_URL" and not supabase_url:
                                    supabase_url = value
                                elif key == "SUPABASE_SERVICE_KEY" and not supabase_key:
                                    supabase_key = value
            except Exception as e:
                print(f"Error loading .env: {e}")

        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment"
            )

        _supabase_client = create_client(supabase_url, supabase_key)

    return _supabase_client
