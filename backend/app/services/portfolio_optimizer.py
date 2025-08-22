"""
AI-Powered Portfolio Optimizer with Crisis Response
Advanced portfolio optimization using machine learning and real-time risk assessment
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import redis
from decouple import config
import openai
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import asyncio
import httpx

@dataclass
class AssetAllocation:
    asset_class: str
    symbol: str
    name: str
    current_weight: float
    target_weight: float
    recommended_action: str
    rationale: str

@dataclass
class PortfolioMetrics:
    total_value: float
    expected_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    var_95: float  # Value at Risk 95%
    beta: float
    currency: str

@dataclass
class HedgingStrategy:
    strategy_name: str
    assets_to_add: List[Dict[str, Any]]
    assets_to_reduce: List[Dict[str, Any]]
    hedging_ratio: float
    expected_protection: float
    cost_percentage: float

class PortfolioOptimizer:
    def __init__(self):
        self.redis_client = redis.from_url(config("REDIS_URL"))
        self.openai_client = openai.OpenAI(api_key=config("OPENAI_API_KEY"))
        
        # Asset universe for Indian market
        self.asset_universe = {
            "equity": {
                "large_cap": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS"],
                "mid_cap": ["MINDTREE.NS", "MPHASIS.NS", "LALPATHLAB.NS"],
                "small_cap": ["ROUTE.NS", "VAIBHAVGBL.NS"],
                "sectoral": {
                    "banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS"],
                    "technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "TECHM.NS"],
                    "pharma": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS"],
                    "energy": ["RELIANCE.NS", "ONGC.NS", "IOC.NS"],
                    "fmcg": ["HINDUNILVR.NS", "NESTLEIND.NS", "ITC.NS"]
                }
            },
            "debt": {
                "government": ["^IRX", "^TNX"],  # Treasury securities
                "corporate": ["LQD", "HYG"],
                "international": ["EMB", "VGIT"]
            },
            "commodities": {
                "precious_metals": ["GC=F", "SI=F", "PALL=F"],  # Gold, Silver, Palladium
                "energy": ["CL=F", "NG=F"],  # Crude Oil, Natural Gas
                "agriculture": ["ZW=F", "ZC=F", "ZS=F"]  # Wheat, Corn, Soybeans
            },
            "alternatives": {
                "reits": ["VNQ", "SCHH"],
                "crypto": ["BTC-USD", "ETH-USD"],
                "volatility": ["^VIX"]
            },
            "defensive": {
                "utilities": ["XLU"],
                "consumer_staples": ["XLP"],
                "healthcare": ["XLV"]
            }
        }
        
        # Crisis response asset allocations
        self.crisis_allocations = {
            "low_risk": {
                "cash": 0.20,
                "government_bonds": 0.30,
                "defensive_equity": 0.25,
                "gold": 0.15,
                "diversified_equity": 0.10
            },
            "moderate_risk": {
                "cash": 0.15,
                "government_bonds": 0.20,
                "defensive_equity": 0.20,
                "gold": 0.10,
                "diversified_equity": 0.25,
                "growth_equity": 0.10
            },
            "aggressive": {
                "cash": 0.10,
                "government_bonds": 0.15,
                "defensive_equity": 0.15,
                "gold": 0.08,
                "diversified_equity": 0.30,
                "growth_equity": 0.22
            }
        }
    
    async def optimize_portfolio(
        self, 
        user_id: str, 
        current_portfolio: Dict[str, Any],
        risk_tolerance: str,
        investment_horizon: int,
        crisis_events: List = None
    ) -> Dict[str, Any]:
        """Main portfolio optimization function with crisis response"""
        
        try:
            # 1. Analyze current portfolio
            current_metrics = await self._calculate_portfolio_metrics(current_portfolio)
            
            # 2. Get market data and predictions
            market_data = await self._get_market_data()
            
            # 3. Apply crisis adjustments if needed
            crisis_adjustments = {}
            if crisis_events:
                crisis_adjustments = await self._apply_crisis_adjustments(
                    current_portfolio, crisis_events, risk_tolerance
                )
            
            # 4. Generate optimal allocation
            optimal_allocation = await self._generate_optimal_allocation(
                current_portfolio,
                risk_tolerance,
                investment_horizon,
                market_data,
                crisis_adjustments
            )
            
            # 5. Generate hedging strategies
            hedging_strategies = await self._generate_hedging_strategies(
                current_portfolio, crisis_events or [], risk_tolerance
            )
            
            # 6. Calculate expected performance
            expected_performance = await self._calculate_expected_performance(optimal_allocation)
            
            # 7. Generate rebalancing instructions
            rebalancing_plan = await self._generate_rebalancing_plan(
                current_portfolio, optimal_allocation
            )
            
            optimization_result = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "current_metrics": current_metrics,
                "optimal_allocation": optimal_allocation,
                "hedging_strategies": hedging_strategies,
                "expected_performance": expected_performance,
                "rebalancing_plan": rebalancing_plan,
                "crisis_adjustments": crisis_adjustments,
                "recommendations": await self._generate_ai_recommendations(
                    current_portfolio, optimal_allocation, crisis_events
                )
            }
            
            # Cache the result
            await self._cache_optimization_result(user_id, optimization_result)
            
            return optimization_result
            
        except Exception as e:
            print(f"Error optimizing portfolio: {e}")
            return {"error": str(e)}
    
    async def _calculate_portfolio_metrics(self, portfolio: Dict[str, Any]) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics"""
        try:
            # Get historical data for portfolio assets
            returns_data = await self._get_historical_returns(portfolio)
            
            if returns_data.empty:
                # Return default metrics if no data
                return PortfolioMetrics(
                    total_value=portfolio.get("total_value", 0),
                    expected_return=0.0,
                    volatility=0.0,
                    sharpe_ratio=0.0,
                    max_drawdown=0.0,
                    var_95=0.0,
                    beta=1.0,
                    currency="INR"
                )
            
            # Calculate portfolio returns
            weights = np.array([holding.get("weight", 0) for holding in portfolio.get("holdings", [])])
            portfolio_returns = (returns_data * weights).sum(axis=1)
            
            # Calculate metrics
            total_value = portfolio.get("total_value", 0)
            expected_return = portfolio_returns.mean() * 252  # Annualized
            volatility = portfolio_returns.std() * np.sqrt(252)  # Annualized
            sharpe_ratio = expected_return / volatility if volatility > 0 else 0
            
            # Calculate maximum drawdown
            cumulative_returns = (1 + portfolio_returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # Calculate VaR (95% confidence)
            var_95 = np.percentile(portfolio_returns, 5) * total_value
            
            # Calculate beta (vs market)
            market_returns = await self._get_market_returns()
            if len(market_returns) > 0 and len(portfolio_returns) == len(market_returns):
                covariance = np.cov(portfolio_returns, market_returns)[0][1]
                market_variance = np.var(market_returns)
                beta = covariance / market_variance if market_variance > 0 else 1.0
            else:
                beta = 1.0
            
            return PortfolioMetrics(
                total_value=total_value,
                expected_return=expected_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                var_95=var_95,
                beta=beta,
                currency="INR"
            )
            
        except Exception as e:
            print(f"Error calculating portfolio metrics: {e}")
            return PortfolioMetrics(0, 0, 0, 0, 0, 0, 1.0, "INR")
    
    async def _get_historical_returns(self, portfolio: Dict[str, Any]) -> pd.DataFrame:
        """Get historical returns for portfolio assets"""
        try:
            # This would integrate with real market data APIs
            # For now, return simulated data structure
            holdings = portfolio.get("holdings", [])
            symbols = [h.get("symbol", "") for h in holdings]
            
            # Simulate returns data
            np.random.seed(42)
            dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
            returns_data = pd.DataFrame(
                np.random.normal(0.0008, 0.02, (252, len(symbols))),
                index=dates,
                columns=symbols
            )
            
            return returns_data
            
        except Exception as e:
            print(f"Error getting historical returns: {e}")
            return pd.DataFrame()
    
    async def _get_market_returns(self) -> np.ndarray:
        """Get market benchmark returns (Nifty 50)"""
        try:
            # Simulate market returns
            np.random.seed(42)
            return np.random.normal(0.0008, 0.015, 252)
            
        except Exception as e:
            print(f"Error getting market returns: {e}")
            return np.array([])
    
    async def _get_market_data(self) -> Dict[str, Any]:
        """Get current market data and conditions"""
        try:
            # This would integrate with real market data APIs
            # For now, return simulated market conditions
            return {
                "market_sentiment": "neutral",
                "volatility_regime": "normal",
                "interest_rate_environment": "rising",
                "inflation_outlook": "moderate",
                "currency_strength": "stable",
                "sector_rotation": "technology_to_value"
            }
            
        except Exception as e:
            print(f"Error getting market data: {e}")
            return {}
    
    async def _apply_crisis_adjustments(
        self, 
        portfolio: Dict[str, Any], 
        crisis_events: List, 
        risk_tolerance: str
    ) -> Dict[str, Any]:
        """Apply crisis-specific portfolio adjustments"""
        
        adjustments = {
            "triggered_by": [],
            "severity_level": 0,
            "recommended_changes": [],
            "emergency_allocations": {}
        }
        
        try:
            if not crisis_events:
                return adjustments
            
            max_severity = max(event.severity for event in crisis_events)
            adjustments["severity_level"] = max_severity
            adjustments["triggered_by"] = [event.description for event in crisis_events[:3]]
            
            # Apply crisis-based allocation changes
            if max_severity >= 8.0:  # Extreme crisis
                adjustments["emergency_allocations"] = self.crisis_allocations["low_risk"]
                adjustments["recommended_changes"] = [
                    "Increase cash allocation to 20%",
                    "Add 15% gold and precious metals",
                    "Reduce equity exposure to 35%",
                    "Add government bonds for stability",
                    "Activate currency hedging"
                ]
            elif max_severity >= 6.0:  # High crisis
                adjustments["emergency_allocations"] = self.crisis_allocations["moderate_risk"]
                adjustments["recommended_changes"] = [
                    "Increase cash allocation to 15%",
                    "Add 10% defensive assets",
                    "Reduce high-beta positions",
                    "Add inflation hedging"
                ]
            elif max_severity >= 4.0:  # Moderate crisis
                adjustments["recommended_changes"] = [
                    "Monitor positions closely",
                    "Consider defensive sector rotation",
                    "Maintain higher cash buffer"
                ]
            
            return adjustments
            
        except Exception as e:
            print(f"Error applying crisis adjustments: {e}")
            return adjustments
    
    async def _generate_optimal_allocation(
        self,
        current_portfolio: Dict[str, Any],
        risk_tolerance: str,
        investment_horizon: int,
        market_data: Dict[str, Any],
        crisis_adjustments: Dict[str, Any]
    ) -> List[AssetAllocation]:
        """Generate optimal asset allocation using AI and modern portfolio theory"""
        
        allocations = []
        
        try:
            # Base allocation based on risk tolerance
            base_allocations = {
                "conservative": {
                    "equity": 0.30, "debt": 0.50, "gold": 0.15, "cash": 0.05
                },
                "moderate": {
                    "equity": 0.50, "debt": 0.30, "gold": 0.10, "cash": 0.10
                },
                "aggressive": {
                    "equity": 0.70, "debt": 0.20, "gold": 0.05, "cash": 0.05
                }
            }
            
            base_allocation = base_allocations.get(risk_tolerance, base_allocations["moderate"])
            
            # Apply crisis adjustments
            if crisis_adjustments.get("emergency_allocations"):
                # Blend base allocation with crisis allocation
                crisis_weight = min(crisis_adjustments["severity_level"] / 10.0, 0.7)
                emergency_alloc = crisis_adjustments["emergency_allocations"]
                
                for asset_class in base_allocation:
                    if asset_class in emergency_alloc:
                        base_allocation[asset_class] = (
                            base_allocation[asset_class] * (1 - crisis_weight) +
                            emergency_alloc.get(asset_class, 0) * crisis_weight
                        )
            
            # Generate specific asset recommendations
            for asset_class, target_weight in base_allocation.items():
                if asset_class == "equity":
                    # Equity allocations
                    equity_allocations = await self._generate_equity_allocations(
                        target_weight, market_data, risk_tolerance
                    )
                    allocations.extend(equity_allocations)
                    
                elif asset_class == "debt":
                    # Debt allocations
                    debt_allocations = await self._generate_debt_allocations(
                        target_weight, market_data
                    )
                    allocations.extend(debt_allocations)
                    
                elif asset_class == "gold":
                    # Gold allocation
                    allocations.append(AssetAllocation(
                        asset_class="commodities",
                        symbol="GC=F",
                        name="Gold Futures",
                        current_weight=0.0,  # Would get from current portfolio
                        target_weight=target_weight,
                        recommended_action="buy" if target_weight > 0.05 else "hold",
                        rationale="Crisis hedging and inflation protection"
                    ))
                    
                elif asset_class == "cash":
                    # Cash allocation
                    allocations.append(AssetAllocation(
                        asset_class="cash",
                        symbol="CASH",
                        name="Cash and Cash Equivalents",
                        current_weight=0.0,
                        target_weight=target_weight,
                        recommended_action="maintain",
                        rationale="Liquidity and opportunity reserves"
                    ))
            
            return allocations
            
        except Exception as e:
            print(f"Error generating optimal allocation: {e}")
            return []
    
    async def _generate_equity_allocations(
        self, 
        total_equity_weight: float, 
        market_data: Dict[str, Any],
        risk_tolerance: str
    ) -> List[AssetAllocation]:
        """Generate specific equity allocations"""
        
        allocations = []
        
        try:
            # Distribute equity allocation across categories
            if risk_tolerance == "conservative":
                large_cap_weight = total_equity_weight * 0.7
                mid_cap_weight = total_equity_weight * 0.2
                small_cap_weight = total_equity_weight * 0.1
            elif risk_tolerance == "aggressive":
                large_cap_weight = total_equity_weight * 0.5
                mid_cap_weight = total_equity_weight * 0.3
                small_cap_weight = total_equity_weight * 0.2
            else:  # moderate
                large_cap_weight = total_equity_weight * 0.6
                mid_cap_weight = total_equity_weight * 0.25
                small_cap_weight = total_equity_weight * 0.15
            
            # Large cap recommendations
            large_cap_stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]
            individual_weight = large_cap_weight / len(large_cap_stocks)
            
            for stock in large_cap_stocks:
                allocations.append(AssetAllocation(
                    asset_class="equity_large_cap",
                    symbol=stock,
                    name=self._get_stock_name(stock),
                    current_weight=0.0,
                    target_weight=individual_weight,
                    recommended_action="buy",
                    rationale="Large cap stability and growth"
                ))
            
            # Add sector-specific allocations based on market conditions
            if market_data.get("sector_rotation") == "technology_to_value":
                # Add banking and energy exposure
                allocations.append(AssetAllocation(
                    asset_class="equity_banking",
                    symbol="ICICIBANK.NS",
                    name="ICICI Bank",
                    current_weight=0.0,
                    target_weight=mid_cap_weight * 0.5,
                    recommended_action="buy",
                    rationale="Value rotation and rising interest rates"
                ))
            
            return allocations
            
        except Exception as e:
            print(f"Error generating equity allocations: {e}")
            return []
    
    async def _generate_debt_allocations(
        self, 
        total_debt_weight: float, 
        market_data: Dict[str, Any]
    ) -> List[AssetAllocation]:
        """Generate debt allocations"""
        
        allocations = []
        
        try:
            # Government bonds for stability
            gov_bond_weight = total_debt_weight * 0.7
            corp_bond_weight = total_debt_weight * 0.3
            
            allocations.extend([
                AssetAllocation(
                    asset_class="debt_government",
                    symbol="^TNX",
                    name="10-Year Treasury",
                    current_weight=0.0,
                    target_weight=gov_bond_weight,
                    recommended_action="buy",
                    rationale="Safe haven and interest rate exposure"
                ),
                AssetAllocation(
                    asset_class="debt_corporate",
                    symbol="LQD",
                    name="Investment Grade Corporate Bonds",
                    current_weight=0.0,
                    target_weight=corp_bond_weight,
                    recommended_action="buy",
                    rationale="Higher yield with moderate risk"
                )
            ])
            
            return allocations
            
        except Exception as e:
            print(f"Error generating debt allocations: {e}")
            return []
    
    async def _generate_hedging_strategies(
        self,
        portfolio: Dict[str, Any],
        crisis_events: List,
        risk_tolerance: str
    ) -> List[HedgingStrategy]:
        """Generate comprehensive hedging strategies"""
        
        strategies = []
        
        try:
            portfolio_value = portfolio.get("total_value", 0)
            
            # 1. Volatility Hedging
            if any(event.event_type == "market_volatility" for event in crisis_events):
                vix_hedge = HedgingStrategy(
                    strategy_name="Volatility Protection",
                    assets_to_add=[
                        {"symbol": "^VIX", "weight": 0.05, "rationale": "Direct volatility hedge"}
                    ],
                    assets_to_reduce=[
                        {"asset_class": "equity_small_cap", "reduction": 0.3}
                    ],
                    hedging_ratio=0.3,
                    expected_protection=0.15,
                    cost_percentage=0.02
                )
                strategies.append(vix_hedge)
            
            # 2. Currency Hedging
            currency_hedge = HedgingStrategy(
                strategy_name="Currency Protection",
                assets_to_add=[
                    {"symbol": "DXY", "weight": 0.08, "rationale": "USD strength hedge"},
                    {"symbol": "GC=F", "weight": 0.12, "rationale": "Currency debasement hedge"}
                ],
                assets_to_reduce=[],
                hedging_ratio=0.2,
                expected_protection=0.10,
                cost_percentage=0.015
            )
            strategies.append(currency_hedge)
            
            # 3. Geopolitical Hedging
            if any("war" in event.description.lower() or "conflict" in event.description.lower() 
                   for event in crisis_events):
                geopolitical_hedge = HedgingStrategy(
                    strategy_name="Geopolitical Risk Hedge",
                    assets_to_add=[
                        {"symbol": "GC=F", "weight": 0.15, "rationale": "Safe haven demand"},
                        {"symbol": "CL=F", "weight": 0.08, "rationale": "Energy security"},
                        {"symbol": "XLU", "weight": 0.10, "rationale": "Defensive utilities"}
                    ],
                    assets_to_reduce=[
                        {"asset_class": "equity_international", "reduction": 0.5}
                    ],
                    hedging_ratio=0.4,
                    expected_protection=0.25,
                    cost_percentage=0.025
                )
                strategies.append(geopolitical_hedge)
            
            # 4. Inflation Hedging
            if any("inflation" in event.description.lower() for event in crisis_events):
                inflation_hedge = HedgingStrategy(
                    strategy_name="Inflation Protection",
                    assets_to_add=[
                        {"symbol": "TIPS", "weight": 0.15, "rationale": "Inflation-protected securities"},
                        {"symbol": "VNQ", "weight": 0.10, "rationale": "Real estate inflation hedge"},
                        {"symbol": "DBC", "weight": 0.08, "rationale": "Commodity basket"}
                    ],
                    assets_to_reduce=[
                        {"asset_class": "debt_long_term", "reduction": 0.4}
                    ],
                    hedging_ratio=0.35,
                    expected_protection=0.20,
                    cost_percentage=0.02
                )
                strategies.append(inflation_hedge)
            
            return strategies
            
        except Exception as e:
            print(f"Error generating hedging strategies: {e}")
            return []
    
    async def _calculate_expected_performance(self, allocation: List[AssetAllocation]) -> Dict[str, Any]:
        """Calculate expected portfolio performance"""
        try:
            # Simulate expected returns based on asset allocation
            total_weight = sum(a.target_weight for a in allocation)
            
            if total_weight == 0:
                return {
                    "expected_annual_return": 0.0,
                    "expected_volatility": 0.0,
                    "expected_sharpe_ratio": 0.0,
                    "confidence_interval": [0.0, 0.0]
                }
            
            # Asset class expected returns (annualized)
            expected_returns = {
                "equity": 0.12,
                "debt": 0.06,
                "commodities": 0.08,
                "cash": 0.04
            }
            
            # Calculate weighted expected return
            portfolio_return = 0.0
            for asset in allocation:
                asset_class = asset.asset_class.split('_')[0]  # Extract main class
                expected_return = expected_returns.get(asset_class, 0.08)
                portfolio_return += asset.target_weight * expected_return
            
            # Estimate volatility (simplified)
            portfolio_volatility = 0.15  # Base volatility
            
            # Adjust for diversification
            diversification_benefit = len(set(a.asset_class for a in allocation)) * 0.01
            portfolio_volatility = max(0.08, portfolio_volatility - diversification_benefit)
            
            sharpe_ratio = (portfolio_return - 0.04) / portfolio_volatility
            
            return {
                "expected_annual_return": portfolio_return,
                "expected_volatility": portfolio_volatility,
                "expected_sharpe_ratio": sharpe_ratio,
                "confidence_interval": [
                    portfolio_return - 1.96 * portfolio_volatility,
                    portfolio_return + 1.96 * portfolio_volatility
                ]
            }
            
        except Exception as e:
            print(f"Error calculating expected performance: {e}")
            return {}
    
    async def _generate_rebalancing_plan(
        self, 
        current_portfolio: Dict[str, Any], 
        optimal_allocation: List[AssetAllocation]
    ) -> Dict[str, Any]:
        """Generate detailed rebalancing instructions"""
        
        plan = {
            "total_trades": 0,
            "estimated_cost": 0.0,
            "time_to_execute": "1-2 days",
            "trade_instructions": [],
            "priority_order": []
        }
        
        try:
            current_holdings = {h.get("symbol", ""): h for h in current_portfolio.get("holdings", [])}
            
            for target_asset in optimal_allocation:
                current_holding = current_holdings.get(target_asset.symbol, {})
                current_weight = current_holding.get("weight", 0.0)
                
                weight_diff = target_asset.target_weight - current_weight
                
                if abs(weight_diff) > 0.01:  # 1% threshold
                    action = "buy" if weight_diff > 0 else "sell"
                    amount = abs(weight_diff) * current_portfolio.get("total_value", 0)
                    
                    instruction = {
                        "symbol": target_asset.symbol,
                        "name": target_asset.name,
                        "action": action,
                        "current_weight": current_weight,
                        "target_weight": target_asset.target_weight,
                        "amount_inr": amount,
                        "priority": "high" if abs(weight_diff) > 0.05 else "medium",
                        "rationale": target_asset.rationale
                    }
                    
                    plan["trade_instructions"].append(instruction)
                    plan["total_trades"] += 1
                    plan["estimated_cost"] += amount * 0.001  # 0.1% transaction cost
            
            # Sort by priority
            plan["trade_instructions"].sort(
                key=lambda x: (x["priority"] == "high", abs(x["target_weight"] - x["current_weight"])),
                reverse=True
            )
            
            plan["priority_order"] = [t["symbol"] for t in plan["trade_instructions"][:5]]
            
            return plan
            
        except Exception as e:
            print(f"Error generating rebalancing plan: {e}")
            return plan
    
    async def _generate_ai_recommendations(
        self,
        current_portfolio: Dict[str, Any],
        optimal_allocation: List[AssetAllocation],
        crisis_events: List
    ) -> List[str]:
        """Generate AI-powered investment recommendations"""
        
        try:
            portfolio_summary = f"Current portfolio value: ₹{current_portfolio.get('total_value', 0):,.2f}"
            allocation_summary = f"Recommended allocation: {len(optimal_allocation)} assets"
            crisis_summary = f"Crisis events: {len(crisis_events)} active"
            
            prompt = f"""
            Based on the following portfolio information:
            {portfolio_summary}
            {allocation_summary}
            {crisis_summary}
            
            Provide 5 specific, actionable investment recommendations for an Indian investor.
            Focus on crisis hedging, risk management, and optimal returns.
            Include specific asset classes and rationale.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert financial advisor specializing in Indian markets and crisis response strategies."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            recommendations_text = response.choices[0].message.content.strip()
            recommendations = [line.strip() for line in recommendations_text.split('\n') if line.strip()]
            
            return recommendations[:5]
            
        except Exception as e:
            print(f"Error generating AI recommendations: {e}")
            return [
                "Maintain 15-20% cash allocation for crisis liquidity",
                "Increase gold allocation to 10-15% for geopolitical hedging",
                "Focus on large-cap Indian equities for stability",
                "Add defensive sectors (utilities, healthcare) during volatility",
                "Consider treasury bonds for capital preservation"
            ]
    
    def _get_stock_name(self, symbol: str) -> str:
        """Get full company name from symbol"""
        name_mapping = {
            "RELIANCE.NS": "Reliance Industries Limited",
            "TCS.NS": "Tata Consultancy Services",
            "HDFCBANK.NS": "HDFC Bank Limited", 
            "INFY.NS": "Infosys Limited",
            "ICICIBANK.NS": "ICICI Bank Limited"
        }
        return name_mapping.get(symbol, symbol)
    
    async def _cache_optimization_result(self, user_id: str, result: Dict[str, Any]):
        """Cache optimization result in Redis"""
        try:
            cache_key = f"portfolio_optimization:{user_id}"
            self.redis_client.setex(
                cache_key,
                3600,  # 1 hour expiration
                json.dumps(result, default=str)
            )
        except Exception as e:
            print(f"Error caching optimization result: {e}")
    
    async def get_cached_optimization(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached optimization result"""
        try:
            cache_key = f"portfolio_optimization:{user_id}"
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"Error getting cached optimization: {e}")
        return None
