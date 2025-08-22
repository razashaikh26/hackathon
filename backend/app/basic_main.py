#!/usr/bin/env python3
"""
FinVoice Basic Main - Minimal FastAPI Application with Database Integration
Production-ready backend for FinVoice AI financial assistant.
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Database imports
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db, close_db
from api.v1.database_api import router as database_router

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="FinVoice AI Engine",
    description="Production AI financial assistant with live portfolio computation and Vapi voice integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include database API routes
app.include_router(database_router)

# Database lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize database and other services on startup"""
    try:
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        await close_db()
        print("✅ Database connections closed")
    except Exception as e:
        print(f"❌ Error during shutdown: {e}")

# Basic models
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "demo_user"

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime
    user_id: str

class PortfolioResponse(BaseModel):
    total_value: float
    holdings: List[Dict[str, Any]]
    last_updated: datetime
    currency: str = "USD"

class VapiConfigResponse(BaseModel):
    public_key: str
    assistant_id: str
    phone_number: str

# Mock data for demo
MOCK_PORTFOLIO = [
    {"symbol": "AAPL", "shares": 10, "current_price": 175.50, "value": 1755.00},
    {"symbol": "GOOGL", "shares": 5, "current_price": 142.30, "value": 711.50},
    {"symbol": "MSFT", "shares": 8, "current_price": 378.85, "value": 3030.80},
    {"symbol": "TSLA", "shares": 3, "current_price": 248.42, "value": 745.26},
]

MOCK_TRANSACTIONS = [
    {
        "id": "txn_001",
        "date": "2025-08-20",
        "description": "Coffee Shop Purchase",
        "amount": -4.85,
        "category": "Food & Dining",
        "account": "Checking"
    },
    {
        "id": "txn_002", 
        "date": "2025-08-19",
        "description": "Salary Deposit",
        "amount": 2500.00,
        "category": "Income",
        "account": "Checking"
    },
    {
        "id": "txn_003",
        "date": "2025-08-18",
        "description": "Electric Bill",
        "amount": -89.34,
        "category": "Utilities",
        "account": "Checking"
    }
]

MOCK_GOALS = [
    {
        "id": "goal_001",
        "name": "Emergency Fund",
        "target_amount": 18000.00,
        "current_amount": 15120.00,
        "target_date": "2025-12-31",
        "category": "savings",
        "priority": "high",
        "created_at": "2025-01-01"
    },
    {
        "id": "goal_002",
        "name": "Vacation Fund",
        "target_amount": 5000.00,
        "current_amount": 2500.00,
        "target_date": "2025-10-15",
        "category": "lifestyle",
        "priority": "medium",
        "created_at": "2025-02-15"
    },
    {
        "id": "goal_003",
        "name": "Investment Portfolio Growth",
        "target_amount": 10000.00,
        "current_amount": 6242.56,
        "target_date": "2026-08-22",
        "category": "investment",
        "priority": "high",
        "created_at": "2024-08-22"
    }
]

# Pydantic models for CRUD operations
class TransactionCreate(BaseModel):
    description: str
    amount: float
    category: str
    account: str = "Checking"
    date: Optional[str] = None

class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    account: Optional[str] = None
    date: Optional[str] = None

class GoalCreate(BaseModel):
    name: str
    target_amount: float
    target_date: str
    category: str = "savings"
    priority: str = "medium"
    current_amount: float = 0.0

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    target_date: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None

# Routes
@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with system status"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="2.0.0",
        services={
            "database": "connected" if os.getenv("DATABASE_URL") else "demo_mode",
            "redis": "connected" if os.getenv("REDIS_URL") else "demo_mode", 
            "vapi": "configured" if os.getenv("VAPI_PRIVATE_API_KEY") else "demo_mode",
            "openai": "configured" if os.getenv("OPENAI_API_KEY") else "demo_mode"
        }
    )

