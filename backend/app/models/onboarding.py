"""
API request and response models for onboarding endpoints.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class OnboardingStartRequest(BaseModel):
    """Request to start a new onboarding session."""
    
    tenant_id: str = Field(..., description="Tenant UUID")
    practice_name: Optional[str] = Field(None, description="Initial practice name if known")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "00000000-0000-0000-0000-000000000001",
                "practice_name": "Healthy Life Medical Center"
            }
        }


class OnboardingStartResponse(BaseModel):
    """Response when starting onboarding."""
    
    session_id: str = Field(..., description="Unique session identifier")
    client_id: str = Field(..., description="Client UUID")
    message: str = Field(..., description="Initial bot message")
    current_step: int = Field(default=0, description="Current step in onboarding")
    current_stage: str = Field(default="Quick Start", description="Current stage name")
    total_questions: int = Field(default=48, description="Total number of questions")
    history: list = Field(default=[], description="Previous conversation history for resume")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123xyz",
                "client_id": "12345678-1234-1234-1234-123456789012",
                "message": "Welcome! I'm here to help onboard your practice. Let's start with the basics. What's your practice name?",
                "current_step": 0
            }
        }


class OnboardingMessageRequest(BaseModel):
    """Request to send a message in an ongoing onboarding session."""
    
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., min_length=1, description="User's message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123xyz",
                "message": "Healthy Life Medical Center"
            }
        }


class OnboardingMessageResponse(BaseModel):
    """Response to a user message."""
    
    session_id: str = Field(..., description="Session identifier")
    bot_message: str = Field(..., description="Bot's response")
    bot_messages: list = Field(default=[], description="All new bot messages (for phase completion + question)")
    current_step: int = Field(..., description="Current step in onboarding")
    current_stage: Optional[str] = Field(None, description="Current stage name")
    total_questions: int = Field(default=48, description="Total number of questions")
    is_completed: bool = Field(default=False, description="Whether onboarding is complete")
    collected_data: Optional[dict] = Field(None, description="Data collected so far")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123xyz",
                "bot_message": "Great! Is there a legal business name that's different from 'Healthy Life Medical Center', or are they the same?",
                "current_step": 1,
                "is_completed": False,
                "collected_data": {
                    "practice_name": "Healthy Life Medical Center"
                }
            }
        }


class OnboardingStatusResponse(BaseModel):
    """Response for onboarding status check."""
    
    session_id: str = Field(..., description="Session identifier")
    client_id: str = Field(..., description="Client UUID")
    current_step: int = Field(..., description="Current step (0-48)")
    total_steps: int = Field(default=48, description="Total number of steps")
    current_stage: Optional[str] = Field(None, description="Current stage name")
    progress_percent: int = Field(..., description="Completion percentage")
    is_completed: bool = Field(..., description="Whether onboarding is complete")
    started_at: datetime = Field(..., description="Session start time")
    completed_at: Optional[datetime] = Field(None, description="Session completion time")
    collected_data: dict = Field(..., description="All collected data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123xyz",
                "client_id": "12345678-1234-1234-1234-123456789012",
                "current_step": 5,
                "total_steps": 10,
                "progress_percent": 50,
                "is_completed": False,
                "started_at": "2025-01-15T10:00:00Z",
                "completed_at": None,
                "collected_data": {
                    "practice_name": "Healthy Life Medical Center",
                    "email": "info@healthylifemedical.com"
                }
            }
        }


class WebhookOnboardingComplete(BaseModel):
    """Webhook payload when onboarding completes."""
    
    event: Literal["onboarding.completed"] = Field(..., description="Event type")
    client_id: str = Field(..., description="Client UUID")
    tenant_id: str = Field(..., description="Tenant UUID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    data: dict = Field(..., description="Complete client data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event": "onboarding.completed",
                "client_id": "12345678-1234-1234-1234-123456789012",
                "tenant_id": "00000000-0000-0000-0000-000000000001",
                "timestamp": "2025-01-15T10:45:00Z",
                "data": {}
            }
        }


class WebhookResponse(BaseModel):
    """Response from webhook endpoint."""
    
    success: bool = Field(..., description="Whether webhook was processed successfully")
    message: str = Field(..., description="Status message")
    client_id: str = Field(..., description="Client UUID")
    ghl_contact_id: Optional[str] = Field(None, description="GoHighLevel contact ID if synced")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Onboarding completed and synced to GoHighLevel",
                "client_id": "12345678-1234-1234-1234-123456789012",
                "ghl_contact_id": "ghl_contact_abc123"
            }
        }
