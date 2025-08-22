import httpx
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from app.core.config import settings

class MarketDataService:
    """
    Service for fetching and analyzing market data
    Integrates with various financial data APIs
    """
    
    def __init__(self):
        self.base_urls = {
            'alpha_vantage': 'https://www.alphavantage.co/query',
            'polygon': 'https://api.polygon.io/v1',
            'news_api': 'https://newsapi.org/v2'
        }
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
    
    async def get_current_market_data(self) -> Dict[str, Any]:
        """Get current market data including indices, forex, commodities"""
        cache_key = "market_data"
        
        # Check cache
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # In production, this would fetch from real APIs
            # For demo purposes, using mock data
            market_data = {
                'timestamp': datetime.now(),
                'indices': {
                    'SPY': 450.25,
                    'QQQ': 375.80,
                    'DIA': 340.15,
                    'IWM': 185.60
                },
                'forex_rates': {
                    'EUR/USD': 1.0850,
                    'GBP/USD': 1.2680,
                    'USD/JPY': 149.25,
                    'USD/CAD': 1.3550
                },
                'commodity_prices': {
                    'Gold': 2025.50,
                    'Silver': 24.80,
                    'Oil_WTI': 78.30,
                    'Oil_Brent': 82.15
                },
                'crypto_prices': {
                    'BTC': 43500.00,
                    'ETH': 2650.00,
                    'BNB': 315.20
                },
                'volatility_index': 18.5,
                'market_sentiment': 'Neutral'
            }
            
            # Cache the data
            self.cache[cache_key] = {
                'data': market_data,
                'timestamp': datetime.now()
            }
            
            return market_data
            
        except Exception as e:
            print(f"Error fetching market data: {e}")
            # Return default data
            return {
                'timestamp': datetime.now(),
                'indices': {},
                'forex_rates': {},
                'commodity_prices': {},
                'crypto_prices': {},
                'volatility_index': 20.0,
                'market_sentiment': 'Unknown'
            }
    
    async def analyze_market_news(self) -> Dict[str, Any]:
        """Analyze market news for sentiment and risk factors"""
        cache_key = "news_analysis"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # In production, this would use real news APIs and NLP
            # Mock analysis for demo
            news_analysis = {
                'overall_sentiment': 'neutral',
                'negative_sentiment': 0.3,
                'positive_sentiment': 0.4,
                'neutral_sentiment': 0.3,
                'inflation_concerns': False,
                'geopolitical_risk': False,
                'fed_policy_changes': False,
                'earnings_outlook': 'mixed',
                'key_themes': [
                    'Technology earnings',
                    'Federal Reserve policy',
                    'Economic indicators'
                ],
                'risk_factors': [
                    'Interest rate uncertainty',
                    'Geopolitical tensions'
                ]
            }
            
            # Cache the analysis
            self.cache[cache_key] = {
                'data': news_analysis,
                'timestamp': datetime.now()
            }
            
            return news_analysis
            
        except Exception as e:
            print(f"Error analyzing market news: {e}")
            return {
                'overall_sentiment': 'unknown',
                'negative_sentiment': 0.5,
                'inflation_concerns': False,
                'geopolitical_risk': False
            }
    
    async def get_stock_data(self, symbol: str, period: str = '1d') -> Dict[str, Any]:
        """Get stock data for a specific symbol"""
        cache_key = f"stock_{symbol}_{period}"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # Mock stock data
            stock_data = {
                'symbol': symbol,
                'current_price': 150.25,
                'change': 2.35,
                'change_percent': 1.59,
                'volume': 45000000,
                'market_cap': 2500000000000,
                'pe_ratio': 28.5,
                'dividend_yield': 0.52,
                'beta': 1.15,
                '52_week_high': 185.00,
                '52_week_low': 125.30
            }
            
            self.cache[cache_key] = {
                'data': stock_data,
                'timestamp': datetime.now()
            }
            
            return stock_data
            
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {e}")
            return {}
    
    async def get_economic_indicators(self) -> Dict[str, Any]:
        """Get key economic indicators"""
        cache_key = "economic_indicators"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # Mock economic data
            indicators = {
                'gdp_growth': 2.1,
                'unemployment_rate': 3.7,
                'inflation_rate': 3.2,
                'fed_funds_rate': 5.25,
                'consumer_confidence': 102.3,
                'manufacturing_pmi': 48.7,
                'services_pmi': 52.1,
                'retail_sales_growth': 0.3
            }
            
            self.cache[cache_key] = {
                'data': indicators,
                'timestamp': datetime.now()
            }
            
            return indicators
            
        except Exception as e:
            print(f"Error fetching economic indicators: {e}")
            return {}
    
    async def get_sector_performance(self) -> Dict[str, Any]:
        """Get sector performance data"""
        try:
            # Mock sector data
            sectors = {
                'Technology': {'return_1d': 1.2, 'return_1w': -2.3, 'return_1m': 5.8},
                'Healthcare': {'return_1d': 0.8, 'return_1w': 1.5, 'return_1m': 3.2},
                'Financial': {'return_1d': -0.5, 'return_1w': 2.1, 'return_1m': 4.1},
                'Energy': {'return_1d': 2.1, 'return_1w': -1.8, 'return_1m': -2.5},
                'Consumer Discretionary': {'return_1d': 0.3, 'return_1w': 0.9, 'return_1m': 2.8},
                'Consumer Staples': {'return_1d': -0.2, 'return_1w': 0.5, 'return_1m': 1.9},
                'Industrials': {'return_1d': 0.7, 'return_1w': 1.2, 'return_1m': 3.5},
                'Materials': {'return_1d': 1.1, 'return_1w': -0.8, 'return_1m': 2.1},
                'Real Estate': {'return_1d': -0.3, 'return_1w': -1.2, 'return_1m': 0.8},
                'Utilities': {'return_1d': 0.1, 'return_1w': 0.3, 'return_1m': 1.2},
                'Communication Services': {'return_1d': 0.9, 'return_1w': -1.5, 'return_1m': 4.2}
            }
            
            return sectors
            
        except Exception as e:
            print(f"Error fetching sector performance: {e}")
            return {}
    
    async def get_market_alerts(self) -> List[Dict[str, Any]]:
        """Generate market alerts based on current conditions"""
        try:
            market_data = await self.get_current_market_data()
            news_analysis = await self.analyze_market_news()
            
            alerts = []
            
            # Volatility alerts
            vix = market_data.get('volatility_index', 20)
            if vix > 30:
                alerts.append({
                    'type': 'high_volatility',
                    'severity': 'high',
                    'title': 'High Market Volatility',
                    'message': f'VIX at {vix} indicates high market stress',
                    'recommendation': 'Consider defensive positioning'
                })
            elif vix > 25:
                alerts.append({
                    'type': 'elevated_volatility',
                    'severity': 'medium',
                    'title': 'Elevated Volatility',
                    'message': f'VIX at {vix} shows increased uncertainty',
                    'recommendation': 'Monitor positions closely'
                })
            
            # News-based alerts
            if news_analysis.get('inflation_concerns', False):
                alerts.append({
                    'type': 'inflation_risk',
                    'severity': 'medium',
                    'title': 'Inflation Concerns',
                    'message': 'Market showing signs of inflation pressure',
                    'recommendation': 'Consider inflation-protected assets'
                })
            
            if news_analysis.get('geopolitical_risk', False):
                alerts.append({
                    'type': 'geopolitical_risk',
                    'severity': 'high',
                    'title': 'Geopolitical Tensions',
                    'message': 'Heightened geopolitical risks detected',
                    'recommendation': 'Consider safe-haven assets'
                })
            
            # Market sentiment alerts
            sentiment = market_data.get('market_sentiment', 'Neutral')
            if sentiment == 'Fear':
                alerts.append({
                    'type': 'market_fear',
                    'severity': 'high',
                    'title': 'Market Fear Sentiment',
                    'message': 'Market showing signs of fear and panic selling',
                    'recommendation': 'Opportunity for contrarian positioning'
                })
            
            return alerts
            
        except Exception as e:
            print(f"Error generating market alerts: {e}")
            return []
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and still valid"""
        if key not in self.cache:
            return False
        
        cache_age = (datetime.now() - self.cache[key]['timestamp']).total_seconds()
        return cache_age < self.cache_duration
    
    async def fetch_with_retry(self, url: str, params: Dict[str, Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Fetch data with retry logic"""
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    return response.json()
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to fetch data after {max_retries} attempts: {e}")
                    return None
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
        
        return None
