import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import asyncio
from pathlib import Path

from app.api.v1.schemas import Investment, Expense, Loan, CreditCard
from app.core.config import settings

class MLAnalysisService:
    """
    Machine Learning service for financial analysis
    Provides anomaly detection, risk scoring, and predictive analytics
    """
    
    def __init__(self):
        self.model_path = Path(settings.MODEL_PATH)
        self.models = {}
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained ML models"""
        try:
            # In production, these would be actual trained models
            # For now, we'll create simple models
            self.models['anomaly_detector'] = IsolationForest(contamination=0.1, random_state=42)
            self.models['risk_scorer'] = StandardScaler()
        except Exception as e:
            print(f"Warning: Could not load ML models: {e}")
    
    async def detect_spending_anomalies(self, expense_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalous spending patterns"""
        if len(expense_df) < 10:
            return []
        
        try:
            # Feature engineering
            features = self._extract_spending_features(expense_df)
            
            # Detect anomalies
            anomaly_scores = self.models['anomaly_detector'].fit_predict(features)
            
            # Return anomalous transactions
            anomalies = []
            for idx, score in enumerate(anomaly_scores):
                if score == -1:  # Anomaly
                    anomalies.append({
                        'index': idx,
                        'amount': expense_df.iloc[idx]['amount'],
                        'category': expense_df.iloc[idx]['category'],
                        'date': expense_df.iloc[idx]['date'],
                        'reason': 'Unusual spending pattern detected'
                    })
            
            return anomalies
            
        except Exception as e:
            print(f"Error in anomaly detection: {e}")
            return []
    
    def _extract_spending_features(self, expense_df: pd.DataFrame) -> np.ndarray:
        """Extract features for ML analysis"""
        try:
            # Time-based features
            expense_df['hour'] = expense_df['date'].dt.hour
            expense_df['day_of_week'] = expense_df['date'].dt.dayofweek
            expense_df['month'] = expense_df['date'].dt.month
            
            # Amount features
            expense_df['log_amount'] = np.log1p(expense_df['amount'])
            
            # Category encoding (simple)
            category_encoded = pd.get_dummies(expense_df['category'], prefix='cat')
            
            # Combine features
            features = pd.concat([
                expense_df[['log_amount', 'hour', 'day_of_week', 'month']],
                category_encoded
            ], axis=1)
            
            return features.fillna(0).values
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return np.array([])
    
    async def calculate_portfolio_risk(self, investments: List[Investment]) -> float:
        """Calculate portfolio risk score (0-10 scale)"""
        if not investments:
            return 0.0
        
        try:
            # Calculate diversification score
            asset_types = set(inv.asset_type for inv in investments)
            diversification_score = min(len(asset_types) / 5, 1.0)  # Max score at 5+ asset types
            
            # Calculate concentration risk
            total_value = sum(inv.total_value for inv in investments)
            concentrations = [inv.total_value / total_value for inv in investments]
            max_concentration = max(concentrations)
            concentration_risk = max_concentration  # Higher concentration = higher risk
            
            # Calculate volatility (simplified)
            volatilities = {
                'stock': 0.8,
                'bond': 0.3,
                'etf': 0.6,
                'crypto': 1.0,
                'gold': 0.5,
                'mutual_fund': 0.4
            }
            
            weighted_volatility = sum(
                (inv.total_value / total_value) * volatilities.get(inv.asset_type, 0.5)
                for inv in investments
            )
            
            # Combine factors (0-10 scale)
            risk_score = (
                (1 - diversification_score) * 3 +  # Lack of diversification (0-3)
                concentration_risk * 3 +           # Concentration risk (0-3)
                weighted_volatility * 4            # Volatility risk (0-4)
            )
            
            return min(risk_score, 10.0)
            
        except Exception as e:
            print(f"Error calculating portfolio risk: {e}")
            return 5.0  # Default medium risk
    
    async def analyze_market_correlation(self, investments: List[Investment], market_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze portfolio correlation with market indices"""
        # Simplified correlation analysis
        correlations = {}
        
        for inv in investments:
            if inv.asset_type == 'stock':
                correlations[inv.symbol] = 0.7  # Simplified correlation with market
            elif inv.asset_type == 'bond':
                correlations[inv.symbol] = -0.2  # Negative correlation
            else:
                correlations[inv.symbol] = 0.3   # Low correlation
        
        return correlations
    
    async def calculate_debt_avalanche_savings(self, loans: List[Loan]) -> float:
        """Calculate potential savings using debt avalanche method"""
        if not loans:
            return 0.0
        
        try:
            # Sort by interest rate (highest first)
            sorted_loans = sorted(loans, key=lambda x: x.interest_rate, reverse=True)
            
            # Calculate total minimum payments
            total_minimum = sum(loan.monthly_payment for loan in loans)
            
            # Simplified calculation - assume extra $200/month available
            extra_payment = 200
            total_available = total_minimum + extra_payment
            
            # Calculate payoff time and interest for avalanche method
            avalanche_interest = 0
            remaining_loans = sorted_loans.copy()
            months = 0
            
            while remaining_loans and months < 360:  # Max 30 years
                months += 1
                
                # Apply minimum payments to all loans
                for loan in remaining_loans[:]:
                    balance = loan.outstanding_balance
                    monthly_rate = loan.interest_rate / 100 / 12
                    interest_payment = balance * monthly_rate
                    principal_payment = min(loan.monthly_payment - interest_payment, balance)
                    
                    loan.outstanding_balance -= principal_payment
                    avalanche_interest += interest_payment
                    
                    if loan.outstanding_balance <= 0:
                        remaining_loans.remove(loan)
                
                # Apply extra payment to highest rate loan
                if remaining_loans:
                    highest_rate_loan = remaining_loans[0]
                    extra_principal = min(extra_payment, highest_rate_loan.outstanding_balance)
                    highest_rate_loan.outstanding_balance -= extra_principal
                    
                    if highest_rate_loan.outstanding_balance <= 0:
                        remaining_loans.remove(highest_rate_loan)
            
            # Calculate traditional payoff interest (simplified)
            traditional_interest = sum(
                loan.outstanding_balance * (loan.interest_rate / 100) * (loan.remaining_term_months / 12)
                for loan in loans
            )
            
            savings = max(0, traditional_interest - avalanche_interest)
            return savings
            
        except Exception as e:
            print(f"Error calculating debt avalanche savings: {e}")
            return 0.0
    
    async def calculate_debt_snowball_timeline(self, loans: List[Loan]) -> int:
        """Calculate payoff timeline using debt snowball method"""
        if not loans:
            return 0
        
        try:
            # Sort by balance (smallest first)
            sorted_loans = sorted(loans, key=lambda x: x.outstanding_balance)
            
            # Simplified calculation
            total_payments = sum(loan.monthly_payment for loan in loans)
            total_balance = sum(loan.outstanding_balance for loan in loans)
            avg_rate = sum(loan.interest_rate for loan in loans) / len(loans)
            
            # Estimate payoff time (months)
            monthly_rate = avg_rate / 100 / 12
            if monthly_rate > 0:
                months = np.log(1 + (total_balance * monthly_rate) / total_payments) / np.log(1 + monthly_rate)
                return int(months)
            else:
                return int(total_balance / total_payments)
                
        except Exception as e:
            print(f"Error calculating snowball timeline: {e}")
            return 60  # Default 5 years
    
    async def calculate_credit_card_payoff_time(self, credit_cards: List[CreditCard]) -> int:
        """Calculate credit card payoff time with minimum payments"""
        if not credit_cards:
            return 0
        
        try:
            total_months = 0
            
            for card in credit_cards:
                if card.current_balance <= 0:
                    continue
                
                balance = card.current_balance
                monthly_rate = card.apr / 100 / 12
                min_payment = card.minimum_payment
                
                if min_payment <= balance * monthly_rate:
                    # Minimum payment doesn't cover interest - will never pay off
                    return 999  # Return very high number
                
                # Calculate payoff time
                if monthly_rate > 0:
                    months = -np.log(1 - (balance * monthly_rate) / min_payment) / np.log(1 + monthly_rate)
                    total_months = max(total_months, months)
                else:
                    months = balance / min_payment
                    total_months = max(total_months, months)
            
            return int(total_months)
            
        except Exception as e:
            print(f"Error calculating payoff time: {e}")
            return 60  # Default 5 years
    
    async def assess_market_risk(self, market_data: Dict[str, Any], news_analysis: Dict[str, Any]) -> float:
        """Assess overall market risk (0-10 scale)"""
        try:
            risk_score = 5.0  # Base risk
            
            # Volatility factor
            vix = market_data.get('volatility_index', 20)
            if vix > 30:
                risk_score += 2
            elif vix > 20:
                risk_score += 1
            
            # News sentiment factor
            if news_analysis.get('negative_sentiment', 0) > 0.6:
                risk_score += 1.5
            
            # Economic indicators
            if news_analysis.get('inflation_concerns', False):
                risk_score += 1
            
            if news_analysis.get('geopolitical_risk', False):
                risk_score += 1
            
            return min(risk_score, 10.0)
            
        except Exception as e:
            print(f"Error assessing market risk: {e}")
            return 5.0
    
    async def assess_portfolio_market_risk(self, investments: List[Investment], market_data: Dict[str, Any]) -> float:
        """Assess portfolio-specific market risk"""
        if not investments:
            return 0.0
        
        try:
            # Calculate market exposure
            total_value = sum(inv.total_value for inv in investments)
            market_exposed_value = sum(
                inv.total_value for inv in investments 
                if inv.asset_type in ['stock', 'etf']
            )
            
            market_exposure = market_exposed_value / total_value if total_value > 0 else 0
            
            # Base market risk
            base_risk = await self.assess_market_risk(market_data, {})
            
            # Adjust for portfolio exposure
            portfolio_risk = base_risk * market_exposure
            
            return min(portfolio_risk, 10.0)
            
        except Exception as e:
            print(f"Error assessing portfolio market risk: {e}")
            return 5.0
    
    async def detect_fraud_indicators(self, expenses: List[Expense]) -> List[Dict[str, Any]]:
        """Detect potential fraud indicators in transactions"""
        indicators = []
        
        if not expenses:
            return indicators
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    'amount': exp.amount,
                    'category': exp.category,
                    'date': exp.date,
                    'merchant': exp.merchant or 'Unknown'
                } for exp in expenses
            ])
            
            # Check for unusual patterns
            
            # 1. Multiple large transactions in short time
            large_threshold = df['amount'].quantile(0.95) if len(df) > 10 else 1000
            large_transactions = df[df['amount'] > large_threshold]
            
            if len(large_transactions) > 1:
                time_diffs = large_transactions['date'].diff().dt.total_seconds() / 3600  # Hours
                if any(diff < 2 for diff in time_diffs if pd.notna(diff)):
                    indicators.append({
                        'type': 'rapid_large_transactions',
                        'description': 'Multiple large transactions within 2 hours',
                        'severity': 'high'
                    })
            
            # 2. Unusual merchant patterns
            merchant_counts = df['merchant'].value_counts()
            if any(count > 5 for count in merchant_counts):
                indicators.append({
                    'type': 'repeated_merchant',
                    'description': 'Excessive transactions with same merchant',
                    'severity': 'medium'
                })
            
            # 3. Round number transactions (potential manual entry fraud)
            round_amounts = df[df['amount'] % 100 == 0]
            if len(round_amounts) > len(df) * 0.3:
                indicators.append({
                    'type': 'suspicious_amounts',
                    'description': 'High percentage of round-number transactions',
                    'severity': 'low'
                })
            
            return indicators
            
        except Exception as e:
            print(f"Error detecting fraud indicators: {e}")
            return []
