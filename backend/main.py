"""
FastAPI Backend for Insurance Policy Advisor
=============================================
This is the main entry point for the backend API.

Endpoints:
- POST /chat - Send a message and get a response
- GET /history/{session_id} - Get conversation history
- DELETE /session/{session_id} - Clear a session
- GET /health - Health check endpoint

Run with: uvicorn main:app --reload --port 8000
API Docs: http://localhost:8000/docs
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime

from agent import InsuranceAgent
from guardrails import (
    check_input, check_output, log_guardrail_trigger,
    get_follow_up_prompt, get_farewell_message,
    reset_session_state, get_session_state
)
from config import CORS_ORIGINS, MAX_HISTORY_LENGTH

# ==============================================================================
# FastAPI App Configuration
# ==============================================================================

app = FastAPI(
    title="Insurance Policy Advisor API",
    description="""
    An AI-powered insurance advisor that helps users find the right insurance policy.
    
    ## Features
    - Multi-turn conversation support
    - Tool-based product search
    - Input/Output guardrails for safety
    - Session management
    
    ## Insurance Categories
    - Health Insurance
    - Term Life Insurance  
    - Motor Insurance
    - Travel Insurance
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration - Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# In-Memory Session Storage
# ==============================================================================
# Note: For production, use Redis or a database

sessions: Dict[str, Dict] = {}


