from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, JSON, ForeignKey, Index, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # User profile data
    date_of_birth = Column(DateTime)
    phone_number = Column(String(20))
    risk_tolerance = Column(String(20))  # conservative, moderate, aggressive
    investment_experience = Column(String(20))  # beginner, intermediate, expert
    annual_income = Column(DECIMAL(15, 2))
    
    # Preferences
    preferred_language = Column(String(10), default='en-IN')
    currency_preference = Column(String(3), default='INR')
    
    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    holdings = relationship("Holding", back_populates="user", cascade="all, delete-orphan")
    portfolio_snapshots = relationship("PortfolioSnapshot", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    blockchain_logs = relationship("BlockchainLog", back_populates="user", cascade="all, delete-orphan")

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_type = Column(String(20), nullable=False)  # checking, savings, investment, credit
    account_name = Column(String(255), nullable=False)
    institution_name = Column(String(255))
    account_number_hash = Column(String(64))  # Hashed for security
    current_balance = Column(DECIMAL(15, 2), default=0.0)
    available_balance = Column(DECIMAL(15, 2), default=0.0)
    currency = Column(String(3), default='INR')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # External API integration
    plaid_account_id = Column(String(255))
    plaid_item_id = Column(String(255))
    
    # Indexes
    __table_args__ = (
        Index('idx_user_accounts', 'user_id'),
        Index('idx_account_type', 'account_type'),
    )
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    
    amount = Column(DECIMAL(15, 2), nullable=False)
    description = Column(String(500), nullable=False)
    category = Column(String(100))
    subcategory = Column(String(100))
    transaction_type = Column(String(10), nullable=False)  # debit, credit
    transaction_date = Column(DateTime, nullable=False)
    currency = Column(String(3), default='INR')
    
    # External API data
    plaid_transaction_id = Column(String(255))
    merchant_name = Column(String(255))
    location = Column(JSON)
    
    # AI Analysis
    is_anomaly = Column(Boolean, default=False)
    confidence_score = Column(Float)
    predicted_category = Column(String(100))
    ai_analysis = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_user_transactions', 'user_id'),
        Index('idx_transaction_date', 'transaction_date'),
        Index('idx_category', 'category'),
    )
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")

class Holding(Base):
    __tablename__ = "holdings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    symbol = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(20), nullable=False)  # stock, etf, mutual_fund, bond, crypto
    exchange = Column(String(10))  # NSE, BSE, etc.
    quantity = Column(DECIMAL(15, 6), nullable=False)
    average_price = Column(DECIMAL(15, 2), nullable=False)
    current_price = Column(DECIMAL(15, 2))
    currency = Column(String(3), default='INR')
    
    # Purchase details
    purchase_date = Column(DateTime, nullable=False)
    purchase_value = Column(DECIMAL(15, 2), nullable=False)
    
    # Current metrics (updated periodically)
    current_value = Column(DECIMAL(15, 2))
    unrealized_pnl = Column(DECIMAL(15, 2))
    unrealized_pnl_percent = Column(Float)
    day_change = Column(DECIMAL(15, 2))
    day_change_percent = Column(Float)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_user_holdings', 'user_id'),
        Index('idx_symbol', 'symbol'),
        Index('idx_asset_type', 'asset_type'),
    )
    
    # Relationships
    user = relationship("User", back_populates="holdings")

class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Portfolio metrics
    total_value = Column(DECIMAL(15, 2), nullable=False)
    total_invested = Column(DECIMAL(15, 2), nullable=False)
    total_pnl = Column(DECIMAL(15, 2), nullable=False)
    total_pnl_percent = Column(Float, nullable=False)
    day_change = Column(DECIMAL(15, 2))
    day_change_percent = Column(Float)
    
    # Risk metrics
    portfolio_beta = Column(Float)
    sharpe_ratio = Column(Float)
    volatility = Column(Float)
    max_drawdown = Column(Float)
    
    # Allocation breakdown
    allocation_breakdown = Column(JSON)  # {"equity": 70, "debt": 20, "gold": 10}
    sector_breakdown = Column(JSON)
    holdings_summary = Column(JSON)
    
    # Metadata
    snapshot_date = Column(DateTime(timezone=True), server_default=func.now())
    market_status = Column(String(20))  # open, closed, pre_market, after_market
    
    # Blockchain reference
    blockchain_hash = Column(String(66))  # Transaction hash for immutable record
    
    # Indexes
    __table_args__ = (
        Index('idx_user_snapshots', 'user_id'),
        Index('idx_snapshot_date', 'snapshot_date'),
    )
    
    # Relationships
    user = relationship("User", back_populates="portfolio_snapshots")

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    target_amount = Column(DECIMAL(15, 2), nullable=False)
    current_amount = Column(DECIMAL(15, 2), default=0.0)
    target_date = Column(DateTime, nullable=False)
    goal_type = Column(String(20), nullable=False)  # emergency, house, education, retirement
    priority = Column(String(10), default='medium')  # low, medium, high
    currency = Column(String(3), default='INR')
    
    # Progress tracking
    monthly_contribution = Column(DECIMAL(15, 2))
    required_monthly_sip = Column(DECIMAL(15, 2))
    progress_percent = Column(Float, default=0.0)
    
    # AI Recommendations
    feasibility_score = Column(Float)
    recommended_strategies = Column(JSON)
    risk_assessment = Column(JSON)
    
    is_achieved = Column(Boolean, default=False)
    achieved_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_user_goals', 'user_id'),
        Index('idx_goal_type', 'goal_type'),
        Index('idx_target_date', 'target_date'),
    )
    
    # Relationships
    user = relationship("User", back_populates="goals")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    action_type = Column(String(50), nullable=False)  # portfolio_view, transaction_add, etc.
    resource_type = Column(String(50))  # portfolio, transaction, goal
    resource_id = Column(String(255))
    
    # Request details
    ip_address = Column(String(45))
    user_agent = Column(Text)
    request_data = Column(JSON)
    response_data = Column(JSON)
    
    # Status
    status = Column(String(20))  # success, error, warning
    error_message = Column(Text)
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    session_id = Column(String(255))
    
    # Indexes
    __table_args__ = (
        Index('idx_user_audit', 'user_id'),
        Index('idx_action_type', 'action_type'),
        Index('idx_timestamp', 'timestamp'),
    )
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class BlockchainLog(Base):
    __tablename__ = "blockchain_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Blockchain details
    transaction_hash = Column(String(66), nullable=False, unique=True)
    block_number = Column(Integer)
    data_hash = Column(String(64), nullable=False)  # Hash of original data
    log_type = Column(String(50), nullable=False)  # portfolio_snapshot, transaction_summary
    
    # Reference to original data
    reference_table = Column(String(50))  # portfolio_snapshots, transactions
    reference_id = Column(UUID(as_uuid=True))
    
    # Network details
    network = Column(String(20), default='polygon_amoy')
    gas_used = Column(Integer)
    gas_price = Column(DECIMAL(20, 0))
    
    # Status
    status = Column(String(20), default='pending')  # pending, confirmed, failed
    confirmation_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    
    # Indexes
    __table_args__ = (
        Index('idx_user_blockchain', 'user_id'),
        Index('idx_tx_hash', 'transaction_hash'),
        Index('idx_log_type', 'log_type'),
        Index('idx_reference', 'reference_table', 'reference_id'),
    )
    
    # Relationships
    user = relationship("User", back_populates="blockchain_logs")
