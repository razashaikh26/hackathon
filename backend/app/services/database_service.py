"""
Database service layer for FinVoice application
Handles all CRUD operations for Neon PostgreSQL database
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, desc, func
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import uuid
from decimal import Decimal

from app.db.models import (
    User, Account, Transaction, Holding, 
    PortfolioSnapshot, Goal, AuditLog, BlockchainLog
)
from app.core.database import get_async_session
import structlog

logger = structlog.get_logger()

class DatabaseService:
    """Comprehensive database service for all financial data operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    # =============== USER OPERATIONS ===============
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: uuid.UUID, user_data: Dict[str, Any]) -> Optional[User]:
        """Update user data"""
        await self.session.execute(
            update(User).where(User.id == user_id).values(**user_data)
        )
        await self.session.commit()
        return await self.get_user(user_id)

    # =============== ACCOUNT OPERATIONS ===============
    
    async def create_account(self, account_data: Dict[str, Any]) -> Account:
        """Create a new account"""
        account = Account(**account_data)
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account
    
    async def get_user_accounts(self, user_id: uuid.UUID) -> List[Account]:
        """Get all accounts for a user"""
        result = await self.session.execute(
            select(Account).where(Account.user_id == user_id)
        )
        return result.scalars().all()
    
    async def get_account(self, account_id: uuid.UUID) -> Optional[Account]:
        """Get account by ID"""
        result = await self.session.execute(
            select(Account).where(Account.id == account_id)
        )
        return result.scalar_one_or_none()
    
    async def update_account_balance(self, account_id: uuid.UUID, new_balance: Decimal) -> Account:
        """Update account balance"""
        await self.session.execute(
            update(Account)
            .where(Account.id == account_id)
            .values(current_balance=new_balance, updated_at=datetime.utcnow())
        )
        await self.session.commit()
        return await self.get_account(account_id)
    
    async def delete_account(self, account_id: uuid.UUID) -> bool:
        """Delete an account"""
        await self.session.execute(
            delete(Account).where(Account.id == account_id)
        )
        await self.session.commit()
        return True

    # =============== TRANSACTION OPERATIONS ===============
    
    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Transaction:
        """Create a new transaction"""
        transaction = Transaction(**transaction_data)
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction
    
    async def get_transactions(
        self, 
        user_id: uuid.UUID, 
        account_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Transaction]:
        """Get transactions with filters"""
        query = select(Transaction).where(Transaction.user_id == user_id)
        
        if account_id:
            query = query.where(Transaction.account_id == account_id)
        if start_date:
            query = query.where(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)
        if category:
            query = query.where(Transaction.category == category)
        
        query = query.order_by(desc(Transaction.transaction_date))
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_transaction(self, transaction_id: uuid.UUID) -> Optional[Transaction]:
        """Get transaction by ID"""
        result = await self.session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()
    
    async def update_transaction(self, transaction_id: uuid.UUID, transaction_data: Dict[str, Any]) -> Optional[Transaction]:
        """Update transaction"""
        await self.session.execute(
            update(Transaction)
            .where(Transaction.id == transaction_id)
            .values(**transaction_data)
        )
        await self.session.commit()
        return await self.get_transaction(transaction_id)
    
    async def delete_transaction(self, transaction_id: uuid.UUID) -> bool:
        """Delete transaction"""
        await self.session.execute(
            delete(Transaction).where(Transaction.id == transaction_id)
        )
        await self.session.commit()
        return True
    
    async def get_expense_summary(
        self, 
        user_id: uuid.UUID, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get expense summary by category"""
        result = await self.session.execute(
            select(
                Transaction.category,
                func.sum(Transaction.amount).label('total_amount'),
                func.count(Transaction.id).label('transaction_count')
            )
            .where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.amount < 0,  # Expenses are negative
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            )
            .group_by(Transaction.category)
        )
        
        categories = []
        total_expenses = Decimal('0')
        
        for row in result.fetchall():
            amount = abs(row.total_amount)
            total_expenses += amount
            categories.append({
                'category': row.category,
                'amount': float(amount),
                'transaction_count': row.transaction_count
            })
        
        # Calculate percentages
        for category in categories:
            if total_expenses > 0:
                category['percentage'] = (category['amount'] / float(total_expenses)) * 100
            else:
                category['percentage'] = 0
        
        return {
            'categories': categories,
            'total_expenses': float(total_expenses),
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        }

    # =============== HOLDINGS OPERATIONS ===============
    
    async def create_holding(self, holding_data: Dict[str, Any]) -> Holding:
        """Create a new holding"""
        holding = Holding(**holding_data)
        self.session.add(holding)
        await self.session.commit()
        await self.session.refresh(holding)
        return holding
    
    async def get_user_holdings(self, user_id: uuid.UUID, active_only: bool = True) -> List[Holding]:
        """Get all holdings for a user"""
        query = select(Holding).where(Holding.user_id == user_id)
        if active_only:
            query = query.where(Holding.is_active == True)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_holding(self, holding_id: uuid.UUID) -> Optional[Holding]:
        """Get holding by ID"""
        result = await self.session.execute(
            select(Holding).where(Holding.id == holding_id)
        )
        return result.scalar_one_or_none()
    
    async def get_holding_by_symbol(self, user_id: uuid.UUID, symbol: str) -> Optional[Holding]:
        """Get holding by symbol"""
        result = await self.session.execute(
            select(Holding).where(
                and_(
                    Holding.user_id == user_id,
                    Holding.symbol == symbol,
                    Holding.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update_holding(self, holding_id: uuid.UUID, holding_data: Dict[str, Any]) -> Optional[Holding]:
        """Update holding"""
        await self.session.execute(
            update(Holding)
            .where(Holding.id == holding_id)
            .values(**holding_data, updated_at=datetime.utcnow())
        )
        await self.session.commit()
        return await self.get_holding(holding_id)
    
    async def update_holding_prices(self, user_id: uuid.UUID, price_updates: Dict[str, Decimal]) -> List[Holding]:
        """Batch update holding prices"""
        holdings = await self.get_user_holdings(user_id)
        updated_holdings = []
        
        for holding in holdings:
            if holding.symbol in price_updates:
                new_price = price_updates[holding.symbol]
                current_value = holding.quantity * new_price
                unrealized_pnl = current_value - holding.purchase_value
                unrealized_pnl_percent = (unrealized_pnl / holding.purchase_value) * 100 if holding.purchase_value > 0 else 0
                
                await self.update_holding(holding.id, {
                    'current_price': new_price,
                    'current_value': current_value,
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pnl_percent': float(unrealized_pnl_percent)
                })
                updated_holdings.append(holding)
        
        return updated_holdings
    
    async def delete_holding(self, holding_id: uuid.UUID) -> bool:
        """Delete holding (soft delete)"""
        await self.session.execute(
            update(Holding)
            .where(Holding.id == holding_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        await self.session.commit()
        return True

    # =============== PORTFOLIO OPERATIONS ===============
    
    async def create_portfolio_snapshot(self, snapshot_data: Dict[str, Any]) -> PortfolioSnapshot:
        """Create a portfolio snapshot"""
        snapshot = PortfolioSnapshot(**snapshot_data)
        self.session.add(snapshot)
        await self.session.commit()
        await self.session.refresh(snapshot)
        return snapshot
    
    async def get_latest_portfolio_snapshot(self, user_id: uuid.UUID) -> Optional[PortfolioSnapshot]:
        """Get latest portfolio snapshot"""
        result = await self.session.execute(
            select(PortfolioSnapshot)
            .where(PortfolioSnapshot.user_id == user_id)
            .order_by(desc(PortfolioSnapshot.snapshot_date))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_portfolio_snapshots(
        self, 
        user_id: uuid.UUID, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 30
    ) -> List[PortfolioSnapshot]:
        """Get portfolio snapshots for performance tracking"""
        query = select(PortfolioSnapshot).where(PortfolioSnapshot.user_id == user_id)
        
        if start_date:
            query = query.where(PortfolioSnapshot.snapshot_date >= start_date)
        if end_date:
            query = query.where(PortfolioSnapshot.snapshot_date <= end_date)
        
        query = query.order_by(desc(PortfolioSnapshot.snapshot_date)).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def calculate_portfolio_performance(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Calculate portfolio performance metrics"""
        holdings = await self.get_user_holdings(user_id)
        
        total_value = sum(h.current_value for h in holdings if h.current_value)
        total_invested = sum(h.purchase_value for h in holdings)
        total_pnl = total_value - total_invested
        total_pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        # Get snapshots for performance tracking
        week_ago = datetime.utcnow() - timedelta(days=7)
        snapshots = await self.get_portfolio_snapshots(user_id, week_ago)
        
        week_change = 0
        week_change_percent = 0
        if len(snapshots) >= 2:
            week_old_value = snapshots[-1].total_value
            week_change = total_value - float(week_old_value)
            week_change_percent = (week_change / float(week_old_value) * 100) if week_old_value > 0 else 0
        
        return {
            'total_value': float(total_value),
            'total_invested': float(total_invested),
            'total_pnl': float(total_pnl),
            'total_pnl_percent': float(total_pnl_percent),
            'week_change': float(week_change),
            'week_change_percent': float(week_change_percent),
            'holdings_count': len(holdings),
            'holdings': [
                {
                    'symbol': h.symbol,
                    'name': h.name,
                    'quantity': float(h.quantity),
                    'current_price': float(h.current_price) if h.current_price else 0,
                    'current_value': float(h.current_value) if h.current_value else 0,
                    'unrealized_pnl': float(h.unrealized_pnl) if h.unrealized_pnl else 0,
                    'unrealized_pnl_percent': h.unrealized_pnl_percent or 0
                } for h in holdings
            ]
        }

    # =============== GOALS OPERATIONS ===============
    
    async def create_goal(self, goal_data: Dict[str, Any]) -> Goal:
        """Create a new financial goal"""
        goal = Goal(**goal_data)
        self.session.add(goal)
        await self.session.commit()
        await self.session.refresh(goal)
        return goal
    
    async def get_user_goals(self, user_id: uuid.UUID, active_only: bool = True) -> List[Goal]:
        """Get all goals for a user"""
        query = select(Goal).where(Goal.user_id == user_id)
        if active_only:
            query = query.where(Goal.is_active == True)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_goal(self, goal_id: uuid.UUID) -> Optional[Goal]:
        """Get goal by ID"""
        result = await self.session.execute(
            select(Goal).where(Goal.id == goal_id)
        )
        return result.scalar_one_or_none()
    
    async def update_goal(self, goal_id: uuid.UUID, goal_data: Dict[str, Any]) -> Optional[Goal]:
        """Update goal"""
        await self.session.execute(
            update(Goal)
            .where(Goal.id == goal_id)
            .values(**goal_data, updated_at=datetime.utcnow())
        )
        await self.session.commit()
        return await self.get_goal(goal_id)
    
    async def update_goal_progress(self, goal_id: uuid.UUID, contribution: Decimal) -> Optional[Goal]:
        """Add contribution to goal"""
        goal = await self.get_goal(goal_id)
        if not goal:
            return None
        
        new_amount = goal.current_amount + contribution
        progress_percent = (new_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
        
        is_achieved = new_amount >= goal.target_amount
        achieved_date = datetime.utcnow() if is_achieved and not goal.is_achieved else goal.achieved_date
        
        return await self.update_goal(goal_id, {
            'current_amount': new_amount,
            'progress_percent': float(progress_percent),
            'is_achieved': is_achieved,
            'achieved_date': achieved_date
        })
    
    async def delete_goal(self, goal_id: uuid.UUID) -> bool:
        """Delete goal (soft delete)"""
        await self.session.execute(
            update(Goal)
            .where(Goal.id == goal_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        await self.session.commit()
        return True

    # =============== AUDIT LOG OPERATIONS ===============
    
    async def create_audit_log(self, audit_data: Dict[str, Any]) -> AuditLog:
        """Create audit log entry"""
        audit_log = AuditLog(**audit_data)
        self.session.add(audit_log)
        await self.session.commit()
        await self.session.refresh(audit_log)
        return audit_log
    
    async def get_user_audit_logs(
        self, 
        user_id: uuid.UUID, 
        action_type: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs for user"""
        query = select(AuditLog).where(AuditLog.user_id == user_id)
        
        if action_type:
            query = query.where(AuditLog.action_type == action_type)
        
        query = query.order_by(desc(AuditLog.timestamp)).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    # =============== BLOCKCHAIN LOG OPERATIONS ===============
    
    async def create_blockchain_log(self, blockchain_data: Dict[str, Any]) -> BlockchainLog:
        """Create blockchain log entry"""
        blockchain_log = BlockchainLog(**blockchain_data)
        self.session.add(blockchain_log)
        await self.session.commit()
        await self.session.refresh(blockchain_log)
        return blockchain_log
    
    async def get_blockchain_logs(
        self, 
        user_id: uuid.UUID, 
        log_type: Optional[str] = None
    ) -> List[BlockchainLog]:
        """Get blockchain logs for user"""
        query = select(BlockchainLog).where(BlockchainLog.user_id == user_id)
        
        if log_type:
            query = query.where(BlockchainLog.log_type == log_type)
        
        query = query.order_by(desc(BlockchainLog.created_at))
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_blockchain_log_status(
        self, 
        transaction_hash: str, 
        status: str, 
        block_number: Optional[int] = None
    ) -> Optional[BlockchainLog]:
        """Update blockchain log status"""
        update_data = {'status': status}
        if block_number:
            update_data['block_number'] = block_number
            update_data['confirmed_at'] = datetime.utcnow()
        
        await self.session.execute(
            update(BlockchainLog)
            .where(BlockchainLog.transaction_hash == transaction_hash)
            .values(**update_data)
        )
        await self.session.commit()
        
        result = await self.session.execute(
            select(BlockchainLog).where(BlockchainLog.transaction_hash == transaction_hash)
        )
        return result.scalar_one_or_none()

    # =============== ANALYTICS OPERATIONS ===============
    
    async def get_financial_overview(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get comprehensive financial overview"""
        # Get portfolio performance
        portfolio_data = await self.calculate_portfolio_performance(user_id)
        
        # Get recent transactions
        recent_transactions = await self.get_transactions(user_id, limit=10)
        
        # Get expense summary for current month
        start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        expense_summary = await self.get_expense_summary(user_id, start_of_month, end_of_month)
        
        # Get active goals
        goals = await self.get_user_goals(user_id)
        
        # Calculate net worth (simplified)
        accounts = await self.get_user_accounts(user_id)
        cash_balance = sum(float(acc.current_balance) for acc in accounts)
        
        return {
            'portfolio': portfolio_data,
            'cash_balance': cash_balance,
            'net_worth': portfolio_data['total_value'] + cash_balance,
            'recent_transactions': [
                {
                    'id': str(t.id),
                    'description': t.description,
                    'amount': float(t.amount),
                    'category': t.category,
                    'date': t.transaction_date.isoformat(),
                    'currency': t.currency
                } for t in recent_transactions
            ],
            'expense_summary': expense_summary,
            'goals': [
                {
                    'id': str(g.id),
                    'name': g.name,
                    'target_amount': float(g.target_amount),
                    'current_amount': float(g.current_amount),
                    'progress_percent': g.progress_percent,
                    'target_date': g.target_date.isoformat(),
                    'goal_type': g.goal_type
                } for g in goals
            ],
            'accounts_count': len(accounts),
            'goals_count': len(goals)
        }

# Dependency function
async def get_database_service() -> DatabaseService:
    """Get database service instance"""
    async with get_async_session() as session:
        return DatabaseService(session)
