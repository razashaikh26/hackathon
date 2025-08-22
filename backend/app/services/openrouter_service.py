"""
OpenRouter AI Service for FinVoice
Provides access to multiple AI models through OpenRouter API
"""

import json
import logging
from typing import Dict, List, Any, Optional
import httpx
from decouple import config

logger = logging.getLogger(__name__)

class OpenRouterService:
    def __init__(self):
        self.api_key = config("OPENROUTER_API_KEY", default="")
        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = "gpt-3.5-turbo"  # Reliable model
        self.premium_model = "anthropic/claude-3.5-sonnet"  # Premium model for better responses
        
        # Headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://finvoice.ai",  # Replace with your domain
            "X-Title": "FinVoice AI Assistant"
        }
        
        # Financial context for Indian markets
        self.indian_financial_context = {
            "tax_brackets_2024": {
                "0-250000": 0,
                "250000-500000": 5,
                "500000-750000": 10,
                "750000-1000000": 15,
                "1000000-1250000": 20,
                "1250000-1500000": 25,
                "1500000+": 30
            },
            "investment_options": {
                "equity": ["Large Cap MF", "Mid Cap MF", "Small Cap MF", "ELSS", "Index Funds"],
                "debt": ["PPF", "NSC", "FD", "Government Bonds", "Corporate Bonds"],
                "hybrid": ["Balanced Advantage", "Conservative Hybrid", "Aggressive Hybrid"],
                "tax_saving": ["ELSS", "PPF", "NSC", "Tax Saver FD", "NPS"]
            },
            "current_rates": {
                "inflation": 6.0,
                "repo_rate": 6.5,
                "fd_rates": "6.5-7.5",
                "ppf_rate": 8.1,
                "nsc_rate": 6.8
            },
            "market_indices": {
                "nifty_50": "Strong momentum, good for long-term",
                "sensex": "Stable performance, blue-chip exposure",
                "nifty_next_50": "Good mid-cap exposure"
            }
        }
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance and usage information from OpenRouter"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/auth/key",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "balance": data.get("data", {}).get("usage", 0),
                        "limit": data.get("data", {}).get("limit", 0),
                        "is_free_tier": data.get("data", {}).get("is_free_tier", True),
                        "label": data.get("data", {}).get("label", ""),
                        "status": "success"
                    }
                else:
                    logger.warning(f"OpenRouter balance check failed: {response.status_code}")
                    return {"status": "error", "message": "Could not retrieve balance"}
                    
        except Exception as e:
            logger.error(f"Error checking OpenRouter balance: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("data", [])
                    
                    # Filter for free and popular models
                    filtered_models = []
                    for model in models:
                        if model.get("pricing", {}).get("prompt", 0) == 0 or "free" in model.get("id", "").lower():
                            filtered_models.append({
                                "id": model.get("id"),
                                "name": model.get("name"),
                                "description": model.get("description", ""),
                                "pricing": model.get("pricing", {}),
                                "context_length": model.get("context_length", 0)
                            })
                    
                    return filtered_models
                else:
                    logger.warning(f"OpenRouter models request failed: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting OpenRouter models: {e}")
            return []
    
    async def get_financial_advice(self, query: str, user_profile: Dict[str, Any] = None, model: str = None) -> Dict[str, Any]:
        """Get financial advice using OpenRouter AI"""
        
        # Check balance first
        balance_info = await self.get_account_balance()
        
        try:
            # Determine which model to use
            selected_model = model or self.default_model
            
            # If balance is low, use free model
            if balance_info.get("status") == "success":
                balance = balance_info.get("balance", 0)
                if balance < 1000:  # Low balance threshold
                    selected_model = self.default_model
                    logger.info("Using free model due to low balance")
            
            # Prepare context-rich prompt
            system_prompt = self._create_financial_system_prompt()
            user_prompt = self._create_user_prompt(query, user_profile)
            
            # Prepare request payload
            payload = {
                "model": selected_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.3,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1
            }
            
            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "choices" in data and len(data["choices"]) > 0:
                        advice_text = data["choices"][0]["message"]["content"].strip()
                        
                        # Add balance information to response
                        result = {
                            "advice": advice_text,
                            "type": "text",
                            "confidence": 0.9,
                            "source": "openrouter",
                            "model_used": selected_model,
                            "balance_info": balance_info,
                            "usage": data.get("usage", {}),
                            "market_context": self._get_current_market_context()
                        }
                        
                        return result
                    else:
                        logger.warning("No choices in OpenRouter response")
                        return await self._fallback_response(query, user_profile)
                        
                else:
                    logger.warning(f"OpenRouter API error: {response.status_code} - {response.text}")
                    return await self._fallback_response(query, user_profile)
                    
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            return await self._fallback_response(query, user_profile)
    
    def _create_financial_system_prompt(self) -> str:
        """Create comprehensive system prompt for financial advice"""
        return f"""You are FinVoice AI, an expert financial advisor specializing in Indian personal finance and investment markets.

CORE EXPERTISE:
- Indian tax laws and regulations (FY 2024-25)
- Mutual funds, stocks, bonds, and alternative investments
- Retirement planning, goal-based investing, tax optimization
- Real estate, insurance, and comprehensive financial planning

CURRENT MARKET CONTEXT (August 2025):
{json.dumps(self.indian_financial_context, indent=2)}

COMMUNICATION STYLE:
- Professional yet conversational and approachable
- Provide specific, actionable advice with numbers and examples
- Include relevant Indian financial instruments (PPF, ELSS, NSC, NPS)
- Use INR currency formatting (₹1,00,000 style)
- Be concise but comprehensive (2-4 sentences)

ADVICE PRINCIPLES:
- Prioritize emergency fund and debt management
- Recommend age-appropriate asset allocation
- Consider risk tolerance and time horizon
- Include tax implications and optimization strategies
- Suggest specific action steps with timelines

Always provide practical, implementable advice tailored to Indian investors."""

    def _create_user_prompt(self, query: str, user_profile: Dict[str, Any] = None) -> str:
        """Create user prompt with context and query"""
        
        base_prompt = f"User Query: {query}\n\n"
        
        if user_profile:
            profile_summary = []
            
            if user_profile.get("age"):
                profile_summary.append(f"Age: {user_profile['age']} years")
            
            if user_profile.get("monthly_income"):
                income = user_profile["monthly_income"]
                profile_summary.append(f"Monthly Income: ₹{income:,.0f}")
            
            if user_profile.get("risk_tolerance"):
                profile_summary.append(f"Risk Tolerance: {user_profile['risk_tolerance']}")
            
            if user_profile.get("employment_type"):
                profile_summary.append(f"Employment: {user_profile['employment_type']}")
            
            if profile_summary:
                base_prompt += f"User Profile: {', '.join(profile_summary)}\n\n"
        
        base_prompt += """Please provide specific, actionable financial advice considering:
1. Current Indian market conditions and tax laws
2. User's profile and circumstances
3. Practical implementation steps
4. Relevant financial products and strategies
5. Expected timelines and outcomes

Focus on being helpful and specific rather than generic."""
        
        return base_prompt
    
    def _get_current_market_context(self) -> Dict[str, Any]:
        """Get current market context for the response"""
        return {
            "market_sentiment": "Cautiously optimistic with selective opportunities",
            "recommended_strategy": "SIP-based investing with focus on quality large caps",
            "key_sectors": ["Technology", "Healthcare", "Financial Services", "Consumer Staples"],
            "interest_rate_trend": "Stable to slightly declining",
            "inflation_outlook": "Moderating but still elevated",
            "investment_advice": "Focus on diversified equity funds and gradual debt allocation"
        }
    
    async def _fallback_response(self, query: str, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Provide fallback response when OpenRouter fails"""
        
        # Simple keyword-based responses for common queries
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['invest', 'investment', 'mutual fund', 'sip']):
            advice = "For investment planning, consider starting with a diversified large-cap mutual fund through SIP. Based on your age, allocate 60-70% to equity and 30-40% to debt instruments. Popular options include HDFC Top 100, ICICI Prudential Bluechip, and SBI Large Cap Fund."
        
        elif any(word in query_lower for word in ['tax', '80c', 'save tax']):
            advice = "For tax saving in FY 2024-25: Invest ₹1.5L in 80C instruments (ELSS, PPF, NSC). Consider NPS for additional ₹50K deduction. ELSS provides both tax benefits and equity market returns. PPF offers guaranteed 8.1% returns with EEE status."
        
        elif any(word in query_lower for word in ['emergency', 'emergency fund']):
            advice = "Build an emergency fund covering 6-12 months of expenses. Keep 50% in high-yield savings account, 30% in liquid funds, and 20% in short-term FDs. Start with ₹5,000/month and gradually increase. This provides financial security during unexpected situations."
        
        elif any(word in query_lower for word in ['retirement', 'retire']):
            advice = "For retirement planning, aim for 25x your annual income as corpus. Start early and use EPF + NPS + mutual funds. Allocate 60-70% equity when young, reducing gradually with age. A ₹50K monthly income needs ~₹1.5 crore corpus."
        
        else:
            advice = "I can help with investment planning, tax optimization, retirement strategies, and comprehensive financial advice. What specific area would you like assistance with? Consider sharing your age, income, and financial goals for personalized recommendations."
        
        return {
            "advice": advice,
            "type": "text",
            "confidence": 0.7,
            "source": "fallback",
            "balance_info": {"status": "unavailable"},
            "market_context": self._get_current_market_context()
        }
    
    async def get_portfolio_analysis(self, portfolio_data: Dict[str, Any], query: str = "") -> Dict[str, Any]:
        """Analyze portfolio using OpenRouter AI"""
        
        balance_info = await self.get_account_balance()
        
        try:
            system_prompt = """You are a portfolio analysis expert for Indian equity and mutual fund markets. 
            Analyze portfolios and provide specific rebalancing recommendations, risk assessment, and optimization strategies.
            Consider Indian market conditions, sectoral allocation, and expense ratios."""
            
            user_prompt = f"""
            Portfolio Analysis Request:
            {json.dumps(portfolio_data, indent=2)}
            
            Specific Query: {query}
            
            Please provide:
            1. Portfolio health assessment
            2. Asset allocation analysis 
            3. Rebalancing recommendations
            4. Risk factors and mitigation
            5. Performance improvement suggestions
            
            Keep recommendations specific to Indian markets with actionable steps.
            """
            
            payload = {
                "model": self.default_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 400,
                "temperature": 0.2
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    advice_text = data["choices"][0]["message"]["content"].strip()
                    
                    return {
                        "advice": advice_text,
                        "type": "portfolio",
                        "confidence": 0.85,
                        "source": "openrouter",
                        "balance_info": balance_info,
                        "analysis_type": "comprehensive"
                    }
                else:
                    return await self._portfolio_fallback(portfolio_data)
                    
        except Exception as e:
            logger.error(f"Portfolio analysis error: {e}")
            return await self._portfolio_fallback(portfolio_data)
    
    async def _portfolio_fallback(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback portfolio analysis"""
        
        total_value = portfolio_data.get("totalValue", 0)
        holdings_count = len(portfolio_data.get("holdings", []))
        today_change = portfolio_data.get("todayChangePercent", 0)
        
        advice = f"""Portfolio Analysis:
        
📊 Current Value: ₹{total_value:,.0f}
📈 Holdings: {holdings_count} investments
{"🟢" if today_change > 0 else "🔴"} Today's Performance: {today_change:+.2f}%

Recommendations:
• Ensure diversification across large, mid, and small cap funds
• Rebalance if any single holding exceeds 15-20%
• Review expense ratios - prefer funds with <1.5% expense ratio
• Consider adding international exposure (5-10%)

Next Steps:
1. Track monthly performance
2. Increase SIP amounts annually
3. Review and rebalance quarterly"""
        
        return {
            "advice": advice,
            "type": "portfolio",
            "confidence": 0.7,
            "source": "fallback",
            "balance_info": {"status": "unavailable"}
        }
    
    async def get_tax_optimization_advice(self, income_data: Dict[str, Any], query: str = "") -> Dict[str, Any]:
        """Get tax optimization advice using OpenRouter"""
        
        try:
            annual_income = income_data.get("annual_income", income_data.get("monthly_income", 0) * 12)
            
            system_prompt = f"""You are a tax optimization expert for Indian tax laws (FY 2024-25).
            Current tax brackets: {json.dumps(self.indian_financial_context['tax_brackets_2024'], indent=2)}
            
            Provide specific tax-saving strategies, deduction recommendations, and investment advice for tax optimization."""
            
            user_prompt = f"""
            Tax Optimization Request:
            Annual Income: ₹{annual_income:,.0f}
            Query: {query}
            
            Please provide:
            1. Current tax bracket and liability estimation
            2. Section 80C optimization strategies
            3. Additional deduction opportunities (80D, 80CCD, etc.)
            4. Tax-efficient investment recommendations
            5. Year-end tax planning checklist
            
            Be specific with amounts and deadlines.
            """
            
            payload = {
                "model": self.default_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 350,
                "temperature": 0.1
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    advice_text = data["choices"][0]["message"]["content"].strip()
                    
                    balance_info = await self.get_account_balance()
                    
                    return {
                        "advice": advice_text,
                        "type": "tax",
                        "confidence": 0.9,
                        "source": "openrouter",
                        "balance_info": balance_info,
                        "tax_year": "FY 2024-25"
                    }
                else:
                    return await self._tax_fallback(annual_income)
                    
        except Exception as e:
            logger.error(f"Tax optimization error: {e}")
            return await self._tax_fallback(annual_income)
    
    async def _tax_fallback(self, annual_income: float) -> Dict[str, Any]:
        """Fallback tax advice"""
        
        # Calculate tax bracket
        tax_rate = 0
        if annual_income > 1500000:
            tax_rate = 30
        elif annual_income > 1250000:
            tax_rate = 25
        elif annual_income > 1000000:
            tax_rate = 20
        elif annual_income > 750000:
            tax_rate = 15
        elif annual_income > 500000:
            tax_rate = 10
        elif annual_income > 250000:
            tax_rate = 5
        
        potential_savings = 150000 * (tax_rate / 100)
        
        advice = f"""Tax Optimization for ₹{annual_income:,.0f} Annual Income:

🎯 Current Tax Bracket: {tax_rate}%
💰 Potential 80C Savings: ₹{potential_savings:,.0f}

Recommendations:
• Section 80C: Invest ₹1.5L (ELSS, PPF, NSC)
• NPS (80CCD-1B): Additional ₹50K deduction  
• Health Insurance (80D): ₹25K family, ₹50K parents
• Home Loan Interest: Up to ₹2L deduction

Priority Actions:
1. Start ELSS SIP ₹12,500/month
2. Maximize PPF contribution
3. Consider NPS for retirement + tax benefit
4. Review insurance coverage for 80D benefit

Plan by December to maximize current year benefits!"""
        
        return {
            "advice": advice,
            "type": "tax",
            "confidence": 0.8,
            "source": "fallback",
            "balance_info": {"status": "unavailable"}
        }

# Global instance
openrouter_service = OpenRouterService()
