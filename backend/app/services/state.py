"""
LangGraph conversation state management.
Defines the state structure for the onboarding conversation flow.
"""

from typing import TypedDict, Optional, List, Annotated
from langchain_core.messages import BaseMessage
import operator


class OnboardingState(TypedDict):
    """
    State for the onboarding conversation.
    
    This state is passed between nodes in the LangGraph workflow.
    Each field represents data collected or metadata about the conversation.
    """
    
    # Session management
    session_id: str
    client_id: str
    tenant_id: str
    
    # Conversation flow
    messages: Annotated[List[BaseMessage], operator.add]
    current_step: int
    current_stage: Optional[str]  # "Quick Start", "Team & Tech", "Identity & Brand", "Digital & Growth"
    
    # Collected data fields (48 questions from questions.json)
    # Stage 1: Quick Start
    q1_admin: Optional[str]  # Full name
    q2_admin: Optional[str]  # Email
    q3_admin: Optional[str]  # Phone
    q4_admin: Optional[str]  # Practice name
    q5_admin: Optional[str]  # Address
    q6_admin: Optional[str]  # City
    q7_admin: Optional[str]  # State
    q8_admin: Optional[str]  # ZIP
    q9_admin: Optional[str]  # EIN
    
    # Stage 2: Team & Tech
    q10_team: Optional[str]  # Number of providers
    q11_team: Optional[str]  # Number of staff
    q12_team: Optional[list]  # Staff roles
    q13_tech: Optional[str]  # EHR system
    q14_marketing: Optional[bool]  # Has marketing company
    q15_marketing: Optional[str]  # Marketing company name (conditional)
    q16_tech: Optional[list]  # Current tools
    
    # Stage 3: Identity & Brand
    q17_personality: Optional[str]  # Practice personality
    q18_personality: Optional[str]  # Target patient
    q19_personality: Optional[str]  # Ideal new patient
    q20_personality: Optional[str]  # What makes you different
    q21_services: Optional[list]  # Services offered
    q22_services: Optional[str]  # Flagship service
    q23_brand: Optional[str]  # Brand colors
    q24_brand: Optional[str]  # Logo file
    q25_brand: Optional[str]  # Brand personality
    q26_brand: Optional[str]  # Keywords/taglines
    q27_messaging: Optional[str]  # Tone preference
    q28_messaging: Optional[str]  # Patient terminology
    
    # Stage 4: Digital & Growth
    q29_online: Optional[bool]  # Has website
    q30_online: Optional[str]  # Website URL (conditional)
    q31_online: Optional[str]  # Why no website (conditional)
    q32_online: Optional[int]  # Website satisfaction (1-5)
    q33_online: Optional[str]  # Website issues (conditional)
    q34_social: Optional[list]  # Social media platforms
    q35_social: Optional[str]  # Instagram handle (conditional)
    q36_social: Optional[str]  # Facebook page (conditional)
    q37_social: Optional[str]  # LinkedIn URL (conditional)
    q38_social: Optional[str]  # Blog URL (conditional)
    q39_content: Optional[str]  # Content creation preference
    q40_content: Optional[str]  # Human content topics (conditional)
    q41_reputation: Optional[str]  # Has review system
    q42_reputation: Optional[int]  # Average rating (1-5)
    q43_reputation: Optional[str]  # Where reviews are
    q44_growth: Optional[list]  # Top 3 goals
    q45_growth: Optional[str]  # Biggest challenge
    q46_automation: Optional[list]  # Tasks to automate
    q47_budget: Optional[str]  # Monthly budget
    q48_notes: Optional[str]  # Additional notes
    
    # Status flags
    is_completed: bool
    needs_clarification: bool
    last_validation_error: Optional[str]


class ConversationCheckpoint(TypedDict):
    """
    Checkpoint data for conversation persistence.
    Allows pausing and resuming conversations.
    """
    
    session_id: str
    client_id: str
    tenant_id: str
    current_step: int
    collected_data: dict
    message_history: List[dict]
    created_at: str
    updated_at: str
