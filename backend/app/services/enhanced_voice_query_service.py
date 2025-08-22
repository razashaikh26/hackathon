"""
Enhanced Voice Query Service
SQL-like financial query processing with natural language understanding
"""

import logging
import re
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FinancialQuery:
    """Structured financial query representation"""
    query_type: str
    sql_equivalent: str
    description: str
    voice_patterns: List[str]
    required_fields: List[str]
    response_template: str

@dataclass
class QueryResult:
    """Query execution result"""
    success: bool
    data: Dict[str, Any]
    formatted_response: str
    sql_executed: Optional[str] = None
    error: Optional[str] = None

class EnhancedVoiceQueryService:
    """Advanced voice query processor with SQL-like capabilities"""
    
    def __init__(self):
        self.query_templates = self._initialize_query_templates()
        self.voice_patterns = self._initialize_voice_patterns()
        
    def _initialize_query_templates(self) -> Dict[str, FinancialQuery]:
        """Initialize SQL-like financial query templates"""
        return {
            "balance": FinancialQuery(
                query_type="balance",
                sql_equivalent="SELECT SUM(amount) as total_balance, account_type, SUM(CASE WHEN account_type='savings' THEN amount ELSE 0 END) as savings_balance, SUM(CASE WHEN account_type='current' THEN amount ELSE 0 END) as current_balance FROM accounts WHERE user_id = ? AND status = 'active'",
                description="Check total account balance across all accounts",
                voice_patterns=[
                    r".*balance.*",
                    r".*money.*",
                    r".*account.*",
                    r".*total.*savings.*",
                    r".*how much.*",
                    r".*available.*"
                ],
                required_fields=["user_id"],
                response_template="Your total balance is ₹{total_balance:,}. This includes ₹{savings_balance:,} in savings and ₹{current_balance:,} in current account."
            ),
            
            "expenses": FinancialQuery(
                query_type="expenses",
                sql_equivalent="SELECT category, SUM(amount) as total_amount, COUNT(*) as transaction_count, AVG(amount) as avg_amount FROM expenses WHERE user_id = ? AND date >= DATE_SUB(NOW(), INTERVAL 30 DAY) GROUP BY category ORDER BY total_amount DESC LIMIT 5",
                description="Analyze monthly expenses by category",
                voice_patterns=[
                    r".*expense.*",
                    r".*spend.*",
                    r".*spent.*",
                    r".*spending.*",
                    r".*where.*money.*",
                    r".*breakdown.*",
                    r".*categories.*"
                ],
                required_fields=["user_id"],
                response_template="Your top expenses this month: {expense_breakdown}. Total spending: ₹{total_expenses:,}."
            ),
            
            "portfolio": FinancialQuery(
                query_type="portfolio",
                sql_equivalent="SELECT p.stock_symbol, p.current_value, p.purchase_value, (p.current_value - p.purchase_value) as profit_loss, ((p.current_value - p.purchase_value) / p.purchase_value * 100) as percentage_change, p.quantity FROM portfolio p WHERE p.user_id = ? ORDER BY p.current_value DESC",
                description="Portfolio performance and holdings analysis",
                voice_patterns=[
                    r".*portfolio.*",
                    r".*investment.*",
                    r".*stock.*",
                    r".*shares.*",
                    r".*mutual.*fund.*",
                    r".*market.*",
                    r".*profit.*",
                    r".*loss.*",
                    r".*performance.*"
                ],
                required_fields=["user_id"],
                response_template="Portfolio value: ₹{total_value:,}. Overall {gain_loss_type}: ₹{total_gain_loss:,} ({percentage_change:.2f}%). Top holdings: {top_holdings}."
            ),
            
            "goals": FinancialQuery(
                query_type="goals",
                sql_equivalent="SELECT goal_name, target_amount, current_amount, deadline, ((current_amount / target_amount) * 100) as progress_percentage, (target_amount - current_amount) as remaining_amount FROM financial_goals WHERE user_id = ? AND status = 'active' ORDER BY deadline ASC",
                description="Financial goals progress tracking",
                voice_patterns=[
                    r".*goal.*",
                    r".*target.*",
                    r".*savings.*goal.*",
                    r".*progress.*",
                    r".*close.*goal.*",
                    r".*achieve.*",
                    r".*financial.*target.*"
                ],
                required_fields=["user_id"],
                response_template="You have {goal_count} active goals. {goal_details}. Keep up the great work!"
            ),
            
            "analytics": FinancialQuery(
                query_type="analytics",
                sql_equivalent="SELECT DATE_FORMAT(date, '%Y-%m') as month, SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as income, SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as expenses, (SUM(CASE WHEN type='income' THEN amount ELSE 0 END) - SUM(CASE WHEN type='expense' THEN amount ELSE 0 END)) as net_savings FROM transactions WHERE user_id = ? AND date >= DATE_SUB(NOW(), INTERVAL 6 MONTH) GROUP BY month ORDER BY month DESC",
                description="Income vs expenses trend analysis",
                voice_patterns=[
                    r".*income.*expense.*",
                    r".*trend.*",
                    r".*analytics.*",
                    r".*pattern.*",
                    r".*flow.*",
                    r".*savings.*rate.*",
                    r".*financial.*health.*"
                ],
                required_fields=["user_id"],
                response_template="Last month: Income ₹{last_income:,}, Expenses ₹{last_expenses:,}. Savings rate: {savings_rate:.1f}%. Trend: {trend_analysis}."
            ),
            
            "market": FinancialQuery(
                query_type="market",
                sql_equivalent="SELECT m.symbol, m.current_price, m.change_percent, m.volume, p.quantity, (p.quantity * m.current_price) as current_value FROM market_data m JOIN portfolio p ON m.symbol = p.stock_symbol WHERE p.user_id = ? ORDER BY current_value DESC",
                description="Market performance for user holdings",
                voice_patterns=[
                    r".*market.*",
                    r".*stock.*price.*",
                    r".*nifty.*",
                    r".*sensex.*",
                    r".*market.*update.*",
                    r".*stock.*market.*",
                    r".*share.*price.*"
                ],
                required_fields=["user_id"],
                response_template="Market update: {market_summary}. Your holdings: {portfolio_performance}. Recommendation: {advice}."
            ),
            
            "transactions": FinancialQuery(
                query_type="transactions",
                sql_equivalent="SELECT t.date, t.description, t.amount, t.category, t.type FROM transactions t WHERE t.user_id = ? ORDER BY t.date DESC LIMIT 10",
                description="Recent transaction history",
                voice_patterns=[
                    r".*transaction.*",
                    r".*recent.*activity.*",
                    r".*last.*payment.*",
                    r".*history.*",
                    r".*recent.*purchase.*"
                ],
                required_fields=["user_id"],
                response_template="Recent transactions: {transaction_list}. Latest: {latest_transaction}."
            ),
            
            "budgets": FinancialQuery(
                query_type="budgets",
                sql_equivalent="SELECT b.category, b.budget_amount, COALESCE(SUM(e.amount), 0) as spent_amount, (b.budget_amount - COALESCE(SUM(e.amount), 0)) as remaining_amount, ((COALESCE(SUM(e.amount), 0) / b.budget_amount) * 100) as usage_percentage FROM budgets b LEFT JOIN expenses e ON b.category = e.category AND b.user_id = e.user_id AND MONTH(e.date) = MONTH(NOW()) WHERE b.user_id = ? GROUP BY b.category, b.budget_amount",
                description="Budget vs actual spending analysis",
                voice_patterns=[
                    r".*budget.*",
                    r".*limit.*",
                    r".*allowance.*",
                    r".*over.*budget.*",
                    r".*budget.*status.*"
                ],
                required_fields=["user_id"],
                response_template="Budget status: {budget_summary}. {budget_alerts}"
            )
        }
    
    def _initialize_voice_patterns(self) -> Dict[str, List[str]]:
        """Initialize voice recognition patterns"""
        return {
            "greeting": [
                r".*hello.*", r".*hi.*", r".*hey.*", r".*good.*morning.*",
                r".*good.*evening.*", r".*namaste.*"
            ],
            "question_words": [
                r".*what.*", r".*how.*", r".*when.*", r".*where.*",
                r".*which.*", r".*show.*", r".*tell.*", r".*give.*"
            ],
            "urgency": [
                r".*urgent.*", r".*important.*", r".*critical.*",
                r".*emergency.*", r".*asap.*"
            ],
            "time_references": [
                r".*today.*", r".*yesterday.*", r".*this.*month.*",
                r".*last.*month.*", r".*this.*year.*", r".*recent.*"
            ]
        }
    
    async def analyze_voice_query(self, transcription: str, user_id: str = "demo_user") -> Tuple[Optional[FinancialQuery], float]:
        """Analyze voice input and match to financial query patterns"""
        cleaned_text = transcription.lower().strip()
        
        best_match = None
        best_score = 0.0
        
        for query_type, query_template in self.query_templates.items():
            score = 0.0
            pattern_count = 0
            
            # Check voice patterns
            for pattern in query_template.voice_patterns:
                if re.search(pattern, cleaned_text):
                    score += 1.0
                    pattern_count += 1
            
            # Normalize score
            if pattern_count > 0:
                score = score / len(query_template.voice_patterns)
                
                # Boost score for exact keyword matches
                if query_type in cleaned_text:
                    score += 0.3
                
                # Check for question words to boost relevance
                for pattern in self.voice_patterns["question_words"]:
                    if re.search(pattern, cleaned_text):
                        score += 0.1
                        break
                
                if score > best_score:
                    best_score = score
                    best_match = query_template
        
        return best_match, best_score
    
    async def execute_financial_query(self, query: FinancialQuery, user_id: str = "demo_user") -> QueryResult:
        """Execute financial query and return structured result"""
        try:
            # For demonstration, generate realistic mock data
            # In production, this would connect to actual database
            mock_data = await self._generate_mock_financial_data(query.query_type, user_id)
            
            # Format response using template
            formatted_response = await self._format_response(query, mock_data)
            
            return QueryResult(
                success=True,
                data=mock_data,
                formatted_response=formatted_response,
                sql_executed=query.sql_equivalent
            )
            
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return QueryResult(
                success=False,
                data={},
                formatted_response=f"Sorry, I couldn't process your {query.query_type} query at the moment.",
                error=str(e)
            )
    
    async def _generate_mock_financial_data(self, query_type: str, user_id: str) -> Dict[str, Any]:
        """Generate realistic mock financial data for demonstration"""
        base_data = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "currency": "INR"
        }
        
        if query_type == "balance":
            return {
                **base_data,
                "total_balance": 125000,
                "savings_balance": 85000,
                "current_balance": 40000,
                "accounts": [
                    {"type": "savings", "bank": "HDFC", "balance": 85000},
                    {"type": "current", "bank": "ICICI", "balance": 40000}
                ]
            }
        
        elif query_type == "expenses":
            expenses = [
                {"category": "Food & Dining", "amount": 15000, "transactions": 45},
                {"category": "Transportation", "amount": 12000, "transactions": 30},
                {"category": "Entertainment", "amount": 8000, "transactions": 15},
                {"category": "Shopping", "amount": 6000, "transactions": 12},
                {"category": "Utilities", "amount": 4000, "transactions": 8}
            ]
            return {
                **base_data,
                "total_expenses": sum(e["amount"] for e in expenses),
                "expense_categories": expenses,
                "period": "last_30_days"
            }
        
        elif query_type == "portfolio":
            holdings = [
                {"symbol": "RELIANCE", "current_value": 95000, "purchase_value": 85000, "quantity": 50},
                {"symbol": "TCS", "current_value": 75000, "purchase_value": 70000, "quantity": 20},
                {"symbol": "HDFC", "current_value": 55000, "purchase_value": 60000, "quantity": 30}
            ]
            total_current = sum(h["current_value"] for h in holdings)
            total_purchase = sum(h["purchase_value"] for h in holdings)
            
            return {
                **base_data,
                "total_value": total_current,
                "total_invested": total_purchase,
                "total_gain_loss": total_current - total_purchase,
                "percentage_change": ((total_current - total_purchase) / total_purchase) * 100,
                "holdings": holdings
            }
        
        elif query_type == "goals":
            goals = [
                {"name": "Emergency Fund", "target": 500000, "current": 125000, "deadline": "2025-12-31"},
                {"name": "House Down Payment", "target": 2000000, "current": 400000, "deadline": "2026-06-30"},
                {"name": "Vacation Fund", "target": 100000, "current": 75000, "deadline": "2025-03-31"}
            ]
            return {
                **base_data,
                "active_goals": goals,
                "total_target": sum(g["target"] for g in goals),
                "total_saved": sum(g["current"] for g in goals)
            }
        
        elif query_type == "analytics":
            return {
                **base_data,
                "last_month_income": 85000,
                "last_month_expenses": 45000,
                "savings_rate": 47.1,
                "trend": "improving",
                "monthly_data": [
                    {"month": "2024-08", "income": 85000, "expenses": 45000},
                    {"month": "2024-07", "income": 80000, "expenses": 48000},
                    {"month": "2024-06", "income": 82000, "expenses": 52000}
                ]
            }
        
        elif query_type == "market":
            return {
                **base_data,
                "nifty_change": 1.2,
                "portfolio_performance": "positive",
                "market_sentiment": "bullish",
                "recommendations": "Consider increasing SIP contributions in equity funds"
            }
        
        else:
            return base_data
    
    async def _format_response(self, query: FinancialQuery, data: Dict[str, Any]) -> str:
        """Format query result into natural language response"""
        try:
            if query.query_type == "balance":
                return f"Your total account balance is ₹{data['total_balance']:,}. This includes ₹{data['savings_balance']:,} in savings and ₹{data['current_balance']:,} in current account. You have accounts with {len(data['accounts'])} banks."
            
            elif query.query_type == "expenses":
                top_3 = data['expense_categories'][:3]
                expense_text = ", ".join([f"{cat['category']} ₹{cat['amount']:,}" for cat in top_3])
                return f"Your top expenses this month are: {expense_text}. Total monthly spending is ₹{data['total_expenses']:,}. You made {sum(cat['transactions'] for cat in top_3)} transactions in these categories."
            
            elif query.query_type == "portfolio":
                gain_loss_type = "gain" if data['total_gain_loss'] > 0 else "loss"
                top_holdings = ", ".join([f"{h['symbol']} ₹{h['current_value']:,}" for h in data['holdings'][:3]])
                return f"Your portfolio value is ₹{data['total_value']:,}. Overall {gain_loss_type} is ₹{abs(data['total_gain_loss']):,} ({data['percentage_change']:.1f}%). Top holdings: {top_holdings}."
            
            elif query.query_type == "goals":
                goal_details = []
                for goal in data['active_goals']:
                    progress = (goal['current'] / goal['target']) * 100
                    goal_details.append(f"{goal['name']} is {progress:.0f}% complete")
                
                return f"You have {len(data['active_goals'])} active financial goals. {', '.join(goal_details)}. Total target: ₹{data['total_target']:,}, achieved: ₹{data['total_saved']:,}."
            
            elif query.query_type == "analytics":
                return f"Last month you earned ₹{data['last_month_income']:,} and spent ₹{data['last_month_expenses']:,}. Your savings rate is {data['savings_rate']:.1f}%. Your financial trend is {data['trend']}. Keep up the excellent financial discipline!"
            
            elif query.query_type == "market":
                return f"Market update: Nifty 50 is up {data['nifty_change']}%. Your portfolio performance is {data['portfolio_performance']} with {data['market_sentiment']} market sentiment. Recommendation: {data['recommendations']}."
            
            else:
                return "I've processed your financial query. The information has been analyzed and is available in your dashboard."
                
        except Exception as e:
            logger.error(f"Response formatting failed: {str(e)}")
            return f"I found your {query.query_type} information, but had trouble formatting the response. Please check your dashboard for details."
    
    async def process_voice_query(self, transcription: str, user_id: str = "demo_user") -> Dict[str, Any]:
        """Main entry point for processing voice queries"""
        try:
            # Analyze the voice input
            detected_query, confidence = await self.analyze_voice_query(transcription, user_id)
            
            if detected_query and confidence > 0.3:  # Confidence threshold
                # Execute the financial query
                result = await self.execute_financial_query(detected_query, user_id)
                
                return {
                    "success": True,
                    "query_type": detected_query.query_type,
                    "confidence": confidence,
                    "sql_equivalent": detected_query.sql_equivalent,
                    "data": result.data,
                    "formatted_response": result.formatted_response,
                    "transcription": transcription,
                    "enhanced_audio_response": True
                }
            else:
                # Fallback for unrecognized queries
                return {
                    "success": False,
                    "query_type": "general",
                    "confidence": confidence,
                    "formatted_response": "I didn't recognize that as a financial query. Try asking about your balance, expenses, portfolio, or goals.",
                    "transcription": transcription,
                    "suggestions": ["Check my balance", "Show my expenses", "Portfolio performance", "Goal progress"]
                }
                
        except Exception as e:
            logger.error(f"Voice query processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "formatted_response": "Sorry, I encountered an error processing your voice query. Please try again.",
                "transcription": transcription
            }

# Global service instance
enhanced_voice_query_service = EnhancedVoiceQueryService()
