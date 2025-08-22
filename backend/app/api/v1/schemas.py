from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class AnalysisSection(BaseModel):
    actionable_suggestions: List[str] = Field(..., description="List of actionable suggestions")
    rationale: str = Field(..., description="Explanation of the analysis")
    severity_level: SeverityLevel = Field(..., description="Severity level of the findings")
    confidence: float = Field(..., ge=0, le=100, description="Confidence percentage (0-100)")
    alternatives: List[str] = Field(default_factory=list, description="Alternative strategies")

class UserProfile(BaseModel):
    user_id: str
    name: str
    age: int
    annual_income: float
    risk_tolerance: str
    investment_experience: str
    financial_goals: List[str]

class Expense(BaseModel):
    id: str
    amount: float
    category: str
    subcategory: Optional[str] = None
    description: str
    date: datetime
    merchant: Optional[str] = None
    is_recurring: bool = False

class Account(BaseModel):
    id: str
    account_type: str
    institution_name: str
    balance: float
    available_balance: Optional[float] = None
    interest_rate: Optional[float] = None
    credit_limit: Optional[float] = None

class Investment(BaseModel):
    id: str
    symbol: str
    name: str
    asset_type: str
    quantity: float
    purchase_price: float
    current_price: float
    total_value: float
    gain_loss: float
    gain_loss_percentage: float

class CreditCard(BaseModel):
    id: str
    name: str
    current_balance: float
    credit_limit: float
    utilization_percentage: float
    apr: float
    minimum_payment: float
    due_date: datetime
    rewards_type: Optional[str] = None

class Insurance(BaseModel):
    id: str
    insurance_type: str
    provider: str
    coverage_amount: float
    premium: float
    premium_frequency: str
    expiry_date: datetime
    beneficiaries: List[str] = []

class Loan(BaseModel):
    id: str
    loan_type: str
    lender: str
    principal_amount: float
    outstanding_balance: float
    interest_rate: float
    monthly_payment: float
    remaining_term_months: int
    next_payment_date: datetime

class Goal(BaseModel):
    id: str
    name: str
    target_amount: float
    current_amount: float
    target_date: datetime
    priority: str
    goal_type: str

class MarketData(BaseModel):
    timestamp: datetime
    indices: Dict[str, float]
    forex_rates: Dict[str, float]
    commodity_prices: Dict[str, float]
    crypto_prices: Dict[str, float]
    market_sentiment: str
    volatility_index: float

class FinancialDataInput(BaseModel):
    user: UserProfile
    expenses: List[Expense]
    accounts: List[Account]
    investments: List[Investment]
    credit_cards: List[CreditCard]
    insurance: List[Insurance]
    loans: List[Loan]
    goals: List[Goal]
    market_data: MarketData

class FinancialAnalysisResponse(BaseModel):
    expense_analysis: AnalysisSection
    portfolio_management: AnalysisSection
    debt_loan_tracking: AnalysisSection
    insurance_management: AnalysisSection
    goal_planning: AnalysisSection
    credit_card_optimization: AnalysisSection
    automated_monitoring: AnalysisSection
    security: AnalysisSection
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class VoiceInput(BaseModel):
    audio_data: str = Field(..., description="Base64 encoded audio data")
    user_id: str
    language: str = "en-US"

class VoiceResponse(BaseModel):
    transcription: str
    analysis: Optional[FinancialAnalysisResponse] = None
    confidence: float
