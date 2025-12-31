"""
Core package initialization.
"""

from app.core.config import settings, get_settings
from app.core.database import supabase, get_supabase

__all__ = [
    "settings",
    "get_settings",
    "supabase",
    "get_supabase",
]
