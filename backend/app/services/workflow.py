"""
LangGraph conversation workflow for onboarding.
Manages the step-by-step conversation flow using LangGraph state machine.
"""

from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.services.state import OnboardingState
from app.services import validators
from app.core.config import settings
from app.core.database import supabase
import logging
import uuid
import json
import os

logger = logging.getLogger(__name__)


# Load questions from JSON config
def load_questions_config() -> Dict[str, Any]:
    """Load questions configuration from JSON file."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'questions.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# Global questions config
_QUESTIONS_CONFIG = load_questions_config()
TOTAL_QUESTIONS = _QUESTIONS_CONFIG['total_questions']
STAGES = {stage['id']: stage for stage in _QUESTIONS_CONFIG['stages']}


def get_question_by_index(index: int) -> Optional[Dict[str, Any]]:
    """Get question by its index (0-based)."""
    for stage in _QUESTIONS_CONFIG['stages']:
        if index < len(stage['questions']):
            return stage['questions'][index]
        index -= len(stage['questions'])
    return None


def get_stage_for_question(question_index: int) -> Optional[str]:
    """Get stage ID for a given question index."""
    count = 0
    for stage in _QUESTIONS_CONFIG['stages']:
        count += len(stage['questions'])
        if question_index < count:
            return stage['id']
    return None


def check_dependency(question: Dict[str, Any], state: Dict[str, Any]) -> bool:
    """Check if question's dependency condition is met."""
    dependency = question.get('dependency')
    if not dependency:
        return True
    
    # Parse dependency (e.g., "Q14 = Yes", "Q29 ≠ No", "Instagram selected")
    if '=' in dependency:
        parts = dependency.split('=')
        if len(parts) == 2:
            dep_q = parts[0].strip()
            dep_value = parts[1].strip()
            
            # Check if it's checking a previous answer
            if dep_q.startswith('Q'):
                # Get the field name for that question
                dep_q_num = int(dep_q[1:])
                dep_question = get_question_by_index(dep_q_num - 1)
                if dep_question:
                    field_name = dep_question['field_name']
                    actual_value = state.get(field_name)
                    return str(actual_value).lower() == dep_value.lower()
    
    elif '≠' in dependency or '!=' in dependency:
        sep = '≠' if '≠' in dependency else '!='
        parts = dependency.split(sep)
        if len(parts) == 2:
            dep_q = parts[0].strip()
            dep_value = parts[1].strip()
            
            if dep_q.startswith('Q'):
                dep_q_num = int(dep_q[1:])
                dep_question = get_question_by_index(dep_q_num - 1)
                if dep_question:
                    field_name = dep_question['field_name']
                    actual_value = state.get(field_name)
                    return str(actual_value).lower() != dep_value.lower()
    
    elif 'selected' in dependency.lower():
        # Handle "Instagram selected", "Facebook selected", etc.
        platform = dependency.replace('selected', '').strip()
        # Check if platform is in the multi-select answer from Q34
        q34_answer = state.get('q34_social', '')
        return platform.lower() in str(q34_answer).lower()
    
    return True


