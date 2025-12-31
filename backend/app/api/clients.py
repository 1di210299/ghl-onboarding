"""
Client management API endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models import (
    ClientResponse,
    ClientCreate,
    ClientUpdate,
    ClientListResponse
)
from app.core.database import supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("", response_model=ClientResponse, status_code=201)
@router.post("/", response_model=ClientResponse, status_code=201)
async def create_client(client: ClientCreate):
    """
    Create a new client record.
    
    This endpoint is typically called when starting onboarding.
    """
    try:
        # Insert into database
        result = supabase.service.table("clients").insert({
            "tenant_id": client.tenant_id,
            "practice_name": client.practice_name,
            "onboarding_completed": False
        }).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create client")
        
        logger.info(f"Created client: {result.data[0]['id']}")
        return result.data[0]
        
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=ClientListResponse)
@router.get("/", response_model=ClientListResponse)
async def list_clients(
    tenant_id: str = Query(..., description="Tenant UUID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status: completed, pending"),
    terminology: Optional[str] = Query(None, description="Filter by terminology preference")
):
    """
    List all clients for a tenant with pagination and filtering.
    
    Supports:
    - Pagination
    - Search by practice name or email
    - Filter by onboarding status
    - Filter by terminology preference
    """
    try:
        # Start query
        query = supabase.service.table("clients").select(
            "*",
            count="exact"
        ).eq("tenant_id", tenant_id)
        
        # Apply filters
        if search:
            query = query.or_(
                f"practice_name.ilike.%{search}%,email.ilike.%{search}%"
            )
        
        if status == "completed":
            query = query.eq("onboarding_completed", True)
        elif status == "pending":
            query = query.eq("onboarding_completed", False)
        
        if terminology:
            query = query.eq("terminology_preference", terminology)
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.order("created_at", desc=True).range(offset, offset + page_size - 1)
        
        # Execute query
        result = query.execute()
        
        return ClientListResponse(
            clients=result.data,
            total=result.count or 0,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error listing clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str):
    """
    Get a specific client by ID.
    
    Returns all client information including onboarding history.
    """
    try:
        result = supabase.service.table("clients").select("*").eq(
            "id", client_id
        ).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Client not found")
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(client_id: str, client_update: ClientUpdate):
    """
    Update client information.
    
    Allows partial updates of any client field.
    """
    try:
        # Build update data (exclude None values)
        update_data = client_update.model_dump(exclude_none=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        # Add updated_at timestamp
        update_data["updated_at"] = "now()"
        
        # Update in database
        result = supabase.service.table("clients").update(update_data).eq(
            "id", client_id
        ).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Client not found")
        
        logger.info(f"Updated client: {client_id}")
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{client_id}", status_code=204)
async def delete_client(client_id: str):
    """
    Delete a client.
    
    This is a hard delete. Use with caution.
    """
    try:
        result = supabase.service.table("clients").delete().eq(
            "id", client_id
        ).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Client not found")
        
        logger.info(f"Deleted client: {client_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client: {e}")
        raise HTTPException(status_code=500, detail=str(e))
