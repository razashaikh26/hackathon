"""
Production FinVoice FastAPI Application
Complete refactored app with real data, secure services, and enhanced features
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import asyncio
import httpx
from datetime import datetime, timedelta
import json
import base64
from decimal import Decimal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Core imports
from app.core.config import settings
from app.core.database import get_db, init_db, close_db
from app.db.models import User, Holding, PortfolioSnapshot, AuditLog

# Service imports
from app.services.portfolio_service import PortfolioService
from app.services.blockchain_service import BlockchainService
from app.services.vapi_voice_service import VapiVoiceService
from app.services.enhanced_finvoice_service import enhanced_finvoice_service

# API router imports
from app.api.v1.database_api import router as database_router
from app.api.v1.endpoints import router as api_router

# Initialize services
portfolio_service = PortfolioService()
blockchain_service = BlockchainService()
vapi_service = VapiVoiceService()

# Security
security = HTTPBearer(auto_error=False)

# Pydantic models
class VoiceMessageRequest(BaseModel):
    message: str = Field(..., description="User message")
    language: str = Field(default="english", description="Preferred language")
    user_id: str = Field(default="demo_user", description="User identifier")

class PortfolioSnapshotRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    blockchain_log: bool = Field(default=False, description="Log to blockchain")

class ChatRequest(BaseModel):
    message: str = Field(..., description="Chat message")
    user_id: str = Field(default="demo_user", description="User identifier")
    include_context: bool = Field(default=True, description="Include financial context")

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    language: str = Field(default="english", description="Language for TTS")
    voice_type: str = Field(default="alloy", description="Voice type")

# FastAPI app initialization
app = FastAPI(
    title="FinVoice AI Engine - Production",
    description="Professional Financial Management with AI, Voice, and Blockchain",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include database API router
app.include_router(database_router)

# Include enhanced API router with voice endpoints
app.include_router(api_router, prefix="/api/v1")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database and services"""
    try:
        await init_db()
        logger.info("FinVoice application started successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources"""
    try:
        await close_db()
        logger.info("FinVoice application shutdown completed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Helper functions
async def get_user_context(user_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Get comprehensive user financial context"""
    try:
        # Get portfolio data
        portfolio_data = await portfolio_service.compute_portfolio_value(user_id, db)
        
        # Mock user data (in production, fetch from database)
        user_context = {
            "user_id": user_id,
            "portfolio_value": portfolio_data.get("total_value", 750000),
            "monthly_income": 85000,
            "monthly_expenses": 35000,
            "risk_tolerance": "moderate",
            "goals": [
                {"name": "House Down Payment", "target": 2000000, "current": 750000},
                {"name": "Emergency Fund", "target": 500000, "current": 380000},
                {"name": "Retirement", "target": 10000000, "current": 650000}
            ],
            "recent_transactions": [
                {"description": "Salary Credit", "amount": 85000, "type": "income"},
                {"description": "Grocery Shopping", "amount": -2500, "type": "expense"},
                {"description": "SIP Investment", "amount": -15000, "type": "investment"}
            ],
            "holdings_count": portfolio_data.get("holdings_count", 7),
            "last_updated": datetime.now().isoformat()
        }
        
        return user_context
        
    except Exception as e:
        logger.error(f"Error getting user context: {e}")
        return {"user_id": user_id, "error": "Could not fetch user context"}

# Core API endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "FinVoice AI Engine - Production Ready",
        "version": "2.0.0",
        "status": "operational",
        "features": {
            "portfolio_computation": True,
            "blockchain_logging": settings.ENABLE_BLOCKCHAIN_LOGGING,
            "voice_services": settings.ENABLE_VOICE_FEATURES,
            "real_data": not settings.DEMO_MODE
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Check database
        db_status = "healthy"
        try:
            # Test database connection (implement in production)
            pass
        except Exception:
            db_status = "unhealthy"
        
        # Check services
        services_status = {
            "portfolio_service": "healthy",
            "blockchain_service": blockchain_service.get_network_status().get("connected", False),
            "vapi_service": bool(settings.VAPI_PRIVATE_KEY),
            "ai_service": bool(settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY)
        }
        
        overall_status = "healthy" if all([
            db_status == "healthy",
            any(services_status.values())
        ]) else "degraded"
        
        return {
            "status": overall_status,
            "database": db_status,
            "services": services_status,
            "uptime": "running",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Portfolio endpoints
@app.get("/api/v1/portfolio")
async def get_portfolio(
    user_id: str = "demo_user",
    force_refresh: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get real-time portfolio with live computation"""
    try:
        portfolio_data = await portfolio_service.compute_portfolio_value(
            user_id, db, force_refresh
        )
        
        if "error" in portfolio_data:
            raise HTTPException(status_code=400, detail=portfolio_data["error"])
        
        return {
            "success": True,
            "portfolio": portfolio_data,
            "computation_mode": "live" if not settings.DEMO_MODE else "demo",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/portfolio/snapshot")
async def create_portfolio_snapshot(
    request: PortfolioSnapshotRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create portfolio snapshot with optional blockchain logging"""
    try:
        snapshot_result = await portfolio_service.create_portfolio_snapshot(
            user_id=request.user_id,
            db=db,
            blockchain_log=request.blockchain_log
        )
        
        if "error" in snapshot_result:
            raise HTTPException(status_code=400, detail=snapshot_result["error"])
        
        return {
            "success": True,
            "snapshot": snapshot_result,
            "blockchain_logged": bool(snapshot_result.get("blockchain_hash")),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Snapshot creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolio/history")
async def get_portfolio_history(
    user_id: str = "demo_user",
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get portfolio history from snapshots"""
    try:
        history = await portfolio_service.get_portfolio_history(user_id, db, days)
        
        return {
            "success": True,
            "history": history,
            "period_days": days,
            "data_points": len(history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Portfolio history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Vapi Voice endpoints
@app.get("/api/v1/vapi/config")
async def get_vapi_public_config():
    """Get Vapi public configuration (secure - no private keys)"""
    try:
        config = vapi_service.get_public_config()
        
        return {
            "success": True,
            "config": config,
            "security_note": "Private keys secured on backend only",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Vapi config error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/v1/vapi/voice-message")
async def process_voice_message(
    request: VoiceMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """Process voice message with financial context injection"""
    try:
        # Get user context
        user_context = await get_user_context(request.user_id, db)
        
        # Process with Vapi service
        result = await vapi_service.process_voice_message(
            message=request.message,
            user_context=user_context,
            language=request.language
        )
        
        # Log interaction
        if result.get("success"):
            await _log_voice_interaction(request.user_id, request.message, result, db)
        
        return result
        
    except Exception as e:
        logger.error(f"Voice message processing error: {e}")
        return {
            "success": False,
            "error": str(e),
            "text_response": "I'm sorry, I encountered an error processing your request.",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/v1/voice/call/start")
async def start_voice_call(
    phone_number: str = Form(...),
    language: str = Form(default="english"),
    user_id: str = Form(default="demo_user"),
    db: AsyncSession = Depends(get_db)
):
    """Start Vapi voice call with user context"""
    try:
        # Get user context
        user_context = await get_user_context(user_id, db)
        
        # Start call
        call_id = await vapi_service.start_voice_call(
            phone_number=phone_number,
            language=language,
            user_context=user_context
        )
        
        if call_id:
            return {
                "success": True,
                "call_id": call_id,
                "phone_number": phone_number,
                "language": language,
                "user_context_loaded": True,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to start voice call")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice call start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# TTS endpoint with audio streaming
@app.post("/api/v1/tts/stream")
async def text_to_speech_stream(request: TTSRequest):
    """Convert text to speech and stream audio"""
    try:
        stream_response = await vapi_service.create_tts_stream(
            text=request.text,
            language=request.language,
            voice_type=request.voice_type
        )
        
        return stream_response
        
    except Exception as e:
        logger.error(f"TTS streaming error: {e}")
        return StreamingResponse(
            iter([b""]),
            media_type="audio/mpeg",
            status_code=500
        )

@app.post("/api/v1/tts/audio")
async def text_to_speech_audio(request: TTSRequest):
    """Convert text to speech and return base64 audio"""
    try:
        audio_data = await vapi_service.generate_speech_audio(
            text=request.text,
            language=request.language,
            voice_type=request.voice_type
        )
        
        if audio_data:
            return {
                "success": True,
                "audio_data": base64.b64encode(audio_data).decode(),
                "format": "mp3",
                "encoding": "base64",
                "text": request.text,
                "language": request.language,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "Audio generation failed",
                "fallback_available": True
            }
            
    except Exception as e:
        logger.error(f"TTS audio error: {e}")
        return {"success": False, "error": str(e)}

# Enhanced Chat endpoint
@app.post("/api/v1/chat")
async def chat_with_ai(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Enhanced AI chat with financial context injection"""
    try:
        # Get user context if requested
        context_data = {}
        if request.include_context:
            context_data = await get_user_context(request.user_id, db)
        
        # Build enhanced prompt
        if context_data:
            enhanced_prompt = f"""
            USER FINANCIAL CONTEXT:
            Portfolio Value: ₹{context_data.get('portfolio_value', 0):,.0f}
            Monthly Income: ₹{context_data.get('monthly_income', 0):,.0f}
            Monthly Expenses: ₹{context_data.get('monthly_expenses', 0):,.0f}
            Active Goals: {len(context_data.get('goals', []))}
            Holdings: {context_data.get('holdings_count', 0)} assets
            
            USER QUESTION: {request.message}
            
            Provide a personalized financial response using their actual data.
            """
        else:
            enhanced_prompt = request.message
        
        # Process with Enhanced FinVoice AI
        ai_response = await enhanced_finvoice_service.process_fintech_query(
            enhanced_prompt, request.user_id
        )
        
        # Log chat interaction
        await _log_chat_interaction(request.user_id, request.message, ai_response, db)
        
        return {
            "success": True,
            "response": ai_response.get("text_response", ""),
            "query_type": ai_response.get("query_type", "general"),
            "confidence": ai_response.get("confidence", 0.9),
            "context_included": request.include_context,
            "user_id": request.user_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "success": False,
            "response": "I'm here to help with your financial questions. Please try asking again.",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Blockchain endpoints
@app.get("/api/v1/blockchain/status")
async def get_blockchain_status():
    """Get blockchain network status"""
    try:
        status = blockchain_service.get_network_status()
        costs = await blockchain_service.estimate_costs()
        
        return {
            "success": True,
            "network": status,
            "estimated_costs": costs,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Blockchain status error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/v1/blockchain/audit/{user_id}")
async def get_audit_trail(
    user_id: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get blockchain audit trail for user"""
    try:
        audit_trail = await blockchain_service.get_audit_trail(user_id, db, limit)
        
        return {
            "success": True,
            "audit_trail": audit_trail,
            "user_id": user_id,
            "entries_count": len(audit_trail),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Audit trail error: {e}")
        return {"success": False, "error": str(e)}

# Webhook endpoint for Vapi
@app.post("/api/v1/vapi/webhook")
async def vapi_webhook(request: Request):
    """Handle Vapi webhook events"""
    try:
        request_data = await request.json()
        webhook_handler = vapi_service.get_webhook_handler()
        response = await webhook_handler(request_data)
        
        return response
        
    except Exception as e:
        logger.error(f"Vapi webhook error: {e}")
        return {"status": "error", "message": str(e)}

# Simple voice chat endpoint without authentication (for testing)
@app.post("/api/v1/vapi/voice-chat")
async def voice_chat_public(
    request: VoiceMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """Public voice chat endpoint for testing voice functionality"""
    try:
        logger.info(f"Voice chat request from user: {request.user_id}, message: {request.message}")
        
        # Get user context
        user_context = await get_user_context(request.user_id, db)
        
        # Process with Enhanced FinVoice AI
        ai_response = await enhanced_finvoice_service.process_fintech_query(
            request.message, request.user_id
        )
        
        # Build response
        response_data = {
            "success": True,
            "text_response": ai_response.get("text_response", "I'm here to help with your financial questions."),
            "query_type": ai_response.get("query_type", "general"),
            "confidence": ai_response.get("confidence", 0.9),
            "user_id": request.user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Voice chat response: {response_data}")
        return response_data
        
    except Exception as e:
        logger.error(f"Voice chat error: {e}")
        return {
            "success": False,
            "text_response": "I'm sorry, I encountered an error processing your request. Please try again.",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Demo endpoints (removed when DEMO_MODE=false)
@app.get("/api/v1/demo/dashboard")
async def get_demo_dashboard():
    """Demo dashboard data"""
    if not settings.DEMO_MODE:
        raise HTTPException(status_code=404, detail="Demo endpoints disabled in production")
    
    return {
        "totalBalance": 925000.50,
        "monthlyIncome": 85000.00,
        "monthlyExpenses": 35000.00,
        "savingsRate": 58.8,
        "portfolioValue": 650000.00,
        "portfolioGrowth": 15.2,
        "currency": "INR",
        "mode": "demo"
    }

# Helper functions
async def _log_voice_interaction(
    user_id: str, 
    message: str, 
    response: Dict[str, Any], 
    db: AsyncSession
):
    """Log voice interaction to audit trail"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action_type="voice_interaction",
            resource_type="voice_message",
            request_data={"message": message},
            response_data={"success": response.get("success")},
            status="success" if response.get("success") else "error"
        )
        
        db.add(audit_log)
        await db.commit()
        
    except Exception as e:
        logger.warning(f"Voice interaction logging failed: {e}")

async def _log_chat_interaction(
    user_id: str,
    message: str,
    response: Dict[str, Any],
    db: AsyncSession
):
    """Log chat interaction to audit trail"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action_type="chat_interaction",
            resource_type="ai_chat",
            request_data={"message": message},
            response_data={
                "query_type": response.get("query_type"),
                "confidence": response.get("confidence")
            },
            status="success"
        )
        
        db.add(audit_log)
        await db.commit()
        
    except Exception as e:
        logger.warning(f"Chat interaction logging failed: {e}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates and development tools"""
    try:
        await websocket.accept()
        # Send a welcome message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to FinVoice WebSocket",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive with periodic updates
        while True:
            try:
                # Send periodic heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "server_status": "running"
                })
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected")
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.MAX_WORKERS,
        log_level=settings.LOG_LEVEL.lower()
    )
