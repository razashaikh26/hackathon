from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.core.security import verify_api_key
from app.api.v1.schemas import (
    FinancialDataInput, 
    FinancialAnalysisResponse,
    VoiceInput,
    VoiceResponse
)
from app.services.financial_engine import FinancialAnalysisEngine
from app.services.voice_service import VoiceService
from app.services.enhanced_voice_query_service import enhanced_voice_query_service
from app.services.blockchain_service import BlockchainService
import structlog
from datetime import datetime

logger = structlog.get_logger()
router = APIRouter()

@router.post("/analyze", response_model=FinancialAnalysisResponse)
async def analyze_financial_data(
    data: FinancialDataInput,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(verify_api_key)
):
    """
    Main endpoint for financial data analysis
    Processes comprehensive financial data and returns AI-driven insights
    """
    try:
        # Initialize the financial analysis engine
        engine = FinancialAnalysisEngine(db)
        
        # Perform comprehensive analysis
        analysis_result = await engine.analyze_comprehensive(data)
        
        # Store analysis result in database (background task)
        background_tasks.add_task(
            engine.store_analysis_result,
            data.user.user_id,
            analysis_result
        )
        
        # Log to blockchain (background task)
        blockchain_service = BlockchainService()
        background_tasks.add_task(
            blockchain_service.log_analysis,
            data.user.user_id,
            analysis_result
        )
        
        logger.info(
            "Financial analysis completed",
            user_id=data.user.user_id,
            severity_levels={
                "expense": analysis_result.expense_analysis.severity_level,
                "portfolio": analysis_result.portfolio_management.severity_level,
                "debt": analysis_result.debt_loan_tracking.severity_level
            }
        )
        
        return analysis_result
        
    except Exception as e:
        logger.error("Error during financial analysis", exc_info=e)
        raise HTTPException(
            status_code=500,
            detail="Error processing financial analysis"
        )

@router.post("/voice", response_model=VoiceResponse)
async def process_voice_input(
    voice_data: VoiceInput,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(verify_api_key)
):
    """
    Process voice input and return transcription with optional analysis
    """
    try:
        voice_service = VoiceService()
        
        # Transcribe audio
        transcription = await voice_service.transcribe_audio(
            voice_data.audio_data,
            voice_data.language
        )
        
        # Try to extract financial intent and perform analysis if possible
        analysis_result = None
        if voice_service.contains_financial_intent(transcription):
            # Extract structured data from transcription
            structured_data = await voice_service.extract_financial_data(
                transcription,
                voice_data.user_id
            )
            
            if structured_data:
                engine = FinancialAnalysisEngine(db)
                analysis_result = await engine.analyze_comprehensive(structured_data)
                
                # Store result (background task)
                background_tasks.add_task(
                    engine.store_analysis_result,
                    voice_data.user_id,
                    analysis_result
                )
        
        return VoiceResponse(
            transcription=transcription,
            analysis=analysis_result,
            confidence=voice_service.last_confidence
        )
        
    except Exception as e:
        logger.error("Error processing voice input", exc_info=e)
        raise HTTPException(
            status_code=500,
            detail="Error processing voice input"
        )