class OnboardingWorkflow:
    """
    LangGraph workflow for managing onboarding conversations.
    """
    
    def __init__(self):
        """Initialize the workflow with LLM and graph."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine.
        
        Returns:
            Configured StateGraph
        """
        workflow = StateGraph(OnboardingState)
        
        # Add nodes for each step
        workflow.add_node("ask_question", self.ask_question_node)
        workflow.add_node("validate_response", self.validate_response_node)
        workflow.add_node("save_data", self.save_data_node)
        workflow.add_node("complete", self.complete_node)
        
        # Define edges - use START instead of set_entry_point in LangGraph 1.0
        workflow.add_edge(START, "ask_question")
        
        # STOP after asking question - don't auto-validate
        workflow.add_edge("ask_question", END)
        
        # When validating, either ask for clarification or save
        workflow.add_conditional_edges(
            "validate_response",
            self.should_continue,
            {
                "clarify": "ask_question",
                "save": "save_data",
                "complete": "complete"
            }
        )
        # After saving, ask next question and STOP
        workflow.add_edge("save_data", "ask_question")
        workflow.add_edge("complete", END)
        
        return workflow.compile()
    
    def ask_question_node(self, state: OnboardingState) -> Dict[str, Any]:
        """
        Node that asks the next question.
        
        Args:
            state: Current conversation state
            
        Returns:
            Updated state with bot's question
        """
        step = state["current_step"]
        
        # Check if we've reached the end
        if step >= TOTAL_QUESTIONS:
            question = "Thank you for completing the onboarding! Your information has been saved."
            state["is_completed"] = True
        elif state.get("needs_clarification"):
            # If we need clarification, ask for it
            question = state.get("last_validation_error", "I didn't quite understand that. Could you please try again?")
            state["needs_clarification"] = False
        else:
            # Get the question from config
            current_question = get_question_by_index(step)
            
            if not current_question:
                question = "Something went wrong. Let's try again."
            else:
                # Check if this question should be skipped due to dependencies
                while current_question and not check_dependency(current_question, state):
                    step += 1
                    state["current_step"] = step
                    current_question = get_question_by_index(step)
                
                if current_question:
                    question = current_question['text']
                    
                    # Add options if it's a choice question
                    if current_question.get('options') and current_question['type'] in ['Multiple Choice', 'Multi-Select']:
                        options = current_question['options']
                        # Handle options as list or string
                        if isinstance(options, list):
                            options_str = ', '.join(options)
                        else:
                            options_str = options
                        question += f"\n\nOptions: {options_str}"
                    
                    # Add note if present
                    if current_question.get('notes'):
                        question += f"\n({current_question['notes']})"
                    
                    # Update current stage
                    stage_id = get_stage_for_question(step)
                    if stage_id:
                        state["current_stage"] = stage_id
                else:
                    question = "Thank you! You've completed all questions."
                    state["is_completed"] = True
        
        # Add bot message to conversation
        bot_message = AIMessage(content=question)
        state["messages"].append(bot_message)
        
        logger.info(f"Step {step}: Asked question from {state.get('current_stage', 'unknown')} stage")
        
        return state
    
    def validate_response_node(self, state: OnboardingState) -> Dict[str, Any]:
        """
        Node that validates the user's response.
        
        Args:
            state: Current conversation state
            
        Returns:
            Updated state with validation results
        """
        step = state["current_step"]
        
        # Get the last user message
        user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
        if not user_messages:
            return state
        
        last_message = user_messages[-1].content
        
        # Get current question config
        current_question = get_question_by_index(step)
        if not current_question:
            state["needs_clarification"] = True
            state["last_validation_error"] = "Error loading question. Please try again."
            return state
        
        # Validate based on question type and validator
        validator_type = current_question.get('validator', 'text')
        is_valid = True
        data = last_message
        error = None
        
        if validator_type == 'email':
            is_valid, data, error = validators.validate_email(last_message)
        elif validator_type == 'text' or validator_type == 'long_text':
            is_valid, data, error = validators.validate_text(last_message)
        elif validator_type == 'boolean':
            # Yes/No questions
            is_valid, data, error = validators.validate_boolean(last_message)
        elif validator_type == 'choice':
            # Multiple choice - validate against options
            options = current_question.get('options', '')
            if options:
                # Handle options as list or comma-separated string
                if isinstance(options, list):
                    valid_options = options
                else:
                    valid_options = [opt.strip() for opt in options.split(',')]
                is_valid, data, error = validators.validate_choice(last_message, valid_options)
            else:
                is_valid, data, error = True, last_message, None
        elif validator_type == 'multi_select':
            # Multi-select - validate against options
            options = current_question.get('options', '')
            if options:
                # Handle options as list or comma-separated string
                if isinstance(options, list):
                    valid_options = options
                else:
                    valid_options = [opt.strip() for opt in options.split(',')]
                is_valid, data, error = validators.validate_multi_select(last_message, valid_options)
            else:
                is_valid, data, error = True, last_message, None
        elif validator_type == 'scale':
            # Scale validation (1-5)
            is_valid, data, error = validators.validate_scale(last_message, 1, 5)
        else:
            # Default text validation
            is_valid, data, error = validators.validate_text(last_message)
        
        if is_valid:
            # Store the validated data using the field_name from config
            field_name = current_question['field_name']
            state[field_name] = data
            
            state["needs_clarification"] = False
            state["last_validation_error"] = None
            logger.info(f"Step {step}: Validation successful for {field_name}")
        else:
            # Need clarification
            state["needs_clarification"] = True
            state["last_validation_error"] = error
            logger.warning(f"Step {step}: Validation failed - {error}")
        
        return state
    
    def save_data_node(self, state: OnboardingState) -> Dict[str, Any]:
        """
        Node that saves collected data to database.
        
        Args:
            state: Current conversation state
            
        Returns:
            Updated state after saving
        """
        try:
            # Move to next step
            state["current_step"] += 1
            
            # Save to database
            self._save_to_database(state)
            
            logger.info(f"Saved data for step {state['current_step'] - 1}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
        
        return state
    
    def complete_node(self, state: OnboardingState) -> Dict[str, Any]:
        """
        Node that handles completion of onboarding.
        
        Args:
            state: Current conversation state
            
        Returns:
            Final state
        """
        state["is_completed"] = True
        
        # Final message
        practice_name = state.get('q4_admin', 'your practice')
        completion_message = (
            f"Thank you! We've successfully collected all the information for {practice_name}. "
            "Your onboarding is now complete, and we'll sync this information to GoHighLevel. "
            "Our team will be in touch soon!"
        )
        
        bot_message = AIMessage(content=completion_message)
        state["messages"].append(bot_message)
        
        # Mark as completed in database
        self._complete_onboarding(state)
        
        logger.info(f"Completed onboarding for client {state['client_id']}")
        
        return state
    
    def should_continue(self, state: OnboardingState) -> str:
        """
        Decide which path to take after validation.
        
        Args:
            state: Current conversation state
            
        Returns:
            Next node name
        """
        if state.get("needs_clarification"):
            return "clarify"
        elif state["current_step"] >= TOTAL_QUESTIONS:
            return "complete"
        else:
            return "save"
    
    def _save_to_database(self, state: OnboardingState) -> None:
        """Save current state to database using stage-based JSONB columns."""
        try:
            # Log current state for debugging
            logger.info(f"Saving to database - Step {state['current_step']}")
            logger.info(f"State keys: {list(state.keys())}")
            logger.info(f"q3_legal: {state.get('q3_legal')}")
            logger.info(f"q7_suite_setup: {state.get('q7_suite_setup')}")
            logger.info(f"q9_admin: {state.get('q9_admin')}")
            
            # Prepare update data
            update_data = {
                "updated_at": "now()",
                "current_stage": state.get("current_stage"),
                "current_question": state["current_step"]
            }
            
            # Extract and populate main fields from onboarding data
            if state.get("q3_legal"):  # Practice legal name
                update_data["legal_name"] = state["q3_legal"]
                logger.info(f"Setting legal_name to: {state['q3_legal']}")
            
            if state.get("q9_admin"):  # Email
                update_data["email"] = state["q9_admin"]
                logger.info(f"Setting email to: {state['q9_admin']}")
            
            if state.get("q7_suite_setup"):  # Phone
                update_data["phone"] = state["q7_suite_setup"]
                logger.info(f"Setting phone to: {state['q7_suite_setup']}")
            
            # Organize data by stage
            quick_start_data = {}
            team_tech_data = {}
            identity_brand_data = {}
            digital_growth_data = {}
            
            # Map field names to stage data
            # Stage 1: Quick Start (Q1-Q9)
            for i in range(1, 10):
                field_name = f"q{i}_admin"
                if state.get(field_name) is not None:
                    quick_start_data[field_name] = state[field_name]
            
            # Stage 2: Team & Tech (Q10-Q16)
            stage2_fields = ['q10_team', 'q11_team', 'q12_team', 'q13_tech', 
                           'q14_marketing', 'q15_marketing', 'q16_tech']
            for field_name in stage2_fields:
                if state.get(field_name) is not None:
                    team_tech_data[field_name] = state[field_name]
            
            # Stage 3: Identity & Brand (Q17-Q28)
            stage3_fields = ['q17_personality', 'q18_personality', 'q19_personality', 'q20_personality',
                           'q21_services', 'q22_services', 'q23_brand', 'q24_brand', 'q25_brand',
                           'q26_brand', 'q27_messaging', 'q28_messaging']
            for field_name in stage3_fields:
                if state.get(field_name) is not None:
                    identity_brand_data[field_name] = state[field_name]
            
            # Stage 4: Digital & Growth (Q29-Q48)
            stage4_fields = ['q29_online', 'q30_online', 'q31_online', 'q32_online', 'q33_online',
                           'q34_social', 'q35_social', 'q36_social', 'q37_social', 'q38_social',
                           'q39_content', 'q40_content', 'q41_reputation', 'q42_reputation', 'q43_reputation',
                           'q44_growth', 'q45_growth', 'q46_automation', 'q47_budget', 'q48_notes']
            for field_name in stage4_fields:
                if state.get(field_name) is not None:
                    digital_growth_data[field_name] = state[field_name]
            
            # Add stage data to update if not empty
            if quick_start_data:
                update_data["quick_start_data"] = quick_start_data
            if team_tech_data:
                update_data["team_tech_data"] = team_tech_data
            if identity_brand_data:
                update_data["identity_brand_data"] = identity_brand_data
            if digital_growth_data:
                update_data["digital_growth_data"] = digital_growth_data
            
            # Update onboarding_data with conversation history
            messages_data = [
                {
                    "role": "assistant" if isinstance(m, AIMessage) else "user",
                    "content": m.content,
                    "timestamp": m.additional_kwargs.get("timestamp", "")
                }
                for m in state["messages"]
            ]
            
            update_data["onboarding_data"] = {
                "session_id": state["session_id"],
                "current_step": state["current_step"],
                "current_stage": state.get("current_stage"),
                "messages": messages_data
            }
            
            # Update in Supabase
            supabase.service.table("clients").update(update_data).eq(
                "id", state["client_id"]
            ).execute()
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            raise
    
    def _complete_onboarding(self, state: OnboardingState) -> None:
        """Mark onboarding as completed in database."""
        try:
            update_data = {
                "onboarding_completed": True,
                "updated_at": "now()"
            }
            
            supabase.service.table("clients").update(update_data).eq(
                "id", state["client_id"]
            ).execute()
            
        except Exception as e:
            logger.error(f"Error completing onboarding: {e}")
            raise
    
    async def process_message(
        self,
        session_id: str,
        client_id: str,
        tenant_id: str,
        message: str,
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a user message through the workflow.
        
        Args:
            session_id: Session identifier
            client_id: Client UUID
            tenant_id: Tenant UUID
            message: User's message
            current_state: Current conversation state
            
        Returns:
            Updated state after processing
        """
        # Create or update state
        if not current_state:
            # Initialize with all 48 question fields set to None
            state = OnboardingState(
                session_id=session_id,
                client_id=client_id,
                tenant_id=tenant_id,
                messages=[],
                current_step=0,
                current_stage=None,
                is_completed=False,
                needs_clarification=False,
                last_validation_error=None,
                # Stage 1: Quick Start
                q1_admin=None, q2_admin=None, q3_admin=None, q4_admin=None,
                q5_admin=None, q6_admin=None, q7_admin=None, q8_admin=None, q9_admin=None,
                # Stage 2: Team & Tech
                q10_team=None, q11_team=None, q12_team=None, q13_tech=None,
                q14_marketing=None, q15_marketing=None, q16_tech=None,
                # Stage 3: Identity & Brand
                q17_personality=None, q18_personality=None, q19_personality=None, q20_personality=None,
                q21_services=None, q22_services=None, q23_brand=None, q24_brand=None, q25_brand=None,
                q26_brand=None, q27_messaging=None, q28_messaging=None,
                # Stage 4: Digital & Growth
                q29_online=None, q30_online=None, q31_online=None, q32_online=None, q33_online=None,
                q34_social=None, q35_social=None, q36_social=None, q37_social=None, q38_social=None,
                q39_content=None, q40_content=None, q41_reputation=None, q42_reputation=None, q43_reputation=None,
                q44_growth=None, q45_growth=None, q46_automation=None, q47_budget=None, q48_notes=None
            )
        else:
            state = current_state
        
        # Add user message to state
        user_message = HumanMessage(content=message)
        state["messages"].append(user_message)
        
        # Process: validate → save → ask next question
        # Step 1: Validate the user's response
        state = self.validate_response_node(state)
        
        # Step 2: Check if validation passed
        if state.get("needs_clarification"):
            # Ask for clarification (same question again)
            state = self.ask_question_node(state)
        else:
            # Step 3: Save the validated data
            state = self.save_data_node(state)
            
            # Step 4: Ask the next question
            state = self.ask_question_node(state)
        
        return state


# Global workflow instance
_workflow_instance = None


def get_workflow() -> OnboardingWorkflow:
    """Get or create workflow instance."""
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = OnboardingWorkflow()
    return _workflow_instance
