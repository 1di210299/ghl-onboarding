"""
Database connection and client management for Supabase.
"""

from supabase import create_client, Client
from app.core.config import settings
from functools import lru_cache
from typing import Optional
import logging
import httpx

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Wrapper for Supabase client with connection management."""
    
    def __init__(self):
        """Initialize Supabase clients."""
        self._anon_client: Optional[Client] = None
        self._service_client: Optional[Client] = None
    
    @property
    def anon(self) -> Client:
        """Get Supabase client with anon key (for authenticated users with RLS)."""
        if self._anon_client is None:
            logger.info("Initializing Supabase anon client")
            self._anon_client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
        return self._anon_client
    
    @property
    def service(self) -> Client:
        """Get Supabase client with service key (bypasses RLS)."""
        if self._service_client is None:
            logger.info("Initializing Supabase service client")
            logger.info(f"Supabase URL: {settings.supabase_url}")
            logger.info(f"Service key length: {len(settings.supabase_service_key)}")
            
            try:
                logger.info("Calling create_client...")
                self._service_client = create_client(
                    settings.supabase_url,
                    settings.supabase_service_key
                )
                logger.info("Supabase client created successfully")
            except Exception as e:
                logger.error(f"Failed to create Supabase client: {type(e).__name__}: {e}")
                raise
        
        logger.info("Returning cached service client")
        return self._service_client
    
    def set_tenant_context(self, tenant_id: str) -> None:
        """
        Set tenant context for Row-Level Security.
        
        Args:
            tenant_id: UUID of the tenant
        """
        try:
            # Execute SQL to set the context
            self.service.rpc('set_tenant_context', {'tenant_uuid': tenant_id}).execute()
            logger.info(f"Set tenant context to {tenant_id}")
        except Exception as e:
            logger.error(f"Failed to set tenant context: {e}")
            raise


@lru_cache()
def get_supabase() -> SupabaseClient:
    """Get cached Supabase client instance."""
    return SupabaseClient()


# Export for convenience
supabase = get_supabase()