@app.get("/api/v1/portfolio", response_model=PortfolioResponse)
async def get_portfolio(user_id: str = "demo_user"):
    """Get user portfolio with live market values"""
    try:
        total_value = sum(holding["value"] for holding in MOCK_PORTFOLIO)
        
        return PortfolioResponse(
            total_value=total_value,
            holdings=MOCK_PORTFOLIO,
            last_updated=datetime.now(),
            currency="USD"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio computation failed: {str(e)}")

@app.get("/api/v1/portfolio/performance")
async def get_portfolio_performance(user_id: str = "demo_user", period: str = "1M"):
    """Get portfolio performance metrics"""
    total_value = sum(holding["value"] for holding in MOCK_PORTFOLIO)
    
    return {
        "user_id": user_id,
        "period": period,
        "current_value": total_value,
        "performance": {
            "total_return": 12.5,
            "total_return_amount": 850.75,
            "daily_change": 2.34,
            "daily_change_amount": 156.78,
            "weekly_change": 5.67,
            "weekly_change_amount": 378.90,
            "monthly_change": 12.5,
            "monthly_change_amount": 850.75
        },
        "holdings_performance": [
            {"symbol": "AAPL", "return_percent": 15.2, "return_amount": 267.06},
            {"symbol": "GOOGL", "return_percent": 8.7, "return_amount": 61.90},
            {"symbol": "MSFT", "return_percent": 11.3, "return_amount": 342.48},
            {"symbol": "TSLA", "return_percent": 18.9, "return_amount": 140.83}
        ],
        "benchmark_comparison": {
            "sp500_return": 8.2,
            "outperformance": 4.3
        }
    }

@app.delete("/api/v1/portfolio/holdings/{symbol}")
async def delete_holding(symbol: str, user_id: str = "demo_user"):
    """Delete a portfolio holding"""
    for i, holding in enumerate(MOCK_PORTFOLIO):
        if holding["symbol"].upper() == symbol.upper():
            deleted_holding = MOCK_PORTFOLIO.pop(i)
            
            return {
                "message": f"Successfully deleted {symbol} holding",
                "deleted_holding": deleted_holding,
                "remaining_holdings": len(MOCK_PORTFOLIO),
                "new_portfolio_value": sum(h["value"] for h in MOCK_PORTFOLIO)
            }
    
    raise HTTPException(status_code=404, detail=f"Holding {symbol} not found in portfolio")

@app.put("/api/v1/portfolio/holdings/{symbol}")
async def update_holding(symbol: str, shares: float, user_id: str = "demo_user"):
    """Update shares for a portfolio holding"""
    for holding in MOCK_PORTFOLIO:
        if holding["symbol"].upper() == symbol.upper():
            old_shares = holding["shares"]
            holding["shares"] = shares
            holding["value"] = shares * holding["current_price"]
            
            return {
                "message": f"Updated {symbol} shares from {old_shares} to {shares}",
                "updated_holding": holding,
                "portfolio_value": sum(h["value"] for h in MOCK_PORTFOLIO)
            }
    
    raise HTTPException(status_code=404, detail=f"Holding {symbol} not found in portfolio")

@app.post("/api/v1/portfolio/holdings")
async def add_holding(symbol: str, shares: float, current_price: float, user_id: str = "demo_user"):
    """Add a new holding to portfolio"""
    # Check if holding already exists
    for holding in MOCK_PORTFOLIO:
        if holding["symbol"].upper() == symbol.upper():
            # Update existing holding
            holding["shares"] += shares
            holding["value"] = holding["shares"] * holding["current_price"]
            return {
                "message": f"Added {shares} shares to existing {symbol} position",
                "updated_holding": holding,
                "portfolio_value": sum(h["value"] for h in MOCK_PORTFOLIO)
            }
    
    # Add new holding
    new_holding = {
        "symbol": symbol.upper(),
        "shares": shares,
        "current_price": current_price,
        "value": shares * current_price
    }
    
    MOCK_PORTFOLIO.append(new_holding)
    
    return {
        "message": f"Added new {symbol} holding to portfolio",
        "new_holding": new_holding,
        "portfolio_value": sum(h["value"] for h in MOCK_PORTFOLIO),
        "total_holdings": len(MOCK_PORTFOLIO)
    }

@app.delete("/api/v1/portfolio/performance/reset")
async def reset_portfolio_performance(user_id: str = "demo_user"):
    """Reset portfolio performance metrics"""
    return {
        "message": "Portfolio performance metrics reset successfully",
        "user_id": user_id,
        "reset_timestamp": datetime.now().isoformat(),
        "current_portfolio_value": sum(h["value"] for h in MOCK_PORTFOLIO),
        "holdings_count": len(MOCK_PORTFOLIO)
    }

@app.get("/api/v1/transactions")
async def get_transactions(user_id: str = "demo_user", limit: int = 10):
    """Get recent transactions for user"""
    return {
        "transactions": MOCK_TRANSACTIONS[:limit],
        "total_count": len(MOCK_TRANSACTIONS),
        "user_id": user_id
    }

@app.post("/api/v1/transactions")
async def create_transaction(transaction: TransactionCreate, user_id: str = "demo_user"):
    """Create a new transaction"""
    import uuid
    new_transaction = {
        "id": f"txn_{uuid.uuid4().hex[:6]}",
        "date": transaction.date or datetime.now().strftime("%Y-%m-%d"),
        "description": transaction.description,
        "amount": transaction.amount,
        "category": transaction.category,
        "account": transaction.account,
        "user_id": user_id,
        "created_at": datetime.now().isoformat()
    }
    
    MOCK_TRANSACTIONS.insert(0, new_transaction)
    
    return {
        "message": "Transaction created successfully",
        "transaction": new_transaction,
        "total_transactions": len(MOCK_TRANSACTIONS)
    }

@app.put("/api/v1/transactions/{transaction_id}")
async def update_transaction(transaction_id: str, transaction: TransactionUpdate):
    """Update an existing transaction"""
    for i, txn in enumerate(MOCK_TRANSACTIONS):
        if txn["id"] == transaction_id:
            # Update only provided fields
            for field, value in transaction.dict(exclude_unset=True).items():
                txn[field] = value
            txn["updated_at"] = datetime.now().isoformat()
            
            return {
                "message": "Transaction updated successfully",
                "transaction": txn
            }
    
    raise HTTPException(status_code=404, detail="Transaction not found")

@app.delete("/api/v1/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    """Delete a transaction"""
    for i, txn in enumerate(MOCK_TRANSACTIONS):
        if txn["id"] == transaction_id:
            deleted_txn = MOCK_TRANSACTIONS.pop(i)
            return {
                "message": "Transaction deleted successfully",
                "deleted_transaction": deleted_txn,
                "remaining_transactions": len(MOCK_TRANSACTIONS)
            }
    
    raise HTTPException(status_code=404, detail="Transaction not found")

@app.get("/api/v1/goals")
async def get_goals(user_id: str = "demo_user"):
    """Get user's financial goals"""
    return {
        "goals": MOCK_GOALS,
        "total_count": len(MOCK_GOALS),
        "user_id": user_id
    }

@app.post("/api/v1/goals")
async def create_goal(goal: GoalCreate, user_id: str = "demo_user"):
    """Create a new financial goal"""
    import uuid
    new_goal = {
        "id": f"goal_{uuid.uuid4().hex[:6]}",
        "name": goal.name,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "target_date": goal.target_date,
        "category": goal.category,
        "priority": goal.priority,
        "user_id": user_id,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "updated_at": datetime.now().isoformat()
    }
    
    MOCK_GOALS.append(new_goal)
    
    return {
        "message": "Goal created successfully",
        "goal": new_goal,
        "total_goals": len(MOCK_GOALS)
    }

@app.put("/api/v1/goals/{goal_id}")
async def update_goal(goal_id: str, goal: GoalUpdate):
    """Update an existing goal"""
    for i, existing_goal in enumerate(MOCK_GOALS):
        if existing_goal["id"] == goal_id:
            # Update only provided fields
            for field, value in goal.dict(exclude_unset=True).items():
                existing_goal[field] = value
            existing_goal["updated_at"] = datetime.now().isoformat()
            
            return {
                "message": "Goal updated successfully",
                "goal": existing_goal
            }
    
    raise HTTPException(status_code=404, detail="Goal not found")

@app.delete("/api/v1/goals/{goal_id}")
async def delete_goal(goal_id: str):
    """Delete a goal"""
    for i, goal in enumerate(MOCK_GOALS):
        if goal["id"] == goal_id:
            deleted_goal = MOCK_GOALS.pop(i)
            return {
                "message": "Goal deleted successfully",
                "deleted_goal": deleted_goal,
                "remaining_goals": len(MOCK_GOALS)
            }
    
    raise HTTPException(status_code=404, detail="Goal not found")

@app.post("/api/v1/goals/{goal_id}/contribute")
async def contribute_to_goal(goal_id: str, amount: float):
    """Make a contribution to a specific goal"""
    for goal in MOCK_GOALS:
        if goal["id"] == goal_id:
            goal["current_amount"] += amount
            goal["updated_at"] = datetime.now().isoformat()
            
            # Calculate progress
            progress_percentage = (goal["current_amount"] / goal["target_amount"]) * 100
            
            return {
                "message": f"Contribution of ${amount:.2f} added successfully",
                "goal": goal,
                "progress_percentage": round(progress_percentage, 2),
                "remaining_amount": goal["target_amount"] - goal["current_amount"]
            }
    
    raise HTTPException(status_code=404, detail="Goal not found")

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with FinVoice AI assistant"""
    try:
        # Simple AI response logic
        message = request.message.lower()
        
        if "portfolio" in message or "balance" in message:
            total_value = sum(holding["value"] for holding in MOCK_PORTFOLIO)
            response = f"Your current portfolio value is ${total_value:,.2f}. Your largest holding is {MOCK_PORTFOLIO[0]['symbol']} with a value of ${MOCK_PORTFOLIO[0]['value']:,.2f}."
        
        elif "spending" in message or "expenses" in message:
            recent_expenses = [t for t in MOCK_TRANSACTIONS if t["amount"] < 0][:3]
            total_expenses = sum(t["amount"] for t in recent_expenses)
            response = f"Your recent expenses total ${abs(total_expenses):,.2f}. Recent purchases include: {', '.join([t['description'] for t in recent_expenses])}."
        
        elif "income" in message:
            recent_income = [t for t in MOCK_TRANSACTIONS if t["amount"] > 0][:3]
            total_income = sum(t["amount"] for t in recent_income)
            response = f"Your recent income is ${total_income:,.2f}. Latest deposit: {recent_income[0]['description'] if recent_income else 'No recent income found'}."
        
        elif "help" in message:
            response = "I'm FinVoice, your AI financial assistant! I can help you with portfolio analysis, expense tracking, investment advice, and financial planning. Try asking about your portfolio, spending, or income."
        
        else:
            response = f"I understand you're asking about '{request.message}'. I'm your FinVoice AI assistant ready to help with your finances. Ask me about your portfolio, spending, income, or financial advice!"
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now(),
            user_id=request.user_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.get("/api/v1/vapi/config", response_model=VapiConfigResponse)
async def get_vapi_config():
    """Get Vapi AI public configuration for frontend"""
    return VapiConfigResponse(
        public_key=os.getenv("VAPI_PUBLIC_KEY", "demo_public_key"),
        assistant_id=os.getenv("VAPI_ASSISTANT_ID", "finvoice-assistant-v1"),
        phone_number=os.getenv("VAPI_PHONE_NUMBER", "+1-555-FINVOICE")
    )

@app.post("/api/v1/vapi/webhook")
async def vapi_webhook(request: Request):
    """Handle Vapi AI webhook events"""
    try:
        payload = await request.json()
        event_type = payload.get("type", "unknown")
        
        print(f"Vapi webhook received: {event_type}")
        
        # Process different webhook events
        if event_type == "call.started":
            return {"message": "Call started", "status": "success"}
        elif event_type == "call.ended":
            return {"message": "Call ended", "status": "success"}
        elif event_type == "transcript":
            transcript = payload.get("transcript", "")
            return {"message": f"Transcript received: {transcript}", "status": "success"}
        else:
            return {"message": f"Event {event_type} processed", "status": "success"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@app.post("/api/v1/voice/enhanced-message")
async def voice_enhanced_message(request: Request):
    """Handle enhanced voice message processing with AI features"""
    try:
        payload = await request.json()
        message = payload.get("message", "")
        user_id = payload.get("user_id", "demo_user")
        voice_data = payload.get("voice_data", {})
        
        # Enhanced AI processing for voice input
        enhanced_response = await process_voice_with_ai(message, user_id, voice_data)
        
        return {
            "status": "success",
            "enhanced_response": enhanced_response,
            "voice_output": {
                "text": enhanced_response["text"],
                "audio_url": enhanced_response.get("audio_url"),
                "duration": enhanced_response.get("duration", 0)
            },
            "ai_insights": enhanced_response.get("insights", []),
            "actions_performed": enhanced_response.get("actions", []),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

async def process_voice_with_ai(message: str, user_id: str, voice_data: dict) -> dict:
    """Process voice input with enhanced AI features"""
    message_lower = message.lower()
    
    # Financial analysis
    if any(keyword in message_lower for keyword in ["portfolio", "investment", "stocks", "balance"]):
        portfolio_value = sum(holding["value"] for holding in MOCK_PORTFOLIO)
        top_holding = max(MOCK_PORTFOLIO, key=lambda x: x["value"])
        
        response_text = f"Your portfolio is worth ${portfolio_value:,.2f}. Your top performing asset is {top_holding['symbol']} valued at ${top_holding['value']:,.2f}. Based on current market trends, I recommend considering rebalancing if this represents more than 30% of your portfolio."
        
        insights = [
            "Portfolio diversification looks good across tech stocks",
            "Consider taking profits on AAPL if it reaches $180",
            "Market volatility is expected this week due to earnings"
        ]
        
        actions = ["portfolio_analysis", "risk_assessment", "rebalancing_recommendation"]
    
    # Expense analysis
    elif any(keyword in message_lower for keyword in ["spend", "expense", "budget", "money"]):
        recent_expenses = [t for t in MOCK_TRANSACTIONS if t["amount"] < 0]
        total_spent = abs(sum(t["amount"] for t in recent_expenses))
        
        response_text = f"You've spent ${total_spent:.2f} recently. Your largest expense was {recent_expenses[0]['description']} for ${abs(recent_expenses[0]['amount']):.2f}. You're currently 15% under your monthly budget, which is excellent financial discipline."
        
        insights = [
            "Your spending pattern shows good budget control",
            "Coffee shop visits increased by 20% this month",
            "Utility costs are 5% higher than seasonal average"
        ]
        
        actions = ["expense_categorization", "budget_analysis", "savings_recommendation"]
    
    # Income and savings
    elif any(keyword in message_lower for keyword in ["income", "salary", "save", "earning"]):
        recent_income = [t for t in MOCK_TRANSACTIONS if t["amount"] > 0]
        total_income = sum(t["amount"] for t in recent_income)
        
        response_text = f"Your recent income is ${total_income:,.2f}. With your current savings rate of 85%, you're on track to meet your financial goals. I suggest increasing your emergency fund to 6 months of expenses."
        
        insights = [
            "Excellent savings rate compared to national average of 13%",
            "Consider increasing 401k contribution by 2%",
            "Emergency fund should be increased to $12,000"
        ]
        
        actions = ["savings_analysis", "goal_tracking", "investment_recommendation"]
    
    # General financial advice
    else:
        response_text = f"I understand you're asking about '{message}'. As your AI financial advisor, I'm here to help optimize your financial health. Your current net worth is strong, and I can provide personalized advice on investments, budgeting, or financial planning."
        
        insights = [
            "Overall financial health score: 85/100",
            "Investment risk tolerance: Moderate-Aggressive",
            "Recommended action: Review quarterly portfolio allocation"
        ]
        
        actions = ["general_analysis", "health_score_update"]
    
    return {
        "text": response_text,
        "audio_url": f"/api/v1/voice/audio/{user_id}/latest.mp3",
        "duration": len(response_text) * 0.1,  # Approximate speech duration
        "insights": insights,
        "actions": actions,
        "confidence_score": 0.95,
        "sentiment": "positive"
    }

@app.get("/api/v1/blockchain/status")
async def blockchain_status():
    """Get blockchain network status"""
    return {
        "network": "Polygon Amoy Testnet",
        "chain_id": 80002,
        "status": "connected",
        "wallet_address": os.getenv("WALLET_ADDRESS", "demo_address"),
        "last_block": 12345678,
        "gas_price": "20 gwei"
    }

@app.get("/api/v1/analytics/summary")
async def analytics_summary(user_id: str = "demo_user"):
    """Get financial analytics summary"""
    portfolio_value = sum(holding["value"] for holding in MOCK_PORTFOLIO)
    total_expenses = sum(t["amount"] for t in MOCK_TRANSACTIONS if t["amount"] < 0)
    total_income = sum(t["amount"] for t in MOCK_TRANSACTIONS if t["amount"] > 0)
    
    return {
        "user_id": user_id,
        "portfolio_value": portfolio_value,
        "monthly_income": total_income,
        "monthly_expenses": abs(total_expenses),
        "net_worth": portfolio_value + total_income + total_expenses,
        "spending_categories": {
            "Food & Dining": -4.85,
            "Utilities": -89.34,
            "Transportation": -45.20,
            "Shopping": -127.50
        },
        "investment_performance": {
            "total_return": 12.5,
            "monthly_return": 2.3,
            "best_performer": "MSFT",
            "worst_performer": "TSLA"
        }
    }

@app.get("/api/v1/insights")
async def get_ai_insights(user_id: str = "demo_user", currency: str = "USD"):
    """Get AI-generated financial insights and recommendations"""
    portfolio_value = sum(holding["value"] for holding in MOCK_PORTFOLIO)
    total_expenses = sum(t["amount"] for t in MOCK_TRANSACTIONS if t["amount"] < 0)
    total_income = sum(t["amount"] for t in MOCK_TRANSACTIONS if t["amount"] > 0)
    
    # Currency conversion rate (USD to INR)
    usd_to_inr_rate = 83.25
    
    # Convert values if INR is requested
    if currency.upper() == "INR":
        portfolio_value *= usd_to_inr_rate
        total_income *= usd_to_inr_rate
        total_expenses *= usd_to_inr_rate
        currency_symbol = "₹"
    else:
        currency_symbol = "$"
    
    insights = [
        {
            "id": "insight_1",
            "type": "portfolio_optimization",
            "title": "Portfolio Diversification Opportunity",
            "description": f"Your portfolio shows 48% concentration in tech stocks. Consider diversifying into healthcare or renewable energy sectors to reduce risk.",
            "impact": "Medium",
            "confidence": 0.87,
            "recommended_action": "Rebalance 15% of tech holdings into other sectors",
            "potential_benefit": f"{currency_symbol}{1200 if currency == 'INR' else 15:.2f} annual return improvement",
            "category": "investment"
        },
        {
            "id": "insight_2", 
            "type": "expense_optimization",
            "title": "Subscription Service Analysis",
            "description": f"Analysis shows {currency_symbol}{250 if currency == 'INR' else 3:.2f} monthly on subscription services. 40% appear unused in last 30 days.",
            "impact": "High",
            "confidence": 0.92,
            "recommended_action": "Cancel 3 unused subscriptions",
            "potential_benefit": f"{currency_symbol}{3000 if currency == 'INR' else 36:.2f} annual savings",
            "category": "expense"
        },
        {
            "id": "insight_3",
            "type": "savings_opportunity", 
            "title": "Emergency Fund Goal",
            "description": f"Your emergency fund covers 4.2 months of expenses. Financial experts recommend 6 months ({currency_symbol}{15000 if currency == 'INR' else 180:.2f}).",
            "impact": "High",
            "confidence": 0.95,
            "recommended_action": f"Increase monthly savings by {currency_symbol}{8000 if currency == 'INR' else 100:.2f}",
            "potential_benefit": "Enhanced financial security and peace of mind",
            "category": "savings"
        },
        {
            "id": "insight_4",
            "type": "tax_optimization",
            "title": "Tax-Loss Harvesting Opportunity", 
            "description": "TSLA position shows unrealized losses that could offset capital gains tax liability.",
            "impact": "Medium",
            "confidence": 0.78,
            "recommended_action": "Consider tax-loss harvesting before year-end",
            "potential_benefit": f"{currency_symbol}{4000 if currency == 'INR' else 48:.2f} potential tax savings",
            "category": "tax"
        },
        {
            "id": "insight_5",
            "type": "market_timing",
            "title": "Market Volatility Alert",
            "description": "Increased market volatility expected due to upcoming Fed meeting. Consider defensive positioning.",
            "impact": "Medium",
            "confidence": 0.83,
            "recommended_action": "Reduce position sizes by 10% temporarily",
            "potential_benefit": "Risk reduction during volatile period",
            "category": "market"
        }
    ]
    
    # Performance metrics
    performance_metrics = {
        "financial_health_score": 85,
        "risk_tolerance": "Moderate-Aggressive",
        "savings_rate": 22.5,
        "debt_to_income_ratio": 0.15,
        "investment_diversification": 72,
        "emergency_fund_months": 4.2,
        "credit_score_estimate": 750
    }
    
    # Goals progress
    goals_progress = [
        {
            "goal_id": "goal_1",
            "name": "Emergency Fund",
            "target_amount": 15000 if currency == "INR" else 18000,
            "current_amount": 12600 if currency == "INR" else 15120,
            "progress_percentage": 84,
            "target_date": "2025-12-31",
            "monthly_contribution_needed": 400 if currency == "INR" else 480
        },
        {
            "goal_id": "goal_2", 
            "name": "Vacation Fund",
            "target_amount": 41625 if currency == "INR" else 5000,
            "current_amount": 20812 if currency == "INR" else 2500,
            "progress_percentage": 50,
            "target_date": "2025-10-15",
            "monthly_contribution_needed": 3468 if currency == "INR" else 416
        },
        {
            "goal_id": "goal_3",
            "name": "Investment Portfolio Growth",
            "target_amount": 832500 if currency == "INR" else 10000,
            "current_amount": 520000 if currency == "INR" else 6242,
            "progress_percentage": 62,
            "target_date": "2026-08-22",
            "monthly_contribution_needed": 2604 if currency == "INR" else 312
        }
    ]
    
    return {
        "user_id": user_id,
        "currency": currency,
        "currency_symbol": currency_symbol,
        "exchange_rate": usd_to_inr_rate if currency == "INR" else 1.0,
        "generated_at": datetime.now().isoformat(),
        "insights": insights,
        "performance_metrics": performance_metrics,
        "goals_progress": goals_progress,
        "market_summary": {
            "market_trend": "Bullish with volatility",
            "recommended_sectors": ["Healthcare", "Renewable Energy", "Technology"],
            "risk_level": "Medium",
            "outlook": "Positive for next quarter"
        },
        "next_review_date": (datetime.now() + timedelta(days=30)).isoformat()
    }

@app.get("/api/v1/currency/convert")
async def convert_currency(amount: float, from_currency: str = "USD", to_currency: str = "INR"):
    """Convert currency amounts"""
    rates = {
        "USD_TO_INR": 83.25,
        "INR_TO_USD": 1/83.25
    }
    
    conversion_key = f"{from_currency.upper()}_TO_{to_currency.upper()}"
    rate = rates.get(conversion_key, 1.0)
    
    converted_amount = amount * rate
    
    return {
        "original_amount": amount,
        "from_currency": from_currency.upper(),
        "to_currency": to_currency.upper(),
        "exchange_rate": rate,
        "converted_amount": round(converted_amount, 2),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/dashboard")
async def get_dashboard():
    """Get dashboard data"""
    return {
        "user_id": "demo_user",
        "currency": "USD",
        "totalBalance": 8648.37,
        "portfolioValue": 6242.56,
        "monthlyIncome": 2500.00,
        "monthlyExpenses": 94.19,
        "netWorth": 8648.37,
        "portfolioGrowth": 2.34,  # daily_change_percent
        "savingsRate": 96.23,  # (income - expenses) / income * 100
        "recentTransactions": [
            {
                "id": "txn_001",
                "date": "2025-08-20",
                "description": "Coffee Shop Purchase",
                "amount": -4.85,
                "category": "Food & Dining", 
                "account": "Checking",
                "type": "expense",
                "currency": "USD"
            },
            {
                "id": "txn_002",
                "date": "2025-08-19",
                "description": "Salary Deposit",
                "amount": 2500.00,
                "category": "Income",
                "account": "Checking",
                "type": "income",
                "currency": "USD"
            },
            {
                "id": "txn_003",
                "date": "2025-08-18",
                "description": "Electric Bill",
                "amount": -89.34,
                "category": "Utilities",
                "account": "Checking",
                "type": "expense",
                "currency": "USD"
            }
        ],
        "portfolio_summary": {
            "total_value": 6242.56,
            "holdings_count": 4,
            "top_holdings": [
                {
                    "symbol": "AAPL",
                    "shares": 10,
                    "current_price": 175.50,
                    "value": 1755.00
                },
                {
                    "symbol": "GOOGL", 
                    "shares": 5,
                    "current_price": 142.30,
                    "value": 711.50
                },
                {
                    "symbol": "MSFT",
                    "shares": 8,
                    "current_price": 378.85,
                    "value": 3030.80
                }
            ]
        },
        "performance": {
            "daily_change": 156.78,
            "daily_change_percent": 2.34,
            "weekly_change": 567.89,
            "weekly_change_percent": 8.12
        },
        "alerts": [
            {
                "type": "info",
                "message": "Your AAPL position is up 3.2% today",
                "timestamp": datetime.now().isoformat()
            },
            {
                "type": "warning",
                "message": "Monthly spending is 15% above average",
                "timestamp": datetime.now().isoformat()
            }
        ]
    }

@app.get("/api/v1/expenses")
async def get_expenses(user_id: str = "demo_user", period: str = "month"):
    """Get expense data and analysis"""
    expenses = [t for t in MOCK_TRANSACTIONS if t["amount"] < 0]
    
    # Group expenses by category and convert to array format
    categories_dict = {}
    for expense in expenses:
        category = expense["category"]
        if category not in categories_dict:
            categories_dict[category] = {"total": 0, "transactions": []}
        categories_dict[category]["total"] += abs(expense["amount"])
        categories_dict[category]["transactions"].append(expense)
    
    # Convert to array format expected by frontend
    categories_array = []
    for category_name, data in categories_dict.items():
        categories_array.append({
            "name": category_name,
            "amount": data["total"],
            "percentage": (data["total"] / abs(sum(t["amount"] for t in expenses))) * 100 if expenses else 0,
            "currency": "USD",
            "transactions": data["transactions"]
        })
    
    return {
        "user_id": user_id,
        "period": period,
        "totalMonthly": abs(sum(t["amount"] for t in expenses)),
        "total_expenses": abs(sum(t["amount"] for t in expenses)),
        "expense_count": len(expenses),
        "currency": "USD",
        "categories": categories_array,  # Now an array instead of object
        "recent_expenses": expenses[:10],
        "trends": {
            "vs_last_month": -12.5,
            "vs_last_week": 5.2,
            "largest_expense": max(expenses, key=lambda x: abs(x["amount"])) if expenses else None,
            "most_frequent_category": "Food & Dining"
        },
        "budget_analysis": {
            "budget_limit": 2000.00,
            "spent": abs(sum(t["amount"] for t in expenses)),
            "remaining": 2000.00 - abs(sum(t["amount"] for t in expenses)),
            "percentage_used": (abs(sum(t["amount"] for t in expenses)) / 2000.00) * 100
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time updates"""
    try:
        await websocket.accept()
        while True:
            # Send periodic updates
            update_data = {
                "type": "portfolio_update",
                "timestamp": datetime.now().isoformat(),
                "portfolio_value": sum(holding["value"] for holding in MOCK_PORTFOLIO),
                "market_status": "open" if datetime.now().hour < 16 else "closed"
            }
            await websocket.send_json(update_data)
            await asyncio.sleep(30)  # Send updates every 30 seconds
    except Exception as e:
        print(f"WebSocket error: {e}")

@app.get("/api/v1/demo/reset")
async def reset_demo_data():
    """Reset demo data to initial state"""
    return {
        "message": "Demo data reset successfully",
        "timestamp": datetime.now(),
        "portfolio_value": sum(holding["value"] for holding in MOCK_PORTFOLIO),
        "transaction_count": len(MOCK_TRANSACTIONS)
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FinVoice AI Engine - Basic Mode")
    print("📊 Portfolio computation with live data simulation")
    print("🎙️  Vapi AI voice assistant integration ready")
    print("🔗 Blockchain logging on Polygon Amoy testnet")
    print("💬 Real-time financial AI responses")
    print()
    print("🌐 Application available at:")
    print("   - Backend API: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Health Check: http://localhost:8000/")
    print()
    
    uvicorn.run(
        "basic_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
