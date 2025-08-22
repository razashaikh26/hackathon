"""
Crisis Response & Geopolitical Monitoring Service
Real-time monitoring of global events that could impact financial markets
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import redis
from dataclasses import dataclass
import openai
from decouple import config
import yfinance as yf
import pandas as pd
import numpy as np

@dataclass
class CrisisEvent:
    event_type: str
    severity: float  # 0-10 scale
    region: str
    description: str
    timestamp: datetime
    market_impact: str
    recommended_actions: List[str]

@dataclass
class MarketVolatility:
    vix_level: float
    change_24h: float
    trend: str
    risk_level: str

class CrisisMonitorService:
    def __init__(self):
        self.redis_client = redis.from_url(config("REDIS_URL"))
        self.openai_client = openai.OpenAI(api_key=config("OPENAI_API_KEY"))
        self.news_sources = [
            "https://newsapi.org/v2/top-headlines",
            "https://api.polygon.io/v1/meta/symbols/SPY/news",
            "https://financialmodelingprep.com/api/v3/stock_news"
        ]
        self.volatility_threshold = 25.0  # VIX threshold for crisis detection
        self.crisis_keywords = [
            "war", "invasion", "conflict", "sanctions", "recession", "inflation",
            "bank failure", "currency crisis", "trade war", "pandemic", "terrorist",
            "natural disaster", "oil crisis", "supply chain", "market crash"
        ]
    
    async def monitor_real_time_events(self) -> List[CrisisEvent]:
        """Monitor real-time geopolitical and economic events"""
        try:
            events = []
            
            # 1. News monitoring
            news_events = await self._monitor_news_feeds()
            events.extend(news_events)
            
            # 2. Market volatility monitoring
            volatility_event = await self._monitor_market_volatility()
            if volatility_event:
                events.append(volatility_event)
            
            # 3. Economic indicators monitoring
            economic_events = await self._monitor_economic_indicators()
            events.extend(economic_events)
            
            # 4. Central bank monitoring
            cb_events = await self._monitor_central_banks()
            events.extend(cb_events)
            
            # Cache events in Redis
            await self._cache_events(events)
            
            return events
            
        except Exception as e:
            print(f"Error monitoring events: {e}")
            return []
    
    async def _monitor_news_feeds(self) -> List[CrisisEvent]:
        """Monitor multiple news sources for crisis indicators"""
        events = []
        
        try:
            async with httpx.AsyncClient() as client:
                # News API monitoring
                news_url = f"https://newsapi.org/v2/everything"
                params = {
                    "q": "war OR recession OR inflation OR crisis OR market crash",
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 50,
                    "apiKey": config("NEWS_API_KEY", "demo_key")
                }
                
                response = await client.get(news_url, params=params)
                if response.status_code == 200:
                    news_data = response.json()
                    
                    for article in news_data.get("articles", [])[:10]:
                        severity = await self._analyze_news_severity(article)
                        if severity >= 6.0:  # High severity threshold
                            event = CrisisEvent(
                                event_type="geopolitical",
                                severity=severity,
                                region=await self._extract_region(article),
                                description=article.get("title", ""),
                                timestamp=datetime.now(),
                                market_impact=await self._predict_market_impact(article),
                                recommended_actions=await self._generate_recommendations(article, severity)
                            )
                            events.append(event)
                            
        except Exception as e:
            print(f"Error monitoring news feeds: {e}")
            
        return events
    
    async def _monitor_market_volatility(self) -> Optional[CrisisEvent]:
        """Monitor VIX and market volatility indicators"""
        try:
            # Get VIX data
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period="5d")
            
            current_vix = float(vix_data['Close'].iloc[-1])
            prev_vix = float(vix_data['Close'].iloc[-2])
            change_24h = ((current_vix - prev_vix) / prev_vix) * 100
            
            volatility = MarketVolatility(
                vix_level=current_vix,
                change_24h=change_24h,
                trend="rising" if change_24h > 0 else "falling",
                risk_level=self._assess_volatility_risk(current_vix)
            )
            
            # Create crisis event if volatility is high
            if current_vix >= self.volatility_threshold:
                return CrisisEvent(
                    event_type="market_volatility",
                    severity=min(10.0, current_vix / 5.0),
                    region="global",
                    description=f"High market volatility detected: VIX at {current_vix:.2f}",
                    timestamp=datetime.now(),
                    market_impact="high_volatility",
                    recommended_actions=await self._generate_volatility_recommendations(volatility)
                )
                
        except Exception as e:
            print(f"Error monitoring market volatility: {e}")
            
        return None
    
    async def _monitor_economic_indicators(self) -> List[CrisisEvent]:
        """Monitor key economic indicators"""
        events = []
        
        try:
            # Monitor key indices for sudden movements
            indices = ["^GSPC", "^DJI", "^IXIC", "^RUT", "GC=F", "CL=F"]  # S&P, Dow, Nasdaq, Russell, Gold, Oil
            
            for symbol in indices:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="2d")
                
                if len(data) >= 2:
                    current_price = float(data['Close'].iloc[-1])
                    prev_price = float(data['Close'].iloc[-2])
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                    
                    # Detect significant movements (>3% for indices, >5% for commodities)
                    threshold = 5.0 if symbol in ["GC=F", "CL=F"] else 3.0
                    
                    if abs(change_pct) >= threshold:
                        severity = min(10.0, abs(change_pct) / 2.0)
                        
                        event = CrisisEvent(
                            event_type="market_movement",
                            severity=severity,
                            region="global",
                            description=f"{symbol} moved {change_pct:.2f}% in 24h",
                            timestamp=datetime.now(),
                            market_impact="significant_movement",
                            recommended_actions=await self._generate_market_movement_recommendations(symbol, change_pct)
                        )
                        events.append(event)
                        
        except Exception as e:
            print(f"Error monitoring economic indicators: {e}")
            
        return events
    
    async def _monitor_central_banks(self) -> List[CrisisEvent]:
        """Monitor central bank announcements and policy changes"""
        events = []
        
        try:
            # This would integrate with central bank APIs or economic calendar APIs
            # For now, we'll use news monitoring for central bank keywords
            cb_keywords = [
                "federal reserve", "ECB", "bank of england", "bank of japan",
                "interest rate", "monetary policy", "quantitative easing"
            ]
            
            # Implementation would fetch from economic calendar APIs
            # This is a placeholder for the structure
            
        except Exception as e:
            print(f"Error monitoring central banks: {e}")
            
        return events
    
    async def _analyze_news_severity(self, article: Dict) -> float:
        """Use AI to analyze news article severity"""
        try:
            content = f"{article.get('title', '')} {article.get('description', '')}"
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze this news article and rate its potential impact on financial markets on a scale of 0-10. Consider geopolitical risks, economic implications, and market volatility potential. Return only a number."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            severity_text = response.choices[0].message.content.strip()
            return float(severity_text) if severity_text.replace('.', '').isdigit() else 0.0
            
        except Exception as e:
            print(f"Error analyzing news severity: {e}")
            return 0.0
    
    async def _extract_region(self, article: Dict) -> str:
        """Extract geographical region from news article"""
        content = f"{article.get('title', '')} {article.get('description', '')}"
        
        regions = {
            "USA": ["united states", "america", "us ", "usa"],
            "Europe": ["europe", "eu ", "eurozone", "germany", "france", "uk"],
            "Asia": ["china", "japan", "india", "asia", "korea"],
            "Middle East": ["middle east", "israel", "iran", "saudi", "uae"],
            "Global": ["global", "worldwide", "international"]
        }
        
        content_lower = content.lower()
        for region, keywords in regions.items():
            if any(keyword in content_lower for keyword in keywords):
                return region
                
        return "Global"
    
    async def _predict_market_impact(self, article: Dict) -> str:
        """Predict market impact category"""
        try:
            content = f"{article.get('title', '')} {article.get('description', '')}"
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Classify the market impact of this news as: 'bullish', 'bearish', 'neutral', 'high_volatility', or 'sector_specific'. Return only the classification."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=20,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return "neutral"
    
    async def _generate_recommendations(self, article: Dict, severity: float) -> List[str]:
        """Generate AI-powered investment recommendations"""
        try:
            content = f"{article.get('title', '')} {article.get('description', '')}"
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"Based on this news event with severity {severity}/10, provide 3-5 specific investment recommendations for crisis hedging. Include asset classes, percentages, and rationale. Format as a Python list of strings."
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=200,
                temperature=0.2
            )
            
            recommendations_text = response.choices[0].message.content.strip()
            # Parse the response into a list (simplified for now)
            return recommendations_text.split('\n')[:5]
            
        except Exception as e:
            return [
                "Increase defensive asset allocation",
                "Consider gold and precious metals exposure",
                "Maintain higher cash reserves",
                "Review and rebalance portfolio"
            ]
    
    async def _generate_volatility_recommendations(self, volatility: MarketVolatility) -> List[str]:
        """Generate recommendations based on market volatility"""
        recommendations = []
        
        if volatility.vix_level > 30:
            recommendations.extend([
                "Increase cash allocation to 15-20%",
                "Add defensive sectors (utilities, consumer staples)",
                "Consider VIX puts or volatility hedging",
                "Reduce leverage and high-beta positions"
            ])
        elif volatility.vix_level > 25:
            recommendations.extend([
                "Increase gold allocation by 5-10%",
                "Add treasury bonds for stability",
                "Consider defensive dividend stocks",
                "Monitor for entry opportunities"
            ])
        
        return recommendations
    
    async def _generate_market_movement_recommendations(self, symbol: str, change_pct: float) -> List[str]:
        """Generate recommendations based on market movements"""
        recommendations = []
        
        if symbol == "GC=F" and change_pct > 5:  # Gold rising
            recommendations.append("Consider reducing gold positions and taking profits")
        elif symbol == "GC=F" and change_pct < -5:  # Gold falling
            recommendations.append("Consider increasing gold allocation for hedging")
        elif symbol in ["^GSPC", "^DJI"] and change_pct < -3:  # Market falling
            recommendations.extend([
                "Increase defensive positioning",
                "Consider dollar-cost averaging opportunities",
                "Review stop-loss levels"
            ])
        
        return recommendations
    
    def _assess_volatility_risk(self, vix_level: float) -> str:
        """Assess risk level based on VIX"""
        if vix_level > 40:
            return "extreme"
        elif vix_level > 30:
            return "high"
        elif vix_level > 20:
            return "moderate"
        else:
            return "low"
    
    async def _cache_events(self, events: List[CrisisEvent]):
        """Cache events in Redis for quick access"""
        try:
            events_data = []
            for event in events:
                event_dict = {
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "region": event.region,
                    "description": event.description,
                    "timestamp": event.timestamp.isoformat(),
                    "market_impact": event.market_impact,
                    "recommended_actions": event.recommended_actions
                }
                events_data.append(event_dict)
            
            # Store in Redis with 1-hour expiration
            self.redis_client.setex(
                "crisis_events",
                3600,
                json.dumps(events_data)
            )
            
        except Exception as e:
            print(f"Error caching events: {e}")
    
    async def get_cached_events(self) -> List[CrisisEvent]:
        """Get cached crisis events from Redis"""
        try:
            cached_data = self.redis_client.get("crisis_events")
            if cached_data:
                events_data = json.loads(cached_data)
                events = []
                
                for event_dict in events_data:
                    event = CrisisEvent(
                        event_type=event_dict["event_type"],
                        severity=event_dict["severity"],
                        region=event_dict["region"],
                        description=event_dict["description"],
                        timestamp=datetime.fromisoformat(event_dict["timestamp"]),
                        market_impact=event_dict["market_impact"],
                        recommended_actions=event_dict["recommended_actions"]
                    )
                    events.append(event)
                
                return events
                
        except Exception as e:
            print(f"Error getting cached events: {e}")
            
        return []
    
    async def execute_crisis_response(self, user_id: str, events: List[CrisisEvent]) -> Dict[str, Any]:
        """Execute automated crisis response based on detected events"""
        try:
            high_severity_events = [e for e in events if e.severity >= 7.0]
            
            if not high_severity_events:
                return {"status": "no_action_required", "events_monitored": len(events)}
            
            # Aggregate recommendations
            all_recommendations = []
            for event in high_severity_events:
                all_recommendations.extend(event.recommended_actions)
            
            # Remove duplicates and prioritize
            unique_recommendations = list(set(all_recommendations))
            
            response = {
                "status": "crisis_response_activated",
                "events_triggered": len(high_severity_events),
                "max_severity": max(e.severity for e in high_severity_events),
                "recommendations": unique_recommendations[:10],  # Top 10 recommendations
                "auto_adjustments": await self._execute_auto_adjustments(user_id, high_severity_events),
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the response
            self.redis_client.setex(
                f"crisis_response:{user_id}",
                1800,  # 30 minutes
                json.dumps(response)
            )
            
            return response
            
        except Exception as e:
            print(f"Error executing crisis response: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _execute_auto_adjustments(self, user_id: str, events: List[CrisisEvent]) -> List[str]:
        """Execute automatic portfolio adjustments based on crisis events"""
        adjustments = []
        
        try:
            # This would integrate with the portfolio service
            # For now, return planned adjustments
            
            max_severity = max(e.severity for e in events)
            
            if max_severity >= 9.0:  # Extreme crisis
                adjustments = [
                    "Increased cash allocation to 25%",
                    "Added 15% gold and precious metals",
                    "Reduced equity exposure by 20%",
                    "Added treasury bonds for stability"
                ]
            elif max_severity >= 7.0:  # High crisis
                adjustments = [
                    "Increased cash allocation to 15%",
                    "Added 10% defensive sectors",
                    "Reduced high-beta positions",
                    "Added inflation hedging assets"
                ]
            
        except Exception as e:
            print(f"Error executing auto adjustments: {e}")
            
        return adjustments
