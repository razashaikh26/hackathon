"""
Advanced Risk Analyzer with Real-time Monitoring
Comprehensive risk assessment and management for financial portfolios
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
import asyncio
import httpx
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

@dataclass
class RiskMetric:
    metric_name: str
    current_value: float
    threshold: float
    risk_level: str  # low, medium, high, extreme
    trend: str  # improving, stable, deteriorating
    recommendation: str

@dataclass
class RiskScenario:
    scenario_name: str
    probability: float
    potential_loss: float
    timeline: str
    mitigation_strategies: List[str]

@dataclass
class RiskAssessment:
    overall_risk_score: float  # 0-100
    risk_category: str
    risk_metrics: List[RiskMetric]
    stress_test_results: Dict[str, Any]
    scenario_analysis: List[RiskScenario]
    recommendations: List[str]
    timestamp: datetime

class RiskAnalyzer:
    def __init__(self):
        self.redis_client = redis.from_url(config("REDIS_URL"))
        self.openai_client = openai.OpenAI(api_key=config("OPENAI_API_KEY"))
        
        # Risk thresholds
        self.risk_thresholds = {
            "portfolio_volatility": {"low": 0.10, "medium": 0.15, "high": 0.20, "extreme": 0.30},
            "max_drawdown": {"low": 0.05, "medium": 0.10, "high": 0.15, "extreme": 0.25},
            "var_95": {"low": 0.02, "medium": 0.05, "high": 0.08, "extreme": 0.12},
            "concentration_risk": {"low": 0.20, "medium": 0.30, "high": 0.40, "extreme": 0.60},
            "correlation_risk": {"low": 0.30, "medium": 0.50, "high": 0.70, "extreme": 0.85},
            "liquidity_risk": {"low": 0.05, "medium": 0.10, "high": 0.20, "extreme": 0.35},
            "currency_risk": {"low": 0.03, "medium": 0.08, "high": 0.15, "extreme": 0.25},
            "sector_concentration": {"low": 0.25, "medium": 0.35, "high": 0.50, "extreme": 0.70}
        }
        
        # Stress test scenarios
        self.stress_scenarios = {
            "market_crash_2008": {"equity_decline": -0.40, "bond_decline": -0.10, "commodity_rise": 0.15},
            "covid_2020": {"equity_decline": -0.35, "bond_rise": 0.05, "gold_rise": 0.25},
            "ukraine_war_2022": {"energy_rise": 0.40, "commodity_rise": 0.30, "equity_decline": -0.15},
            "inflation_shock": {"bond_decline": -0.20, "commodity_rise": 0.35, "currency_decline": -0.15},
            "recession_scenario": {"equity_decline": -0.25, "bond_rise": 0.10, "defensive_outperform": 0.05},
            "geopolitical_crisis": {"safe_haven_rise": 0.20, "emerging_decline": -0.30, "volatility_spike": 0.50}
        }
    
    async def analyze_portfolio_risk(
        self, 
        user_id: str,
        portfolio: Dict[str, Any],
        market_data: Dict[str, Any] = None,
        crisis_events: List = None
    ) -> RiskAssessment:
        """Comprehensive portfolio risk analysis"""
        
        try:
            # 1. Calculate individual risk metrics
            risk_metrics = await self._calculate_risk_metrics(portfolio, market_data)
            
            # 2. Perform stress testing
            stress_results = await self._perform_stress_tests(portfolio)
            
            # 3. Scenario analysis
            scenarios = await self._scenario_analysis(portfolio, crisis_events or [])
            
            # 4. Calculate overall risk score
            overall_score = await self._calculate_overall_risk_score(risk_metrics, stress_results)
            
            # 5. Generate recommendations
            recommendations = await self._generate_risk_recommendations(
                risk_metrics, stress_results, scenarios, crisis_events
            )
            
            # 6. Determine risk category
            risk_category = self._determine_risk_category(overall_score)
            
            assessment = RiskAssessment(
                overall_risk_score=overall_score,
                risk_category=risk_category,
                risk_metrics=risk_metrics,
                stress_test_results=stress_results,
                scenario_analysis=scenarios,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
            # Cache the assessment
            await self._cache_risk_assessment(user_id, assessment)
            
            return assessment
            
        except Exception as e:
            print(f"Error analyzing portfolio risk: {e}")
            return self._default_risk_assessment()
    
    async def _calculate_risk_metrics(
        self, 
        portfolio: Dict[str, Any], 
        market_data: Dict[str, Any] = None
    ) -> List[RiskMetric]:
        """Calculate comprehensive risk metrics"""
        
        metrics = []
        
        try:
            holdings = portfolio.get("holdings", [])
            total_value = portfolio.get("total_value", 0)
            
            if not holdings or total_value == 0:
                return self._default_risk_metrics()
            
            # 1. Portfolio Volatility
            portfolio_volatility = await self._calculate_portfolio_volatility(holdings)
            volatility_metric = RiskMetric(
                metric_name="Portfolio Volatility",
                current_value=portfolio_volatility,
                threshold=self.risk_thresholds["portfolio_volatility"]["medium"],
                risk_level=self._assess_risk_level(portfolio_volatility, "portfolio_volatility"),
                trend=await self._calculate_trend(user_id=portfolio.get("user_id"), metric="volatility"),
                recommendation=self._get_volatility_recommendation(portfolio_volatility)
            )
            metrics.append(volatility_metric)
            
            # 2. Concentration Risk
            concentration_risk = self._calculate_concentration_risk(holdings)
            concentration_metric = RiskMetric(
                metric_name="Concentration Risk",
                current_value=concentration_risk,
                threshold=self.risk_thresholds["concentration_risk"]["medium"],
                risk_level=self._assess_risk_level(concentration_risk, "concentration_risk"),
                trend="stable",
                recommendation=self._get_concentration_recommendation(concentration_risk)
            )
            metrics.append(concentration_metric)
            
            # 3. Sector Concentration
            sector_risk = self._calculate_sector_concentration(holdings)
            sector_metric = RiskMetric(
                metric_name="Sector Concentration",
                current_value=sector_risk,
                threshold=self.risk_thresholds["sector_concentration"]["medium"],
                risk_level=self._assess_risk_level(sector_risk, "sector_concentration"),
                trend="stable",
                recommendation=self._get_sector_recommendation(sector_risk)
            )
            metrics.append(sector_metric)
            
            # 4. Liquidity Risk
            liquidity_risk = await self._calculate_liquidity_risk(holdings)
            liquidity_metric = RiskMetric(
                metric_name="Liquidity Risk", 
                current_value=liquidity_risk,
                threshold=self.risk_thresholds["liquidity_risk"]["medium"],
                risk_level=self._assess_risk_level(liquidity_risk, "liquidity_risk"),
                trend="stable",
                recommendation=self._get_liquidity_recommendation(liquidity_risk)
            )
            metrics.append(liquidity_metric)
            
            # 5. Currency Risk
            currency_risk = self._calculate_currency_risk(holdings)
            currency_metric = RiskMetric(
                metric_name="Currency Risk",
                current_value=currency_risk,
                threshold=self.risk_thresholds["currency_risk"]["medium"],
                risk_level=self._assess_risk_level(currency_risk, "currency_risk"),
                trend="stable", 
                recommendation=self._get_currency_recommendation(currency_risk)
            )
            metrics.append(currency_metric)
            
            # 6. Correlation Risk
            correlation_risk = await self._calculate_correlation_risk(holdings)
            correlation_metric = RiskMetric(
                metric_name="Asset Correlation",
                current_value=correlation_risk,
                threshold=self.risk_thresholds["correlation_risk"]["medium"],
                risk_level=self._assess_risk_level(correlation_risk, "correlation_risk"),
                trend="stable",
                recommendation=self._get_correlation_recommendation(correlation_risk)
            )
            metrics.append(correlation_metric)
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating risk metrics: {e}")
            return self._default_risk_metrics()
    
    async def _calculate_portfolio_volatility(self, holdings: List[Dict]) -> float:
        """Calculate portfolio volatility"""
        try:
            # Simulate portfolio volatility calculation
            # In real implementation, this would use historical returns data
            weights = np.array([h.get("weight", 0) for h in holdings])
            
            # Simulated individual asset volatilities
            individual_volatilities = np.random.uniform(0.15, 0.35, len(holdings))
            
            # Simulated correlation matrix
            n_assets = len(holdings)
            correlation_matrix = np.random.uniform(0.3, 0.7, (n_assets, n_assets))
            np.fill_diagonal(correlation_matrix, 1.0)
            
            # Portfolio volatility calculation
            covariance_matrix = np.outer(individual_volatilities, individual_volatilities) * correlation_matrix
            portfolio_variance = np.dot(weights, np.dot(covariance_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            return float(portfolio_volatility)
            
        except Exception as e:
            print(f"Error calculating portfolio volatility: {e}")
            return 0.20  # Default moderate volatility
    
    def _calculate_concentration_risk(self, holdings: List[Dict]) -> float:
        """Calculate concentration risk (max single position weight)"""
        try:
            if not holdings:
                return 0.0
            
            weights = [h.get("weight", 0) for h in holdings]
            max_weight = max(weights) if weights else 0.0
            
            return float(max_weight)
            
        except Exception as e:
            print(f"Error calculating concentration risk: {e}")
            return 0.0
    
    def _calculate_sector_concentration(self, holdings: List[Dict]) -> float:
        """Calculate sector concentration risk"""
        try:
            if not holdings:
                return 0.0
            
            # Group by sector and calculate total exposure
            sector_weights = {}
            for holding in holdings:
                sector = holding.get("sector", "Unknown")
                weight = holding.get("weight", 0)
                sector_weights[sector] = sector_weights.get(sector, 0) + weight
            
            # Return maximum sector exposure
            max_sector_weight = max(sector_weights.values()) if sector_weights else 0.0
            
            return float(max_sector_weight)
            
        except Exception as e:
            print(f"Error calculating sector concentration: {e}")
            return 0.0
    
    async def _calculate_liquidity_risk(self, holdings: List[Dict]) -> float:
        """Calculate liquidity risk based on asset types"""
        try:
            if not holdings:
                return 0.0
            
            # Liquidity scores by asset type
            liquidity_scores = {
                "cash": 1.0,
                "large_cap_equity": 0.9,
                "government_bonds": 0.85,
                "mid_cap_equity": 0.7,
                "corporate_bonds": 0.6,
                "small_cap_equity": 0.4,
                "real_estate": 0.2,
                "private_equity": 0.1,
                "commodity": 0.5
            }
            
            total_illiquid = 0.0
            total_weight = 0.0
            
            for holding in holdings:
                asset_type = holding.get("asset_type", "mid_cap_equity")
                weight = holding.get("weight", 0)
                liquidity_score = liquidity_scores.get(asset_type, 0.5)
                
                # Higher score = more liquid, so illiquidity = 1 - liquidity
                illiquidity = 1 - liquidity_score
                total_illiquid += weight * illiquidity
                total_weight += weight
            
            average_illiquidity = total_illiquid / total_weight if total_weight > 0 else 0.0
            
            return float(average_illiquidity)
            
        except Exception as e:
            print(f"Error calculating liquidity risk: {e}")
            return 0.1  # Default low liquidity risk
    
    def _calculate_currency_risk(self, holdings: List[Dict]) -> float:
        """Calculate currency exposure risk"""
        try:
            if not holdings:
                return 0.0
            
            # Calculate non-INR exposure
            foreign_exposure = 0.0
            total_weight = 0.0
            
            for holding in holdings:
                currency = holding.get("currency", "INR")
                weight = holding.get("weight", 0)
                
                if currency != "INR":
                    foreign_exposure += weight
                
                total_weight += weight
            
            currency_risk = foreign_exposure / total_weight if total_weight > 0 else 0.0
            
            return float(currency_risk)
            
        except Exception as e:
            print(f"Error calculating currency risk: {e}")
            return 0.0
    
    async def _calculate_correlation_risk(self, holdings: List[Dict]) -> float:
        """Calculate average correlation between assets"""
        try:
            if len(holdings) < 2:
                return 0.0
            
            # Simulate correlation calculation
            # In real implementation, use historical returns correlation
            n_assets = len(holdings)
            
            # Generate simulated correlation matrix
            correlations = []
            for i in range(n_assets):
                for j in range(i + 1, n_assets):
                    # Simulate correlation based on asset types
                    correlation = np.random.uniform(0.2, 0.8)
                    correlations.append(correlation)
            
            average_correlation = np.mean(correlations) if correlations else 0.0
            
            return float(average_correlation)
            
        except Exception as e:
            print(f"Error calculating correlation risk: {e}")
            return 0.5  # Default moderate correlation
    
    async def _perform_stress_tests(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive stress testing"""
        
        stress_results = {}
        
        try:
            holdings = portfolio.get("holdings", [])
            total_value = portfolio.get("total_value", 0)
            
            if not holdings or total_value == 0:
                return {"error": "Invalid portfolio data"}
            
            for scenario_name, scenario_params in self.stress_scenarios.items():
                scenario_loss = await self._calculate_scenario_impact(holdings, scenario_params)
                
                stress_results[scenario_name] = {
                    "potential_loss_percentage": scenario_loss,
                    "potential_loss_amount": total_value * scenario_loss,
                    "recovery_time_estimate": self._estimate_recovery_time(scenario_loss),
                    "mitigation_effectiveness": await self._assess_mitigation_effectiveness(holdings, scenario_params)
                }
            
            # Calculate worst-case scenario
            worst_case_loss = max([result["potential_loss_percentage"] for result in stress_results.values()])
            
            stress_results["summary"] = {
                "worst_case_loss": worst_case_loss,
                "average_loss": np.mean([result["potential_loss_percentage"] for result in stress_results.values()]),
                "stress_test_score": self._calculate_stress_test_score(stress_results),
                "overall_resilience": self._assess_portfolio_resilience(stress_results)
            }
            
            return stress_results
            
        except Exception as e:
            print(f"Error performing stress tests: {e}")
            return {"error": str(e)}
    
    async def _calculate_scenario_impact(self, holdings: List[Dict], scenario_params: Dict[str, float]) -> float:
        """Calculate portfolio impact for a specific stress scenario"""
        
        try:
            total_impact = 0.0
            total_weight = 0.0
            
            for holding in holdings:
                weight = holding.get("weight", 0)
                asset_type = holding.get("asset_type", "equity")
                
                # Map asset types to scenario parameters
                impact = 0.0
                if "equity" in asset_type.lower():
                    impact = scenario_params.get("equity_decline", 0)
                elif "bond" in asset_type.lower() or "debt" in asset_type.lower():
                    impact = scenario_params.get("bond_decline", scenario_params.get("bond_rise", 0))
                elif "commodity" in asset_type.lower() or "gold" in asset_type.lower():
                    impact = scenario_params.get("commodity_rise", 0)
                elif "energy" in asset_type.lower():
                    impact = scenario_params.get("energy_rise", scenario_params.get("commodity_rise", 0))
                
                total_impact += weight * impact
                total_weight += weight
            
            portfolio_impact = total_impact / total_weight if total_weight > 0 else 0.0
            
            return abs(portfolio_impact)  # Return absolute loss
            
        except Exception as e:
            print(f"Error calculating scenario impact: {e}")
            return 0.0
    
    def _estimate_recovery_time(self, loss_percentage: float) -> str:
        """Estimate portfolio recovery time based on loss severity"""
        if loss_percentage <= 0.05:
            return "1-3 months"
        elif loss_percentage <= 0.10:
            return "6-12 months"
        elif loss_percentage <= 0.20:
            return "1-2 years"
        elif loss_percentage <= 0.30:
            return "2-4 years"
        else:
            return "4+ years"
    
    async def _assess_mitigation_effectiveness(self, holdings: List[Dict], scenario_params: Dict[str, float]) -> float:
        """Assess how well the current portfolio is positioned to mitigate the scenario"""
        
        try:
            # Calculate defensive positioning
            defensive_weight = 0.0
            total_weight = 0.0
            
            for holding in holdings:
                asset_type = holding.get("asset_type", "equity")
                weight = holding.get("weight", 0)
                
                # Defensive assets get higher mitigation scores
                if any(defensive in asset_type.lower() for defensive in ["cash", "government", "gold", "utility"]):
                    defensive_weight += weight
                
                total_weight += weight
            
            defensive_ratio = defensive_weight / total_weight if total_weight > 0 else 0.0
            
            # Mitigation effectiveness: higher defensive ratio = better mitigation
            mitigation_score = min(1.0, defensive_ratio * 2)  # Scale to 0-1
            
            return mitigation_score
            
        except Exception as e:
            print(f"Error assessing mitigation effectiveness: {e}")
            return 0.5
    
    def _calculate_stress_test_score(self, stress_results: Dict[str, Any]) -> float:
        """Calculate overall stress test score (0-100)"""
        try:
            losses = [result["potential_loss_percentage"] for key, result in stress_results.items() 
                     if isinstance(result, dict) and "potential_loss_percentage" in result]
            
            if not losses:
                return 50.0  # Default moderate score
            
            average_loss = np.mean(losses)
            max_loss = max(losses)
            
            # Score calculation: lower losses = higher score
            score = 100 * (1 - (average_loss * 0.7 + max_loss * 0.3))
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            print(f"Error calculating stress test score: {e}")
            return 50.0
    
    def _assess_portfolio_resilience(self, stress_results: Dict[str, Any]) -> str:
        """Assess overall portfolio resilience"""
        try:
            score = stress_results.get("summary", {}).get("stress_test_score", 50.0)
            
            if score >= 80:
                return "Highly Resilient"
            elif score >= 60:
                return "Moderately Resilient" 
            elif score >= 40:
                return "Vulnerable"
            else:
                return "High Risk"
                
        except Exception as e:
            return "Unknown"
    
    async def _scenario_analysis(self, portfolio: Dict[str, Any], crisis_events: List) -> List[RiskScenario]:
        """Perform forward-looking scenario analysis"""
        
        scenarios = []
        
        try:
            # Base economic scenarios
            base_scenarios = [
                {
                    "name": "Economic Recession",
                    "probability": 0.25,
                    "impact": -0.20,
                    "timeline": "6-18 months",
                    "description": "Economic downturn with declining GDP"
                },
                {
                    "name": "High Inflation Period",
                    "probability": 0.30,
                    "impact": -0.15,
                    "timeline": "12-24 months", 
                    "description": "Sustained high inflation eroding real returns"
                },
                {
                    "name": "Market Correction",
                    "probability": 0.40,
                    "impact": -0.12,
                    "timeline": "3-6 months",
                    "description": "10-20% market decline from recent highs"
                }
            ]
            
            # Add crisis-specific scenarios if events are detected
            if crisis_events:
                for event in crisis_events[:3]:  # Top 3 events
                    crisis_scenario = {
                        "name": f"Crisis: {event.event_type}",
                        "probability": min(0.6, event.severity / 10.0),
                        "impact": -0.05 * event.severity,
                        "timeline": "1-12 months",
                        "description": event.description
                    }
                    base_scenarios.append(crisis_scenario)
            
            # Convert to RiskScenario objects
            portfolio_value = portfolio.get("total_value", 0)
            
            for scenario in base_scenarios:
                risk_scenario = RiskScenario(
                    scenario_name=scenario["name"],
                    probability=scenario["probability"],
                    potential_loss=abs(scenario["impact"]) * portfolio_value,
                    timeline=scenario["timeline"],
                    mitigation_strategies=await self._generate_mitigation_strategies(scenario)
                )
                scenarios.append(risk_scenario)
            
            # Sort by probability * impact (expected loss)
            scenarios.sort(key=lambda x: x.probability * x.potential_loss, reverse=True)
            
            return scenarios[:5]  # Return top 5 scenarios
            
        except Exception as e:
            print(f"Error in scenario analysis: {e}")
            return []
    
    async def _generate_mitigation_strategies(self, scenario: Dict[str, Any]) -> List[str]:
        """Generate mitigation strategies for specific scenarios"""
        
        strategies = []
        scenario_name = scenario.get("name", "").lower()
        
        try:
            if "recession" in scenario_name:
                strategies = [
                    "Increase cash allocation to 20%",
                    "Focus on defensive dividend stocks",
                    "Add government bonds for stability",
                    "Reduce cyclical sector exposure"
                ]
            elif "inflation" in scenario_name:
                strategies = [
                    "Increase commodity exposure",
                    "Add inflation-protected securities (TIPS)",
                    "Consider real estate investment",
                    "Reduce long-duration bonds"
                ]
            elif "correction" in scenario_name:
                strategies = [
                    "Implement stop-loss orders",
                    "Dollar-cost average during decline",
                    "Increase value stock allocation",
                    "Maintain dry powder for opportunities"
                ]
            elif "crisis" in scenario_name:
                strategies = [
                    "Increase gold and safe haven allocation",
                    "Add volatility hedging instruments",
                    "Reduce leverage and margin",
                    "Diversify across uncorrelated assets"
                ]
            else:
                strategies = [
                    "Maintain diversified allocation",
                    "Regular rebalancing",
                    "Monitor risk metrics closely",
                    "Keep adequate liquidity"
                ]
            
            return strategies
            
        except Exception as e:
            print(f"Error generating mitigation strategies: {e}")
            return ["Review and rebalance portfolio", "Consult with financial advisor"]
    
    async def _calculate_overall_risk_score(
        self, 
        risk_metrics: List[RiskMetric], 
        stress_results: Dict[str, Any]
    ) -> float:
        """Calculate overall portfolio risk score (0-100)"""
        
        try:
            if not risk_metrics:
                return 50.0  # Default moderate risk
            
            # Calculate weighted average of risk levels
            risk_level_scores = {"low": 20, "medium": 50, "high": 75, "extreme": 95}
            
            total_score = 0.0
            total_weight = 0.0
            
            # Risk metric weights
            metric_weights = {
                "Portfolio Volatility": 0.25,
                "Concentration Risk": 0.20,
                "Sector Concentration": 0.15,
                "Liquidity Risk": 0.15,
                "Currency Risk": 0.10,
                "Asset Correlation": 0.15
            }
            
            for metric in risk_metrics:
                weight = metric_weights.get(metric.metric_name, 0.1)
                score = risk_level_scores.get(metric.risk_level, 50)
                
                total_score += weight * score
                total_weight += weight
            
            base_score = total_score / total_weight if total_weight > 0 else 50.0
            
            # Adjust based on stress test results
            stress_score = stress_results.get("summary", {}).get("stress_test_score", 50.0)
            
            # Combined score (70% risk metrics, 30% stress test)
            overall_score = base_score * 0.7 + (100 - stress_score) * 0.3
            
            return max(0.0, min(100.0, overall_score))
            
        except Exception as e:
            print(f"Error calculating overall risk score: {e}")
            return 50.0
    
    async def _generate_risk_recommendations(
        self,
        risk_metrics: List[RiskMetric],
        stress_results: Dict[str, Any],
        scenarios: List[RiskScenario],
        crisis_events: List = None
    ) -> List[str]:
        """Generate AI-powered risk management recommendations"""
        
        try:
            # Collect high-risk areas
            high_risk_metrics = [m for m in risk_metrics if m.risk_level in ["high", "extreme"]]
            
            recommendations = []
            
            # Add metric-specific recommendations
            for metric in high_risk_metrics:
                recommendations.append(metric.recommendation)
            
            # Add stress test recommendations
            worst_case_loss = stress_results.get("summary", {}).get("worst_case_loss", 0)
            if worst_case_loss > 0.25:
                recommendations.append("Consider implementing downside protection strategies")
                recommendations.append("Increase allocation to uncorrelated assets")
            
            # Add scenario-specific recommendations
            for scenario in scenarios[:2]:  # Top 2 scenarios
                if scenario.probability > 0.3:
                    recommendations.extend(scenario.mitigation_strategies[:2])
            
            # Add crisis-specific recommendations
            if crisis_events:
                recommendations.append("Activate crisis response protocols")
                recommendations.append("Increase monitoring frequency to daily")
            
            # Use AI to generate additional personalized recommendations
            ai_recommendations = await self._generate_ai_risk_recommendations(
                risk_metrics, stress_results, crisis_events
            )
            recommendations.extend(ai_recommendations)
            
            # Remove duplicates and prioritize
            unique_recommendations = list(dict.fromkeys(recommendations))
            
            return unique_recommendations[:8]  # Return top 8 recommendations
            
        except Exception as e:
            print(f"Error generating risk recommendations: {e}")
            return [
                "Review portfolio diversification",
                "Consider reducing concentration risk",
                "Maintain adequate liquidity",
                "Monitor market conditions closely"
            ]
    
    async def _generate_ai_risk_recommendations(
        self,
        risk_metrics: List[RiskMetric],
        stress_results: Dict[str, Any],
        crisis_events: List = None
    ) -> List[str]:
        """Generate AI-powered risk recommendations"""
        
        try:
            # Prepare context for AI
            risk_summary = ", ".join([f"{m.metric_name}: {m.risk_level}" for m in risk_metrics])
            stress_summary = f"Worst case loss: {stress_results.get('summary', {}).get('worst_case_loss', 0):.1%}"
            crisis_summary = f"Active crisis events: {len(crisis_events or [])}"
            
            prompt = f"""
            Portfolio Risk Analysis:
            Risk Metrics: {risk_summary}
            Stress Test: {stress_summary}
            Crisis Events: {crisis_summary}
            
            Provide 3 specific, actionable risk management recommendations for an Indian investor.
            Focus on immediate actions to reduce portfolio risk.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert risk management advisor specializing in Indian financial markets."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.2
            )
            
            ai_recommendations = response.choices[0].message.content.strip().split('\n')
            return [rec.strip() for rec in ai_recommendations if rec.strip()][:3]
            
        except Exception as e:
            print(f"Error generating AI recommendations: {e}")
            return []
    
    def _assess_risk_level(self, value: float, metric_type: str) -> str:
        """Assess risk level based on value and thresholds"""
        
        thresholds = self.risk_thresholds.get(metric_type, {})
        
        if value <= thresholds.get("low", 0):
            return "low"
        elif value <= thresholds.get("medium", 0):
            return "medium" 
        elif value <= thresholds.get("high", 0):
            return "high"
        else:
            return "extreme"
    
    async def _calculate_trend(self, user_id: str, metric: str) -> str:
        """Calculate trend for a risk metric (requires historical data)"""
        try:
            # This would analyze historical risk metric data
            # For now, return default trend
            return "stable"
        except:
            return "stable"
    
    def _determine_risk_category(self, risk_score: float) -> str:
        """Determine overall risk category"""
        if risk_score <= 25:
            return "Low Risk"
        elif risk_score <= 50:
            return "Moderate Risk"
        elif risk_score <= 75:
            return "High Risk"
        else:
            return "Extreme Risk"
    
    # Recommendation methods for each metric
    def _get_volatility_recommendation(self, volatility: float) -> str:
        if volatility > 0.25:
            return "Consider adding defensive assets to reduce portfolio volatility"
        elif volatility > 0.20:
            return "Monitor volatility and consider rebalancing if it increases further"
        else:
            return "Portfolio volatility is within acceptable range"
    
    def _get_concentration_recommendation(self, concentration: float) -> str:
        if concentration > 0.30:
            return "Reduce position size of largest holding to improve diversification"
        elif concentration > 0.20:
            return "Monitor concentration risk and consider diversification"
        else:
            return "Concentration risk is well-managed"
    
    def _get_sector_recommendation(self, sector_risk: float) -> str:
        if sector_risk > 0.40:
            return "Diversify across sectors to reduce concentration risk"
        elif sector_risk > 0.30:
            return "Consider adding exposure to underrepresented sectors"
        else:
            return "Sector diversification is adequate"
    
    def _get_liquidity_recommendation(self, liquidity_risk: float) -> str:
        if liquidity_risk > 0.20:
            return "Increase allocation to liquid assets for better portfolio flexibility"
        elif liquidity_risk > 0.15:
            return "Monitor liquidity needs and maintain adequate cash reserves"
        else:
            return "Portfolio liquidity is sufficient"
    
    def _get_currency_recommendation(self, currency_risk: float) -> str:
        if currency_risk > 0.15:
            return "Consider currency hedging for foreign exposures"
        elif currency_risk > 0.10:
            return "Monitor currency movements and hedge if volatility increases"
        else:
            return "Currency risk is manageable"
    
    def _get_correlation_recommendation(self, correlation: float) -> str:
        if correlation > 0.70:
            return "Add uncorrelated assets to improve portfolio diversification"
        elif correlation > 0.50:
            return "Consider assets with lower correlation to existing holdings"
        else:
            return "Asset correlation provides good diversification benefits"
    
    def _default_risk_assessment(self) -> RiskAssessment:
        """Return default risk assessment in case of errors"""
        return RiskAssessment(
            overall_risk_score=50.0,
            risk_category="Moderate Risk",
            risk_metrics=self._default_risk_metrics(),
            stress_test_results={"error": "Unable to perform stress tests"},
            scenario_analysis=[],
            recommendations=["Review portfolio allocation", "Consult financial advisor"],
            timestamp=datetime.now()
        )
    
    def _default_risk_metrics(self) -> List[RiskMetric]:
        """Return default risk metrics"""
        return [
            RiskMetric("Portfolio Volatility", 0.15, 0.15, "medium", "stable", "Monitor volatility levels"),
            RiskMetric("Concentration Risk", 0.20, 0.30, "low", "stable", "Diversification is adequate"),
            RiskMetric("Liquidity Risk", 0.10, 0.10, "medium", "stable", "Maintain adequate liquidity")
        ]
    
    async def _cache_risk_assessment(self, user_id: str, assessment: RiskAssessment):
        """Cache risk assessment in Redis"""
        try:
            cache_key = f"risk_assessment:{user_id}"
            
            # Convert to dict for JSON serialization
            assessment_dict = {
                "overall_risk_score": assessment.overall_risk_score,
                "risk_category": assessment.risk_category,
                "risk_metrics": [
                    {
                        "metric_name": m.metric_name,
                        "current_value": m.current_value,
                        "threshold": m.threshold,
                        "risk_level": m.risk_level,
                        "trend": m.trend,
                        "recommendation": m.recommendation
                    } for m in assessment.risk_metrics
                ],
                "stress_test_results": assessment.stress_test_results,
                "scenario_analysis": [
                    {
                        "scenario_name": s.scenario_name,
                        "probability": s.probability,
                        "potential_loss": s.potential_loss,
                        "timeline": s.timeline,
                        "mitigation_strategies": s.mitigation_strategies
                    } for s in assessment.scenario_analysis
                ],
                "recommendations": assessment.recommendations,
                "timestamp": assessment.timestamp.isoformat()
            }
            
            self.redis_client.setex(
                cache_key,
                1800,  # 30 minutes
                json.dumps(assessment_dict)
            )
            
        except Exception as e:
            print(f"Error caching risk assessment: {e}")
    
    async def get_cached_risk_assessment(self, user_id: str) -> Optional[RiskAssessment]:
        """Get cached risk assessment"""
        try:
            cache_key = f"risk_assessment:{user_id}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                
                # Convert back to RiskAssessment object
                risk_metrics = [
                    RiskMetric(**metric) for metric in data["risk_metrics"]
                ]
                
                scenario_analysis = [
                    RiskScenario(**scenario) for scenario in data["scenario_analysis"]
                ]
                
                return RiskAssessment(
                    overall_risk_score=data["overall_risk_score"],
                    risk_category=data["risk_category"],
                    risk_metrics=risk_metrics,
                    stress_test_results=data["stress_test_results"],
                    scenario_analysis=scenario_analysis,
                    recommendations=data["recommendations"],
                    timestamp=datetime.fromisoformat(data["timestamp"])
                )
                
        except Exception as e:
            print(f"Error getting cached risk assessment: {e}")
            
        return None
