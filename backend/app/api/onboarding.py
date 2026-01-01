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
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from datetime import datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/onboarding", tags=["onboarding"])


# In-memory session storage (in production, use Redis or database)
_sessions = {}


@router.post("/start", response_model=OnboardingStartResponse)
async def start_onboarding(request: OnboardingStartRequest):
    """
    Start a new onboarding session OR resume an incomplete one.
    
    Creates a client record and initializes the conversation workflow.
    If an incomplete session exists, it will resume from where they left off.
    """
    try:
        logger.info(f"Starting onboarding for tenant: {request.tenant_id}, practice: {request.practice_name}")
        
        service_client = supabase.service
        
        # Check for ANY incomplete onboarding for this practice (not just recent)
        incomplete = service_client.table("clients").select("*").eq(
            "tenant_id", request.tenant_id
        ).eq(
            "practice_name", request.practice_name or "New Practice"
        ).eq(
            "onboarding_completed", False
        ).order("created_at", desc=True).limit(1).execute()
        
        if incomplete.data:
            # Found incomplete onboarding - let them resume
            existing_client = incomplete.data[0]
            client_id = existing_client["id"]
            onboarding_data = existing_client.get("onboarding_data", {})
            current_step = onboarding_data.get("current_step", 0)
            messages = onboarding_data.get("messages", [])
            saved_answers = onboarding_data.get("answers", {})  # NEW: Get indexed answers
            
            logger.info(f"Found incomplete onboarding for client {client_id}, resuming from step {current_step}")
            logger.info(f"Restoring {len(saved_answers)} saved answers")
            
            # Generate new session for resuming
            session_id = f"sess_{uuid.uuid4().hex[:16]}"
            
            # Restore state from database
            workflow = get_workflow()
            from langchain_core.messages import HumanMessage, AIMessage
            
            # Reconstruct messages
            restored_messages = []
            for msg in messages:
                if msg.get('role') == 'assistant':
                    restored_messages.append(AIMessage(content=msg.get('content', '')))
                else:
                    restored_messages.append(HumanMessage(content=msg.get('content', '')))
            
            initial_state = {
                "session_id": session_id,
                "client_id": client_id,
                "tenant_id": request.tenant_id,
                "practice_name": request.practice_name or "New Practice",
                "messages": restored_messages,
                "current_step": current_step,
                "current_stage": onboarding_data.get("current_stage"),
                "is_completed": False,
                "needs_clarification": False,
                "last_validation_error": None,
                # Initialize all 48 question fields
                **{f"q{i}_admin": None for i in range(1, 10)},
                **{f"q{i}_team": None for i in [10, 11]},
                "q12_communication": None,
                "q13_readiness": None,
                "q14_marketing": None,
                "q15_marketing": None,
                "q16_stack": None,
                **{f"q{i}_practice_type": None for i in [17]},
                "q18_ideal_client": None,
                "q19_boundaries": None,
                **{f"q{i}_messaging": None for i in [20, 21]},
                **{f"q{i}_brand_voice": None for i in [22, 23]},
                **{f"q{i}_brand": None for i in range(24, 29)},
                **{f"q{i}_website": None for i in range(29, 34)},
                "q34_social": None,
                **{f"q{i}_social_ig": None for i in [35]},
                **{f"q{i}_social_fb": None for i in [36]},
                **{f"q{i}_social_li": None for i in [37]},
                "q38_blog": None,
                **{f"q{i}_suite_model": None for i in [39]},
                "q40_saya": None,
                **{f"q{i}_seo": None for i in [41]},
                **{f"q{i}_ads": None for i in [42]},
                **{f"q{i}_growth": None for i in [43, 44, 45]},
                "q46_risk": None,
                "q47_success": None,
                "q48_notes": None
            }
            
            # Restore saved answers from indexed data
            for field_name, value in saved_answers.items():
                if field_name in initial_state:
                    initial_state[field_name] = value
            
            logger.info(f"Restored state with {len([k for k,v in initial_state.items() if k.startswith('q') and v is not None])} answered questions")
            _sessions[session_id] = initial_state
            
            # Add welcome back message
            welcome_back = f"""<div class='welcome-back'>
<div class='welcome-icon'>👋</div>
<h3>Welcome back!</h3>
<p>I see you started your onboarding but didn't finish.</p>
<div class='resume-progress'>
  <div class='progress-stats'>
    <span class='completed-count'>{current_step}</span>
    <span class='separator'>/</span>
    <span class='total-count'>48</span>
  </div>
  <p class='progress-label'>questions completed</p>
</div>
<p class='continue-prompt'>Let's pick up where you left off! Ready to continue?</p>
</div>"""
            
            welcome_msg = AIMessage(content=welcome_back)
            initial_state["messages"].append(welcome_msg)
            
            # Get next question
            from app.services.workflow import get_question_by_index
            next_q = get_question_by_index(current_step)
            if next_q:
                next_question = next_q['text']
                if next_q.get('options'):
                    if isinstance(next_q['options'], list):
                        options_str = ', '.join(next_q['options'])
                    else:
                        options_str = next_q['options']
                    next_question += f"\n\nOptions: {options_str}"
                if next_q.get('notes'):
                    next_question += f"\n({next_q['notes']})"
            else:
                next_question = "What is your full name?"
            
            # Format history for frontend
            history = [
                {"role": "assistant" if msg.get('role') == 'assistant' else "user", 
                 "content": msg.get('content', '')}
                for msg in messages
            ]
            history.append({"role": "assistant", "content": welcome_back})
            history.append({"role": "assistant", "content": next_question})
            
            return OnboardingStartResponse(
                session_id=session_id,
                client_id=client_id,
                message=next_question,
                current_step=current_step,
                total_questions=48,
                history=history
            )
        
        # No incomplete session - Check for recent duplicate (within last 30 seconds) to prevent double-submission
        from datetime import timedelta
        thirty_seconds_ago = (datetime.utcnow() - timedelta(seconds=30)).isoformat()
        
        recent_duplicate = service_client.table("clients").select("id, created_at").eq(
            "tenant_id", request.tenant_id
        ).eq(
            "practice_name", request.practice_name or "New Practice"
        ).eq(
            "onboarding_completed", False
        ).gte(
            "created_at", thirty_seconds_ago
        ).order("created_at", desc=True).limit(1).execute()
        
        if recent_duplicate.data:
            logger.info(f"Found recent duplicate client, reusing: {recent_duplicate.data[0]['id']}")
            client_id = recent_duplicate.data[0]["id"]
            
            # Generate new session for existing client
            session_id = f"sess_{uuid.uuid4().hex[:16]}"
            logger.info(f"Generated session_id for existing client: {session_id}")
            
            # Initialize state with all fields (same as new client flow)
            workflow = get_workflow()
            initial_state = {
                "session_id": session_id,
                "client_id": client_id,
                "tenant_id": request.tenant_id,
                "practice_name": request.practice_name or "New Practice",
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
            
            _sessions[session_id] = initial_state
            
            logger.info("Getting first question from workflow...")
            result = workflow.graph.invoke(initial_state)
            logger.info(f"Workflow result: current_step={result.get('current_step')}, messages count={len(result.get('messages', []))}")
            
            # Extract the bot's question from messages
            messages = result.get("messages", [])
            bot_messages = [m for m in messages if isinstance(m, (AIMessage, SystemMessage))]
            
            if bot_messages:
                first_question = bot_messages[-1].content
            else:
                # Fallback: get directly from config
                from app.services.workflow import get_question_by_index
                question_config = get_question_by_index(0)
                first_question = question_config['text'] if question_config else "What is your full name?"
            
            logger.info(f"First question for reused client: {first_question[:100]}...")
            logger.info(f"Reusing existing onboarding session: {session_id} for client: {client_id}")
            
            return OnboardingStartResponse(
                session_id=session_id,
                client_id=client_id,
                message=first_question,
                current_step=0,
                total_questions=48
            )
        
        # No recent duplicate, create new client record
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
        
        logger.info(f"Inserting new client into Supabase: {client_data}")
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
            "practice_name": request.practice_name or "New Practice",
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
        from langchain_core.messages import AIMessage
        first_q = get_question_by_index(0)
        logger.info(f"First question retrieved: {first_q['id']}")
        first_question = first_q['text']
        if first_q.get('options'):
            first_question += f"\n\nOptions: {first_q['options']}"
        
        # Add first question to initial state messages
        initial_state["messages"].append(AIMessage(content=first_question))
        
        # Save initial state with first question to database
        try:
            messages_data = [
                {
                    "role": "assistant" if isinstance(m, (AIMessage, SystemMessage)) else "user",
                    "content": m.content
                }
                for m in initial_state["messages"]
            ]
            
            service_client.table("clients").update({
                "onboarding_data": {
                    "session_id": session_id,
                    "current_step": 0,
                    "current_stage": None,
                    "messages": messages_data
                }
            }).eq("id", client_id).execute()
            logger.info(f"Saved initial question to database for client: {client_id}")
        except Exception as e:
            logger.error(f"Error saving initial question to database: {e}")
        
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
        
        # Track number of messages before processing
        from langchain_core.messages import AIMessage
        messages_before = len([m for m in current_state["messages"] if isinstance(m, AIMessage)])
        
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
        
        # Get all NEW AI messages (including phase completion + question)
        ai_messages = [m for m in updated_state["messages"] if isinstance(m, AIMessage)]
        new_ai_messages = ai_messages[messages_before:]  # Only new messages
        bot_messages = [m.content for m in new_ai_messages]
        bot_message = bot_messages[-1] if bot_messages else "I'm processing your response..."
        
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
            
            # Import at function level to avoid circular imports
            from app.services.ghl_integration import GHLIntegrationService
            import asyncio
            
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
                        # Update database with GHL contact ID and mark as completed
                        try:
                            supabase.service.table("clients").update({
                                "ghl_contact_id": result["contact_id"],
                                "onboarding_completed": True
                            }).eq("id", current_state["client_id"]).execute()
                            
                            logger.info(f"Successfully synced to GHL. Contact ID: {result['contact_id']}")
                        except Exception as db_error:
                            logger.error(f"Error updating database after GHL sync: {db_error}", exc_info=True)
                    else:
                        logger.error(f"Failed to sync to GHL: {result.get('error')}")
                
                except Exception as e:
                    logger.error(f"Error in GHL sync: {e}", exc_info=True)
            
            # Fire and forget (don't wait for GHL sync)
            asyncio.create_task(sync_to_ghl())
        
        logger.info(f"Processed message for session: {session_id}, step: {updated_state['current_step']}, new messages: {len(bot_messages)}")
        
        return OnboardingMessageResponse(
            session_id=session_id,
            bot_message=bot_message,
            bot_messages=bot_messages,
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
