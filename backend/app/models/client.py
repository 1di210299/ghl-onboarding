"""
Pydantic models for data validation and serialization.
These models define the structure of client data collected during onboarding.
"""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, EmailStr, HttpUrl, field_validator, model_validator
import re


class Address(BaseModel):
    """Physical address model with validation."""
    
    street: str = Field(..., min_length=1, max_length=255, description="Street address")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    state: str = Field(..., min_length=2, max_length=2, description="Two-letter state code")
    zip: str = Field(..., min_length=5, max_length=10, description="ZIP or ZIP+4 code")
    
    @field_validator('state')
    @classmethod
    def validate_state(cls, v: str) -> str:
        """Validate state code is uppercase two letters."""
        if not re.match(r'^[A-Z]{2}$', v.upper()):
            raise ValueError('State must be a two-letter code (e.g., CA, NY)')
        return v.upper()
    
    @field_validator('zip')
    @classmethod
    def validate_zip(cls, v: str) -> str:
        """Validate ZIP code format."""
        # Remove any spaces or dashes
        clean_zip = v.replace(' ', '').replace('-', '')
        
        if not re.match(r'^\d{5}(\d{4})?$', clean_zip):
            raise ValueError('ZIP code must be 5 digits or ZIP+4 format')
        
        # Format as XXXXX or XXXXX-XXXX
        if len(clean_zip) == 9:
            return f"{clean_zip[:5]}-{clean_zip[5:]}"
        return clean_zip
    
    class Config:
        json_schema_extra = {
            "example": {
                "street": "123 Medical Plaza Dr",
                "city": "Los Angeles",
                "state": "CA",
                "zip": "90210"
            }
        }


class SocialLinks(BaseModel):
    """Social media links with optional fields."""
    
    facebook: Optional[HttpUrl] = Field(None, description="Facebook page URL")
    instagram: Optional[HttpUrl] = Field(None, description="Instagram profile URL")
    linkedin: Optional[HttpUrl] = Field(None, description="LinkedIn page URL")
    twitter: Optional[HttpUrl] = Field(None, description="Twitter/X profile URL")
    
    @model_validator(mode='after')
    def at_least_one_link(self):
        """Ensure at least one social link is provided."""
        if not any([self.facebook, self.instagram, self.linkedin, self.twitter]):
            raise ValueError('At least one social media link must be provided')
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "facebook": "https://facebook.com/healthylifemedical",
                "instagram": "https://instagram.com/healthylifemedical"
            }
        }


class BrandColors(BaseModel):
    """Brand color scheme with hex color validation."""
    
    primary: str = Field(..., description="Primary brand color in hex format")
    secondary: str = Field(..., description="Secondary brand color in hex format")
    
    @field_validator('primary', 'secondary')
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        """Validate hex color format."""
        # Add # if not present
        if not v.startswith('#'):
            v = f'#{v}'
        
        # Validate hex format (#RGB or #RRGGBB)
        if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', v):
            raise ValueError('Color must be a valid hex code (e.g., #FF5733 or #F57)')
        
        # Convert short form to long form
        if len(v) == 4:
            v = f'#{v[1]}{v[1]}{v[2]}{v[2]}{v[3]}{v[3]}'
        
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "primary": "#0066CC",
                "secondary": "#FF6B35"
            }
        }


class ConversationMessage(BaseModel):
    """Single message in the conversation history."""
    
    role: Literal["assistant", "user"] = Field(..., description="Message sender role")
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "assistant",
                "content": "What's your practice name?",
                "timestamp": "2025-01-15T10:30:00Z"
            }
        }


class OnboardingData(BaseModel):
    """Complete onboarding conversation history and metadata."""
    
    session_id: str = Field(..., description="Unique session identifier")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Onboarding start time")
    completed_at: Optional[datetime] = Field(None, description="Onboarding completion time")
    messages: List[ConversationMessage] = Field(default_factory=list, description="Conversation history")
    current_step: int = Field(default=0, description="Current question step (0-10)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123xyz",
                "started_at": "2025-01-15T10:00:00Z",
                "completed_at": "2025-01-15T10:45:00Z",
                "messages": [],
                "current_step": 10
            }
        }