@router.post("/voice/enhanced-message")
async def process_enhanced_voice_message(
    audio: UploadFile = File(...),
    language: str = Form(default="en-IN"),
    user_id: str = Form(default="demo_user"),
    use_vapi: str = Form(default="true"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Enhanced voice message processing with SQL-like query capabilities
    Processes audio files and returns intelligent financial responses
    """
    try:
        logger.info(f"Processing enhanced voice message for user: {user_id}")
        
        # Convert use_vapi string to boolean
        use_vapi_bool = use_vapi.lower() in ('true', '1', 'yes')
        
        # Read audio file
        audio_content = await audio.read()
        
        # Initialize voice service for transcription
        voice_service = VoiceService()
        
        # Convert audio bytes to base64 for transcription
        import base64
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        
        # Transcribe audio to text
        transcription = await voice_service.transcribe_audio(audio_base64, language)
        
        if not transcription:
            return {
                "success": False,
                "error": "Could not transcribe audio",
                "text_response": "Sorry, I couldn't understand your voice message. Please try speaking more clearly."
            }
        
        logger.info(f"Transcription: {transcription}")
        
        # Process with enhanced query service
        query_result = await enhanced_voice_query_service.process_voice_query(
            transcription, 
            user_id
        )
        
        # Build comprehensive response
        response_data = {
            "success": query_result["success"],
            "transcription": transcription,
            "user_message": transcription,
            "text_response": query_result["formatted_response"],
            "language": language,
            "user_id": user_id
        }
        
        if query_result["success"]:
            response_data.update({
                "query_type": query_result["query_type"],
                "confidence": query_result["confidence"],
                "sql_equivalent": query_result["sql_equivalent"],
                "financial_data": query_result["data"],
                "enhanced_processing": True
            })
        else:
            response_data.update({
                "suggestions": query_result.get("suggestions", []),
                "confidence": query_result.get("confidence", 0.0)
            })
        
        logger.info(f"Enhanced voice processing completed successfully for user: {user_id}")
        return response_data
        
    except Exception as e:
        logger.error(f"Enhanced voice processing failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "text_response": "Sorry, I encountered an error processing your voice message. Please try again.",
            "transcription": ""
        }

@router.post("/voice/text-to-speech")
async def convert_text_to_speech(
    request_data: dict,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Convert text to speech with enhanced voice quality
    Returns audio response for voice output
    """
    try:
        text = request_data.get("text", "")
        language = request_data.get("language", "en-IN")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        logger.info(f"Converting text to speech: {text[:50]}...")
        
        # Initialize voice service
        voice_service = VoiceService()
        
        # Generate speech (this would use actual TTS service in production)
        # For demo, we'll return a success response
        response_data = {
            "success": True,
            "text": text,
            "language": language,
            "audio_response": None,  # Would contain base64 audio in production
            "message": "Text-to-speech processing completed"
        }
        
        logger.info("Text-to-speech conversion completed")
        return response_data
        
    except Exception as e:
        logger.error(f"Text-to-speech conversion failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Text-to-speech conversion failed"
        }

@router.get("/portfolio/{user_id}")
async def get_portfolio_summary(
    user_id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(verify_api_key)
):
    """Get portfolio summary for a user"""
    try:
        engine = FinancialAnalysisEngine(db)
        portfolio_data = await engine.get_portfolio_summary(user_id)
        return portfolio_data
        
    except Exception as e:
        logger.error("Error fetching portfolio", exc_info=e)
        raise HTTPException(
            status_code=500,
            detail="Error fetching portfolio data"
        )

@router.get("/insights/{user_id}")
async def get_user_insights(
    user_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(verify_api_key)
):
    """Get recent insights for a user"""
    try:
        engine = FinancialAnalysisEngine(db)
        insights = await engine.get_recent_insights(user_id, limit)
        return {"insights": insights}
        
    except Exception as e:
        logger.error("Error fetching insights", exc_info=e)
        raise HTTPException(
            status_code=500,
            detail="Error fetching insights"
        )

@router.post("/goals/{user_id}")
async def create_financial_goal(
    user_id: str,
    goal_data: dict,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(verify_api_key)
):
    """Create a new financial goal with AI recommendations"""
    try:
        engine = FinancialAnalysisEngine(db)
        goal = await engine.create_goal_with_recommendations(user_id, goal_data)
        
        # Recalculate financial plan (background task)
        background_tasks.add_task(
            engine.recalculate_financial_plan,
            user_id
        )
        
        return goal
        
    except Exception as e:
        logger.error("Error creating goal", exc_info=e)
        raise HTTPException(
            status_code=500,
            detail="Error creating financial goal"
        )

@router.get("/market-alerts")
async def get_market_alerts(
    current_user: dict = Depends(verify_api_key)
):
    """Get current market alerts and risk notifications"""
    try:
        engine = FinancialAnalysisEngine(None)
        alerts = await engine.get_market_alerts()
        return {"alerts": alerts}
        
    except Exception as e:
        logger.error("Error fetching market alerts", exc_info=e)
        raise HTTPException(
            status_code=500,
            detail="Error fetching market alerts"
        )

# Enhanced VAPI Integration Endpoints

@router.get("/vapi/config")
async def get_vapi_config():
    """Get public VAPI configuration for frontend"""
    try:
        # Return safe configuration for frontend use
        config = {
            "config": {
                "public_key": "584ce1e5-dc84-43b3-9ec1-40099b3c315f",  # Safe for frontend
                "assistant_id": "finvoice-ai-assistant",
                "supported_languages": ["english", "hindi", "tamil", "telugu", "bengali", "marathi"],
                "features": {
                    "voice_calls": True,
                    "real_time_conversation": True,
                    "multi_language": True,
                    "financial_context": True,
                    "sql_like_queries": True
                },
                "endpoints": {
                    "voice_chat": "/api/v1/vapi/voice-chat",
                    "start_call": "/api/v1/vapi/start-call",
                    "call_status": "/api/v1/vapi/call-status",
                    "webhook": "/api/v1/vapi/webhook"
                }
            }
        }
        return config
    except Exception as e:
        logger.error(f"Error getting VAPI config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get VAPI configuration")

@router.post("/vapi/voice-chat")
async def vapi_voice_chat(
    request_data: dict,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Enhanced VAPI voice chat with SQL-like query processing"""
    try:
        message = request_data.get("message", "")
        language = request_data.get("language", "english")
        user_id = request_data.get("user_id", "demo_user")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        logger.info(f"VAPI voice chat request: {message[:50]}... for user: {user_id}")
        
        # Process with enhanced query service
        query_result = await enhanced_voice_query_service.process_voice_query(message, user_id)
        
        response = {
            "success": query_result["success"],
            "text_response": query_result["formatted_response"],
            "assistant_id": "finvoice-ai-assistant",
            "user_message": message,
            "language": language
        }
        
        if query_result["success"]:
            response.update({
                "query_type": query_result["query_type"],
                "confidence": query_result["confidence"],
                "sql_equivalent": query_result["sql_equivalent"],
                "enhanced_processing": True
            })
        
        logger.info(f"VAPI voice chat completed for user: {user_id}")
        return response
        
    except Exception as e:
        logger.error(f"VAPI voice chat failed: {str(e)}")
        return {
            "success": False,
            "text_response": "Sorry, I encountered an error processing your message. Please try again.",
            "error": str(e),
            "assistant_id": "finvoice-ai-assistant"
        }

@router.post("/vapi/start-call")
async def vapi_start_call(request_data: dict):
    """Start a VAPI voice call (placeholder for future implementation)"""
    try:
        phone_number = request_data.get("phone_number", "")
        language = request_data.get("language", "english")
        
        if not phone_number:
            raise HTTPException(status_code=400, detail="Phone number is required")
        
        logger.info(f"VAPI call start request for: {phone_number}")
        
        # For now, return a mock response
        # In production, this would integrate with actual VAPI call service
        return {
            "success": True,
            "call_id": f"call_{phone_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "assistant_id": "finvoice-ai-assistant",
            "message": "Call feature is coming soon. Currently supporting voice messages only."
        }
        
    except Exception as e:
        logger.error(f"VAPI call start failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to start call"
        }

@router.get("/vapi/call-status/{call_id}")
async def vapi_call_status(call_id: str):
    """Get VAPI call status (placeholder for future implementation)"""
    try:
        logger.info(f"VAPI call status request for: {call_id}")
        
        return {
            "call_id": call_id,
            "status": "not_implemented",
            "message": "Call status feature is coming soon"
        }
        
    except Exception as e:
        logger.error(f"VAPI call status failed: {str(e)}")
        return {"error": "Failed to get call status"}

@router.post("/vapi/webhook")
async def vapi_webhook(request_data: dict):
    """VAPI webhook endpoint for handling call events"""
    try:
        event_type = request_data.get("type", "")
        call_id = request_data.get("call_id", "")
        
        logger.info(f"VAPI webhook received: {event_type} for call: {call_id}")
        
        # Handle different webhook events
        if event_type == "call_started":
            logger.info(f"Call started: {call_id}")
        elif event_type == "call_ended":
            logger.info(f"Call ended: {call_id}")
        elif event_type == "transcript":
            transcript = request_data.get("transcript", "")
            logger.info(f"Transcript received: {transcript}")
        
        return {"status": "received", "message": "Webhook processed successfully"}
        
    except Exception as e:
        logger.error(f"VAPI webhook processing failed: {str(e)}")
        return {"error": "Webhook processing failed"}
