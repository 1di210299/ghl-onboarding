"""
Webhook endpoints.
Handles incoming webhooks for various events.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models import WebhookOnboardingComplete, WebhookResponse
from app.core.database import supabase
from app.core.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


async def trigger_n8n_webhook(client_data: dict) -> dict:
    """
    Trigger n8n webhook for GoHighLevel sync.
    
    Args:
        client_data: Complete client data to sync
        
    Returns:
        Response from n8n webhook
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.n8n_webhook_url,
                json={
                    "event": "onboarding.completed",
                    "data": client_data
                }
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error triggering n8n webhook: {e}")
        raise


@router.post("/onboarding-complete", response_model=WebhookResponse)
async def onboarding_complete_webhook(
    payload: WebhookOnboardingComplete,
    background_tasks: BackgroundTasks
):
    """
    Webhook endpoint called when onboarding completes.
    
    This triggers:
    1. n8n workflow to sync data to GoHighLevel
    2. Any other post-onboarding automation
    
    The n8n workflow runs in the background to avoid blocking.
    """
    try:
        client_id = payload.client_id
        
        # Fetch complete client data
        result = supabase.service.table("clients").select("*").eq(
            "id", client_id
        ).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Client not found")
        
        client_data = result.data[0]
        
        # Verify onboarding is actually completed
        if not client_data.get("onboarding_completed"):
            raise HTTPException(
                status_code=400,
                detail="Client onboarding is not marked as completed"
            )
        
        # Trigger n8n webhook in background
        background_tasks.add_task(trigger_n8n_webhook, client_data)
        
        logger.info(f"Triggered onboarding complete webhook for client: {client_id}")
        
        return WebhookResponse(
            success=True,
            message="Onboarding completion webhook processed successfully",
            client_id=client_id,
            ghl_contact_id=client_data.get("ghl_contact_id")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ghl-sync-complete")
async def ghl_sync_complete_webhook(payload: dict):
    """
    Webhook endpoint called by n8n after GoHighLevel sync completes.
    
    Updates the client record with the GHL contact ID.
    """
    try:
        client_id = payload.get("client_id")
        ghl_contact_id = payload.get("ghl_contact_id")
        
        if not client_id or not ghl_contact_id:
            raise HTTPException(
                status_code=400,
                detail="Missing client_id or ghl_contact_id"
            )
        
        # Update client with GHL contact ID
        result = supabase.service.table("clients").update({
            "ghl_contact_id": ghl_contact_id,
            "updated_at": "now()"
        }).eq("id", client_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Client not found")
        
        logger.info(f"Updated client {client_id} with GHL contact ID: {ghl_contact_id}")
        
        return {
            "success": True,
            "message": "GHL contact ID updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing GHL sync webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def webhook_health():
    """Health check endpoint for webhook monitoring."""
    return {
        "status": "healthy",
        "service": "webhooks",
        "n8n_configured": bool(settings.n8n_webhook_url)
    }
