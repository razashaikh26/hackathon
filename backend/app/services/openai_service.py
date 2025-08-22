import openai
import asyncio
import json
from typing import Dict, Any, List, Optional
from app.core.config import settings

class OpenAIService:
    """
    Service for OpenAI API integration
    Provides NLP capabilities and personalized insights
    """
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-3.5-turbo"
    
    async def generate_personalized_insights(self, user_data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Generate personalized financial insights using OpenAI"""
        if not settings.OPENAI_API_KEY:
            return self._generate_fallback_insights(user_data, analysis)
        
        try:
            prompt = self._create_insights_prompt(user_data, analysis)
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional financial advisor AI. Provide personalized, actionable financial insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            insights_text = response.choices[0].message.content
            insights = [insight.strip() for insight in insights_text.split('\n') if insight.strip()]
            
            return insights[:5]  # Return top 5 insights
            
        except Exception as e:
            print(f"Error generating OpenAI insights: {e}")
            return self._generate_fallback_insights(user_data, analysis)
    
    async def analyze_financial_text(self, text: str) -> Dict[str, Any]:
        """Analyze financial text for sentiment and key information"""
        if not settings.OPENAI_API_KEY:
            return {'sentiment': 'neutral', 'key_points': []}
        
        try:
            prompt = f"""
            Analyze the following financial text and provide:
            1. Sentiment (positive, negative, neutral)
            2. Key financial topics mentioned
            3. Any numerical data or percentages
            4. Risk level assessment (low, medium, high)
            
            Text: {text}
            
            Respond in JSON format.
            """
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial text analyst. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error analyzing financial text: {e}")
            return {
                'sentiment': 'neutral',
                'key_points': [],
                'risk_level': 'medium'
            }
    
    async def generate_goal_recommendations(self, goal_data: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations for achieving financial goals"""
        if not settings.OPENAI_API_KEY:
            return self._generate_fallback_goal_recommendations(goal_data)
        
        try:
            prompt = f"""
            Based on the following user profile and financial goal, provide specific recommendations:
            
            User Profile:
            - Age: {user_profile.get('age', 'Unknown')}
            - Annual Income: ${user_profile.get('annual_income', 0):,}
            - Risk Tolerance: {user_profile.get('risk_tolerance', 'Moderate')}
            
            Goal:
            - Goal: {goal_data.get('name', 'Unknown')}
            - Target Amount: ${goal_data.get('target_amount', 0):,}
            - Time Frame: {goal_data.get('time_frame', 'Unknown')}
            - Current Amount: ${goal_data.get('current_amount', 0):,}
            
            Provide:
            1. Monthly savings requirement
            2. Investment strategy recommendations
            3. Timeline feasibility assessment
            4. Alternative approaches
            5. Risk considerations
            
            Respond in JSON format with clear, actionable advice.
            """
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a certified financial planner. Provide practical, personalized advice in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.5
            )
            
            recommendations = json.loads(response.choices[0].message.content)
            return recommendations
            
        except Exception as e:
            print(f"Error generating goal recommendations: {e}")
            return self._generate_fallback_goal_recommendations(goal_data)
    
    async def explain_financial_concept(self, concept: str, user_level: str = "intermediate") -> str:
        """Explain financial concepts in user-friendly terms"""
        if not settings.OPENAI_API_KEY:
            return f"Financial concept: {concept}. Please consult a financial advisor for detailed explanation."
        
        try:
            prompt = f"""
            Explain the financial concept "{concept}" in simple terms for someone with {user_level} financial knowledge.
            Make it practical and actionable. Use examples where helpful.
            Keep the explanation under 200 words.
            """
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial educator. Explain concepts clearly and simply."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.6
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error explaining concept {concept}: {e}")
            return f"Unable to explain {concept} at this time. Please consult financial resources."
    
    async def optimize_tax_strategy(self, financial_data: Dict[str, Any]) -> List[str]:
        """Generate tax optimization strategies"""
        if not settings.OPENAI_API_KEY:
            return self._generate_fallback_tax_strategies()
        
        try:
            prompt = f"""
            Based on this financial profile, suggest tax optimization strategies:
            
            Income: ${financial_data.get('annual_income', 0):,}
            Investment Gains/Losses: ${financial_data.get('investment_gains', 0):,}
            Retirement Contributions: ${financial_data.get('retirement_contributions', 0):,}
            Tax Bracket: {financial_data.get('tax_bracket', 'Unknown')}
            
            Provide 5-7 specific, actionable tax strategies.
            """
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a tax planning specialist. Provide legal, ethical tax optimization advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.4
            )
            
            strategies_text = response.choices[0].message.content
            strategies = [strategy.strip() for strategy in strategies_text.split('\n') if strategy.strip() and not strategy.startswith('#')]
            
            return strategies[:7]
            
        except Exception as e:
            print(f"Error generating tax strategies: {e}")
            return self._generate_fallback_tax_strategies()
    
    def _create_insights_prompt(self, user_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Create a prompt for generating personalized insights"""
        return f"""
        Generate 5 personalized financial insights for this user:
        
        User Profile:
        - Age: {user_data.get('age', 'Unknown')}
        - Income: ${user_data.get('annual_income', 0):,}
        - Risk Tolerance: {user_data.get('risk_tolerance', 'Moderate')}
        
        Current Analysis:
        - Monthly Expenses: ${analysis.get('monthly_expenses', 0):,}
        - Portfolio Value: ${analysis.get('portfolio_value', 0):,}
        - Total Debt: ${analysis.get('total_debt', 0):,}
        - Emergency Fund: ${analysis.get('emergency_fund', 0):,}
        
        Provide specific, actionable insights that are relevant to this user's situation.
        Each insight should be one clear sentence.
        """
    
    def _generate_fallback_insights(self, user_data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Generate fallback insights when OpenAI is not available"""
        insights = []
        
        # Income-based insights
        income = user_data.get('annual_income', 0)
        if income > 0:
            insights.append(f"With an annual income of ${income:,}, consider maximizing retirement contributions")
        
        # Expense insights
        monthly_expenses = analysis.get('monthly_expenses', 0)
        if monthly_expenses > income / 12 * 0.8:
            insights.append("Your expenses are high relative to income - focus on budgeting")
        
        # Portfolio insights
        portfolio_value = analysis.get('portfolio_value', 0)
        if portfolio_value < income:
            insights.append("Consider increasing investment contributions for long-term growth")
        
        # Debt insights
        total_debt = analysis.get('total_debt', 0)
        if total_debt > income * 0.3:
            insights.append("Focus on debt reduction to improve financial flexibility")
        
        # Emergency fund
        emergency_fund = analysis.get('emergency_fund', 0)
        if emergency_fund < monthly_expenses * 6:
            insights.append("Build emergency fund to cover 6 months of expenses")
        
        return insights[:5]
    
    def _generate_fallback_goal_recommendations(self, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback goal recommendations"""
        target_amount = goal_data.get('target_amount', 0)
        current_amount = goal_data.get('current_amount', 0)
        time_frame_months = goal_data.get('time_frame_months', 60)
        
        remaining = target_amount - current_amount
        monthly_required = remaining / time_frame_months if time_frame_months > 0 else 0
        
        return {
            'monthly_savings_required': monthly_required,
            'investment_strategy': 'Consider balanced portfolio for medium-term goals',
            'timeline_assessment': 'Review timeline based on current savings capacity',
            'alternatives': ['Extend timeline', 'Reduce target amount', 'Increase income'],
            'risk_considerations': 'Consider market volatility for investment-based goals'
        }
    
    def _generate_fallback_tax_strategies(self) -> List[str]:
        """Generate fallback tax strategies"""
        return [
            "Maximize retirement account contributions (401k, IRA)",
            "Consider tax-loss harvesting for investment portfolios",
            "Review timing of capital gains and losses",
            "Explore health savings account (HSA) contributions",
            "Consider municipal bonds for high earners",
            "Review business expense deductions if self-employed",
            "Plan charitable giving for tax benefits"
        ]