def get_session(session_id: str) -> Dict:
    """Get or create a session"""
    if session_id not in sessions:
        sessions[session_id] = {
            "history": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    return sessions[session_id]


def update_session(session_id: str, user_msg: str, assistant_msg: str):
    """Update session with new messages"""
    session = get_session(session_id)
    session["history"].append({"role": "user", "content": user_msg})
    session["history"].append({"role": "assistant", "content": assistant_msg})
    session["updated_at"] = datetime.now().isoformat()
    
    # Limit history length
    if len(session["history"]) > MAX_HISTORY_LENGTH:
        session["history"] = session["history"][-MAX_HISTORY_LENGTH:]


# ==============================================================================
# Request/Response Models
# ==============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's message",
        examples=["I need health insurance for my family of 4"]
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID for conversation continuity. "
                    "If not provided, a new session is created.",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(
        ...,
        description="The agent's response message"
    )
    session_id: str = Field(
        ...,
        description="Session ID for continuing the conversation"
    )
    guardrail_triggered: bool = Field(
        False,
        description="Whether a guardrail was triggered (for transparency)"
    )
    chat_ended: bool = Field(
        False,
        description="Whether the chat has been terminated"
    )
    end_reason: str = Field(
        "",
        description="Reason for chat termination if chat_ended is True"
    )


class Message(BaseModel):
    """Model for a single message"""
    role: str = Field(..., description="Either 'user' or 'assistant'")
    content: str = Field(..., description="The message content")


class HistoryResponse(BaseModel):
    """Response model for history endpoint"""
    session_id: str
    history: List[Message]
    created_at: str
    updated_at: str
    message_count: int


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    service: str
    timestamp: str


# ==============================================================================
# Initialize Agent
# ==============================================================================

# Lazy initialization to handle missing API key gracefully
_agent: Optional[InsuranceAgent] = None


def get_agent() -> InsuranceAgent:
    """Get or initialize the agent"""
    global _agent
    if _agent is None:
        try:
            _agent = InsuranceAgent()
        except ValueError as e:
            raise HTTPException(
                status_code=503,
                detail=str(e)
            )
    return _agent


# ==============================================================================
# API Endpoints
# ==============================================================================

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Send a message to the insurance advisor and get a response.
    
    This endpoint:
    1. Validates input with guardrails (including exit detection)
    2. Processes the message with the AI agent
    3. Validates output with guardrails
    4. Returns the response with session ID and chat status
    
    The session_id can be used in subsequent requests to maintain
    conversation context.
    
    Enhanced Features:
    - Exit intent detection (bye, done, no thanks, etc.)
    - Follow-up prompts after providing insurance details
    - Guardrail failure tracking with auto-termination
    - Polite handling of off-topic requests including jokes
    """
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    session = get_session(session_id)
    
    # Input guardrail check with session tracking
    input_check = check_input(request.message, session_id)
    
    # Handle exit intent
    if input_check.get("is_exit_intent") or input_check.get("should_end_chat"):
        log_guardrail_trigger(
            request.message,
            input_check.get("category", "exit_intent"),
            is_input=True
        )
        
        # Update session with farewell
        if input_check.get("message"):
            update_session(session_id, request.message, input_check["message"])
        
        return ChatResponse(
            response=input_check.get("message", get_farewell_message()),
            session_id=session_id,
            guardrail_triggered=not input_check["is_safe"],
            chat_ended=True,
            end_reason=input_check.get("end_reason", "user_exit")
        )
    
    # Handle guardrail failures (non-exit)
    if not input_check["is_safe"]:
        log_guardrail_trigger(
            request.message,
            input_check["category"],
            is_input=True
        )
        
        # Update session even for blocked messages (for context)
        update_session(session_id, request.message, input_check["message"])
        
        return ChatResponse(
            response=input_check["message"],
            session_id=session_id,
            guardrail_triggered=True,
            chat_ended=input_check.get("should_end_chat", False),
            end_reason=input_check.get("end_reason", "")
        )
    
    # Get agent and process message
    agent = get_agent()
    
    try:
        response = await agent.process_message(
            message=request.message,
            history=session["history"]
        )
    except Exception as e:
        print(f"Agent error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process message. Please try again."
        )
    
    # Output guardrail check with session tracking
    output_check = check_output(response, session_id)
    final_response = output_check["sanitized_response"]
    
    if not output_check["is_safe"]:
        log_guardrail_trigger(
            response[:100],
            output_check["category"],
            is_input=False
        )
    
    # Add follow-up prompt if insurance details were provided
    if output_check.get("show_follow_up"):
        final_response += get_follow_up_prompt()
    
    # Update session history
    update_session(session_id, request.message, final_response)
    
    return ChatResponse(
        response=final_response,
        session_id=session_id,
        guardrail_triggered=not output_check["is_safe"],
        chat_ended=False,
        end_reason=""
    )


@app.get("/history/{session_id}", response_model=HistoryResponse, tags=["Session"])
async def get_history(session_id: str):
    """
    Retrieve conversation history for a session.
    
    Returns all messages in the conversation along with metadata.
    """
    if session_id not in sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found: {session_id}"
        )
    
    session = sessions[session_id]
    
    return HistoryResponse(
        session_id=session_id,
        history=[Message(**msg) for msg in session["history"]],
        created_at=session["created_at"],
        updated_at=session["updated_at"],
        message_count=len(session["history"])
    )


@app.delete("/session/{session_id}", tags=["Session"])
async def clear_session(session_id: str):
    """
    Clear a session and its conversation history.
    
    This permanently deletes the conversation and resets guardrail state.
    Use this for the "Reset Chat" functionality.
    """
    # Clear session data
    if session_id in sessions:
        del sessions[session_id]
    
    # Reset guardrail state for this session
    reset_session_state(session_id)
    
    return {"message": f"Session {session_id} cleared successfully", "status": "reset"}


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.
    
    Returns the service status. Use this to verify the API is running.
    """
    return HealthResponse(
        status="healthy",
        service="insurance-advisor-api",
        timestamp=datetime.now().isoformat()
    )


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint - redirects to API documentation.
    """
    return {
        "message": "Welcome to the Insurance Policy Advisor API",
        "docs": "/docs",
        "health": "/health"
    }


# ==============================================================================
# Startup Event
# ==============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    print("=" * 60)
    print("  Insurance Policy Advisor API Starting...")
    print("=" * 60)
    print(f"  CORS Origins: {CORS_ORIGINS}")
    print(f"  API Docs: http://localhost:8000/docs")
    print("=" * 60)


# ==============================================================================
# Main Entry Point
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
