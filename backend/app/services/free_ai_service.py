"""
Free AI Service for FinVoice Chatbot
Integrates multiple free AI APIs for financial advice
"""

import json
import logging
import requests
import asyncio
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)

class FreeAIService:
    def __init__(self):
        self.api_endpoints = {
            "huggingface": {
                "base_url": "https://api-inference.huggingface.co/models",
                "models": {
                    "conversation": "microsoft/DialoGPT-medium",
                    "text_generation": "gpt2",
                    "financial_bert": "ProsusAI/finbert",
                    "sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest"
                }
            },
            "ollama_demo": {
                "base_url": "https://ollama.ai/api",
                "models": ["llama2", "mistral", "codellama"]
            },
            "groq": {
                "base_url": "https://api.groq.com/openai/v1/chat/completions",
                "model": "llama2-70b-4096"
            }
        }
        
        self.financial_templates = {
            "investment": [
                "For investment planning, I recommend a diversified approach based on your profile.",
                "Let's build a solid investment strategy tailored to your goals and risk tolerance.",
                "Investment success comes from consistent planning and regular review.",
                "Based on current market conditions, here are personalized investment options for you."
            ],
            "savings": [
                "Building a strong savings foundation is crucial for your financial security.",
                "Let me help you optimize your savings strategy with current interest rates.",
                "Emergency fund planning is essential - let's calculate the right amount for you.",
                "Smart savings allocation can significantly boost your financial growth."
            ],
            "expenses": [
                "Expense optimization is key to increasing your investment capacity.",
                "Let's analyze your spending patterns and find improvement opportunities.",
                "Budget management becomes easier with the right tracking methods.",
                "Smart expense planning can free up significant funds for your goals."
            ],
            "goals": [
                "Goal-based financial planning ensures you stay on track for success.",
                "Let's create a roadmap to achieve your financial dreams systematically.",
                "Every financial goal needs a specific plan with timelines and amounts.",
                "I'll help you prioritize and plan for multiple financial objectives."
            ],
            "tax": [
                "Tax optimization can save you thousands while building wealth.",
                "Let's maximize your tax benefits with smart investment choices.",
                "Strategic tax planning throughout the year yields better results.",
                "I'll show you how to legally minimize taxes while growing wealth."
            ],
            "retirement": [
                "Retirement planning requires starting early for maximum benefit.",
                "Let's calculate your retirement corpus and create an action plan.",
                "Multiple retirement instruments can optimize your post-work life.",
                "Early retirement planning gives you financial freedom and security."
            ]
        }
        
        self.indian_context = {
            "instruments": {
                "equity": ["Nifty 50 ETF", "Large Cap Mutual Funds", "Mid Cap Funds", "Small Cap Funds", "Sectoral ETFs"],
                "debt": ["PPF", "NSC", "Government Bonds", "Corporate Bonds", "FDs", "GILT Funds"],
                "tax_saving": ["ELSS", "PPF", "NSC", "Tax Saver FD", "NPS", "Life Insurance"],
                "insurance": ["Term Life Insurance", "Health Insurance", "Critical Illness", "Motor Insurance"],
                "real_estate": ["Residential Property", "Commercial Property", "REITs", "Land Investment"],
                "alternatives": ["Gold ETF", "Silver ETF", "Commodities", "International Funds"]
            },
            "returns": {
                "equity_long_term": "12-15% annually (5+ years)",
                "equity_short_term": "Variable (high volatility)",
                "debt": "6-8% annually",
                "fd": "6-7% annually",
                "ppf": "7-8% annually (tax-free)",
                "real_estate": "8-10% annually",
                "gold": "6-8% annually"
            },
            "current_market": {
                "nifty_50": "Strong fundamentals, good for long-term",
                "mid_cap": "Higher growth potential, moderate risk",
                "small_cap": "High risk-reward, for experienced investors",
                "debt_funds": "Stable returns, good for conservative investors"
            },
            "tax_brackets_2024": [
                {"range": "₹0 - ₹3L", "rate": "0%", "advice": "Focus on wealth building"},
                {"range": "₹3L - ₹7L", "rate": "5%", "advice": "Start tax planning"},
                {"range": "₹7L - ₹10L", "rate": "10%", "advice": "Optimize 80C investments"},
                {"range": "₹10L - ₹12L", "rate": "15%", "advice": "Consider NPS for extra benefits"},
                {"range": "₹12L - ₹15L", "rate": "20%", "advice": "Comprehensive tax strategy needed"},
                {"range": "Above ₹15L", "rate": "30%", "advice": "Advanced tax optimization essential"}
            ]
        }

    async def get_financial_advice(self, query: str, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get financial advice using multiple AI approaches"""
        try:
            # Try different AI services in order of preference
            advice = await self._try_ai_services(query, user_profile)
            
            if not advice:
                # Enhanced fallback with real financial data context
                advice = self._get_contextual_advice(query, user_profile)
            
            return {
                "advice": advice,
                "type": "text",
                "confidence": 0.9,
                "source": "enhanced_ai_service",
                "timestamp": datetime.now().isoformat(),
                "market_context": self._get_market_context(),
                "user_tips": self._get_personalized_tips(user_profile)
            }
            
        except Exception as e:
            logger.error(f"Error getting financial advice: {e}")
            return self._get_fallback_advice(query)

    async def _try_ai_services(self, query: str, user_profile: Dict[str, Any] = None) -> Optional[str]:
        """Try different AI services to get advice"""
        
        # Try Hugging Face API (Free tier available)
        try:
            advice = await self._query_huggingface(query, user_profile)
            if advice:
                return advice
        except Exception as e:
            logger.warning(f"Hugging Face API failed: {e}")
        
        # Try local/demo APIs
        try:
            advice = await self._query_free_apis(query, user_profile)
            if advice:
                return advice
        except Exception as e:
            logger.warning(f"Free APIs failed: {e}")
        
        return None

    async def _query_huggingface(self, query: str, user_profile: Dict[str, Any] = None) -> Optional[str]:
        """Query Hugging Face Inference API (Free tier)"""
        try:
            # Use the conversation model for financial advice
            url = f"{self.api_endpoints['huggingface']['base_url']}/microsoft/DialoGPT-medium"
            
            # Format the query for financial context
            financial_query = f"Financial advice: {query}"
            if user_profile and user_profile.get('monthly_income'):
                financial_query += f" (Income: ₹{user_profile['monthly_income']:,}/month)"
            
            payload = {
                "inputs": financial_query,
                "parameters": {
                    "max_length": 150,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        result = await response.json()
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get('generated_text', '')
                            # Clean and format the response
                            return self._format_ai_response(generated_text, query)
                    
        except Exception as e:
            logger.error(f"Hugging Face query error: {e}")
        
        return None

    async def _query_free_apis(self, query: str, user_profile: Dict[str, Any] = None) -> Optional[str]:
        """Query other free AI APIs"""
        try:
            # Mock API call - in production, replace with actual free AI services
            # Examples: Cohere free tier, AI21 free tier, etc.
            
            # Simulate AI response based on query analysis
            advice = self._generate_smart_response(query, user_profile)
            return advice
            
        except Exception as e:
            logger.error(f"Free APIs query error: {e}")
        
        return None

    def _generate_smart_response(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Generate intelligent response based on query analysis"""
        
        query_lower = query.lower()
        
        # Advanced query analysis for more specific responses
        if any(word in query_lower for word in ['child', 'education', 'school', 'college']):
            return self._generate_education_advice(query_lower, user_profile)
        elif any(word in query_lower for word in ['house', 'home', 'property', 'real estate']):
            return self._generate_property_advice(query_lower, user_profile)
        elif any(word in query_lower for word in ['retirement', 'pension', 'old age']):
            return self._generate_retirement_advice(query_lower, user_profile)
        elif any(word in query_lower for word in ['tax', '80c', 'deduction', 'save tax']):
            return self._generate_tax_advice(query_lower, user_profile)
        elif any(word in query_lower for word in ['emergency', 'fund', 'crisis']):
            return self._generate_emergency_fund_advice(query_lower, user_profile)
        
        # Detect query type for general categories
        if any(word in query_lower for word in ['invest', 'investment', 'mutual fund', 'stocks', 'portfolio']):
            category = "investment"
        elif any(word in query_lower for word in ['save', 'saving', 'deposit', 'fd']):
            category = "savings"
        elif any(word in query_lower for word in ['expense', 'spending', 'budget', 'cost', 'reduce']):
            category = "expenses"
        elif any(word in query_lower for word in ['goal', 'plan', 'target', 'future']):
            category = "goals"
        else:
            category = "general"
        
        # Get base advice from templates
        if category in self.financial_templates:
            base_advice = random.choice(self.financial_templates[category])
        else:
            base_advice = "Let me help you with your financial question."
        
        # Add contextual information
        context_advice = self._add_contextual_advice(query_lower, user_profile, category)
        
        # Combine base advice with context
        full_advice = f"{base_advice} {context_advice}"
        
        return full_advice

    def _add_contextual_advice(self, query: str, user_profile: Dict[str, Any], category: str) -> str:
        """Add contextual advice based on user profile and query specifics"""
        
        context = []
        
        # Add income-based advice
        if user_profile and user_profile.get('monthly_income'):
            income = user_profile['monthly_income']
            if income < 30000:
                context.append("With your current income, focus on building emergency fund first with simple savings accounts or FDs.")
                if category == "investment":
                    context.append("Start with ₹500/month SIP in large-cap funds once emergency fund is ready.")
            elif income < 50000:
                context.append("Consider starting SIPs of ₹2000-3000/month in large-cap mutual funds for long-term wealth creation.")
                if category == "tax":
                    context.append("Invest ₹8000/month in ELSS for tax saving and wealth building.")
            elif income < 100000:
                context.append("You can allocate ₹10,000-15,000/month for investments across equity and debt instruments.")
                if category == "investment":
                    context.append("Diversify with 70% equity (large+mid cap) and 30% debt/PPF.")
            else:
                context.append("With higher income, explore diversified portfolio with equity, debt, real estate, and alternative investments.")
                if category == "tax":
                    context.append("Maximize all tax-saving options: 80C (₹1.5L), NPS (₹50K), health insurance (₹25K).")
        
        # Add specific instrument suggestions based on category
        if category == "investment":
            instruments = self.indian_context["instruments"]["equity"]
            context.append(f"Top options: {', '.join(instruments[:3])} offering {self.indian_context['returns']['equity']} returns.")
        elif category == "savings":
            instruments = self.indian_context["instruments"]["debt"]
            context.append(f"Safe options: {', '.join(instruments[:3])} with {self.indian_context['returns']['fd']} returns.")
        
        # Add query-specific advice with detailed explanations
        if "tax" in query:
            context.append("Section 80C limit is ₹1.5L annually. ELSS has 3-year lock-in vs 15-year for PPF. NPS offers additional ₹50K deduction under 80CCD(1B).")
        
        if "retirement" in query:
            context.append("Target 25x annual income as retirement corpus. Start NPS immediately for long-term tax-efficient growth.")
        
        if "emergency" in query:
            context.append("Keep emergency fund liquid: 50% savings account, 30% liquid funds, 20% short-term FDs for easy access.")
        
        return " ".join(context)

    def _get_contextual_advice(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Enhanced contextual advice with real financial data"""
        # First get template-based advice
        base_advice = self._get_template_advice(query, user_profile)
        
        # Add current market context
        market_insight = self._add_market_context(query)
        
        # Add personalized recommendations
        personal_recs = self._get_personal_recommendations(query, user_profile)
        
        # Combine all advice
        full_advice = base_advice
        
        if market_insight:
            full_advice += f"\n\nMarket Insight: {market_insight}"
        
        if personal_recs:
            full_advice += f"\n\nPersonal Recommendation: {personal_recs}"
        
        return full_advice

    def _add_market_context(self, query: str) -> str:
        """Add current market context to advice"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['invest', 'mutual fund', 'equity', 'stocks']):
            return "Current market shows strong fundamentals in large-cap stocks. Nifty 50 has delivered consistent returns. SIP remains the best strategy for volatility management."
        
        elif any(word in query_lower for word in ['debt', 'bonds', 'fixed']):
            return "Interest rates are stabilizing, making this a good time for debt investments. Government bonds offer 7-8% returns with safety."
        
        elif any(word in query_lower for word in ['gold', 'commodity']):
            return "Gold prices are consolidating. Consider 5-10% allocation for portfolio diversification. Gold ETFs are more convenient than physical gold."
        
        elif any(word in query_lower for word in ['real estate', 'property', 'house']):
            return "Real estate prices are showing steady growth in major cities. Home loan rates are attractive at 8-9%. Consider ready-to-move properties for immediate possession."
        
        return ""

    def _get_personal_recommendations(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Get personalized recommendations based on user profile"""
        if not user_profile:
            return ""
        
        income = user_profile.get('monthly_income', 0)
        age = user_profile.get('age', 30)
        query_lower = query.lower()
        
        recommendations = []
        
        # Income-based recommendations
        if income > 100000:
            if 'invest' in query_lower:
                recommendations.append("Consider portfolio management services (PMS) for amounts above ₹50L")
            if 'tax' in query_lower:
                recommendations.append("Explore NPS Tier 2 for additional tax benefits beyond ₹50K limit")
        
        elif income > 50000:
            if 'invest' in query_lower:
                recommendations.append("Perfect income level for diversified MF portfolio across large, mid, and small cap")
            if 'goal' in query_lower:
                recommendations.append("You can comfortably plan for multiple goals with systematic investment")
        
        else:
            if 'invest' in query_lower:
                recommendations.append("Start with large-cap funds and gradually add mid-cap as income grows")
            recommendations.append("Focus on building emergency fund first before aggressive investments")
        
        # Age-based recommendations
        if age < 30:
            recommendations.append("Your young age allows for aggressive equity allocation (70-80%)")
            if 'retirement' in query_lower:
                recommendations.append("Starting retirement planning now can build a corpus of ₹5-10 crores by age 60")
        
        elif age < 45:
            recommendations.append("Balanced approach: 60% equity, 40% debt allocation recommended")
            if 'child' in query_lower:
                recommendations.append("Education costs are rising 10-12% annually. Start planning immediately")
        
        else:
            recommendations.append("Focus on wealth preservation with 40% equity, 60% debt allocation")
            recommendations.append("Consider senior citizen saving schemes and health insurance priority")
        
        return " | ".join(recommendations) if recommendations else ""

    def _get_market_context(self) -> Dict[str, str]:
        """Get current market context for response"""
        return {
            "equity_outlook": "Positive long-term outlook with periodic volatility",
            "interest_rates": "Stable to declining trend, favorable for borrowers",
            "inflation": "Controlled at 5-6%, manageable for financial planning",
            "best_sectors": "Technology, Banking, Healthcare showing strong fundamentals"
        }

    def _get_personalized_tips(self, user_profile: Dict[str, Any] = None) -> List[str]:
        """Get personalized tips based on user profile"""
        if not user_profile:
            return ["Start tracking expenses", "Build emergency fund", "Begin SIP investments"]
        
        income = user_profile.get('monthly_income', 50000)
        tips = []
        
        if income < 30000:
            tips = [
                "Use free investment apps for small SIPs",
                "Maximize employer benefits (PF, insurance)",
                "Focus on skill development for income growth"
            ]
        elif income < 100000:
            tips = [
                "Automate investments for discipline",
                "Review and increase SIP annually",
                "Consider term insurance for family protection"
            ]
        else:
            tips = [
                "Explore tax-efficient investment strategies",
                "Consider professional financial planning",
                "Look into alternative investments for diversification"
            ]
        
        return tips
        
        if "child" in query or "education" in query:
            context.append("Education inflation is 10-12% annually. For girl child, SSY offers 8% tax-free returns with compounding benefits.")
        
        if "sip" in query:
            context.append("Start small and increase by 10-15% annually (step-up SIP). Use auto-debit on salary day for discipline.")
        
        if "reduce" in query and "expense" in query:
            context.append("Use 50-30-20 rule: 50% needs, 30% wants, 20% savings. Track expenses for 30 days to identify leakages.")
        
        if "mutual fund" in query:
            context.append("Choose direct plans over regular for lower expense ratios. Review portfolio annually, rebalance if needed.")
        
        if "home" in query or "house" in query:
            context.append("Follow 40% EMI rule. Save 20% down payment separately. Consider location, connectivity, and builder reputation.")
        
        return " ".join(context)

    def _format_ai_response(self, ai_text: str, original_query: str) -> str:
        """Format and clean AI response"""
        
        # Remove query repetition if present
        if original_query in ai_text:
            ai_text = ai_text.replace(original_query, "").strip()
        
        # Clean up common AI artifacts
        ai_text = ai_text.replace("Financial advice:", "").strip()
        ai_text = ai_text.replace("AI:", "").strip()
        ai_text = ai_text.replace("Response:", "").strip()
        
        # Ensure it starts properly
        if not ai_text:
            return "I'd be happy to help with your financial question. Please provide more details."
        
        # Add Indian context if missing
        if "₹" not in ai_text and "rupee" not in ai_text.lower() and "indian" not in ai_text.lower():
            ai_text += " Consider Indian options like PPF, ELSS, and mutual funds for your financial goals."
        
        return ai_text

    def _get_template_advice(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Get advice using templates when AI services fail"""
        
        query_lower = query.lower()
        income = user_profile.get('monthly_income', 50000) if user_profile else 50000
        
        # Investment queries with detailed advice
        if any(word in query_lower for word in ['invest', 'mutual fund', 'sip', 'stocks']):
            monthly_investment = min(income * 0.2, 20000)  # 20% of income or max 20k
            advice = f"For investing in India, start with ₹{monthly_investment:,.0f}/month SIP in diversified equity mutual funds. "
            advice += "Allocation: 60% large-cap funds (stable growth), 30% mid-cap funds (higher growth), 10% international funds (diversification). "
            advice += "ELSS funds offer tax benefits under Section 80C with 3-year lock-in. "
            advice += f"Expected returns: 12-15% annually over 5+ years. Review and rebalance annually."
            return advice
        
        # Savings queries with specific amounts
        elif any(word in query_lower for word in ['save', 'emergency', 'fd', 'deposit']):
            emergency_target = income * 6 * 0.7  # 6 months of 70% income
            monthly_savings = min(income * 0.15, 15000)
            advice = f"Build emergency fund of ₹{emergency_target:,.0f} (6 months expenses). "
            advice += f"Save ₹{monthly_savings:,.0f}/month: 50% in high-yield savings (4-5%), 30% in liquid funds (4-6%), 20% in FDs (6-7%). "
            advice += "PPF offers 7-8% tax-free returns for 15-year lock-in. Complete emergency fund first, then start PPF."
            return advice
        
        # Goal planning with calculations
        elif any(word in query_lower for word in ['goal', 'plan', 'house', 'car', 'retirement']):
            if 'house' in query_lower:
                max_emi = income * 0.4
                loan_eligible = max_emi * 12 * 20  # 20 years
                advice = f"For home purchase, max EMI should be ₹{max_emi:,.0f} (40% of income). "
                advice += f"Eligible for loan: ₹{loan_eligible:,.0f}. Save 20% down payment separately in FDs/liquid funds. "
                advice += "Get pre-approved loan for better negotiation. Consider location, connectivity, and resale value."
            else:
                advice = "Set SMART financial goals: Specific amount, Measurable progress, Achievable timeline, Relevant to life, Time-bound. "
                advice += f"For goals, allocate ₹{income * 0.1:,.0f}/month and use SIP calculators to determine investment amount. "
                advice += "Short-term goals (<3 years): Debt funds. Medium-term (3-7 years): Balanced funds. Long-term (>7 years): Equity funds."
            return advice
        
        # Expense management with actionable steps
        elif any(word in query_lower for word in ['expense', 'budget', 'spending', 'reduce']):
            needs_budget = income * 0.5
            wants_budget = income * 0.3
            savings_budget = income * 0.2
            advice = f"Follow 50-30-20 rule: Needs ₹{needs_budget:,.0f} (50%), Wants ₹{wants_budget:,.0f} (30%), Savings ₹{savings_budget:,.0f} (20%). "
            advice += "Track expenses for 30 days using apps like Walnut/ET Money. "
            advice += "Quick wins: Cancel unused subscriptions, cook more at home, use public transport, compare prices before big purchases. "
            advice += "Review and optimize categories where spending exceeds 50% (needs) or 30% (wants)."
            return advice
        
        # Tax planning with calculations
        elif any(word in query_lower for word in ['tax', '80c', 'deduction']):
            annual_income = income * 12
            if annual_income > 500000:
                tax_rate = "20-30%"
                potential_savings = "₹45,000-60,000"
            elif annual_income > 250000:
                tax_rate = "5-20%"
                potential_savings = "₹15,000-30,000"
            else:
                return "Your income is below taxable limit. Focus on building wealth through SIPs and emergency fund for future tax planning."
            
            advice = f"In {tax_rate} tax bracket, save {potential_savings} annually through: "
            advice += "80C (₹1.5L): ELSS ₹8000/month, PPF ₹4500/month. "
            advice += "80CCD(1B): NPS ₹4000/month (extra ₹50K deduction). "
            advice += "80D: Health insurance ₹25K family, ₹50K parents. Plan investments by December for current financial year."
            return advice
        
        # Insurance with coverage amounts
        elif any(word in query_lower for word in ['insurance', 'term', 'health']):
            term_coverage = income * 12 * 15  # 15x annual income
            health_coverage = 500000 if income < 50000 else 1000000
            advice = f"Essential insurance: Term life ₹{term_coverage:,.0f} (15x income), Health ₹{health_coverage:,.0f} family floater. "
            advice += f"Term premium: ₹{income * 0.01:,.0f}/month approx. Health premium: ₹{income * 0.02:,.0f}/month. "
            advice += "Buy pure insurance, avoid ULIPs for investment. Get early for lower premiums. Critical illness add-on recommended."
            return advice
        
        # Default comprehensive response
        else:
            advice = f"Based on ₹{income:,.0f} monthly income, here's your financial roadmap: "
            advice += f"1. Emergency fund: ₹{income * 4:,.0f} (6 months expenses) "
            advice += f"2. Investments: ₹{income * 0.2:,.0f}/month SIP in equity MFs "
            advice += f"3. Insurance: Term life + health coverage "
            advice += f"4. Tax saving: ₹12,500/month in 80C instruments "
            advice += "Start with emergency fund, then SIPs, ensure adequate insurance. I can help with specific areas - just ask!"
            return advice

    def _get_enhanced_advice(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Get enhanced advice with better context and personality"""
        
        query_lower = query.lower()
        
        # Handle greetings and casual conversation
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            return self._get_greeting_response(user_profile)
        
        if any(word in query_lower for word in ['how are you', 'what can you do', 'help me']):
            return self._get_capability_response(user_profile)
        
        if any(word in query_lower for word in ['thank', 'thanks', 'great', 'awesome']):
            return self._get_appreciation_response()
        
        # Handle financial queries with enhanced context
        return self._get_enhanced_financial_advice(query, user_profile)
    
    def _get_greeting_response(self, user_profile: Dict[str, Any] = None) -> str:
        """Generate personalized greeting"""
        income = user_profile.get('monthly_income', 0) if user_profile else 0
        
        greetings = [
            f"Hello! I'm your AI financial advisor. Based on current market conditions, here's what I can help you with:",
            f"Hi there! Welcome to FinVoice. I'm here to help you make smart financial decisions.",
            f"Greetings! Let's work together to build your wealth and secure your financial future."
        ]
        
        base_greeting = random.choice(greetings)
        
        if income > 0:
            if income < 30000:
                context = " I see you're starting your financial journey - let's focus on building a strong foundation with emergency funds and basic investments."
            elif income < 100000:
                context = f" With your ₹{income:,}/month income, we can create a balanced portfolio mixing growth and stability."
            else:
                context = f" Given your strong income of ₹{income:,}/month, we can explore advanced wealth-building strategies."
        else:
            context = " I can help with investment planning, expense optimization, goal setting, tax planning, and much more!"
        
        return base_greeting + context
    
    def _get_capability_response(self, user_profile: Dict[str, Any] = None) -> str:
        """Explain chatbot capabilities"""
        return """I'm your comprehensive financial advisor! Here's how I can help you:

💰 **Investment Planning**: SIP recommendations, mutual fund selection, portfolio optimization
📊 **Goal Setting**: Education planning, retirement corpus, home buying strategies  
💳 **Expense Management**: Budget optimization, expense tracking, savings strategies
🎯 **Tax Planning**: 80C optimization, NPS benefits, tax-saving investments
🏦 **Insurance Planning**: Term life, health insurance, coverage calculations
📈 **Market Insights**: Current opportunities, sector analysis, timing strategies

I provide specific calculations, product recommendations, and actionable steps tailored to Indian markets. What would you like to explore today?"""
    
    def _get_appreciation_response(self) -> str:
        """Response to user appreciation"""
        responses = [
            "You're welcome! I'm always here to help you make informed financial decisions. Feel free to ask anything else!",
            "Glad I could help! Building wealth is a journey, and I'm here to guide you every step of the way.",
            "Happy to assist! Remember, consistent investing and smart planning are key to financial success. What else can I help with?"
        ]
        return random.choice(responses)
    
    def _get_enhanced_financial_advice(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Enhanced financial advice with market context"""
        query_lower = query.lower()
        income = user_profile.get('monthly_income', 50000) if user_profile else 50000
        
        # Market context (you can update this with real data)
        market_context = {
            "nifty_trend": "bullish",
            "interest_rates": "stable", 
            "inflation": "6.2%",
            "best_sectors": ["Technology", "Healthcare", "Financial Services"],
            "fd_rates": "6.5-7%",
            "mutual_fund_performance": "positive"
        }
        
        # Enhanced investment advice
        if any(word in query_lower for word in ['invest', 'sip', 'mutual fund', 'portfolio']):
            monthly_investment = min(income * 0.2, 25000)
            advice = f"🚀 **Investment Strategy for You:**\n\n"
            advice += f"Based on your income and current market conditions (Nifty trending {market_context['nifty_trend']}), here's my recommendation:\n\n"
            advice += f"💡 **Monthly SIP**: ₹{monthly_investment:,}\n"
            advice += f"📊 **Allocation**: 60% Large Cap, 25% Mid Cap, 15% International\n"
            advice += f"🎯 **Top Sectors**: {', '.join(market_context['best_sectors'])}\n"
            advice += f"📈 **Expected Returns**: 12-15% annually\n\n"
            advice += f"Start with blue-chip funds like HDFC Top 100 or ICICI Pru Bluechip, then add Mirae Asset Large Cap for diversification."
            return advice
        
        # Enhanced savings advice  
        elif any(word in query_lower for word in ['save', 'emergency', 'fd']):
            emergency_amount = income * 6 * 0.7
            advice = f"💰 **Smart Savings Strategy:**\n\n"
            advice += f"🎯 **Emergency Fund Target**: ₹{emergency_amount:,} (6 months expenses)\n"
            advice += f"🏦 **Current FD Rates**: {market_context['fd_rates']}\n"
            advice += f"📊 **Optimal Mix**:\n"
            advice += f"   • 40% High-yield Savings (instant access)\n"
            advice += f"   • 35% Liquid Mutual Funds (1-day access)\n"
            advice += f"   • 25% Short-term FDs (higher returns)\n\n"
            advice += f"Consider banks like SBI, HDFC, or ICICI for best rates. Build this before investing!"
            return advice
            
        # Enhanced goal planning
        elif any(word in query_lower for word in ['goal', 'education', 'house', 'retirement']):
            if 'house' in query_lower:
                max_emi = income * 0.4
                loan_amount = max_emi * 240  # 20 year loan
                advice = f"🏠 **Home Buying Strategy:**\n\n"
                advice += f"💳 **Max EMI Capacity**: ₹{max_emi:,}/month (40% rule)\n"
                advice += f"🏦 **Loan Eligibility**: ₹{loan_amount:,}\n"
                advice += f"💰 **Down Payment**: Save ₹{loan_amount * 0.2:,} separately\n"
                advice += f"📊 **Current Home Loan Rates**: 8.5-9.5%\n\n"
                advice += f"💡 **Pro Tips**: Get pre-approval, consider under-construction for better prices, check RERA registration!"
            else:
                advice = f"🎯 **Goal-Based Financial Planning:**\n\n"
                advice += f"For systematic goal achievement:\n"
                advice += f"• **Short-term (1-3 years)**: Debt funds, FDs\n"
                advice += f"• **Medium-term (3-7 years)**: Balanced funds\n"
                advice += f"• **Long-term (7+ years)**: Equity funds\n\n"
                advice += f"Use SIP calculators to determine exact amounts. I can help with specific goal calculations!"
            return advice
            
        # Enhanced expense management
        elif any(word in query_lower for word in ['expense', 'budget', 'reduce', 'spending']):
            needs_budget = income * 0.5
            wants_budget = income * 0.3  
            savings_budget = income * 0.2
            advice = f"💳 **Smart Budget Optimization:**\n\n"
            advice += f"📊 **50-30-20 Rule Applied**:\n"
            advice += f"   🏠 Needs: ₹{needs_budget:,} (50%)\n"
            advice += f"   🎯 Wants: ₹{wants_budget:,} (30%)\n"
            advice += f"   💰 Savings: ₹{savings_budget:,} (20%)\n\n"
            advice += f"💡 **Quick Savings Tips**:\n"
            advice += f"• Cancel unused subscriptions\n"
            advice += f"• Use cashback credit cards wisely\n"
            advice += f"• Cook at home 5 days/week\n"
            advice += f"• Review insurance annually for better rates"
            return advice
            
        # Default enhanced response
        else:
            advice = f"🤖 **AI Financial Advisor at Your Service!**\n\n"
            advice += f"I notice you're asking about financial planning. With current market conditions showing:\n"
            advice += f"• Nifty: {market_context['nifty_trend']} trend\n"
            advice += f"• Inflation: {market_context['inflation']}\n"
            advice += f"• FD Rates: {market_context['fd_rates']}\n\n"
            advice += f"💡 I can provide specific advice on:\n"
            advice += f"📈 Investment strategies and fund selection\n"
            advice += f"🎯 Goal-based financial planning\n"
            advice += f"💰 Tax optimization strategies\n"
            advice += f"📊 Portfolio rebalancing\n\n"
            advice += f"What specific area would you like me to help you with?"
            return advice
    
    def _get_contextual_fallback_advice(self, query: str, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced fallback advice with context"""
        return {
            "advice": "I'm here to help you build wealth and achieve financial freedom! I can assist with investments, savings, tax planning, and much more. What specific financial goal are you working towards?",
            "type": "text",
            "confidence": 0.8,
            "source": "contextual_fallback",
            "timestamp": datetime.now().isoformat()
        }

    async def get_portfolio_insights(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI insights for portfolio"""
        try:
            total_value = portfolio_data.get('totalValue', 0)
            holdings_count = len(portfolio_data.get('holdings', []))
            today_change = portfolio_data.get('todayChangePercent', 0)
            
            insights = []
            
            if total_value < 100000:
                insights.append("Consider increasing your portfolio value through regular SIPs.")
            elif total_value > 1000000:
                insights.append("Good portfolio size! Focus on rebalancing and diversification.")
            
            if holdings_count < 3:
                insights.append("Diversify your portfolio across more funds or sectors.")
            elif holdings_count > 10:
                insights.append("Consider consolidating holdings to reduce complexity.")
            
            if today_change > 2:
                insights.append("Strong performance today! Stay disciplined and avoid overconfidence.")
            elif today_change < -2:
                insights.append("Market volatility is normal. Stick to your long-term plan.")
            
            advice = " ".join(insights) if insights else "Your portfolio looks balanced. Continue regular investing and review quarterly."
            
            return {
                "advice": advice,
                "type": "portfolio",
                "confidence": 0.85,
                "source": "portfolio_analysis"
            }
            
        except Exception as e:
            logger.error(f"Portfolio insights error: {e}")
            return {
                "advice": "Regular portfolio review and rebalancing are key to long-term success.",
                "type": "portfolio",
                "confidence": 0.6
            }

    async def get_expense_insights(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI insights for expenses"""
        try:
            total_monthly = expense_data.get('totalMonthly', 0)
            categories = expense_data.get('categories', [])
            
            insights = []
            
            if categories:
                top_category = categories[0]
                if top_category.get('percentage', 0) > 40:
                    insights.append(f"Your {top_category['name']} expenses are quite high at {top_category['percentage']}%. Consider optimizing this category.")
            
            if total_monthly > 0:
                insights.append("Track daily expenses using apps to identify savings opportunities.")
                insights.append("Review recurring subscriptions and cancel unused ones.")
            
            advice = " ".join(insights) if insights else "Monitor expenses regularly and maintain a monthly budget for better financial control."
            
            return {
                "advice": advice,
                "type": "expense",
                "confidence": 0.8,
                "source": "expense_analysis"
            }
            
        except Exception as e:
            logger.error(f"Expense insights error: {e}")
            return {
                "advice": "Regular expense tracking helps identify savings opportunities and maintain financial discipline.",
                "type": "expense",
                "confidence": 0.6
            }

    def get_quick_tips(self, category: str) -> List[str]:
        """Get quick financial tips by category"""
        tips = {
            "investment": [
                "Start SIP with just ₹500/month",
                "Diversify across large, mid, and small cap funds",
                "Stay invested for minimum 5 years",
                "Don't time the market, invest regularly"
            ],
            "savings": [
                "Automate savings on salary day",
                "Keep emergency fund separate from investments",
                "Use high-yield savings accounts",
                "Save before you spend, not spend then save"
            ],
            "tax": [
                "Invest ₹1.5L in 80C instruments",
                "Consider NPS for extra ₹50K deduction",
                "Plan investments by December",
                "Keep all investment proofs organized"
            ],
            "budget": [
                "Use 50-30-20 rule for allocation",
                "Track every expense for one month",
                "Set category-wise spending limits",
                "Review and adjust monthly"
            ]
        }
        
        return tips.get(category, [
            "Start your financial journey today",
            "Consistency beats timing in investments",
            "Emergency fund is your financial safety net",
            "Invest regularly, review quarterly"
        ])

    def _generate_education_advice(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Generate education planning advice"""
        income = user_profile.get('monthly_income', 50000) if user_profile else 50000
        
        if 'girl' in query or 'daughter' in query:
            return f"For girl child education, use Sukanya Samriddhi Yojana offering 8% returns with tax benefits. Also start equity SIP of ₹{income * 0.1:,.0f}/month in diversified funds for higher education corpus."
        
        if any(word in query for word in ['10 year', '15 year', 'long term']):
            monthly_sip = income * 0.15
            return f"For long-term education planning, start SIP of ₹{monthly_sip:,.0f}/month in equity mutual funds. Mix of large-cap (60%) and mid-cap (40%) funds can potentially build ₹25-30 lakhs corpus in 15 years."
        
        return "For child's education, start early with Sukanya Samriddhi Yojana (for girls) and equity mutual fund SIPs. Plan for ₹20-30 lakhs for engineering/medical courses. Use step-up SIPs to increase investment with income growth."

    def _generate_property_advice(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Generate property buying advice"""
        income = user_profile.get('monthly_income', 50000) if user_profile else 50000
        
        max_emi = income * 0.4  # 40% EMI rule
        loan_amount = max_emi * 12 * 20  # 20 year loan assumption
        
        return f"For home buying, follow 40% EMI rule - max EMI ₹{max_emi:,.0f}/month. You can afford loan of ₹{loan_amount:,.0f}. Save 20% down payment separately. Consider under-construction projects for better prices. Use home loan for tax benefits under 80C and 24(b)."

    def _generate_retirement_advice(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Generate retirement planning advice"""
        age = user_profile.get('age', 30) if user_profile else 30
        income = user_profile.get('monthly_income', 50000) if user_profile else 50000
        
        years_to_retire = 60 - age
        retirement_corpus_needed = income * 12 * 25  # 25x annual income rule
        
        if years_to_retire > 20:
            return f"Start retirement planning now! You need ₹{retirement_corpus_needed:,.0f} corpus. Invest ₹{income * 0.2:,.0f}/month in equity funds + ₹{income * 0.05:,.0f} in NPS for tax benefits. PPF and EPF are also excellent for retirement."
        elif years_to_retire > 10:
            return f"Accelerate retirement savings! Target ₹{retirement_corpus_needed:,.0f} corpus. Invest ₹{income * 0.3:,.0f}/month in balanced funds. Maximize NPS contribution for extra tax deduction."
        else:
            return "Focus on debt instruments and conservative hybrid funds. Ensure adequate health insurance. Consider senior citizen saving schemes post-retirement."

    def _generate_tax_advice(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Generate tax planning advice"""
        income = user_profile.get('monthly_income', 50000) if user_profile else 50000
        annual_income = income * 12
        
        if annual_income > 500000:
            tax_bracket = "20-30%"
            monthly_80c = 12500  # 1.5L annually
        elif annual_income > 250000:
            tax_bracket = "5-20%"
            monthly_80c = 8000
        else:
            return "Your income is below tax threshold. Focus on building emergency fund and starting small SIPs for future tax planning."
        
        return f"In {tax_bracket} tax bracket, save ₹{monthly_80c:,}/month in 80C instruments: ELSS (₹8000), PPF (₹4500). Add NPS ₹4000/month for extra ₹50K deduction. Total tax saving: ₹45,000-60,000 annually."

    def _generate_emergency_fund_advice(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Generate emergency fund advice"""
        income = user_profile.get('monthly_income', 50000) if user_profile else 50000
        expenses = income * 0.7  # Assume 70% of income as expenses
        
        emergency_fund = expenses * 6  # 6 months expenses
        
        return f"Build emergency fund of ₹{emergency_fund:,.0f} (6 months expenses). Keep 50% in savings account, 30% in liquid mutual funds, 20% in short-term FDs. Start with ₹{income * 0.1:,.0f}/month allocation until target is reached."

# Create global instance
free_ai_service = FreeAIService()
