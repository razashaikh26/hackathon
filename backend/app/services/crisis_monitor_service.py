"""
Crisis Monitor Service - Wrapper for the Crisis Monitor
"""

from .crisis_monitor import CrisisMonitor

class CrisisMonitorService:
    def __init__(self):
        self.monitor = CrisisMonitor()
    
    async def get_current_events(self):
        return await self.monitor.get_current_crisis_events()
    
    async def analyze_market_impact(self):
        return await self.monitor.analyze_market_impact()
    
    async def get_crisis_summary(self):
        return await self.monitor.get_crisis_summary()
