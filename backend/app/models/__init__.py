"""
Models package initialization.
"""

from app.models.client import (
    Address,
    SocialLinks,
    BrandColors,
    ConversationMessage,
    OnboardingData,
    ClientData,
    ClientResponse,
    ClientCreate,
    ClientUpdate,
    ClientListResponse
)

from app.models.onboarding import (
    OnboardingStartRequest,
    OnboardingStartResponse,
    OnboardingMessageRequest,
    OnboardingMessageResponse,
    OnboardingStatusResponse,
    WebhookOnboardingComplete,
    WebhookResponse
)

__all__ = [
    # Client models
    "Address",
    "SocialLinks",
    "BrandColors",
    "ConversationMessage",
    "OnboardingData",
    "ClientData",
    "ClientResponse",
    "ClientCreate",
    "ClientUpdate",
    "ClientListResponse",
    # Onboarding models
    "OnboardingStartRequest",
    "OnboardingStartResponse",
    "OnboardingMessageRequest",
    "OnboardingMessageResponse",
    "OnboardingStatusResponse",
    "WebhookOnboardingComplete",
    "WebhookResponse",
]
