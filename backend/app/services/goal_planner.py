"""
Goal Planner & Investment Recommender Service
SIP planning and investment recommendations for Indian market
"""

import json
import logging
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import openai
from decouple import config
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class GoalType(Enum):
    HOUSE = "house"
    CAR = "car"
    EDUCATION = "education"
    WEDDING = "wedding"
    VACATION = "vacation"
    RETIREMENT = "retirement"
    EMERGENCY = "emergency"
    GENERAL = "general"

class RiskProfile(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

@dataclass
class FinancialGoal:
    id: str
    name: str
    goal_type: GoalType
    target_amount: float
    target_date: datetime
    current_amount: float
    monthly_contribution: float
    priority: int  # 1 = highest priority
    description: str
    is_flexible: bool  # Can target date be adjusted?

@dataclass
class SIPRecommendation:
    goal_id: str
    fund_name: str
    fund_type: str
    recommended_amount: float
    expected_return: float
    risk_level: str
    fund_category: str
    why_recommended: str
    expense_ratio: float
    fund_house: str
    min_sip: float
    lock_in_period: Optional[str]

@dataclass
class GoalAnalysis:
    goal: FinancialGoal
    feasibility: str  # feasible, challenging, not_feasible
    required_monthly_sip: float
    projected_final_amount: float
    shortfall_amount: float
    alternative_strategies: List[str]
    recommended_funds: List[SIPRecommendation]
    probability_of_success: float

class GoalPlannerService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=config("OPENAI_API_KEY"))
        
        # Indian mutual fund database (simplified)
        self.indian_mutual_funds = self._load_indian_funds()
        
        # Expected returns by asset class
        self.expected_returns = {
            "equity_large_cap": 12.0,
            "equity_mid_cap": 14.0,
            "equity_small_cap": 16.0,
            "equity_multi_cap": 13.0,
            "debt_funds": 7.5,
            "hybrid_funds": 10.0,
            "gold_funds": 8.0,
            "international_funds": 11.0,
            "index_funds": 11.5,
            "elss": 13.5
        }
        
        # Risk-return mapping
        self.risk_categories = {
            RiskProfile.CONSERVATIVE: ["debt_funds", "hybrid_funds", "equity_large_cap"],
            RiskProfile.MODERATE: ["equity_large_cap", "equity_multi_cap", "hybrid_funds", "index_funds"],
            RiskProfile.AGGRESSIVE: ["equity_mid_cap", "equity_small_cap", "equity_multi_cap", "international_funds"]
        }
    
    def _load_indian_funds(self) -> Dict[str, Dict[str, Any]]:
        """Load popular Indian mutual funds database"""
        return {
            # Large Cap Equity Funds
            "hdfc_top_100": {
                "name": "HDFC Top 100 Fund",
                "type": "equity_large_cap",
                "fund_house": "HDFC Mutual Fund",
                "expense_ratio": 1.8,
                "min_sip": 500,
                "expected_return": 12.0,
                "risk": "moderate",
                "aum": "₹25,000 Cr",
                "lock_in": None,
                "category": "Large Cap"
            },
            "icici_bluechip": {
                "name": "ICICI Prudential Bluechip Fund",
                "type": "equity_large_cap",
                "fund_house": "ICICI Prudential MF",
                "expense_ratio": 1.9,
                "min_sip": 1000,
                "expected_return": 11.8,
                "risk": "moderate",
                "aum": "₹30,000 Cr",
                "lock_in": None,
                "category": "Large Cap"
            },
            
            # Multi Cap Funds
            "sbi_multi_cap": {
                "name": "SBI Multi Cap Fund",
                "type": "equity_multi_cap",
                "fund_house": "SBI Mutual Fund",
                "expense_ratio": 1.7,
                "min_sip": 500,
                "expected_return": 13.0,
                "risk": "moderate_high",
                "aum": "₹15,000 Cr",
                "lock_in": None,
                "category": "Multi Cap"
            },
            
            # Mid Cap Funds
            "hdfc_mid_cap": {
                "name": "HDFC Mid-Cap Opportunities Fund",
                "type": "equity_mid_cap",
                "fund_house": "HDFC Mutual Fund",
                "expense_ratio": 2.0,
                "min_sip": 500,
                "expected_return": 14.5,
                "risk": "high",
                "aum": "₹18,000 Cr",
                "lock_in": None,
                "category": "Mid Cap"
            },
            
            # Small Cap Funds
            "axis_small_cap": {
                "name": "Axis Small Cap Fund",
                "type": "equity_small_cap",
                "fund_house": "Axis Mutual Fund",
                "expense_ratio": 2.1,
                "min_sip": 500,
                "expected_return": 16.0,
                "risk": "very_high",
                "aum": "₹12,000 Cr",
                "lock_in": None,
                "category": "Small Cap"
            },
            
            # ELSS Funds
            "axis_long_term_equity": {
                "name": "Axis Long Term Equity Fund",
                "type": "elss",
                "fund_house": "Axis Mutual Fund",
                "expense_ratio": 1.8,
                "min_sip": 500,
                "expected_return": 13.5,
                "risk": "moderate_high",
                "aum": "₹25,000 Cr",
                "lock_in": "3 years",
                "category": "ELSS",
                "tax_benefit": "80C"
            },
            "mirae_tax_saver": {
                "name": "Mirae Asset Tax Saver Fund",
                "type": "elss",
                "fund_house": "Mirae Asset MF",
                "expense_ratio": 1.5,
                "min_sip": 500,
                "expected_return": 14.0,
                "risk": "moderate_high",
                "aum": "₹20,000 Cr",
                "lock_in": "3 years",
                "category": "ELSS",
                "tax_benefit": "80C"
            },
            
            # Debt Funds
            "hdfc_short_term_debt": {
                "name": "HDFC Short Term Debt Fund",
                "type": "debt_funds",
                "fund_house": "HDFC Mutual Fund",
                "expense_ratio": 1.2,
                "min_sip": 1000,
                "expected_return": 7.5,
                "risk": "low",
                "aum": "₹10,000 Cr",
                "lock_in": None,
                "category": "Debt"
            },
            
            # Hybrid Funds
            "hdfc_balanced_advantage": {
                "name": "HDFC Balanced Advantage Fund",
                "type": "hybrid_funds",
                "fund_house": "HDFC Mutual Fund",
                "expense_ratio": 1.6,
                "min_sip": 500,
                "expected_return": 10.5,
                "risk": "moderate",
                "aum": "₹35,000 Cr",
                "lock_in": None,
                "category": "Hybrid"
            },
            
            # Index Funds
            "utm_nifty_50": {
                "name": "UTI Nifty 50 Index Fund",
                "type": "index_funds",
                "fund_house": "UTI Mutual Fund",
                "expense_ratio": 0.2,
                "min_sip": 500,
                "expected_return": 11.5,
                "risk": "moderate",
                "aum": "₹8,000 Cr",
                "lock_in": None,
                "category": "Index"
            },
            
            # International Funds
            "motilal_nasdaq_100": {
                "name": "Motilal Oswal NASDAQ 100 Fund",
                "type": "international_funds",
                "fund_house": "Motilal Oswal MF",
                "expense_ratio": 1.9,
                "min_sip": 500,
                "expected_return": 11.0,
                "risk": "high",
                "aum": "₹5,000 Cr",
                "lock_in": None,
                "category": "International"
            }
        }
    
    async def analyze_goal(
        self, 
        goal: FinancialGoal, 
        user_profile: Dict[str, Any]
    ) -> GoalAnalysis:
        """Analyze a financial goal and provide recommendations"""
        
        try:
            # Calculate time to goal
            months_to_goal = self._calculate_months_to_goal(goal.target_date)
            
            # Calculate required SIP amount
            required_sip = self._calculate_required_sip(
                goal.target_amount, 
                goal.current_amount, 
                months_to_goal
            )
            
            # Assess feasibility
            feasibility = self._assess_goal_feasibility(
                required_sip, 
                user_profile.get("available_for_investment", 0)
            )
            
            # Get fund recommendations
            recommended_funds = await self._recommend_funds_for_goal(
                goal, 
                user_profile, 
                required_sip
            )
            
            # Calculate projected amounts
            projected_amount = self._calculate_projected_amount(
                goal.current_amount,
                goal.monthly_contribution or required_sip,
                months_to_goal,
                self._get_expected_return_for_goal(goal, user_profile)
            )
            
            # Calculate shortfall
            shortfall = max(0, goal.target_amount - projected_amount)
            
            # Generate alternative strategies
            alternatives = await self._generate_alternative_strategies(
                goal, user_profile, feasibility, shortfall
            )
            
            # Calculate probability of success
            success_probability = self._calculate_success_probability(
                feasibility, goal.goal_type, months_to_goal
            )
            
            return GoalAnalysis(
                goal=goal,
                feasibility=feasibility,
                required_monthly_sip=required_sip,
                projected_final_amount=projected_amount,
                shortfall_amount=shortfall,
                alternative_strategies=alternatives,
                recommended_funds=recommended_funds,
                probability_of_success=success_probability
            )
            
        except Exception as e:
            logger.error(f"Error analyzing goal: {e}")
            return self._default_goal_analysis(goal)
    
    def _calculate_months_to_goal(self, target_date: datetime) -> float:
        """Calculate months between now and target date"""
        today = datetime.now()
        if target_date <= today:
            return 1  # Minimum 1 month
        
        delta = target_date - today
        return delta.days / 30.44  # Average days per month
    
    def _calculate_required_sip(
        self, 
        target_amount: float, 
        current_amount: float, 
        months: float,
        expected_return: float = 12.0
    ) -> float:
        """Calculate required monthly SIP amount"""
        
        # Amount still needed
        future_value_needed = target_amount - self._calculate_future_value(
            current_amount, months, expected_return
        )
        
        if future_value_needed <= 0:
            return 0  # Goal already achieved
        
        # Monthly return rate
        monthly_rate = expected_return / (12 * 100)
        
        if monthly_rate == 0:
            return future_value_needed / months
        
        # SIP calculation: FV = PMT * [((1 + r)^n - 1) / r]
        # PMT = FV * r / ((1 + r)^n - 1)
        sip_amount = future_value_needed * monthly_rate / ((1 + monthly_rate) ** months - 1)
        
        return max(500, sip_amount)  # Minimum SIP of ₹500
    
    def _calculate_future_value(self, present_value: float, months: float, annual_return: float) -> float:
        """Calculate future value of current amount"""
        monthly_rate = annual_return / (12 * 100)
        return present_value * ((1 + monthly_rate) ** months)
    
    def _calculate_projected_amount(
        self, 
        current_amount: float, 
        monthly_sip: float, 
        months: float, 
        annual_return: float
    ) -> float:
        """Calculate projected final amount"""
        
        # Future value of current amount
        fv_current = self._calculate_future_value(current_amount, months, annual_return)
        
        # Future value of SIP
        monthly_rate = annual_return / (12 * 100)
        if monthly_rate == 0:
            fv_sip = monthly_sip * months
        else:
            fv_sip = monthly_sip * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        
        return fv_current + fv_sip
    
    def _assess_goal_feasibility(self, required_sip: float, available_amount: float) -> str:
        """Assess if goal is feasible based on available investment amount"""
        
        if required_sip <= available_amount * 0.7:
            return "feasible"
        elif required_sip <= available_amount * 1.2:
            return "challenging"
        else:
            return "not_feasible"
    
    def _get_expected_return_for_goal(self, goal: FinancialGoal, user_profile: Dict[str, Any]) -> float:
        """Get expected return based on goal type and user profile"""
        
        risk_tolerance = user_profile.get("risk_tolerance", "moderate")
        time_horizon = self._calculate_months_to_goal(goal.target_date) / 12  # years
        
        # Conservative approach for short-term goals
        if time_horizon < 3:
            return 8.0  # Debt funds and conservative hybrid
        elif time_horizon < 7:
            return 10.0 if risk_tolerance == "conservative" else 12.0
        else:
            if risk_tolerance == "conservative":
                return 10.0
            elif risk_tolerance == "aggressive":
                return 14.0
            else:
                return 12.0
    
    async def _recommend_funds_for_goal(
        self, 
        goal: FinancialGoal, 
        user_profile: Dict[str, Any], 
        required_sip: float
    ) -> List[SIPRecommendation]:
        """Recommend mutual funds for the goal"""
        
        risk_tolerance = RiskProfile(user_profile.get("risk_tolerance", "moderate"))
        time_horizon = self._calculate_months_to_goal(goal.target_date) / 12
        
        # Select appropriate fund categories
        suitable_categories = self._select_fund_categories(risk_tolerance, time_horizon, goal.goal_type)
        
        recommendations = []
        
        for category in suitable_categories[:3]:  # Top 3 categories
            best_fund = self._select_best_fund_in_category(category, required_sip)
            if best_fund:
                recommendation = self._create_sip_recommendation(
                    goal, best_fund, required_sip, category
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _select_fund_categories(
        self, 
        risk_profile: RiskProfile, 
        time_horizon: float, 
        goal_type: GoalType
    ) -> List[str]:
        """Select appropriate fund categories based on profile and goal"""
        
        categories = []
        
        # Time-based selection
        if time_horizon < 3:
            # Short term: Conservative approach
            categories = ["debt_funds", "hybrid_funds", "equity_large_cap"]
        elif time_horizon < 7:
            # Medium term: Balanced approach
            categories = ["equity_large_cap", "hybrid_funds", "equity_multi_cap"]
        else:
            # Long term: Can take more risk
            categories = ["equity_multi_cap", "equity_large_cap", "equity_mid_cap"]
        
        # Risk profile adjustment
        risk_suitable = self.risk_categories[risk_profile]
        categories = [cat for cat in categories if cat in risk_suitable]
        
        # Goal-specific adjustments
        if goal_type == GoalType.RETIREMENT:
            categories.insert(0, "elss")  # Tax saving benefit
        elif goal_type == GoalType.EDUCATION and time_horizon > 10:
            categories.insert(0, "equity_mid_cap")  # Higher growth potential
        elif goal_type == GoalType.EMERGENCY:
            categories = ["debt_funds", "hybrid_funds"]  # Safety first
        
        return categories
    
    def _select_best_fund_in_category(self, category: str, required_sip: float) -> Optional[Dict[str, Any]]:
        """Select the best fund in a given category"""
        
        suitable_funds = [
            (fund_id, fund_data) for fund_id, fund_data in self.indian_mutual_funds.items()
            if fund_data["type"] == category and fund_data["min_sip"] <= required_sip
        ]
        
        if not suitable_funds:
            # Fallback: find funds with lower minimum SIP
            suitable_funds = [
                (fund_id, fund_data) for fund_id, fund_data in self.indian_mutual_funds.items()
                if fund_data["type"] == category
            ]
        
        if suitable_funds:
            # Select based on expected return and expense ratio
            best_fund = max(
                suitable_funds,
                key=lambda x: x[1]["expected_return"] - x[1]["expense_ratio"]
            )
            return {"id": best_fund[0], **best_fund[1]}
        
        return None
    
    def _create_sip_recommendation(
        self, 
        goal: FinancialGoal, 
        fund: Dict[str, Any], 
        required_sip: float, 
        category: str
    ) -> SIPRecommendation:
        """Create SIP recommendation object"""
        
        # Adjust recommended amount based on fund minimum
        recommended_amount = max(fund["min_sip"], required_sip / 3)  # Divide among 3 funds
        
        # Generate recommendation reason
        why_recommended = self._generate_recommendation_reason(fund, goal, category)
        
        return SIPRecommendation(
            goal_id=goal.id,
            fund_name=fund["name"],
            fund_type=fund["category"],
            recommended_amount=recommended_amount,
            expected_return=fund["expected_return"],
            risk_level=fund["risk"],
            fund_category=category,
            why_recommended=why_recommended,
            expense_ratio=fund["expense_ratio"],
            fund_house=fund["fund_house"],
            min_sip=fund["min_sip"],
            lock_in_period=fund.get("lock_in")
        )
    
    def _generate_recommendation_reason(self, fund: Dict[str, Any], goal: FinancialGoal, category: str) -> str:
        """Generate explanation for why this fund is recommended"""
        
        reasons = []
        
        # Performance reason
        if fund["expected_return"] > 12:
            reasons.append(f"High growth potential ({fund['expected_return']}% expected return)")
        elif fund["expected_return"] > 8:
            reasons.append(f"Balanced growth approach ({fund['expected_return']}% expected return)")
        else:
            reasons.append(f"Stable returns with lower risk ({fund['expected_return']}% expected return)")
        
        # Cost efficiency
        if fund["expense_ratio"] < 1.5:
            reasons.append("Low expense ratio")
        
        # Fund house reputation
        reputed_houses = ["HDFC", "ICICI", "SBI", "Axis", "UTI"]
        if any(house in fund["fund_house"] for house in reputed_houses):
            reasons.append("Reputed fund house")
        
        # Goal-specific reasons
        time_horizon = self._calculate_months_to_goal(goal.target_date) / 12
        
        if goal.goal_type == GoalType.RETIREMENT and "elss" in category:
            reasons.append("Tax saving benefit under 80C")
        elif time_horizon < 3 and "debt" in category:
            reasons.append("Suitable for short-term goals")
        elif time_horizon > 7 and "equity" in category:
            reasons.append("Long-term wealth creation potential")
        
        return "; ".join(reasons[:3])  # Limit to 3 reasons
    
    async def _generate_alternative_strategies(
        self, 
        goal: FinancialGoal, 
        user_profile: Dict[str, Any], 
        feasibility: str, 
        shortfall: float
    ) -> List[str]:
        """Generate alternative strategies for achieving the goal"""
        
        strategies = []
        
        if feasibility == "not_feasible":
            strategies.extend([
                f"Extend target date by 1-2 years to reduce required SIP",
                f"Reduce target amount by ₹{shortfall * 0.3:,.0f} (30%)",
                "Increase monthly income through side hustle or upskilling",
                "Consider higher-risk investments for better returns"
            ])
        elif feasibility == "challenging":
            strategies.extend([
                "Start with smaller SIP and increase by 10% annually",
                "Use windfalls (bonus, tax refund) for lump sum investments",
                "Review and reduce unnecessary expenses",
                "Consider step-up SIP to gradually increase investment"
            ])
        else:  # feasible
            strategies.extend([
                "Consider additional lump sum investments when possible",
                "Automate SIP to ensure disciplined investing",
                "Review and rebalance portfolio annually",
                "Stay invested for the entire duration"
            ])
        
        # Goal-specific strategies
        if goal.goal_type == GoalType.HOUSE:
            strategies.append("Explore home loan options to reduce cash requirement")
        elif goal.goal_type == GoalType.CAR:
            strategies.append("Consider certified pre-owned vehicles to reduce cost")
        elif goal.goal_type == GoalType.EDUCATION:
            strategies.append("Research education loans and scholarships")
        
        return strategies[:5]  # Limit to 5 strategies
    
    def _calculate_success_probability(
        self, 
        feasibility: str, 
        goal_type: GoalType, 
        months_to_goal: float
    ) -> float:
        """Calculate probability of achieving the goal"""
        
        base_probability = {
            "feasible": 0.85,
            "challenging": 0.65,
            "not_feasible": 0.35
        }[feasibility]
        
        # Adjust based on time horizon
        time_factor = min(1.0, months_to_goal / 60)  # 5 years = optimal
        base_probability *= (0.7 + 0.3 * time_factor)
        
        # Adjust based on goal type (some goals are more achievable)
        goal_adjustments = {
            GoalType.EMERGENCY: 0.1,      # Easier to achieve
            GoalType.CAR: 0.05,           # Moderate
            GoalType.VACATION: 0.1,       # Easier
            GoalType.EDUCATION: 0.0,      # Moderate
            GoalType.HOUSE: -0.05,        # Harder
            GoalType.RETIREMENT: -0.1,    # Harder due to long timeline
            GoalType.WEDDING: 0.05,       # Moderate
            GoalType.GENERAL: 0.0         # Neutral
        }
        
        adjustment = goal_adjustments.get(goal_type, 0.0)
        final_probability = max(0.1, min(0.95, base_probability + adjustment))
        
        return final_probability
    
    def _default_goal_analysis(self, goal: FinancialGoal) -> GoalAnalysis:
        """Return default goal analysis for error cases"""
        return GoalAnalysis(
            goal=goal,
            feasibility="challenging",
            required_monthly_sip=5000.0,
            projected_final_amount=goal.target_amount * 0.8,
            shortfall_amount=goal.target_amount * 0.2,
            alternative_strategies=[
                "Review goal timeline and amount",
                "Consider professional financial advice",
                "Start with systematic investment planning"
            ],
            recommended_funds=[],
            probability_of_success=0.6
        )
    
    async def generate_comprehensive_goal_plan(
        self, 
        goals: List[FinancialGoal], 
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive plan for multiple goals"""
        
        try:
            # Analyze each goal
            goal_analyses = []
            for goal in goals:
                analysis = await self.analyze_goal(goal, user_profile)
                goal_analyses.append(analysis)
            
            # Calculate total investment required
            total_required_sip = sum(analysis.required_monthly_sip for analysis in goal_analyses)
            available_amount = user_profile.get("available_for_investment", 0)
            
            # Prioritize goals
            prioritized_goals = self._prioritize_goals(goal_analyses, available_amount)
            
            # Generate allocation strategy
            allocation_strategy = self._generate_allocation_strategy(prioritized_goals, available_amount)
            
            # Overall assessment
            overall_assessment = self._assess_overall_plan(goal_analyses, total_required_sip, available_amount)
            
            return {
                "goal_analyses": goal_analyses,
                "total_required_sip": total_required_sip,
                "available_amount": available_amount,
                "prioritized_goals": prioritized_goals,
                "allocation_strategy": allocation_strategy,
                "overall_assessment": overall_assessment,
                "recommendations": self._generate_overall_recommendations(goal_analyses, user_profile)
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive goal plan: {e}")
            return {"error": str(e)}
    
    def _prioritize_goals(self, goal_analyses: List[GoalAnalysis], available_amount: float) -> List[Dict[str, Any]]:
        """Prioritize goals based on urgency, feasibility, and importance"""
        
        prioritized = []
        
        for analysis in goal_analyses:
            goal = analysis.goal
            
            # Calculate priority score
            urgency_score = self._calculate_urgency_score(goal.target_date)
            importance_score = self._calculate_importance_score(goal.goal_type)
            feasibility_score = {"feasible": 1.0, "challenging": 0.7, "not_feasible": 0.3}[analysis.feasibility]
            
            overall_score = (urgency_score * 0.4 + importance_score * 0.3 + feasibility_score * 0.3)
            
            prioritized.append({
                "goal": goal,
                "analysis": analysis,
                "priority_score": overall_score,
                "recommended_allocation": min(analysis.required_monthly_sip, available_amount * 0.4)
            })
        
        # Sort by priority score
        prioritized.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return prioritized
    
    def _calculate_urgency_score(self, target_date: datetime) -> float:
        """Calculate urgency score based on target date"""
        months_to_goal = self._calculate_months_to_goal(target_date)
        
        if months_to_goal < 12:
            return 1.0  # Very urgent
        elif months_to_goal < 36:
            return 0.8  # Urgent
        elif months_to_goal < 60:
            return 0.6  # Moderate
        elif months_to_goal < 120:
            return 0.4  # Low urgency
        else:
            return 0.2  # Very low urgency
    
    def _calculate_importance_score(self, goal_type: GoalType) -> float:
        """Calculate importance score based on goal type"""
        importance_mapping = {
            GoalType.EMERGENCY: 1.0,      # Highest importance
            GoalType.RETIREMENT: 0.9,     # Very important
            GoalType.EDUCATION: 0.8,      # Important
            GoalType.HOUSE: 0.7,          # Important
            GoalType.WEDDING: 0.6,        # Moderate
            GoalType.CAR: 0.5,            # Moderate
            GoalType.VACATION: 0.3,       # Lower importance
            GoalType.GENERAL: 0.4         # Variable
        }
        
        return importance_mapping.get(goal_type, 0.5)
    
    def _generate_allocation_strategy(self, prioritized_goals: List[Dict[str, Any]], available_amount: float) -> Dict[str, Any]:
        """Generate investment allocation strategy across goals"""
        
        if not prioritized_goals:
            return {"error": "No goals to allocate"}
        
        strategy = {
            "total_allocation": 0,
            "goal_allocations": [],
            "remaining_amount": available_amount,
            "strategy_notes": []
        }
        
        remaining_amount = available_amount
        
        for item in prioritized_goals:
            goal = item["goal"]
            analysis = item["analysis"]
            
            if remaining_amount <= 0:
                break
            
            # Allocate based on priority and feasibility
            if analysis.feasibility == "feasible":
                allocated_amount = min(analysis.required_monthly_sip, remaining_amount)
            elif analysis.feasibility == "challenging":
                allocated_amount = min(analysis.required_monthly_sip * 0.7, remaining_amount)
            else:  # not_feasible
                allocated_amount = min(remaining_amount * 0.2, analysis.required_monthly_sip * 0.5)
            
            if allocated_amount >= 500:  # Minimum SIP amount
                strategy["goal_allocations"].append({
                    "goal_name": goal.name,
                    "goal_id": goal.id,
                    "allocated_amount": allocated_amount,
                    "required_amount": analysis.required_monthly_sip,
                    "allocation_percentage": (allocated_amount / analysis.required_monthly_sip) * 100,
                    "recommended_funds": analysis.recommended_funds[:2]  # Top 2 funds
                })
                
                remaining_amount -= allocated_amount
                strategy["total_allocation"] += allocated_amount
        
        strategy["remaining_amount"] = remaining_amount
        
        # Add strategy notes
        if remaining_amount > 1000:
            strategy["strategy_notes"].append(f"₹{remaining_amount:,.0f} available for additional goals or emergency fund")
        
        if strategy["total_allocation"] < available_amount * 0.8:
            strategy["strategy_notes"].append("Consider increasing investment amount to achieve goals faster")
        
        return strategy
    
    def _assess_overall_plan(self, goal_analyses: List[GoalAnalysis], total_required: float, available: float) -> Dict[str, Any]:
        """Assess the overall financial plan"""
        
        feasible_goals = len([a for a in goal_analyses if a.feasibility == "feasible"])
        total_goals = len(goal_analyses)
        
        if total_required <= available:
            assessment = "excellent"
            message = "All goals are achievable with current investment capacity"
        elif total_required <= available * 1.3:
            assessment = "good"
            message = "Most goals achievable with minor adjustments"
        elif total_required <= available * 2.0:
            assessment = "challenging"
            message = "Significant planning required to achieve goals"
        else:
            assessment = "difficult"
            message = "Goals need major revision or timeline extension"
        
        return {
            "assessment": assessment,
            "message": message,
            "feasible_goals_ratio": feasible_goals / total_goals if total_goals > 0 else 0,
            "investment_gap": max(0, total_required - available),
            "over_allocation": max(0, total_required / available - 1) * 100 if available > 0 else 0
        }
    
    def _generate_overall_recommendations(self, goal_analyses: List[GoalAnalysis], user_profile: Dict[str, Any]) -> List[str]:
        """Generate overall recommendations for the financial plan"""
        
        recommendations = []
        
        # Based on overall assessment
        total_required = sum(a.required_monthly_sip for a in goal_analyses)
        available = user_profile.get("available_for_investment", 0)
        
        if total_required > available * 1.5:
            recommendations.append("Consider extending goal timelines to reduce monthly investment burden")
            recommendations.append("Look for ways to increase monthly income or reduce expenses")
        
        # Based on goal types
        goal_types = [a.goal.goal_type for a in goal_analyses]
        
        if GoalType.EMERGENCY not in goal_types:
            recommendations.append("Add emergency fund as highest priority goal (6-12 months expenses)")
        
        if GoalType.RETIREMENT not in goal_types and user_profile.get("age", 30) > 25:
            recommendations.append("Start retirement planning early to benefit from compounding")
        
        # Based on risk profile
        risk_tolerance = user_profile.get("risk_tolerance", "moderate")
        if risk_tolerance == "conservative" and any(a.goal.target_date > datetime.now() + timedelta(days=2555) for a in goal_analyses):
            recommendations.append("Consider moderate risk investments for long-term goals to beat inflation")
        
        # Investment discipline
        recommendations.extend([
            "Set up automatic SIP to ensure disciplined investing",
            "Review and rebalance portfolio annually",
            "Increase SIP by 10-15% annually with salary increments"
        ])
        
        return recommendations[:6]  # Limit to 6 recommendations

# Utility functions
def create_goal_from_voice_input(voice_text: str, user_id: str) -> FinancialGoal:
    """Create financial goal from voice input like 'Save for Car 500000'"""
    
    # Simple parsing - in production, use NLP
    words = voice_text.lower().split()
    
    # Extract goal type
    goal_type = GoalType.GENERAL
    if "car" in words:
        goal_type = GoalType.CAR
    elif "house" in words or "home" in words:
        goal_type = GoalType.HOUSE
    elif "education" in words:
        goal_type = GoalType.EDUCATION
    elif "wedding" in words:
        goal_type = GoalType.WEDDING
    elif "vacation" in words:
        goal_type = GoalType.VACATION
    elif "retirement" in words:
        goal_type = GoalType.RETIREMENT
    elif "emergency" in words:
        goal_type = GoalType.EMERGENCY
    
    # Extract amount (simple regex)
    import re
    amount_match = re.search(r'(\d+)', voice_text)
    target_amount = float(amount_match.group(1)) if amount_match else 100000
    
    # Default timeline based on goal type
    timeline_mapping = {
        GoalType.CAR: 24,
        GoalType.HOUSE: 60,
        GoalType.EDUCATION: 36,
        GoalType.WEDDING: 24,
        GoalType.VACATION: 12,
        GoalType.RETIREMENT: 360,
        GoalType.EMERGENCY: 6,
        GoalType.GENERAL: 36
    }
    
    months_ahead = timeline_mapping[goal_type]
    target_date = datetime.now() + timedelta(days=months_ahead * 30)
    
    return FinancialGoal(
        id=f"goal_{user_id}_{int(datetime.now().timestamp())}",
        name=f"{goal_type.value.title()} Goal",
        goal_type=goal_type,
        target_amount=target_amount,
        target_date=target_date,
        current_amount=0,
        monthly_contribution=0,
        priority=1,
        description=f"Goal created from voice input: {voice_text}",
        is_flexible=True
    )

def format_sip_recommendation_for_display(recommendation: SIPRecommendation) -> Dict[str, Any]:
    """Format SIP recommendation for frontend display"""
    return {
        "fund_name": recommendation.fund_name,
        "fund_house": recommendation.fund_house,
        "category": recommendation.fund_category,
        "recommended_amount": recommendation.recommended_amount,
        "min_sip": recommendation.min_sip,
        "expected_return": recommendation.expected_return,
        "risk_level": recommendation.risk_level,
        "expense_ratio": recommendation.expense_ratio,
        "lock_in_period": recommendation.lock_in_period,
        "why_recommended": recommendation.why_recommended,
        "monthly_sip_formatted": f"₹{recommendation.recommended_amount:,.0f}",
        "return_formatted": f"{recommendation.expected_return}% p.a.",
        "expense_formatted": f"{recommendation.expense_ratio}%"
    }
