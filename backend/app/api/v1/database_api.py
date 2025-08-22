"""
Database-powered API endpoints for FinVoice
Complete CRUD operations for all financial data
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import bcrypt

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.database_service import DatabaseService
from app.db.models import User, Account, Transaction, Holding, Goal

router = APIRouter(prefix="/api/v1/db", tags=["Database Operations"])

# =============== PYDANTIC MODELS ===============

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    risk_tolerance: Optional[str] = "moderate"
    currency_preference: str = "INR"
    annual_income: Optional[float] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    risk_tolerance: Optional[str] = None
    currency_preference: Optional[str] = None
    annual_income: Optional[float] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    risk_tolerance: Optional[str]
    currency_preference: str
    is_active: bool
    created_at: datetime

class LoginResponse(BaseModel):
    user: UserResponse
    message: str
    success: bool

class AccountCreate(BaseModel):
    account_type: str = Field(..., description="checking, savings, investment, credit")
    account_name: str
    institution_name: Optional[str] = None
    current_balance: float = 0.0
    currency: str = "INR"

class AccountResponse(BaseModel):
    id: str
    account_type: str
    account_name: str
    institution_name: Optional[str]
    current_balance: float
    currency: str
    is_active: bool
    created_at: datetime

class TransactionCreate(BaseModel):
    account_id: str
    amount: float
    description: str
    category: str
    transaction_type: str = Field(..., description="debit or credit")
    transaction_date: Optional[datetime] = None
    currency: str = "INR"

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    transaction_date: Optional[datetime] = None

class TransactionResponse(BaseModel):
    id: str
    amount: float
    description: str
    category: str
    transaction_type: str
    transaction_date: datetime
    currency: str
    created_at: datetime

class HoldingCreate(BaseModel):
    symbol: str
    name: str
    asset_type: str = Field(..., description="stock, etf, mutual_fund, bond, crypto")
    quantity: float
    average_price: float
    purchase_date: Optional[datetime] = None
    currency: str = "INR"

class HoldingUpdate(BaseModel):
    quantity: Optional[float] = None
    current_price: Optional[float] = None

class HoldingResponse(BaseModel):
    id: str
    symbol: str
    name: str
    asset_type: str
    quantity: float
    average_price: float
    current_price: Optional[float]
    current_value: Optional[float]
    unrealized_pnl: Optional[float]
    unrealized_pnl_percent: Optional[float]
    currency: str
    is_active: bool

class GoalCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_amount: float
    target_date: datetime
    goal_type: str = Field(..., description="emergency, house, education, retirement")
    priority: str = "medium"
    monthly_contribution: Optional[float] = None
    currency: str = "INR"

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[float] = None
    target_date: Optional[datetime] = None
    monthly_contribution: Optional[float] = None
    priority: Optional[str] = None

class GoalResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    target_amount: float
    current_amount: float
    target_date: datetime
    goal_type: str
    priority: str
    progress_percent: float
    is_achieved: bool
    currency: str

class PortfolioPerformanceResponse(BaseModel):
    total_value: float
    total_invested: float
    total_pnl: float
    total_pnl_percent: float
    week_change: float
    week_change_percent: float
    holdings_count: int
    holdings: List[Dict[str, Any]]

class FinancialOverviewResponse(BaseModel):
    portfolio: PortfolioPerformanceResponse
    cash_balance: float
    net_worth: float
    recent_transactions: List[Dict[str, Any]]
    expense_summary: Dict[str, Any]
    goals: List[Dict[str, Any]]
    accounts_count: int
    goals_count: int

# =============== HELPER FUNCTIONS ===============

async def get_db_service(session: AsyncSession = Depends(get_db)) -> DatabaseService:
    """Get database service instance"""
    return DatabaseService(session)

def get_demo_user_id() -> uuid.UUID:
    """Get demo user ID - in production, this would come from authentication"""
    return uuid.UUID("550e8400-e29b-41d4-a716-446655440000")  # Fixed demo UUID

# =============== USER ENDPOINTS ===============

@router.post("/auth/login", response_model=LoginResponse)
async def login_user(
    login_data: UserLogin,
    db_service: DatabaseService = Depends(get_db_service)
):
    """User login"""
    try:
        # Get user by email
        user = await db_service.get_user_by_email(login_data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not bcrypt.checkpw(login_data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            risk_tolerance=user.risk_tolerance,
            currency_preference=user.currency_preference,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
        return LoginResponse(
            user=user_response,
            message="Login successful",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = await db_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Hash password
        hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_dict = user_data.dict(exclude={'password'})
        user_dict['id'] = uuid.uuid4()
        user_dict['hashed_password'] = hashed_password
        
        user = await db_service.create_user(user_dict)
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            risk_tolerance=user.risk_tolerance,
            currency_preference=user.currency_preference,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str = Path(..., description="User ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get user by ID"""
    try:
        user = await db_service.get_user(uuid.UUID(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            risk_tolerance=user.risk_tolerance,
            currency_preference=user.currency_preference,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Update user by ID"""
    try:
        user = await db_service.update_user(uuid.UUID(user_id), user_data.dict(exclude_unset=True))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            risk_tolerance=user.risk_tolerance,
            currency_preference=user.currency_preference,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

# =============== ACCOUNT ENDPOINTS ===============

@router.post("/accounts", response_model=AccountResponse)
async def create_account(
    account_data: AccountCreate,
    user_id: str = Query(..., description="User ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Create a new account"""
    try:
        account_dict = account_data.dict()
        account_dict['user_id'] = uuid.UUID(user_id)
        account_dict['id'] = uuid.uuid4()
        
        account = await db_service.create_account(account_dict)
        
        return AccountResponse(
            id=str(account.id),
            account_type=account.account_type,
            account_name=account.account_name,
            institution_name=account.institution_name,
            current_balance=float(account.current_balance),
            currency=account.currency,
            is_active=account.is_active,
            created_at=account.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating account: {str(e)}")

@router.get("/accounts", response_model=List[AccountResponse])
async def get_user_accounts(
    user_id: str = Query(..., description="User ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all accounts for a user"""
    try:
        accounts = await db_service.get_user_accounts(uuid.UUID(user_id))
        
        return [
            AccountResponse(
                id=str(acc.id),
                account_type=acc.account_type,
                account_name=acc.account_name,
                institution_name=acc.institution_name,
                current_balance=float(acc.current_balance),
                currency=acc.currency,
                is_active=acc.is_active,
                created_at=acc.created_at
            ) for acc in accounts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving accounts: {str(e)}")

@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: str = Path(..., description="Account ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Delete an account"""
    try:
        success = await db_service.delete_account(uuid.UUID(account_id))
        if not success:
            raise HTTPException(status_code=404, detail="Account not found")
        
        return {"message": "Account deleted successfully", "account_id": account_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting account: {str(e)}")

# =============== TRANSACTION ENDPOINTS ===============

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    user_id: str = Query(..., description="User ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Create a new transaction"""
    try:
        transaction_dict = transaction_data.dict()
        transaction_dict['user_id'] = uuid.UUID(user_id)
        transaction_dict['account_id'] = uuid.UUID(transaction_data.account_id)
        transaction_dict['id'] = uuid.uuid4()
        
        if not transaction_dict.get('transaction_date'):
            transaction_dict['transaction_date'] = datetime.utcnow()
        
        transaction = await db_service.create_transaction(transaction_dict)
        
        return TransactionResponse(
            id=str(transaction.id),
            amount=float(transaction.amount),
            description=transaction.description,
            category=transaction.category,
            transaction_type=transaction.transaction_type,
            transaction_date=transaction.transaction_date,
            currency=transaction.currency,
            created_at=transaction.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating transaction: {str(e)}")

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    user_id: str = Query(..., description="User ID"),
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(100, description="Number of transactions to return"),
    offset: int = Query(0, description="Number of transactions to skip"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get transactions with optional filters"""
    try:
        account_uuid = uuid.UUID(account_id) if account_id else None
        
        transactions = await db_service.get_transactions(
            user_id=uuid.UUID(user_id),
            account_id=account_uuid,
            start_date=start_date,
            end_date=end_date,
            category=category,
            limit=limit,
            offset=offset
        )
        
        return [
            TransactionResponse(
                id=str(txn.id),
                amount=float(txn.amount),
                description=txn.description,
                category=txn.category,
                transaction_type=txn.transaction_type,
                transaction_date=txn.transaction_date,
                currency=txn.currency,
                created_at=txn.created_at
            ) for txn in transactions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving transactions: {str(e)}")

@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str = Path(..., description="Transaction ID"),
    transaction_data: TransactionUpdate = ...,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Update a transaction"""
    try:
        update_dict = transaction_data.dict(exclude_unset=True)
        
        transaction = await db_service.update_transaction(uuid.UUID(transaction_id), update_dict)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return TransactionResponse(
            id=str(transaction.id),
            amount=float(transaction.amount),
            description=transaction.description,
            category=transaction.category,
            transaction_type=transaction.transaction_type,
            transaction_date=transaction.transaction_date,
            currency=transaction.currency,
            created_at=transaction.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating transaction: {str(e)}")

@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: str = Path(..., description="Transaction ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Delete a transaction"""
    try:
        success = await db_service.delete_transaction(uuid.UUID(transaction_id))
        if not success:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return {"message": "Transaction deleted successfully", "transaction_id": transaction_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting transaction: {str(e)}")

@router.get("/transactions/expenses/summary")
async def get_expense_summary(
    user_id: str = Query(..., description="User ID"),
    start_date: Optional[datetime] = Query(None, description="Start date (defaults to start of current month)"),
    end_date: Optional[datetime] = Query(None, description="End date (defaults to end of current month)"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get expense summary by category"""
    try:
        if not start_date:
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        summary = await db_service.get_expense_summary(uuid.UUID(user_id), start_date, end_date)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating expense summary: {str(e)}")

# =============== HOLDINGS ENDPOINTS ===============

@router.post("/holdings", response_model=HoldingResponse)
async def create_holding(
    holding_data: HoldingCreate,
    user_id: str = Query(..., description="User ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Create a new holding"""
    try:
        holding_dict = holding_data.dict()
        holding_dict['user_id'] = uuid.UUID(user_id)
        holding_dict['id'] = uuid.uuid4()
        
        if not holding_dict.get('purchase_date'):
            holding_dict['purchase_date'] = datetime.utcnow()
        
        # Calculate purchase value
        holding_dict['purchase_value'] = holding_dict['quantity'] * holding_dict['average_price']
        holding_dict['current_price'] = holding_dict['average_price']  # Initially same
        holding_dict['current_value'] = holding_dict['purchase_value']
        
        # Calculate initial P&L (zero since current_price = average_price initially)
        holding_dict['unrealized_pnl'] = Decimal('0.00')
        holding_dict['unrealized_pnl_percent'] = 0.0
        
        holding = await db_service.create_holding(holding_dict)
        
        return HoldingResponse(
            id=str(holding.id),
            symbol=holding.symbol,
            name=holding.name,
            asset_type=holding.asset_type,
            quantity=float(holding.quantity),
            average_price=float(holding.average_price),
            current_price=float(holding.current_price) if holding.current_price else None,
            current_value=float(holding.current_value) if holding.current_value else None,
            unrealized_pnl=float(holding.unrealized_pnl) if holding.unrealized_pnl else None,
            unrealized_pnl_percent=holding.unrealized_pnl_percent,
            currency=holding.currency,
            is_active=holding.is_active
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating holding: {str(e)}")

@router.get("/holdings", response_model=List[HoldingResponse])
async def get_user_holdings(
    user_id: str = Query(..., description="User ID"),
    active_only: bool = Query(True, description="Return only active holdings"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all holdings for a user"""
    try:
        holdings = await db_service.get_user_holdings(uuid.UUID(user_id), active_only)
        
        return [
            HoldingResponse(
                id=str(h.id),
                symbol=h.symbol,
                name=h.name,
                asset_type=h.asset_type,
                quantity=float(h.quantity),
                average_price=float(h.average_price),
                current_price=float(h.current_price) if h.current_price else None,
                current_value=float(h.current_value) if h.current_value else None,
                unrealized_pnl=float(h.unrealized_pnl) if h.unrealized_pnl else None,
                unrealized_pnl_percent=h.unrealized_pnl_percent,
                currency=h.currency,
                is_active=h.is_active
            ) for h in holdings
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving holdings: {str(e)}")

@router.put("/holdings/{holding_id}", response_model=HoldingResponse)
async def update_holding(
    holding_id: str = Path(..., description="Holding ID"),
    holding_data: HoldingUpdate = ...,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Update a holding"""
    try:
        update_dict = holding_data.dict(exclude_unset=True)
        
        # If quantity or current_price is updated, recalculate values
        if 'current_price' in update_dict or 'quantity' in update_dict:
            holding = await db_service.get_holding(uuid.UUID(holding_id))
            if not holding:
                raise HTTPException(status_code=404, detail="Holding not found")
            
            new_quantity = Decimal(str(update_dict.get('quantity', holding.quantity)))
            new_price = Decimal(str(update_dict.get('current_price', holding.current_price or holding.average_price)))
            
            update_dict['current_value'] = new_quantity * new_price
            update_dict['unrealized_pnl'] = update_dict['current_value'] - holding.purchase_value
            if holding.purchase_value > 0:
                update_dict['unrealized_pnl_percent'] = float((update_dict['unrealized_pnl'] / holding.purchase_value) * 100)
        
        holding = await db_service.update_holding(uuid.UUID(holding_id), update_dict)
        if not holding:
            raise HTTPException(status_code=404, detail="Holding not found")
        
        return HoldingResponse(
            id=str(holding.id),
            symbol=holding.symbol,
            name=holding.name,
            asset_type=holding.asset_type,
            quantity=float(holding.quantity),
            average_price=float(holding.average_price),
            current_price=float(holding.current_price) if holding.current_price else None,
            current_value=float(holding.current_value) if holding.current_value else None,
            unrealized_pnl=float(holding.unrealized_pnl) if holding.unrealized_pnl else None,
            unrealized_pnl_percent=holding.unrealized_pnl_percent,
            currency=holding.currency,
            is_active=holding.is_active
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating holding: {str(e)}")

@router.delete("/holdings/{holding_id}")
async def delete_holding(
    holding_id: str = Path(..., description="Holding ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Delete a holding (soft delete)"""
    try:
        success = await db_service.delete_holding(uuid.UUID(holding_id))
        if not success:
            raise HTTPException(status_code=404, detail="Holding not found")
        
        return {"message": "Holding deleted successfully", "holding_id": holding_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting holding: {str(e)}")

@router.get("/portfolio/performance", response_model=PortfolioPerformanceResponse)
async def get_portfolio_performance(
    user_id: str = Query(..., description="User ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get portfolio performance metrics"""
    try:
        performance = await db_service.calculate_portfolio_performance(uuid.UUID(user_id))
        
        return PortfolioPerformanceResponse(**performance)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating portfolio performance: {str(e)}")

# =============== GOALS ENDPOINTS ===============

@router.post("/goals", response_model=GoalResponse)
async def create_goal(
    goal_data: GoalCreate,
    user_id: str = Query(..., description="User ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Create a new financial goal"""
    try:
        goal_dict = goal_data.dict()
        goal_dict['user_id'] = uuid.UUID(user_id)
        goal_dict['id'] = uuid.uuid4()
        
        goal = await db_service.create_goal(goal_dict)
        
        return GoalResponse(
            id=str(goal.id),
            name=goal.name,
            description=goal.description,
            target_amount=float(goal.target_amount),
            current_amount=float(goal.current_amount),
            target_date=goal.target_date,
            goal_type=goal.goal_type,
            priority=goal.priority,
            progress_percent=goal.progress_percent,
            is_achieved=goal.is_achieved,
            currency=goal.currency
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating goal: {str(e)}")

@router.get("/goals", response_model=List[GoalResponse])
async def get_user_goals(
    user_id: str = Query(..., description="User ID"),
    active_only: bool = Query(True, description="Return only active goals"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get all goals for a user"""
    try:
        goals = await db_service.get_user_goals(uuid.UUID(user_id), active_only)
        
        return [
            GoalResponse(
                id=str(g.id),
                name=g.name,
                description=g.description,
                target_amount=float(g.target_amount),
                current_amount=float(g.current_amount),
                target_date=g.target_date,
                goal_type=g.goal_type,
                priority=g.priority,
                progress_percent=g.progress_percent,
                is_achieved=g.is_achieved,
                currency=g.currency
            ) for g in goals
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving goals: {str(e)}")

@router.put("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str = Path(..., description="Goal ID"),
    goal_data: GoalUpdate = ...,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Update a goal"""
    try:
        update_dict = goal_data.dict(exclude_unset=True)
        
        goal = await db_service.update_goal(uuid.UUID(goal_id), update_dict)
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        return GoalResponse(
            id=str(goal.id),
            name=goal.name,
            description=goal.description,
            target_amount=float(goal.target_amount),
            current_amount=float(goal.current_amount),
            target_date=goal.target_date,
            goal_type=goal.goal_type,
            priority=goal.priority,
            progress_percent=goal.progress_percent,
            is_achieved=goal.is_achieved,
            currency=goal.currency
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating goal: {str(e)}")

@router.post("/goals/{goal_id}/contribute")
async def contribute_to_goal(
    goal_id: str = Path(..., description="Goal ID"),
    contribution: float = Query(..., description="Contribution amount"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Make a contribution to a goal"""
    try:
        goal = await db_service.update_goal_progress(uuid.UUID(goal_id), Decimal(str(contribution)))
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        return {
            "message": f"Contribution of {contribution} added successfully",
            "goal_id": goal_id,
            "new_amount": float(goal.current_amount),
            "progress_percent": goal.progress_percent,
            "is_achieved": goal.is_achieved
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding contribution: {str(e)}")

@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: str = Path(..., description="Goal ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Delete a goal (soft delete)"""
    try:
        success = await db_service.delete_goal(uuid.UUID(goal_id))
        if not success:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        return {"message": "Goal deleted successfully", "goal_id": goal_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting goal: {str(e)}")

# =============== OVERVIEW ENDPOINTS ===============

@router.get("/overview", response_model=FinancialOverviewResponse)
async def get_financial_overview(
    user_id: str = Query(..., description="User ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get comprehensive financial overview"""
    try:
        overview = await db_service.get_financial_overview(uuid.UUID(user_id))
        
        return FinancialOverviewResponse(
            portfolio=PortfolioPerformanceResponse(**overview['portfolio']),
            cash_balance=overview['cash_balance'],
            net_worth=overview['net_worth'],
            recent_transactions=overview['recent_transactions'],
            expense_summary=overview['expense_summary'],
            goals=overview['goals'],
            accounts_count=overview['accounts_count'],
            goals_count=overview['goals_count']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating financial overview: {str(e)}")

# =============== DEMO DATA ENDPOINTS ===============

@router.post("/demo/create-users")
async def create_demo_users(
    db_service: DatabaseService = Depends(get_db_service)
):
    """Create demo users for testing"""
    try:
        demo_users = []
        
        # Demo User 1 - Conservative Investor
        user1_data = {
            'id': uuid.uuid4(),
            'email': 'conservative@finvoice.com',
            'hashed_password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'full_name': 'Rajesh Kumar',
            'risk_tolerance': 'conservative',
            'currency_preference': 'INR',
            'annual_income': 850000.0
        }
        
        user1 = await db_service.create_user(user1_data)
        demo_users.append({
            'id': str(user1.id),
            'email': user1.email,
            'full_name': user1.full_name,
            'credentials': 'conservative@finvoice.com / password123'
        })
        
        # Demo User 2 - Aggressive Investor
        user2_data = {
            'id': uuid.uuid4(),
            'email': 'aggressive@finvoice.com',
            'hashed_password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'full_name': 'Priya Sharma',
            'risk_tolerance': 'aggressive',
            'currency_preference': 'INR',
            'annual_income': 1250000.0
        }
        
        user2 = await db_service.create_user(user2_data)
        demo_users.append({
            'id': str(user2.id),
            'email': user2.email,
            'full_name': user2.full_name,
            'credentials': 'aggressive@finvoice.com / password123'
        })
        
        return {
            "message": "Demo users created successfully",
            "users": demo_users
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating demo users: {str(e)}")

@router.post("/demo/clear")
async def clear_demo_data(
    user_id: str = Query(..., description="User ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Clear all demo data for a user"""
    try:
        user_uuid = uuid.UUID(user_id)
        
        # First delete transactions to avoid foreign key constraints
        transactions = await db_service.get_transactions(user_uuid, limit=1000)
        for transaction in transactions:
            await db_service.delete_transaction(transaction.id)
        
        # Get all holdings and mark them as inactive
        holdings = await db_service.get_user_holdings(user_uuid, active_only=False)
        for holding in holdings:
            await db_service.delete_holding(holding.id)
        
        # Get all accounts and delete them
        accounts = await db_service.get_user_accounts(user_uuid)
        for account in accounts:
            await db_service.delete_account(account.id)
        
        # Get all goals and delete them
        goals = await db_service.get_user_goals(user_uuid, active_only=False)
        for goal in goals:
            await db_service.delete_goal(goal.id)
        
        return {
            "message": f"Demo data cleared successfully for user {user_id}",
            "transactions_deleted": len(transactions),
            "holdings_deleted": len(holdings),
            "accounts_deleted": len(accounts),
            "goals_deleted": len(goals)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing demo data: {str(e)}")

@router.post("/demo/populate")
async def populate_demo_data(
    user_id: str = Query(..., description="User ID"),
    db_service: DatabaseService = Depends(get_db_service)
):
    """Populate demo data for testing"""
    try:
        user_uuid = uuid.UUID(user_id)
        
        # Get user to determine portfolio type
        user = await db_service.get_user(user_uuid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create demo accounts
        checking_account = await db_service.create_account({
            'id': uuid.uuid4(),
            'user_id': user_uuid,
            'account_type': 'checking',
            'account_name': 'Primary Checking',
            'institution_name': 'HDFC Bank',
            'current_balance': Decimal('45000.00'),
            'currency': 'INR'
        })
        
        savings_account = await db_service.create_account({
            'id': uuid.uuid4(),
            'user_id': user_uuid,
            'account_type': 'savings',
            'account_name': 'Emergency Fund',
            'institution_name': 'ICICI Bank',
            'current_balance': Decimal('185000.00'),
            'currency': 'INR'
        })
        
        # Create transactions based on user profile
        base_transactions = [
            {
                'id': uuid.uuid4(),
                'user_id': user_uuid,
                'account_id': checking_account.id,
                'amount': Decimal('85000.00'),
                'description': 'Salary Credit',
                'category': 'Income',
                'transaction_type': 'credit',
                'transaction_date': datetime.utcnow() - timedelta(days=1),
                'currency': 'INR'
            },
            {
                'id': uuid.uuid4(),
                'user_id': user_uuid,
                'account_id': checking_account.id,
                'amount': Decimal('-1250.00'),
                'description': 'Grocery Shopping - Big Bazaar',
                'category': 'Food & Dining',
                'transaction_type': 'debit',
                'transaction_date': datetime.utcnow() - timedelta(days=2),
                'currency': 'INR'
            },
            {
                'id': uuid.uuid4(),
                'user_id': user_uuid,
                'account_id': checking_account.id,
                'amount': Decimal('-18000.00'),
                'description': 'Apartment Rent',
                'category': 'Housing',
                'transaction_type': 'debit',
                'transaction_date': datetime.utcnow() - timedelta(days=3),
                'currency': 'INR'
            },
            {
                'id': uuid.uuid4(),
                'user_id': user_uuid,
                'account_id': checking_account.id,
                'amount': Decimal('-750.00'),
                'description': 'Metro Card Recharge',
                'category': 'Transportation',
                'transaction_type': 'debit',
                'transaction_date': datetime.utcnow() - timedelta(days=4),
                'currency': 'INR'
            }
        ]
        
        for txn_data in base_transactions:
            await db_service.create_transaction(txn_data)
        
        # Create holdings based on risk profile
        if user.risk_tolerance == 'conservative':
            holdings_data = [
                {
                    'id': uuid.uuid4(),
                    'user_id': user_uuid,
                    'symbol': 'RELIANCE',
                    'name': 'Reliance Industries Limited',
                    'asset_type': 'stock',
                    'quantity': Decimal('25'),
                    'average_price': Decimal('2480.00'),
                    'current_price': Decimal('2520.00'),
                    'purchase_date': datetime.utcnow() - timedelta(days=45),
                    'purchase_value': Decimal('62000.00'),
                    'current_value': Decimal('63000.00'),
                    'currency': 'INR'
                },
                {
                    'id': uuid.uuid4(),
                    'user_id': user_uuid,
                    'symbol': 'HDFCBANK',
                    'name': 'HDFC Bank Limited',
                    'asset_type': 'stock',
                    'quantity': Decimal('40'),
                    'average_price': Decimal('1620.00'),
                    'current_price': Decimal('1645.00'),
                    'purchase_date': datetime.utcnow() - timedelta(days=30),
                    'purchase_value': Decimal('64800.00'),
                    'current_value': Decimal('65800.00'),
                    'currency': 'INR'
                },
                {
                    'id': uuid.uuid4(),
                    'user_id': user_uuid,
                    'symbol': 'GOLDBEES',
                    'name': 'Nippon India ETF Gold BeES',
                    'asset_type': 'etf',
                    'quantity': Decimal('150'),
                    'average_price': Decimal('54.20'),
                    'current_price': Decimal('55.80'),
                    'purchase_date': datetime.utcnow() - timedelta(days=60),
                    'purchase_value': Decimal('8130.00'),
                    'current_value': Decimal('8370.00'),
                    'currency': 'INR'
                }
            ]
        else:  # aggressive
            holdings_data = [
                {
                    'id': uuid.uuid4(),
                    'user_id': user_uuid,
                    'symbol': 'TCS',
                    'name': 'Tata Consultancy Services',
                    'asset_type': 'stock',
                    'quantity': Decimal('35'),
                    'average_price': Decimal('3580.00'),
                    'current_price': Decimal('3720.00'),
                    'purchase_date': datetime.utcnow() - timedelta(days=20),
                    'purchase_value': Decimal('125300.00'),
                    'current_value': Decimal('130200.00'),
                    'currency': 'INR'
                },
                {
                    'id': uuid.uuid4(),
                    'user_id': user_uuid,
                    'symbol': 'INFY',
                    'name': 'Infosys Limited',
                    'asset_type': 'stock',
                    'quantity': Decimal('60'),
                    'average_price': Decimal('1485.00'),
                    'current_price': Decimal('1520.00'),
                    'purchase_date': datetime.utcnow() - timedelta(days=25),
                    'purchase_value': Decimal('89100.00'),
                    'current_value': Decimal('91200.00'),
                    'currency': 'INR'
                },
                {
                    'id': uuid.uuid4(),
                    'user_id': user_uuid,
                    'symbol': 'NIFTYBEES',
                    'name': 'Nippon India ETF Nifty BeES',
                    'asset_type': 'etf',
                    'quantity': Decimal('250'),
                    'average_price': Decimal('242.50'),
                    'current_price': Decimal('248.75'),
                    'purchase_date': datetime.utcnow() - timedelta(days=15),
                    'purchase_value': Decimal('60625.00'),
                    'current_value': Decimal('62187.50'),
                    'currency': 'INR'
                },
                {
                    'id': uuid.uuid4(),
                    'user_id': user_uuid,
                    'symbol': 'ADANIGREEN',
                    'name': 'Adani Green Energy Limited',
                    'asset_type': 'stock',
                    'quantity': Decimal('75'),
                    'average_price': Decimal('920.00'),
                    'current_price': Decimal('980.00'),
                    'purchase_date': datetime.utcnow() - timedelta(days=35),
                    'purchase_value': Decimal('69000.00'),
                    'current_value': Decimal('73500.00'),
                    'currency': 'INR'
                }
            ]
        
        for holding_data in holdings_data:
            # Calculate P&L for each holding
            purchase_value = holding_data['quantity'] * holding_data['average_price']
            current_value = holding_data['quantity'] * holding_data['current_price']
            unrealized_pnl = current_value - purchase_value
            unrealized_pnl_percent = (unrealized_pnl / purchase_value) * 100 if purchase_value > 0 else 0
            
            # Add calculated values
            holding_data['unrealized_pnl'] = unrealized_pnl
            holding_data['unrealized_pnl_percent'] = float(unrealized_pnl_percent)
            
            await db_service.create_holding(holding_data)
        
        # Create goals based on risk profile
        if user.risk_tolerance == 'conservative':
            goals_data = [
                {
                    'id': uuid.uuid4(),
                    'user_id': user_uuid,
                    'name': 'Emergency Fund',
                    'description': '8 months of expenses as safety net',
                    'target_amount': Decimal('400000.00'),
                    'current_amount': Decimal('185000.00'),
                    'target_date': datetime.utcnow() + timedelta(days=365),
                    'goal_type': 'emergency',
                    'priority': 'high',
                    'progress_percent': 46.25,
                    'currency': 'INR'
                },
                {
                    'id': uuid.uuid4(),
                    'user_id': user_uuid,
                    'name': 'Fixed Deposit',
                    'description': 'Safe investment for stable returns',
                    'target_amount': Decimal('500000.00'),
                    'current_amount': Decimal('120000.00'),
                    'target_date': datetime.utcnow() + timedelta(days=730),
                    'goal_type': 'investment',
                    'priority': 'medium',
                    'progress_percent': 24.0,
                    'currency': 'INR'
                }
            ]
        else:  # aggressive
            goals_data = [
                {
                    'id': uuid.uuid4(),
                    'user_id': user_uuid,
                    'name': 'Wealth Building',
                    'description': 'Aggressive growth portfolio',
                    'target_amount': Decimal('2000000.00'),
                    'current_amount': Decimal('350000.00'),
                    'target_date': datetime.utcnow() + timedelta(days=1460),  # 4 years
                    'goal_type': 'investment',
                    'priority': 'high',
                    'progress_percent': 17.5,
                    'currency': 'INR'
                },
                {
                    'id': uuid.uuid4(),
                    'user_id': user_uuid,
                    'name': 'Startup Investment',
                    'description': 'High-risk high-reward opportunity',
                    'target_amount': Decimal('800000.00'),
                    'current_amount': Decimal('150000.00'),
                    'target_date': datetime.utcnow() + timedelta(days=1095),  # 3 years
                    'goal_type': 'business',
                    'priority': 'medium',
                    'progress_percent': 18.75,
                    'currency': 'INR'
                }
            ]
        
        for goal_data in goals_data:
            await db_service.create_goal(goal_data)
        
        return {
            "message": f"Demo data populated successfully for {user.full_name} ({user.risk_tolerance} profile)",
            "user_profile": user.risk_tolerance,
            "accounts_created": 2,
            "transactions_created": len(base_transactions),
            "holdings_created": len(holdings_data),
            "goals_created": len(goals_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error populating demo data: {str(e)}")
