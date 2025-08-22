"""
FinVoice AI Services Package
"""

__version__ = "1.0.0"
__author__ = "FinVoice Team"

# Import all services for easy access
try:
    from .voice_service import VoiceService
except ImportError:
    VoiceService = None

try:
    from .expense_categorization import ExpenseCategorizationEngine
except ImportError:
    ExpenseCategorizationEngine = None

try:
    from .ai_advisory import AIAdvisoryService
except ImportError:
    AIAdvisoryService = None

try:
    from .goal_planner import GoalPlannerService, FinancialGoal, GoalType
except ImportError:
    GoalPlannerService = None
    FinancialGoal = None
    GoalType = None

__all__ = [
    "VoiceService",
    "ExpenseCategorizationEngine", 
    "AIAdvisoryService",
    "GoalPlannerService",
    "FinancialGoal",
    "GoalType"
]