class ClientData(BaseModel):
    """Complete client data model matching database schema."""
    
    # Required fields
    practice_name: str = Field(..., min_length=1, max_length=255, description="Practice name")
    
    # Optional practice info
    legal_name: Optional[str] = Field(None, max_length=255, description="Legal business name")
    
    # Contact information
    address: Optional[Address] = Field(None, description="Physical address")
    website: Optional[HttpUrl] = Field(None, description="Practice website URL")
    email: Optional[EmailStr] = Field(None, description="Practice email address")
    phone: Optional[str] = Field(None, description="Practice phone number")
    
    # Social media
    social_links: Optional[SocialLinks] = Field(None, description="Social media links")
    
    # Branding
    terminology_preference: Optional[Literal["patients", "members", "clients"]] = Field(
        None,
        description="Preferred terminology for people served"
    )
    brand_colors: Optional[BrandColors] = Field(None, description="Brand color scheme")
    
    # Business
    business_goals: Optional[List[str]] = Field(
        None,
        min_length=1,
        max_length=5,
        description="Top 3-5 business goals"
    )
    
    # Integration
    ghl_contact_id: Optional[str] = Field(None, description="GoHighLevel contact ID")
    
    # Status
    onboarding_completed: bool = Field(default=False, description="Onboarding completion status")
    onboarding_data: Optional[OnboardingData] = Field(None, description="Full conversation history")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate and format phone number."""
        if v is None:
            return v
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', v)
        
        # Check if we have 10 or 11 digits (with optional country code)
        if len(digits) == 10:
            # Format as (XXX) XXX-XXXX
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            # Format as +1 (XXX) XXX-XXXX
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            raise ValueError('Phone number must be 10 digits or include country code')
    
    @field_validator('business_goals')
    @classmethod
    def validate_business_goals(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Ensure business goals are not empty strings."""
        if v is None:
            return v
        
        # Filter out empty strings and strip whitespace
        cleaned = [goal.strip() for goal in v if goal.strip()]
        
        if not cleaned:
            raise ValueError('Business goals cannot be empty')
        
        if len(cleaned) < 1:
            raise ValueError('At least one business goal is required')
        
        return cleaned
    
    class Config:
        json_schema_extra = {
            "example": {
                "practice_name": "Healthy Life Medical Center",
                "legal_name": "Healthy Life Medical Center LLC",
                "address": {
                    "street": "123 Medical Plaza Dr",
                    "city": "Los Angeles",
                    "state": "CA",
                    "zip": "90210"
                },
                "website": "https://healthylifemedical.com",
                "email": "info@healthylifemedical.com",
                "phone": "(555) 123-4567",
                "social_links": {
                    "facebook": "https://facebook.com/healthylifemedical"
                },
                "terminology_preference": "patients",
                "brand_colors": {
                    "primary": "#0066CC",
                    "secondary": "#FF6B35"
                },
                "business_goals": [
                    "Increase patient retention by 30%",
                    "Launch telemedicine services",
                    "Improve online reputation"
                ]
            }
        }


class ClientResponse(ClientData):
    """Client response model with database fields."""
    
    id: str = Field(..., description="Client UUID")
    tenant_id: str = Field(..., description="Tenant UUID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ClientCreate(BaseModel):
    """Request model for creating a new client."""
    
    tenant_id: str = Field(..., description="Tenant UUID")
    practice_name: str = Field(..., min_length=1, max_length=255, description="Practice name")


class ClientUpdate(BaseModel):
    """Request model for updating client data."""
    
    practice_name: Optional[str] = Field(None, min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    address: Optional[Address] = None
    website: Optional[HttpUrl] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    social_links: Optional[SocialLinks] = None
    terminology_preference: Optional[Literal["patients", "members", "clients"]] = None
    brand_colors: Optional[BrandColors] = None
    business_goals: Optional[List[str]] = None
    ghl_contact_id: Optional[str] = None
    onboarding_completed: Optional[bool] = None
    onboarding_data: Optional[OnboardingData] = None


class ClientListResponse(BaseModel):
    """Response model for listing clients."""
    
    clients: List[ClientResponse]
    total: int
    page: int
    page_size: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "clients": [],
                "total": 42,
                "page": 1,
                "page_size": 20
            }
        }
