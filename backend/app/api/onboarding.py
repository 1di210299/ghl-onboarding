"""
Onboarding API endpoints.
Handles the conversational onboarding flow.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.models import (
    OnboardingStartRequest,
    OnboardingStartResponse,
    OnboardingMessageRequest,
    OnboardingMessageResponse,
    OnboardingStatusResponse
)
from app.services.workflow import get_workflow
from app.services.ghl_integration import GHLIntegrationService
from app.core.database import supabase
from app.core.config import settings
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/onboarding", tags=["onboarding"])


# In-memory session storage (in production, use Redis or database)
_sessions = {}


@router.post("/start", response_model=OnboardingStartResponse)
async def start_onboarding(request: OnboardingStartRequest):
    """
    Start a new onboarding session.
    
    Creates a client record and initializes the conversation workflow.
    """
    try:
        logger.info(f"Starting onboarding for tenant: {request.tenant_id}, practice: {request.practice_name}")
        
        # Create client record
        client_data = {
            "tenant_id": request.tenant_id,
            "practice_name": request.practice_name or "New Practice",
            "onboarding_completed": False,
            "onboarding_data": {
                "started_at": datetime.utcnow().isoformat(),
                "current_step": 0,
                "messages": []
            }
        }
        
        logger.info(f"Inserting client into Supabase: {client_data}")
        logger.info("About to call supabase.service...")
        try:
            logger.info("Getting service client...")
            service_client = supabase.service
            logger.info("Service client obtained, getting table...")
            table = service_client.table("clients")
            logger.info("Table obtained, inserting data...")
            insert_query = table.insert(client_data)
            logger.info("Insert query created, executing...")
            result = insert_query.execute()
            logger.info(f"Supabase insert result: {result}")
        except Exception as e:
            logger.error(f"Detailed error during Supabase operation: {type(e).__name__}: {e}")
            raise
        
        if not result.data:
            logger.error("Failed to create client - no data returned")
            raise HTTPException(status_code=500, detail="Failed to create client")
        
        logger.info(f"Client created successfully: {result.data[0]}")
        client = result.data[0]
        client_id = client["id"]
        
        # Generate session ID
        session_id = f"sess_{uuid.uuid4().hex[:16]}"
        logger.info(f"Generated session_id: {session_id}")
        
        # Initialize workflow state with all 48 fields
        logger.info("Getting workflow...")
        workflow = get_workflow()
        logger.info("Workflow obtained successfully")
        initial_state = {
            "session_id": session_id,
            "client_id": client_id,
            "tenant_id": request.tenant_id,
            "messages": [],
            "current_step": 0,
            "current_stage": None,
            "is_completed": False,
            "needs_clarification": False,
            "last_validation_error": None,
            # Initialize all 48 question fields to None
            **{f"q{i}_admin": None for i in range(1, 10)},
            **{f"q{i}_team": None for i in [10, 11]},
            "q12_team": None,
            "q13_tech": None,
            "q14_marketing": None,
            "q15_marketing": None,
            "q16_tech": None,
            **{f"q{i}_personality": None for i in range(17, 21)},
            **{f"q{i}_services": None for i in [21, 22]},
            **{f"q{i}_brand": None for i in range(23, 27)},
            **{f"q{i}_messaging": None for i in [27, 28]},
            **{f"q{i}_online": None for i in range(29, 34)},
            **{f"q{i}_social": None for i in range(34, 39)},
            **{f"q{i}_content": None for i in [39, 40]},
            **{f"q{i}_reputation": None for i in range(41, 44)},
            **{f"q{i}_growth": None for i in [44, 45]},
            "q46_automation": None,
            "q47_budget": None,
            "q48_notes": None
        }
        
        # Store session
        _sessions[session_id] = initial_state
        
        # Get first question from JSON config
        logger.info("Getting first question...")
        from app.services.workflow import get_question_by_index
        first_q = get_question_by_index(0)
        logger.info(f"First question retrieved: {first_q['id']}")
        first_question = first_q['text']
        if first_q.get('options'):
            first_question += f"\n\nOptions: {first_q['options']}"
        
        logger.info(f"Started onboarding session: {session_id} for client: {client_id}")
        
        return OnboardingStartResponse(
            session_id=session_id,
            client_id=client_id,
            message=first_question,
            current_step=0,
            current_stage="Quick Start",
            total_questions=48
        )
        
    except Exception as e:
        logger.error(f"Error starting onboarding: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message", response_model=OnboardingMessageResponse)
async def send_message(request: OnboardingMessageRequest):
    """
    Send a message in an ongoing onboarding session.
    
    Processes the user's response and returns the next question or completion status.
    """
    try:
        session_id = request.session_id
        
        # Get session state
        if session_id not in _sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        current_state = _sessions[session_id]
        
        # Process message through workflow
        workflow = get_workflow()
        updated_state = await workflow.process_message(
            session_id=session_id,
            client_id=current_state["client_id"],
            tenant_id=current_state["tenant_id"],
            message=request.message,
            current_state=current_state
        )
        
        # Update session
        _sessions[session_id] = updated_state
        
        # Get bot's response (last AI message)
        from langchain_core.messages import AIMessage
        ai_messages = [m for m in updated_state["messages"] if isinstance(m, AIMessage)]
        bot_message = ai_messages[-1].content if ai_messages else "I'm processing your response..."
        
        # Collect data for response (only non-None question fields)
        collected_data = {
            k: v for k, v in updated_state.items()
            if k.startswith('q') and '_' in k and v is not None
        }
        
        # Check if onboarding is completed
        is_completed = updated_state.get("is_completed", False)
        
        # If completed, sync to GHL in background
        if is_completed and settings.ghl_api_key and settings.ghl_location_id:
            logger.info(f"Onboarding completed for session {session_id}, syncing to GHL...")
            # Sync to GHL in background (don't block response)
            from app.services.ghl_integration import GHLIntegrationService
            
            async def sync_to_ghl():
                try:
                    ghl_service = GHLIntegrationService(
                        api_key=settings.ghl_api_key,
                        location_id=settings.ghl_location_id
                    )
                    
                    result = await ghl_service.sync_onboarding_to_ghl(
                        onboarding_data=collected_data,
                        practice_name=current_state.get("practice_name", "Unknown Practice"),
                        workflow_id=settings.ghl_workflow_id if hasattr(settings, 'ghl_workflow_id') else None
                    )
                    
                    if result["success"]:
                        # Update database with GHL contact ID
                        supabase.service.table("clients").update({
                            "ghl_contact_id": result["contact_id"],
                            "ghl_synced_at": result["synced_at"]
                        }).eq("id", current_state["client_id"]).execute()
                        
                        logger.info(f"Successfully synced to GHL. Contact ID: {result['contact_id']}")
                    else:
                        logger.error(f"Failed to sync to GHL: {result.get('error')}")
                
                except Exception as e:
                    logger.error(f"Error in GHL sync: {e}", exc_info=True)
            
            # Fire and forget (don't wait for GHL sync)
            import asyncio
            asyncio.create_task(sync_to_ghl())
        
        logger.info(f"Processed message for session: {session_id}, step: {updated_state['current_step']}")
        
        return OnboardingMessageResponse(
            session_id=session_id,
            bot_message=bot_message,
            current_step=updated_state["current_step"],
            current_stage=updated_state.get("current_stage"),
            total_questions=48,
            is_completed=is_completed,
            collected_data=collected_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{session_id}", response_model=OnboardingStatusResponse)
async def get_onboarding_status(session_id: str):
    """
    Get the current status of an onboarding session.
    
    Returns progress information and all collected data.
    """
    try:
        # Get session state
        if session_id not in _sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state = _sessions[session_id]
        
        # Calculate progress
        current_step = state["current_step"]
        total_steps = 48
        progress_percent = min(int((current_step / total_steps) * 100), 100)
        
        # Collect data (only question fields)
        collected_data = {
            k: v for k, v in state.items()
            if k.startswith('q') and '_' in k and v is not None
        }
        
        # Get timestamps from database
        client_result = supabase.service.table("clients").select(
            "created_at, onboarding_data"
        ).eq("id", state["client_id"]).execute()
        
        started_at = datetime.utcnow()
        completed_at = None
        
        if client_result.data:
            client = client_result.data[0]
            started_at = datetime.fromisoformat(client["created_at"].replace('Z', '+00:00'))
            
            if state.get("is_completed"):
                onboarding_data = client.get("onboarding_data", {})
                if onboarding_data.get("completed_at"):
                    completed_at = datetime.fromisoformat(onboarding_data["completed_at"])
        
        return OnboardingStatusResponse(
            session_id=session_id,
            client_id=state["client_id"],
            current_step=current_step,
            total_steps=total_steps,
            progress_percent=progress_percent,
            is_completed=state.get("is_completed", False),
            started_at=started_at,
            completed_at=completed_at,
            collected_data=collected_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Pydantic models for generate-answer endpoint
class GenerateAnswerRequest(BaseModel):
    question: str
    practice_name: str = "Medical Practice"
    context: dict = {}


class GenerateAnswerResponse(BaseModel):
    answer: str


@router.post("/generate-answer", response_model=GenerateAnswerResponse)
async def generate_answer(request: GenerateAnswerRequest):
    """
    Generate a realistic answer to the current onboarding question using OpenAI.
    
    This endpoint helps auto-fill responses for testing or demo purposes.
    """
    try:
        # Initialize OpenAI
        llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.7,
            api_key=settings.openai_api_key
        )
        
        # Create a prompt to generate a realistic answer
        system_prompt = f"""You are helping to generate realistic test data for a healthcare practice onboarding system.
Practice Name: {request.practice_name}
Current Stage: {request.context.get('stage', 'Unknown')}
Question #{request.context.get('current_step', 0) + 1}

Generate a realistic, professional answer to the following question. The answer should be:
- Appropriate for a healthcare/medical practice
- Natural and conversational
- Specific and detailed (not generic)
- Between 5-50 words depending on the question type
- If it's a yes/no question, answer with just "Yes" or "No"
- If it's a multiple choice, pick ONE option from the list
- If it's asking for a name/email/address, provide realistic data

Question: {request.question}

Provide ONLY the answer, nothing else."""

        # Generate answer
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Generate the answer:")
        ]
        
        response = llm.invoke(messages)
        answer = response.content.strip()
        
        logger.info(f"Generated answer for question: {request.question[:50]}... -> {answer[:50]}...")
        
        return GenerateAnswerResponse(answer=answer)
        
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")
