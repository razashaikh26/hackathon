"""
AI Advisory Chatbot for FinVoice
Personalized financial advisory with Indian market expertise
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

import openai
from decouple import config
import redis
import asyncio
from .free_ai_service import free_ai_service
from .openrouter_service import openrouter_service

logger = logging.getLogger(__name__)

class AdvisoryType(Enum):
    SAVINGS = "savings"
    SPENDING = "spending"
    INVESTMENT = "investment"
    DEBT = "debt"
    GOAL_PLANNING = "goal_planning"
    BUDGET = "budget"
    INSURANCE = "insurance"
    TAX_PLANNING = "tax_planning"

@dataclass
class FinancialProfile:
    user_id: str
    age: int
    monthly_income: float
    monthly_expenses: float
    current_savings: float
    debt_amount: float
    risk_tolerance: str  # conservative, moderate, aggressive
    financial_goals: List[Dict[str, Any]]
    dependents: int
    employment_type: str  # salaried, business, freelance
    location: str  # for city-specific advice

@dataclass
class AdvisoryResponse:
    advisory_type: AdvisoryType
    title: str
    summary: str
    detailed_advice: str
    action_items: List[str]
    priority: str  # high, medium, low
    estimated_impact: str
    relevant_products: List[Dict[str, Any]]
    follow_up_questions: List[str]
    confidence_score: float
    timestamp: datetime

class AIAdvisoryService:
    def __init__(self):
        # OpenRouter API Key
        self.openrouter_api_key = config("OPENROUTER_API_KEY", default="")
        
        # Check if we should use free AI only
        self.use_free_ai_only = config("USE_FREE_AI_ONLY", default="false").lower() == "true"
        
        # Priority order: OpenRouter -> OpenAI -> Free AI
        self.has_openrouter = bool(self.openrouter_api_key)
        
        # Try to initialize OpenAI client only if not forced to use free AI and no OpenRouter
        if not self.use_free_ai_only and not self.has_openrouter:
            try:
                openai_key = config("OPENAI_API_KEY", default=None)
                if openai_key and openai_key != "your_openai_api_key_here":
                    self.openai_client = openai.OpenAI(api_key=openai_key)
                    self.has_openai = True
                else:
                    self.openai_client = None
                    self.has_openai = False
            except Exception as e:
                logger.warning(f"OpenAI not available: {e}")
                self.openai_client = None
                self.has_openai = False
        else:
            if self.has_openrouter:
                logger.info("Using OpenRouter as primary AI service")
            else:
                logger.info("Using free AI only as configured")
            self.openai_client = None
            self.has_openai = False
        
        # Initialize Redis if available
        try:
            redis_url = config("REDIS_URL", default=None)
            if redis_url:
                self.redis_client = redis.from_url(redis_url)
            else:
                self.redis_client = None
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            self.redis_client = None
        
        # Indian financial context
        self.indian_financial_context = self._load_indian_context()
        
        # Advisory templates
        self.advisory_templates = self._load_advisory_templates()
    
    def _load_indian_context(self) -> Dict[str, Any]:
        """Load Indian financial market context"""
        return {
            "tax_brackets": [
                {"min": 0, "max": 250000, "rate": 0},
                {"min": 250000, "max": 500000, "rate": 5},
                {"min": 500000, "max": 750000, "rate": 10},
                {"min": 750000, "max": 1000000, "rate": 15},
                {"min": 1000000, "max": 1250000, "rate": 20},
                {"min": 1250000, "max": 1500000, "rate": 25},
                {"min": 1500000, "max": float('inf'), "rate": 30}
            ],
            "recommended_allocations": {
                "emergency_fund": {"min": 6, "max": 12, "unit": "months_expense"},
                "equity": {"young": 70, "middle": 50, "senior": 30},
                "debt": {"young": 20, "middle": 40, "senior": 60},
                "real_estate": {"max": 30},
                "gold": {"max": 10}
            },
            "popular_instruments": {
                "savings": ["SBI FD", "HDFC FD", "Post Office Schemes", "NSC"],
                "equity": ["Nifty 50 ETF", "Large Cap MF", "Mid Cap MF", "Small Cap MF"],
                "debt": ["Government Bonds", "Corporate Bonds", "Debt MF"],
                "tax_saving": ["ELSS", "PPF", "NSC", "Tax Saver FD", "NPS"]
            },
            "inflation_rate": 6.0,
            "benchmark_returns": {
                "equity": 12.0,
                "debt": 7.0,
                "real_estate": 8.0,
                "gold": 6.0,
                "fd": 6.5
            }
        }
    
    def _load_advisory_templates(self) -> Dict[str, Dict[str, str]]:
        """Load advisory response templates"""
        return {
            "savings": {
                "positive": "Great job on building your savings! Your current savings rate of {savings_rate}% is {comparison} the recommended 20% target.",
                "negative": "Your savings could use some improvement. Currently saving {savings_rate}%, but aim for at least 20% of income.",
                "action": "Consider automating savings through SIPs and increasing contributions gradually."
            },
            "spending": {
                "high": "Your spending in {category} category is higher than recommended. Consider reducing expenses by {reduction_amount}.",
                "optimal": "Your spending pattern looks healthy across most categories.",
                "suggestion": "Track expenses daily and set category-wise budgets to maintain control."
            },
            "investment": {
                "conservative": "Given your conservative risk profile, focus on debt instruments and blue-chip equity funds.",
                "moderate": "A balanced approach with 60% equity and 40% debt would suit your moderate risk appetite.",
                "aggressive": "With your aggressive risk tolerance, you can allocate up to 80% in equity investments."
            },
            "debt": {
                "high": "Your debt-to-income ratio of {ratio}% is concerning. Prioritize debt reduction immediately.",
                "manageable": "Your debt levels are manageable, but consider faster repayment to save on interest.",
                "none": "Excellent! No debt gives you financial flexibility to focus on wealth building."
            }
        }
    
    async def get_personalized_advice(
        self, 
        profile: FinancialProfile, 
        query: str = None,
        advisory_type: AdvisoryType = None
    ) -> AdvisoryResponse:
        """Generate personalized financial advice"""
        
        try:
            # Analyze financial health
            health_analysis = await self._analyze_financial_health(profile)
            
            # Determine advisory type if not specified
            if not advisory_type:
                advisory_type = await self._determine_advisory_type(query, health_analysis)
            
            # Generate specific advice based on type
            advice = await self._generate_advice_by_type(advisory_type, profile, health_analysis, query)
            
            return advice
            
        except Exception as e:
            logger.error(f"Error generating personalized advice: {e}")
            return self._default_advisory_response(advisory_type or AdvisoryType.SAVINGS)
    
    async def _analyze_financial_health(self, profile: FinancialProfile) -> Dict[str, Any]:
        """Analyze user's financial health across multiple dimensions"""
        
        analysis = {
            "savings_rate": self._calculate_savings_rate(profile),
            "debt_to_income": self._calculate_debt_to_income(profile),
            "emergency_fund_months": self._calculate_emergency_fund_coverage(profile),
            "investment_allocation": self._analyze_investment_allocation(profile),
            "risk_capacity": self._assess_risk_capacity(profile),
            "goal_feasibility": await self._assess_goal_feasibility(profile),
            "tax_efficiency": self._analyze_tax_efficiency(profile),
            "overall_score": 0.0
        }
        
        # Calculate overall financial health score
        analysis["overall_score"] = self._calculate_health_score(analysis)
        
        return analysis
    
    def _calculate_savings_rate(self, profile: FinancialProfile) -> float:
        """Calculate monthly savings rate"""
        if profile.monthly_income <= 0:
            return 0.0
        
        monthly_savings = profile.monthly_income - profile.monthly_expenses
        return (monthly_savings / profile.monthly_income) * 100
    
    def _calculate_debt_to_income(self, profile: FinancialProfile) -> float:
        """Calculate debt-to-income ratio"""
        if profile.monthly_income <= 0:
            return 0.0
        
        return (profile.debt_amount / (profile.monthly_income * 12)) * 100
    
    def _calculate_emergency_fund_coverage(self, profile: FinancialProfile) -> float:
        """Calculate emergency fund coverage in months"""
        if profile.monthly_expenses <= 0:
            return 0.0
        
        return profile.current_savings / profile.monthly_expenses
    
    def _analyze_investment_allocation(self, profile: FinancialProfile) -> Dict[str, Any]:
        """Analyze current investment allocation"""
        # This would analyze actual portfolio data
        # For now, return recommended allocation based on age
        
        age_group = "young" if profile.age < 35 else "middle" if profile.age < 50 else "senior"
        recommended = self.indian_financial_context["recommended_allocations"]
        
        return {
            "recommended_equity": recommended["equity"][age_group],
            "recommended_debt": recommended["debt"][age_group],
            "age_group": age_group,
            "rebalancing_needed": False  # Would be calculated based on actual allocation
        }
    
    def _assess_risk_capacity(self, profile: FinancialProfile) -> Dict[str, Any]:
        """Assess user's risk-taking capacity"""
        
        # Factors affecting risk capacity
        income_stability = 1.0 if profile.employment_type == "salaried" else 0.7
        age_factor = max(0.3, 1.0 - (profile.age - 25) / 40)  # Decreases with age
        dependent_factor = max(0.5, 1.0 - (profile.dependents * 0.1))
        emergency_factor = min(1.0, profile.current_savings / (profile.monthly_expenses * 6))
        
        capacity_score = (income_stability + age_factor + dependent_factor + emergency_factor) / 4
        
        # Map to risk level
        if capacity_score > 0.7:
            capacity_level = "high"
        elif capacity_score > 0.4:
            capacity_level = "moderate"
        else:
            capacity_level = "low"
        
        return {
            "capacity_score": capacity_score,
            "capacity_level": capacity_level,
            "factors": {
                "income_stability": income_stability,
                "age_factor": age_factor,
                "dependent_factor": dependent_factor,
                "emergency_factor": emergency_factor
            }
        }
    
    async def _assess_goal_feasibility(self, profile: FinancialProfile) -> List[Dict[str, Any]]:
        """Assess feasibility of financial goals"""
        
        goal_assessments = []
        monthly_investable = max(0, profile.monthly_income - profile.monthly_expenses)
        
        for goal in profile.financial_goals:
            target_amount = goal.get("target_amount", 0)
            target_date = goal.get("target_date")
            goal_name = goal.get("name", "Financial Goal")
            
            if target_date:
                try:
                    target_datetime = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                    months_to_goal = max(1, (target_datetime - datetime.now()).days / 30)
                    
                    # Calculate required monthly SIP
                    required_monthly = self._calculate_sip_amount(target_amount, months_to_goal, 12.0)
                    
                    feasibility = "feasible" if required_monthly <= monthly_investable * 0.8 else "challenging"
                    
                    goal_assessments.append({
                        "name": goal_name,
                        "target_amount": target_amount,
                        "months_to_goal": months_to_goal,
                        "required_monthly_sip": required_monthly,
                        "feasibility": feasibility,
                        "confidence": 0.8 if feasibility == "feasible" else 0.4
                    })
                    
                except Exception as e:
                    logger.error(f"Error assessing goal {goal_name}: {e}")
        
        return goal_assessments
    
    def _calculate_sip_amount(self, target_amount: float, months: float, annual_return: float) -> float:
        """Calculate required SIP amount for a target"""
        monthly_rate = annual_return / (12 * 100)
        if monthly_rate == 0:
            return target_amount / months
        
        # SIP formula: PMT = FV * r / ((1 + r)^n - 1)
        return target_amount * monthly_rate / ((1 + monthly_rate) ** months - 1)
    
    def _analyze_tax_efficiency(self, profile: FinancialProfile) -> Dict[str, Any]:
        """Analyze tax efficiency and suggest optimizations"""
        
        annual_income = profile.monthly_income * 12
        
        # Find tax bracket
        tax_rate = 0
        for bracket in self.indian_financial_context["tax_brackets"]:
            if bracket["min"] <= annual_income <= bracket["max"]:
                tax_rate = bracket["rate"]
                break
        
        # Calculate potential savings
        max_80c_deduction = 150000  # Current limit
        potential_tax_savings = max_80c_deduction * (tax_rate / 100)
        
        return {
            "current_tax_bracket": tax_rate,
            "annual_income": annual_income,
            "max_80c_benefit": max_80c_deduction,
            "potential_tax_savings": potential_tax_savings,
            "suggestions": ["ELSS", "PPF", "NSC", "Life Insurance", "NPS"] if tax_rate > 0 else []
        }
    
    def _calculate_health_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall financial health score (0-100)"""
        
        scores = []
        
        # Savings rate score (0-25 points)
        savings_rate = analysis["savings_rate"]
        if savings_rate >= 30:
            scores.append(25)
        elif savings_rate >= 20:
            scores.append(20)
        elif savings_rate >= 10:
            scores.append(15)
        else:
            scores.append(savings_rate / 2)
        
        # Debt score (0-25 points)
        debt_ratio = analysis["debt_to_income"]
        if debt_ratio <= 20:
            scores.append(25)
        elif debt_ratio <= 40:
            scores.append(20)
        elif debt_ratio <= 60:
            scores.append(15)
        else:
            scores.append(max(0, 25 - debt_ratio / 4))
        
        # Emergency fund score (0-25 points)
        emergency_months = analysis["emergency_fund_months"]
        if emergency_months >= 12:
            scores.append(25)
        elif emergency_months >= 6:
            scores.append(20)
        elif emergency_months >= 3:
            scores.append(15)
        else:
            scores.append(emergency_months * 5)
        
        # Investment/Goal score (0-25 points)
        goal_feasibility = analysis.get("goal_feasibility", [])
        feasible_goals = len([g for g in goal_feasibility if g["feasibility"] == "feasible"])
        total_goals = len(goal_feasibility)
        
        if total_goals > 0:
            goal_score = (feasible_goals / total_goals) * 25
        else:
            goal_score = 15  # Default score if no goals set
        
        scores.append(goal_score)
        
        return sum(scores)
    
    async def _determine_advisory_type(self, query: str, health_analysis: Dict[str, Any]) -> AdvisoryType:
        """Determine the type of advisory needed"""
        
        if not query:
            # Default based on health analysis
            if health_analysis["savings_rate"] < 10:
                return AdvisoryType.SAVINGS
            elif health_analysis["debt_to_income"] > 40:
                return AdvisoryType.DEBT
            else:
                return AdvisoryType.INVESTMENT
        
        # Use AI to classify query intent if OpenAI is available
        if self.has_openai and self.openai_client:
            try:
                prompt = f"""
                Classify this financial query into one of these categories:
                - savings: Questions about saving money, building emergency fund
                - spending: Questions about expenses, budgeting, cost reduction
                - investment: Questions about investing, mutual funds, stocks, portfolio
                - debt: Questions about loans, credit cards, debt management
                - goal_planning: Questions about financial goals, planning for purchases
                - budget: Questions about budget planning and allocation
                - insurance: Questions about insurance planning
                - tax_planning: Questions about tax optimization
                
                Query: "{query}"
                
                Respond with just the category name:
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a financial advisory classifier."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=20,
                    temperature=0.1
                )
                
                category = response.choices[0].message.content.strip().lower()
                
                try:
                    return AdvisoryType(category)
                except ValueError:
                    pass
                    
            except Exception as e:
                logger.warning(f"Error determining advisory type with AI: {e}")
        
        # Fallback to keyword-based classification
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['save', 'saving', 'emergency', 'deposit']):
            return AdvisoryType.SAVINGS
        elif any(word in query_lower for word in ['expense', 'spending', 'budget', 'cost']):
            return AdvisoryType.SPENDING
        elif any(word in query_lower for word in ['invest', 'investment', 'mutual fund', 'stocks', 'portfolio']):
            return AdvisoryType.INVESTMENT
        elif any(word in query_lower for word in ['debt', 'loan', 'credit', 'emi']):
            return AdvisoryType.DEBT
        elif any(word in query_lower for word in ['goal', 'plan', 'target', 'future']):
            return AdvisoryType.GOAL_PLANNING
        elif any(word in query_lower for word in ['budget', 'allocation', 'money management']):
            return AdvisoryType.BUDGET
        elif any(word in query_lower for word in ['tax', '80c', 'deduction', 'return']):
            return AdvisoryType.TAX_PLANNING
        elif any(word in query_lower for word in ['insurance', 'cover', 'protection']):
            return AdvisoryType.INSURANCE
        else:
            return AdvisoryType.SAVINGS
    
    async def _generate_advice_by_type(
        self, 
        advisory_type: AdvisoryType, 
        profile: FinancialProfile, 
        health_analysis: Dict[str, Any],
        query: str = None
    ) -> AdvisoryResponse:
        """Generate specific advice based on advisory type"""
        
        if advisory_type == AdvisoryType.SAVINGS:
            return await self._generate_savings_advice(profile, health_analysis)
        elif advisory_type == AdvisoryType.SPENDING:
            return await self._generate_spending_advice(profile, health_analysis)
        elif advisory_type == AdvisoryType.INVESTMENT:
            return await self._generate_investment_advice(profile, health_analysis)
        elif advisory_type == AdvisoryType.DEBT:
            return await self._generate_debt_advice(profile, health_analysis)
        elif advisory_type == AdvisoryType.GOAL_PLANNING:
            return await self._generate_goal_planning_advice(profile, health_analysis)
        elif advisory_type == AdvisoryType.BUDGET:
            return await self._generate_budget_advice(profile, health_analysis)
        elif advisory_type == AdvisoryType.TAX_PLANNING:
            return await self._generate_tax_advice(profile, health_analysis)
        else:
            return await self._generate_general_advice(profile, health_analysis, query)
    
    async def _generate_savings_advice(self, profile: FinancialProfile, analysis: Dict[str, Any]) -> AdvisoryResponse:
        """Generate savings-specific advice"""
        
        savings_rate = analysis["savings_rate"]
        emergency_months = analysis["emergency_fund_months"]
        
        if savings_rate < 10:
            priority = "high"
            title = "Boost Your Savings Rate"
            summary = f"Your current savings rate of {savings_rate:.1f}% needs immediate attention."
        elif savings_rate < 20:
            priority = "medium"
            title = "Improve Your Savings Discipline"
            summary = f"You're saving {savings_rate:.1f}%, which is good but can be optimized."
        else:
            priority = "low"
            title = "Excellent Savings Habits"
            summary = f"Your {savings_rate:.1f}% savings rate is commendable!"
        
        # Generate action items
        action_items = []
        if emergency_months < 6:
            action_items.append(f"Build emergency fund to ₹{profile.monthly_expenses * 6:,.0f} (6 months expenses)")
        
        action_items.extend([
            "Set up automatic transfers to savings account",
            "Consider high-yield savings accounts or FDs",
            "Track expenses to identify saving opportunities"
        ])
        
        # Relevant products
        products = [
            {"name": "High-Yield Savings Account", "type": "savings", "returns": "4-6% p.a."},
            {"name": "Fixed Deposits", "type": "savings", "returns": "6-7% p.a."},
            {"name": "Liquid Mutual Funds", "type": "savings", "returns": "3-5% p.a."}
        ]
        
        detailed_advice = await self._generate_detailed_advice(
            "savings", profile, analysis, savings_rate, emergency_months
        )
        
        return AdvisoryResponse(
            advisory_type=AdvisoryType.SAVINGS,
            title=title,
            summary=summary,
            detailed_advice=detailed_advice,
            action_items=action_items,
            priority=priority,
            estimated_impact="High - Foundation of financial health",
            relevant_products=products,
            follow_up_questions=[
                "How can I automate my savings?",
                "What's the best emergency fund strategy?",
                "Should I prioritize savings or investments?"
            ],
            confidence_score=0.9,
            timestamp=datetime.now()
        )
    
    async def _generate_investment_advice(self, profile: FinancialProfile, analysis: Dict[str, Any]) -> AdvisoryResponse:
        """Generate investment-specific advice"""
        
        allocation = analysis["investment_allocation"]
        risk_capacity = analysis["risk_capacity"]
        
        title = f"Investment Strategy for {profile.risk_tolerance.title()} Risk Profile"
        summary = f"Based on your {allocation['age_group']} age group and {profile.risk_tolerance} risk appetite."
        
        # Generate allocation advice
        recommended_equity = allocation["recommended_equity"]
        recommended_debt = allocation["recommended_debt"]
        
        action_items = [
            f"Allocate {recommended_equity}% to equity mutual funds",
            f"Allocate {recommended_debt}% to debt instruments",
            "Start SIP in diversified equity funds",
            "Review and rebalance portfolio annually"
        ]
        
        # Investment products based on risk profile
        if profile.risk_tolerance == "conservative":
            products = [
                {"name": "Debt Mutual Funds", "type": "debt", "returns": "7-9% p.a."},
                {"name": "Government Bonds", "type": "debt", "returns": "6-8% p.a."},
                {"name": "Large Cap Equity Funds", "type": "equity", "returns": "10-12% p.a."}
            ]
        elif profile.risk_tolerance == "aggressive":
            products = [
                {"name": "Small Cap Mutual Funds", "type": "equity", "returns": "14-18% p.a."},
                {"name": "Mid Cap Mutual Funds", "type": "equity", "returns": "12-16% p.a."},
                {"name": "Sectoral Funds", "type": "equity", "returns": "Variable"}
            ]
        else:  # moderate
            products = [
                {"name": "Balanced Advantage Funds", "type": "hybrid", "returns": "10-12% p.a."},
                {"name": "Large & Mid Cap Funds", "type": "equity", "returns": "11-14% p.a."},
                {"name": "Corporate Bond Funds", "type": "debt", "returns": "7-9% p.a."}
            ]
        
        detailed_advice = await self._generate_detailed_advice(
            "investment", profile, analysis, recommended_equity, recommended_debt
        )
        
        return AdvisoryResponse(
            advisory_type=AdvisoryType.INVESTMENT,
            title=title,
            summary=summary,
            detailed_advice=detailed_advice,
            action_items=action_items,
            priority="medium",
            estimated_impact="High - Wealth building foundation",
            relevant_products=products,
            follow_up_questions=[
                "How much should I invest monthly?",
                "Which mutual funds are best for me?",
                "When should I rebalance my portfolio?"
            ],
            confidence_score=0.85,
            timestamp=datetime.now()
        )
    
    async def _generate_debt_advice(self, profile: FinancialProfile, analysis: Dict[str, Any]) -> AdvisoryResponse:
        """Generate debt management advice"""
        
        debt_ratio = analysis["debt_to_income"]
        
        if debt_ratio > 50:
            priority = "high"
            title = "Urgent Debt Management Required"
            summary = f"Your debt-to-income ratio of {debt_ratio:.1f}% requires immediate action."
        elif debt_ratio > 30:
            priority = "medium"
            title = "Optimize Your Debt Strategy"
            summary = f"Your {debt_ratio:.1f}% debt ratio can be improved with proper planning."
        else:
            priority = "low"
            title = "Debt Under Control"
            summary = f"Your {debt_ratio:.1f}% debt ratio is manageable."
        
        action_items = [
            "List all debts with interest rates and balances",
            "Prioritize high-interest debt repayment",
            "Consider debt consolidation if beneficial",
            "Avoid taking new unnecessary debt"
        ]
        
        if debt_ratio > 40:
            action_items.insert(0, "Create emergency debt repayment plan")
        
        products = [
            {"name": "Balance Transfer", "type": "debt", "benefit": "Lower interest rates"},
            {"name": "Personal Loan Consolidation", "type": "debt", "benefit": "Single EMI"},
            {"name": "Home Loan Against Property", "type": "debt", "benefit": "Lowest rates"}
        ]
        
        detailed_advice = await self._generate_detailed_advice(
            "debt", profile, analysis, debt_ratio
        )
        
        return AdvisoryResponse(
            advisory_type=AdvisoryType.DEBT,
            title=title,
            summary=summary,
            detailed_advice=detailed_advice,
            action_items=action_items,
            priority=priority,
            estimated_impact="High - Reduces financial stress",
            relevant_products=products,
            follow_up_questions=[
                "Should I pay minimum or accelerate debt payments?",
                "Is debt consolidation right for me?",
                "How to negotiate with creditors?"
            ],
            confidence_score=0.88,
            timestamp=datetime.now()
        )
    
    async def _generate_goal_planning_advice(self, profile: FinancialProfile, analysis: Dict[str, Any]) -> AdvisoryResponse:
        """Generate goal planning advice"""
        
        goal_assessments = analysis.get("goal_feasibility", [])
        
        if not goal_assessments:
            title = "Set Financial Goals for Success"
            summary = "Having clear financial goals is crucial for wealth building."
            priority = "medium"
        else:
            feasible_count = len([g for g in goal_assessments if g["feasibility"] == "feasible"])
            total_count = len(goal_assessments)
            
            title = f"Goal Achievement Strategy ({feasible_count}/{total_count} goals feasible)"
            summary = f"You have {total_count} financial goals, {feasible_count} are currently feasible."
            priority = "medium" if feasible_count > total_count / 2 else "high"
        
        action_items = [
            "Define specific, measurable financial goals",
            "Set realistic timelines for each goal",
            "Calculate required monthly savings/investments",
            "Track progress monthly and adjust as needed"
        ]
        
        # Add specific advice for each goal
        for goal in goal_assessments:
            if goal["feasibility"] == "challenging":
                action_items.append(f"Revise timeline or amount for {goal['name']}")
        
        products = [
            {"name": "SIP Calculator", "type": "tool", "benefit": "Plan monthly investments"},
            {"name": "Goal-based Mutual Funds", "type": "investment", "benefit": "Target-oriented investing"},
            {"name": "PPF for Long-term Goals", "type": "investment", "benefit": "Tax-free returns"}
        ]
        
        detailed_advice = await self._generate_detailed_advice(
            "goal_planning", profile, analysis
        )
        
        return AdvisoryResponse(
            advisory_type=AdvisoryType.GOAL_PLANNING,
            title=title,
            summary=summary,
            detailed_advice=detailed_advice,
            action_items=action_items,
            priority=priority,
            estimated_impact="High - Provides direction and motivation",
            relevant_products=products,
            follow_up_questions=[
                "How do I prioritize multiple goals?",
                "Should I adjust my goals based on income changes?",
                "What if I can't achieve my goals on time?"
            ],
            confidence_score=0.82,
            timestamp=datetime.now()
        )
    
    async def _generate_spending_advice(self, profile: FinancialProfile, analysis: Dict[str, Any]) -> AdvisoryResponse:
        """Generate spending optimization advice"""
        
        # This would analyze actual spending patterns
        # For now, provide general advice
        
        expense_ratio = (profile.monthly_expenses / profile.monthly_income) * 100
        
        if expense_ratio > 80:
            priority = "high"
            title = "Reduce Expenses Immediately"
            summary = f"Your expenses consume {expense_ratio:.1f}% of income - needs urgent attention."
        elif expense_ratio > 70:
            priority = "medium"
            title = "Optimize Your Spending"
            summary = f"Your {expense_ratio:.1f}% expense ratio can be improved."
        else:
            priority = "low"
            title = "Good Expense Control"
            summary = f"Your {expense_ratio:.1f}% expense ratio is well-managed."
        
        action_items = [
            "Track all expenses for 30 days",
            "Identify and cut unnecessary subscriptions",
            "Negotiate bills (internet, mobile, insurance)",
            "Use budgeting apps for better control"
        ]
        
        detailed_advice = await self._generate_detailed_advice(
            "spending", profile, analysis, expense_ratio
        )
        
        return AdvisoryResponse(
            advisory_type=AdvisoryType.SPENDING,
            title=title,
            summary=summary,
            detailed_advice=detailed_advice,
            action_items=action_items,
            priority=priority,
            estimated_impact="Medium - Frees up money for savings",
            relevant_products=[
                {"name": "Expense Tracking Apps", "type": "tool", "benefit": "Better visibility"},
                {"name": "Cashback Credit Cards", "type": "financial", "benefit": "Earn on spending"}
            ],
            follow_up_questions=[
                "Which expenses should I cut first?",
                "How to negotiate better rates?",
                "What's a reasonable budget for entertainment?"
            ],
            confidence_score=0.75,
            timestamp=datetime.now()
        )
    
    async def _generate_budget_advice(self, profile: FinancialProfile, analysis: Dict[str, Any]) -> AdvisoryResponse:
        """Generate budget planning advice"""
        
        title = "Smart Budget Allocation Strategy"
        summary = "A well-planned budget is the foundation of financial success."
        
        # 50-30-20 rule adapted for Indian context
        needs_budget = profile.monthly_income * 0.50  # Housing, food, utilities
        wants_budget = profile.monthly_income * 0.30  # Entertainment, dining out
        savings_budget = profile.monthly_income * 0.20  # Savings and investments
        
        action_items = [
            f"Allocate ₹{needs_budget:,.0f} (50%) for essential needs",
            f"Limit wants to ₹{wants_budget:,.0f} (30%)",
            f"Save/invest ₹{savings_budget:,.0f} (20%) minimum",
            "Review and adjust budget monthly"
        ]
        
        detailed_advice = f"""
        Based on your monthly income of ₹{profile.monthly_income:,.0f}, here's a recommended budget allocation:
        
        **Essential Needs (50% - ₹{needs_budget:,.0f}):**
        - Rent/EMI: ₹{needs_budget * 0.6:,.0f}
        - Groceries: ₹{needs_budget * 0.25:,.0f}
        - Utilities: ₹{needs_budget * 0.15:,.0f}
        
        **Wants (30% - ₹{wants_budget:,.0f}):**
        - Dining out: ₹{wants_budget * 0.4:,.0f}
        - Entertainment: ₹{wants_budget * 0.3:,.0f}
        - Shopping: ₹{wants_budget * 0.3:,.0f}
        
        **Savings & Investments (20% - ₹{savings_budget:,.0f}):**
        - Emergency fund: ₹{savings_budget * 0.3:,.0f}
        - Mutual funds: ₹{savings_budget * 0.5:,.0f}
        - Insurance: ₹{savings_budget * 0.2:,.0f}
        
        Adjust these percentages based on your specific situation and goals.
        """
        
        return AdvisoryResponse(
            advisory_type=AdvisoryType.BUDGET,
            title=title,
            summary=summary,
            detailed_advice=detailed_advice,
            action_items=action_items,
            priority="medium",
            estimated_impact="High - Brings financial discipline",
            relevant_products=[
                {"name": "Budget Tracking Apps", "type": "tool", "benefit": "Easy monitoring"},
                {"name": "Automated Savings", "type": "service", "benefit": "Disciplined saving"}
            ],
            follow_up_questions=[
                "How do I stick to my budget?",
                "Should I adjust budget percentages?",
                "What if my income varies monthly?"
            ],
            confidence_score=0.85,
            timestamp=datetime.now()
        )
    
    async def _generate_tax_advice(self, profile: FinancialProfile, analysis: Dict[str, Any]) -> AdvisoryResponse:
        """Generate tax planning advice"""
        
        tax_analysis = analysis["tax_efficiency"]
        tax_bracket = tax_analysis["current_tax_bracket"]
        potential_savings = tax_analysis["potential_tax_savings"]
        
        if tax_bracket > 20:
            priority = "high"
            title = "Optimize Tax Planning - High Bracket"
        elif tax_bracket > 5:
            priority = "medium"
            title = "Tax Optimization Opportunities"
        else:
            priority = "low"
            title = "Basic Tax Planning"
        
        summary = f"You're in {tax_bracket}% tax bracket. Potential savings: ₹{potential_savings:,.0f}"
        
        action_items = [
            f"Invest ₹1.5L in 80C instruments to save ₹{potential_savings:,.0f}",
            "Consider NPS for additional ₹50K deduction",
            "Plan health insurance for 80D benefits",
            "Keep track of all tax-saving investments"
        ]
        
        products = [
            {"name": "ELSS Mutual Funds", "type": "investment", "benefit": "80C + Growth potential"},
            {"name": "PPF", "type": "investment", "benefit": "EEE status"},
            {"name": "NPS", "type": "retirement", "benefit": "Extra 50K deduction"},
            {"name": "Health Insurance", "type": "insurance", "benefit": "80D deduction"}
        ]
        
        detailed_advice = await self._generate_detailed_advice(
            "tax_planning", profile, analysis, tax_bracket, potential_savings
        )
        
        return AdvisoryResponse(
            advisory_type=AdvisoryType.TAX_PLANNING,
            title=title,
            summary=summary,
            detailed_advice=detailed_advice,
            action_items=action_items,
            priority=priority,
            estimated_impact=f"Medium - Save ₹{potential_savings:,.0f} annually",
            relevant_products=products,
            follow_up_questions=[
                "Which 80C option is best for me?",
                "How much should I invest in NPS?",
                "What are the tax implications of different investments?"
            ],
            confidence_score=0.90,
            timestamp=datetime.now()
        )
    
    async def _generate_general_advice(self, profile: FinancialProfile, analysis: Dict[str, Any], query: str) -> AdvisoryResponse:
        """Generate general financial advice"""
        
        try:
            # Use AI for comprehensive advice generation if available
            if self.has_openai and self.openai_client:
                try:
                    context = {
                        "profile": asdict(profile),
                        "analysis": analysis,
                        "query": query
                    }
                    
                    prompt = f"""
                    As a financial advisor for Indian markets, provide comprehensive advice for this user:
                    
                    Profile: {json.dumps(context, default=str, indent=2)}
                    
                    Generate specific, actionable advice considering:
                    1. Indian tax laws and investment options
                    2. User's current financial health
                    3. Age-appropriate strategies
                    4. Risk tolerance alignment
                    
                    Focus on practical steps they can take immediately.
                    """
                    
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert financial advisor specializing in Indian markets. Provide practical, actionable advice."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        max_tokens=500,
                        temperature=0.3
                    )
                    
                    ai_advice = response.choices[0].message.content.strip()
                    
                    return AdvisoryResponse(
                        advisory_type=AdvisoryType.INVESTMENT,  # Default
                        title="Personalized Financial Advice",
                        summary="Comprehensive advice based on your financial profile",
                        detailed_advice=ai_advice,
                        action_items=[
                            "Review the detailed advice carefully",
                            "Prioritize actions based on your current situation",
                            "Consider consulting a financial advisor for complex decisions",
                            "Start with the highest impact recommendations"
                        ],
                        priority="medium",
                        estimated_impact="Variable - depends on implementation",
                        relevant_products=[],
                        follow_up_questions=[
                            "How do I prioritize these recommendations?",
                            "What's the expected timeline for results?",
                            "Should I implement all suggestions at once?"
                        ],
                        confidence_score=0.75,
                        timestamp=datetime.now()
                    )
                except Exception as e:
                    logger.warning(f"OpenAI error in general advice: {e}")
            
            # Fallback to template-based advice using free AI service
            free_advice = await free_ai_service.get_financial_advice(query, asdict(profile))
            
            return AdvisoryResponse(
                advisory_type=AdvisoryType.INVESTMENT,  # Default
                title="Financial Guidance",
                summary="Practical advice for your financial situation",
                detailed_advice=free_advice.get("advice", "General financial guidance provided"),
                action_items=[
                    "Build emergency fund covering 6 months expenses",
                    "Start SIP in diversified mutual funds",
                    "Track expenses and maintain budget",
                    "Review insurance coverage annually"
                ],
                priority="medium",
                estimated_impact="High - Fundamental financial health",
                relevant_products=[
                    {"name": "Equity Mutual Funds", "type": "investment", "returns": "12-15% p.a."},
                    {"name": "PPF", "type": "savings", "returns": "7-8% p.a. (tax-free)"},
                    {"name": "ELSS", "type": "tax_saving", "returns": "12-15% p.a. + tax benefit"}
                ],
                follow_up_questions=[
                    "How do I get started with investing?",
                    "What's the right emergency fund amount?",
                    "How often should I review my finances?"
                ],
                confidence_score=0.7,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating general advice: {e}")
            return self._default_advisory_response(AdvisoryType.SAVINGS)
    
    async def _generate_detailed_advice(self, advice_type: str, profile: FinancialProfile, analysis: Dict[str, Any], *args) -> str:
        """Generate detailed advice content"""
        
        try:
            # Try OpenAI if available
            if self.has_openai and self.openai_client:
                try:
                    base_prompt = f"""
                    Generate detailed financial advice for a {profile.age}-year-old {profile.employment_type} 
                    with ₹{profile.monthly_income:,.0f} monthly income in India.
                    
                    Focus on {advice_type} optimization with specific actionable steps.
                    Include Indian investment options, tax implications, and realistic timelines.
                    
                    Keep the advice practical and implementable.
                    """
                    
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": "You are a certified financial planner specializing in Indian financial markets."
                            },
                            {
                                "role": "user",
                                "content": base_prompt
                            }
                        ],
                        max_tokens=300,
                        temperature=0.2
                    )
                    
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    logger.warning(f"OpenAI error in detailed advice: {e}")
            
            # Fallback to template-based detailed advice
            return self._generate_template_detailed_advice(advice_type, profile, analysis, *args)
            
        except Exception as e:
            logger.error(f"Error generating detailed advice: {e}")
            return f"Detailed {advice_type} advice based on your financial profile and current market conditions."
    
    def _generate_template_detailed_advice(self, advice_type: str, profile: FinancialProfile, analysis: Dict[str, Any], *args) -> str:
        """Generate template-based detailed advice"""
        
        income = profile.monthly_income
        age = profile.age
        
        if advice_type == "savings":
            return f"""
            Based on your ₹{income:,.0f} monthly income, aim to save at least 20% (₹{income * 0.2:,.0f}) monthly.
            
            Priority areas:
            1. Emergency Fund: Build ₹{profile.monthly_expenses * 6:,.0f} in liquid savings
            2. High-yield instruments: Consider FDs or liquid funds for safety
            3. PPF for long-term tax-free growth (₹12,500/month for 80C benefit)
            
            Start with automated transfers on salary day to build discipline.
            """
        
        elif advice_type == "investment":
            equity_percent = 70 if age < 35 else 50 if age < 50 else 30
            return f"""
            Recommended allocation for {age}-year-old investor:
            
            • Equity: {equity_percent}% (₹{income * 0.2 * equity_percent / 100:,.0f}/month in equity MFs)
            • Debt: {100 - equity_percent}% (₹{income * 0.2 * (100 - equity_percent) / 100:,.0f}/month in debt instruments)
            
            Start with large-cap funds, then add mid-cap as portfolio grows.
            Use ELSS for tax saving while building wealth.
            """
        
        elif advice_type == "debt":
            return f"""
            Debt management strategy:
            
            1. List all debts with interest rates
            2. Pay minimum on all, extra on highest interest debt
            3. Consider balance transfer if beneficial
            4. Target debt-free status within 3-5 years
            
            Allocate ₹{income * 0.3:,.0f}/month for debt repayment if possible.
            """
        
        else:
            return f"Focus on {advice_type} optimization with systematic planning and regular review."
    
    def _default_advisory_response(self, advisory_type: AdvisoryType) -> AdvisoryResponse:
        """Return default advisory response for error cases"""
        return AdvisoryResponse(
            advisory_type=advisory_type,
            title="Financial Advisory",
            summary="General financial guidance based on best practices",
            detailed_advice="Focus on building emergency fund, investing regularly, and maintaining good financial discipline.",
            action_items=[
                "Build emergency fund of 6 months expenses",
                "Start SIP in diversified mutual funds",
                "Track expenses and maintain budget",
                "Review insurance coverage"
            ],
            priority="medium",
            estimated_impact="High - Fundamental financial health",
            relevant_products=[],
            follow_up_questions=[
                "How do I get started with investing?",
                "What's the right emergency fund amount?",
                "How often should I review my finances?"
            ],
            confidence_score=0.6,
            timestamp=datetime.now()
        )
    
    async def cache_advisory_response(self, user_id: str, response: AdvisoryResponse):
        """Cache advisory response for quick retrieval"""
        try:
            if self.redis_client:
                cache_key = f"advisory:{user_id}:{response.advisory_type.value}"
                cache_data = asdict(response)
                # Convert datetime to string for JSON serialization
                cache_data["timestamp"] = cache_data["timestamp"].isoformat()
                
                self.redis_client.setex(
                    cache_key,
                    3600,  # 1 hour
                    json.dumps(cache_data)
                )
        except Exception as e:
            logger.error(f"Error caching advisory response: {e}")
    
    async def get_cached_advisory(self, user_id: str, advisory_type: AdvisoryType) -> Optional[AdvisoryResponse]:
        """Get cached advisory response"""
        try:
            if self.redis_client:
                cache_key = f"advisory:{user_id}:{advisory_type.value}"
                cached_data = self.redis_client.get(cache_key)
                
                if cached_data:
                    data = json.loads(cached_data)
                    data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                    data["advisory_type"] = AdvisoryType(data["advisory_type"])
                    
                    return AdvisoryResponse(**data)
                    
        except Exception as e:
            logger.error(f"Error getting cached advisory: {e}")
            
            return None

    async def get_openrouter_balance(self) -> Dict[str, Any]:
        """Get OpenRouter account balance and usage information"""
        try:
            if self.has_openrouter:
                return await openrouter_service.get_account_balance()
            else:
                return {"status": "not_configured", "message": "OpenRouter API key not provided"}
        except Exception as e:
            logger.error(f"Error getting OpenRouter balance: {e}")
            return {"status": "error", "message": str(e)}

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available AI models from OpenRouter"""
        try:
            if self.has_openrouter:
                return await openrouter_service.get_available_models()
            else:
                return []
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []

    async def get_general_advice(self, user_profile: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Get general financial advice based on user query"""
        try:
            # First, try OpenRouter if available
            if self.has_openrouter and not self.use_free_ai_only:
                try:
                    logger.info("Using OpenRouter for general advice")
                    return await openrouter_service.get_financial_advice(query, user_profile)
                except Exception as e:
                    logger.warning(f"OpenRouter failed, falling back: {e}")
            
            # Then try OpenAI if available
            if self.has_openai and self.openai_client:
                try:
                    prompt = f"""
                    You are an expert financial advisor specializing in Indian financial markets and personal finance.
                    
                    User Query: {query}
                    User Profile: {json.dumps(user_profile, indent=2)}
                    
                    Provide helpful, specific financial advice in a conversational tone. 
                    Keep responses concise but informative (2-3 sentences).
                    Include specific Indian financial instruments when relevant (PPF, ELSS, NSE stocks, etc.).
                    Use INR currency formatting.
                    
                    Focus on actionable advice that the user can implement.
                    """
                    
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a helpful financial advisor specializing in Indian markets."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=200,
                        temperature=0.3
                    )
                    
                    advice_text = response.choices[0].message.content.strip()
                    
                    return {
                        "advice": advice_text,
                        "type": "text",
                        "confidence": 0.9,
                        "source": "openai"
                    }
                except Exception as e:
                    logger.warning(f"OpenAI API error, falling back to free AI: {e}")
            
            # Fallback to free AI service
            logger.info("Using free AI service")
            return await free_ai_service.get_financial_advice(query, user_profile)
            
        except Exception as e:
            logger.error(f"Error getting general advice: {e}")
            return {
                "advice": "I'm here to help with your financial questions. Please let me know what specific area you'd like assistance with!",
                "type": "text",
                "confidence": 0.5,
                "source": "fallback"
            }

    async def get_portfolio_advice(self, user_id: str, portfolio_data: Dict[str, Any], specific_query: str) -> Dict[str, Any]:
        """Get portfolio-specific advice"""
        try:
            # First, try OpenRouter if available
            if self.has_openrouter and not self.use_free_ai_only:
                try:
                    logger.info("Using OpenRouter for portfolio advice")
                    return await openrouter_service.get_portfolio_analysis(portfolio_data, specific_query)
                except Exception as e:
                    logger.warning(f"OpenRouter portfolio analysis failed: {e}")
            
            # Then try OpenAI if available
            if self.has_openai and self.openai_client:
                try:
                    prompt = f"""
                    User Query: {specific_query}
                    Portfolio Data: {json.dumps(portfolio_data, indent=2)}
                    
                    Provide specific portfolio advice for an Indian investor.
                    Include recommendations for rebalancing, new investments, or risk management.
                    Mention specific Indian stocks, mutual funds, or ETFs when appropriate.
                    Keep response conversational and actionable.
                    """
                    
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a portfolio advisor specializing in Indian equity and debt markets."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=250,
                        temperature=0.3
                    )
                    
                    return {
                        "advice": response.choices[0].message.content.strip(),
                        "type": "portfolio",
                        "confidence": 0.85,
                        "source": "openai"
                    }
                except Exception as e:
                    logger.warning(f"OpenAI API error, falling back to free AI: {e}")
            
            # Fallback to free AI service
            logger.info("Using free AI for portfolio advice")
            return await free_ai_service.get_portfolio_insights(portfolio_data)
            
        except Exception as e:
            logger.error(f"Error getting portfolio advice: {e}")
            return {
                "advice": "I can help analyze your portfolio. Please share details about your current holdings and investment goals.",
                "type": "text",
                "confidence": 0.5,
                "source": "fallback"
            }

    async def get_goal_advice(self, user_id: str, goals_data: Dict[str, Any], specific_query: str) -> Dict[str, Any]:
        """Get goal-specific financial advice"""
        try:
            # Try OpenAI first if available
            if self.has_openai and self.openai_client:
                try:
                    prompt = f"""
                    User Query: {specific_query}
                    Goals Data: {json.dumps(goals_data, indent=2)}
                    
                    Provide advice on financial goal setting and achievement strategies.
                    Include specific SIP amounts, investment options, and timelines.
                    Mention Indian tax-saving options when relevant (80C, ELSS, PPF).
                    """
                    
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a financial planner specializing in goal-based investing for Indian investors."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=250,
                        temperature=0.3
                    )
                    
                    return {
                        "advice": response.choices[0].message.content.strip(),
                        "type": "goal",
                        "confidence": 0.85,
                        "source": "openai"
                    }
                except Exception as e:
                    logger.warning(f"OpenAI API error, falling back to template advice: {e}")
            
            # Fallback to template-based advice
            return {
                "advice": "I can help you set and achieve financial goals. Consider using SIP calculators to determine monthly investment amounts. For tax-saving goals, explore ELSS, PPF, and NPS options.",
                "type": "goal",
                "confidence": 0.7,
                "source": "template"
            }
            
        except Exception as e:
            logger.error(f"Error getting goal advice: {e}")
            return {
                "advice": "I can help you set and achieve financial goals. What specific goal would you like to work on?",
                "type": "text",
                "confidence": 0.5,
                "source": "fallback"
            }

    async def get_expense_advice(self, user_id: str, expense_data: Dict[str, Any], specific_query: str) -> Dict[str, Any]:
        """Get expense management advice"""
        try:
            # First, try OpenRouter if available
            if self.has_openrouter and not self.use_free_ai_only:
                try:
                    logger.info("Using OpenRouter for expense advice")
                    return await openrouter_service.get_financial_advice(
                        f"Expense management query: {specific_query}", 
                        {"expense_data": expense_data}
                    )
                except Exception as e:
                    logger.warning(f"OpenRouter expense advice failed: {e}")
            
            # Then try OpenAI if available
            if self.has_openai and self.openai_client:
                try:
                    prompt = f"""
                    User Query: {specific_query}
                    Expense Data: {json.dumps(expense_data, indent=2)}
                    
                    Provide advice on expense management and budgeting.
                    Include specific tips for reducing expenses in Indian context.
                    Suggest apps, strategies, or lifestyle changes.
                    """
                    
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a financial advisor specializing in expense management and budgeting for Indian households."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=250,
                        temperature=0.3
                    )
                    
                    return {
                        "advice": response.choices[0].message.content.strip(),
                        "type": "expense",
                        "confidence": 0.85,
                        "source": "openai"
                    }
                except Exception as e:
                    logger.warning(f"OpenAI API error, falling back to free AI: {e}")
            
            # Fallback to free AI service
            logger.info("Using free AI for expense advice")
            return await free_ai_service.get_expense_insights(expense_data)
            
        except Exception as e:
            logger.error(f"Error getting expense advice: {e}")
            return {
                "advice": "I can help you manage your expenses better. What specific area of spending would you like to optimize?",
                "type": "text",
                "confidence": 0.5,
                "source": "fallback"
            }

# Utility functions
async def create_financial_profile_from_data(user_data: Dict[str, Any]) -> FinancialProfile:
    """Create financial profile from user data"""
    return FinancialProfile(
        user_id=user_data.get("user_id", ""),
        age=user_data.get("age", 30),
        monthly_income=user_data.get("monthly_income", 0),
        monthly_expenses=user_data.get("monthly_expenses", 0),
        current_savings=user_data.get("current_savings", 0),
        debt_amount=user_data.get("debt_amount", 0),
        risk_tolerance=user_data.get("risk_tolerance", "moderate"),
        financial_goals=user_data.get("financial_goals", []),
        dependents=user_data.get("dependents", 0),
        employment_type=user_data.get("employment_type", "salaried"),
        location=user_data.get("location", "bangalore")
    )
