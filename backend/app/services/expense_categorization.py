"""
Expense Categorization Engine for FinVoice
Advanced AI-powered expense categorization with Indian market context
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

import openai
from decouple import config
import redis
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class ExpenseCategory:
    id: str
    name: str
    keywords: List[str]
    parent_category: Optional[str]
    color: str
    icon: str
    budget_percentage: float

@dataclass
class CategorizedExpense:
    id: str
    description: str
    amount: float
    category: str
    subcategory: str
    date: datetime
    confidence_score: float
    auto_categorized: bool
    merchant: Optional[str]
    location: Optional[str]
    payment_method: Optional[str]

class ExpenseCategorizationEngine:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=config("OPENAI_API_KEY"))
        self.redis_client = redis.from_url(config("REDIS_URL")) if config("REDIS_URL", default=None) else None
        
        # Indian market expense categories
        self.categories = self._initialize_indian_categories()
        
        # Merchant database for Indian context
        self.indian_merchants = self._initialize_merchant_database()
        
        # Learning patterns cache
        self.user_patterns = {}
    
    def _initialize_indian_categories(self) -> Dict[str, ExpenseCategory]:
        """Initialize expense categories for Indian market"""
        categories = {
            # Food & Dining
            "food_delivery": ExpenseCategory(
                id="food_delivery",
                name="Food Delivery",
                keywords=["zomato", "swiggy", "ubereats", "foodpanda", "dominos", "pizza", "burger", "biryani"],
                parent_category="food",
                color="#FF6B6B",
                icon="🍕",
                budget_percentage=15.0
            ),
            "restaurants": ExpenseCategory(
                id="restaurants",
                name="Restaurants & Dining",
                keywords=["restaurant", "cafe", "coffee", "dinner", "lunch", "breakfast", "dine", "meal"],
                parent_category="food",
                color="#FF8E53",
                icon="🍽️",
                budget_percentage=10.0
            ),
            "groceries": ExpenseCategory(
                id="groceries",
                name="Groceries",
                keywords=["bigbasket", "grofers", "grocery", "vegetable", "fruit", "rice", "dal", "oil", "masala"],
                parent_category="food",
                color="#4ECDC4",
                icon="🛒",
                budget_percentage=20.0
            ),
            
            # Transportation
            "cab_taxi": ExpenseCategory(
                id="cab_taxi",
                name="Cab & Taxi",
                keywords=["uber", "ola", "taxi", "cab", "auto", "rickshaw"],
                parent_category="transportation",
                color="#45B7D1",
                icon="🚕",
                budget_percentage=8.0
            ),
            "public_transport": ExpenseCategory(
                id="public_transport",
                name="Public Transport",
                keywords=["metro", "bus", "train", "railway", "bmtc", "dmrc", "local"],
                parent_category="transportation",
                color="#96CEB4",
                icon="🚌",
                budget_percentage=3.0
            ),
            "fuel": ExpenseCategory(
                id="fuel",
                name="Fuel & Vehicle",
                keywords=["petrol", "diesel", "fuel", "hp", "bharat petroleum", "indian oil", "reliance"],
                parent_category="transportation",
                color="#FFEAA7",
                icon="⛽",
                budget_percentage=10.0
            ),
            
            # Shopping
            "online_shopping": ExpenseCategory(
                id="online_shopping",
                name="Online Shopping",
                keywords=["amazon", "flipkart", "myntra", "ajio", "nykaa", "shopping", "ecommerce"],
                parent_category="shopping",
                color="#DDA0DD",
                icon="🛍️",
                budget_percentage=8.0
            ),
            "clothing": ExpenseCategory(
                id="clothing",
                name="Clothing & Fashion",
                keywords=["clothes", "shirt", "jeans", "shoes", "fashion", "apparel", "dress"],
                parent_category="shopping",
                color="#FFB6C1",
                icon="👕",
                budget_percentage=5.0
            ),
            
            # Bills & Utilities
            "electricity": ExpenseCategory(
                id="electricity",
                name="Electricity",
                keywords=["electricity", "power", "bescom", "mseb", "kseb", "bill"],
                parent_category="bills",
                color="#F39C12",
                icon="💡",
                budget_percentage=3.0
            ),
            "mobile_internet": ExpenseCategory(
                id="mobile_internet",
                name="Mobile & Internet",
                keywords=["airtel", "jio", "vodafone", "bsnl", "mobile", "internet", "broadband", "wifi"],
                parent_category="bills",
                color="#9B59B6",
                icon="📱",
                budget_percentage=3.0
            ),
            "rent": ExpenseCategory(
                id="rent",
                name="Rent",
                keywords=["rent", "house rent", "flat rent", "maintenance"],
                parent_category="bills",
                color="#E74C3C",
                icon="🏠",
                budget_percentage=30.0
            ),
            
            # Healthcare
            "medical": ExpenseCategory(
                id="medical",
                name="Medical & Healthcare",
                keywords=["doctor", "hospital", "medical", "medicine", "pharmacy", "apollo", "max", "fortis"],
                parent_category="healthcare",
                color="#1ABC9C",
                icon="🏥",
                budget_percentage=5.0
            ),
            
            # Entertainment
            "entertainment": ExpenseCategory(
                id="entertainment",
                name="Entertainment",
                keywords=["movie", "cinema", "pvr", "inox", "netflix", "spotify", "prime", "hotstar"],
                parent_category="entertainment",
                color="#3498DB",
                icon="🎬",
                budget_percentage=5.0
            ),
            
            # Investment & Savings
            "mutual_funds": ExpenseCategory(
                id="mutual_funds",
                name="Mutual Funds",
                keywords=["sip", "mutual fund", "zerodha", "groww", "paytm money", "investment"],
                parent_category="investment",
                color="#27AE60",
                icon="📈",
                budget_percentage=20.0
            ),
            
            # Miscellaneous
            "personal_care": ExpenseCategory(
                id="personal_care",
                name="Personal Care",
                keywords=["salon", "spa", "cosmetics", "personal", "grooming"],
                parent_category="personal",
                color="#F1C40F",
                icon="💄",
                budget_percentage=3.0
            )
        }
        
        return categories
    
    def _initialize_merchant_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize Indian merchant/vendor database"""
        return {
            # Food Delivery
            "zomato": {"category": "food_delivery", "type": "online", "confidence": 0.95},
            "swiggy": {"category": "food_delivery", "type": "online", "confidence": 0.95},
            "dominos": {"category": "food_delivery", "type": "restaurant", "confidence": 0.90},
            
            # Groceries
            "bigbasket": {"category": "groceries", "type": "online", "confidence": 0.95},
            "grofers": {"category": "groceries", "type": "online", "confidence": 0.95},
            "reliance fresh": {"category": "groceries", "type": "retail", "confidence": 0.90},
            "dmart": {"category": "groceries", "type": "retail", "confidence": 0.90},
            
            # Transportation
            "uber": {"category": "cab_taxi", "type": "ride_sharing", "confidence": 0.95},
            "ola": {"category": "cab_taxi", "type": "ride_sharing", "confidence": 0.95},
            "uber eats": {"category": "food_delivery", "type": "delivery", "confidence": 0.95},
            
            # Shopping
            "amazon": {"category": "online_shopping", "type": "ecommerce", "confidence": 0.90},
            "flipkart": {"category": "online_shopping", "type": "ecommerce", "confidence": 0.90},
            "myntra": {"category": "clothing", "type": "ecommerce", "confidence": 0.95},
            "ajio": {"category": "clothing", "type": "ecommerce", "confidence": 0.95},
            
            # Bills & Services
            "airtel": {"category": "mobile_internet", "type": "telecom", "confidence": 0.95},
            "jio": {"category": "mobile_internet", "type": "telecom", "confidence": 0.95},
            "vodafone": {"category": "mobile_internet", "type": "telecom", "confidence": 0.95},
            
            # Healthcare
            "apollo": {"category": "medical", "type": "hospital", "confidence": 0.95},
            "max hospital": {"category": "medical", "type": "hospital", "confidence": 0.95},
            "fortis": {"category": "medical", "type": "hospital", "confidence": 0.95},
            
            # Entertainment
            "netflix": {"category": "entertainment", "type": "streaming", "confidence": 0.95},
            "spotify": {"category": "entertainment", "type": "streaming", "confidence": 0.95},
            "pvr": {"category": "entertainment", "type": "cinema", "confidence": 0.95},
            "inox": {"category": "entertainment", "type": "cinema", "confidence": 0.95},
            
            # Investment
            "zerodha": {"category": "mutual_funds", "type": "investment", "confidence": 0.95},
            "groww": {"category": "mutual_funds", "type": "investment", "confidence": 0.95},
            "paytm money": {"category": "mutual_funds", "type": "investment", "confidence": 0.95}
        }
    
    async def categorize_expense(
        self, 
        description: str, 
        amount: float, 
        user_id: str,
        date: datetime = None,
        merchant: str = None
    ) -> CategorizedExpense:
        """Categorize a single expense using multiple methods"""
        
        date = date or datetime.now()
        expense_id = f"exp_{user_id}_{int(date.timestamp())}"
        
        try:
            # Method 1: Merchant-based categorization
            merchant_category, merchant_confidence = self._categorize_by_merchant(description, merchant)
            
            # Method 2: Keyword-based categorization
            keyword_category, keyword_confidence = self._categorize_by_keywords(description)
            
            # Method 3: AI-based categorization
            ai_category, ai_confidence = await self._categorize_by_ai(description, amount)
            
            # Method 4: User pattern-based categorization
            pattern_category, pattern_confidence = await self._categorize_by_user_patterns(description, user_id)
            
            # Combine results and select best category
            final_category, final_confidence, auto_categorized = self._combine_categorization_results([
                (merchant_category, merchant_confidence, "merchant"),
                (keyword_category, keyword_confidence, "keyword"),
                (ai_category, ai_confidence, "ai"),
                (pattern_category, pattern_confidence, "pattern")
            ])
            
            # Extract additional information
            extracted_merchant = self._extract_merchant(description)
            payment_method = self._extract_payment_method(description)
            
            categorized_expense = CategorizedExpense(
                id=expense_id,
                description=description,
                amount=amount,
                category=final_category,
                subcategory=self._get_subcategory(final_category, description),
                date=date,
                confidence_score=final_confidence,
                auto_categorized=auto_categorized,
                merchant=extracted_merchant,
                location=None,  # Could be extracted from description
                payment_method=payment_method
            )
            
            # Learn from this categorization for future improvements
            await self._learn_from_categorization(user_id, categorized_expense)
            
            return categorized_expense
            
        except Exception as e:
            logger.error(f"Error categorizing expense: {e}")
            return self._default_categorized_expense(expense_id, description, amount, date)
    
    def _categorize_by_merchant(self, description: str, merchant: str = None) -> Tuple[str, float]:
        """Categorize based on known merchant database"""
        try:
            # Check direct merchant match
            if merchant and merchant.lower() in self.indian_merchants:
                merchant_info = self.indian_merchants[merchant.lower()]
                return merchant_info["category"], merchant_info["confidence"]
            
            # Check description for merchant names
            description_lower = description.lower()
            for merchant_name, merchant_info in self.indian_merchants.items():
                if merchant_name in description_lower:
                    return merchant_info["category"], merchant_info["confidence"]
            
            return "miscellaneous", 0.1
            
        except Exception as e:
            logger.error(f"Error in merchant-based categorization: {e}")
            return "miscellaneous", 0.1
    
    def _categorize_by_keywords(self, description: str) -> Tuple[str, float]:
        """Categorize based on keyword matching"""
        try:
            description_lower = description.lower()
            best_category = "miscellaneous"
            best_score = 0.0
            
            for category_id, category in self.categories.items():
                score = 0.0
                matched_keywords = 0
                
                for keyword in category.keywords:
                    if keyword in description_lower:
                        matched_keywords += 1
                        # Longer keywords get higher scores
                        score += len(keyword) / len(description_lower)
                
                # Normalize score based on number of keywords matched
                if matched_keywords > 0:
                    final_score = min(0.9, score + (matched_keywords * 0.1))
                    if final_score > best_score:
                        best_score = final_score
                        best_category = category_id
            
            return best_category, best_score
            
        except Exception as e:
            logger.error(f"Error in keyword-based categorization: {e}")
            return "miscellaneous", 0.1
    
    async def _categorize_by_ai(self, description: str, amount: float) -> Tuple[str, float]:
        """Use AI to categorize expense"""
        try:
            if not self.openai_client:
                return "miscellaneous", 0.1
            
            # Prepare category options for AI
            category_options = [cat.name for cat in self.categories.values()]
            category_descriptions = {cat.id: cat.name for cat in self.categories.values()}
            
            prompt = f"""
            Categorize this expense transaction for an Indian user:
            Description: "{description}"
            Amount: ₹{amount}
            
            Available categories:
            {json.dumps(category_descriptions, indent=2)}
            
            Consider Indian context, merchants, and spending patterns.
            
            Respond with JSON:
            {{
                "category": "category_id",
                "confidence": 0.0-1.0,
                "reasoning": "brief explanation"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at categorizing expenses for Indian users. Focus on accuracy and Indian market context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            category = result.get("category", "miscellaneous")
            confidence = float(result.get("confidence", 0.5))
            
            # Validate category exists
            if category not in self.categories:
                category = "miscellaneous"
                confidence = 0.3
            
            return category, confidence
            
        except Exception as e:
            logger.error(f"Error in AI-based categorization: {e}")
            return "miscellaneous", 0.3
    
    async def _categorize_by_user_patterns(self, description: str, user_id: str) -> Tuple[str, float]:
        """Categorize based on user's historical patterns"""
        try:
            if not self.redis_client:
                return "miscellaneous", 0.1
            
            # Get user patterns from cache
            patterns_key = f"user_patterns:{user_id}"
            patterns_data = self.redis_client.get(patterns_key)
            
            if not patterns_data:
                return "miscellaneous", 0.1
            
            patterns = json.loads(patterns_data)
            
            # Find similar descriptions in user history
            description_lower = description.lower()
            best_match_category = "miscellaneous"
            best_similarity = 0.0
            
            for historical_desc, historical_category in patterns.items():
                similarity = self._calculate_description_similarity(description_lower, historical_desc.lower())
                if similarity > best_similarity and similarity > 0.7:  # High threshold for pattern matching
                    best_similarity = similarity
                    best_match_category = historical_category
            
            confidence = min(0.8, best_similarity)  # Cap confidence for pattern matching
            return best_match_category, confidence
            
        except Exception as e:
            logger.error(f"Error in pattern-based categorization: {e}")
            return "miscellaneous", 0.1
    
    def _calculate_description_similarity(self, desc1: str, desc2: str) -> float:
        """Calculate similarity between two descriptions"""
        # Simple word overlap similarity
        words1 = set(desc1.split())
        words2 = set(desc2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _combine_categorization_results(self, results: List[Tuple[str, float, str]]) -> Tuple[str, float, bool]:
        """Combine results from different categorization methods"""
        # Weighted scoring
        weights = {
            "merchant": 0.4,
            "ai": 0.3,
            "pattern": 0.2,
            "keyword": 0.1
        }
        
        category_scores = defaultdict(float)
        
        for category, confidence, method in results:
            if category != "miscellaneous":
                weight = weights.get(method, 0.1)
                category_scores[category] += confidence * weight
        
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            best_score = category_scores[best_category]
            auto_categorized = best_score > 0.6
        else:
            best_category = "miscellaneous"
            best_score = 0.3
            auto_categorized = False
        
        return best_category, best_score, auto_categorized
    
    def _get_subcategory(self, category: str, description: str) -> str:
        """Get subcategory based on main category and description"""
        subcategory_mapping = {
            "food_delivery": ["indian", "chinese", "italian", "fast_food", "dessert"],
            "restaurants": ["fine_dining", "casual", "cafe", "street_food"],
            "groceries": ["vegetables", "fruits", "dairy", "grains", "spices"],
            "online_shopping": ["electronics", "books", "home", "personal"],
            "entertainment": ["movies", "streaming", "music", "games"]
        }
        
        if category in subcategory_mapping:
            description_lower = description.lower()
            for subcategory in subcategory_mapping[category]:
                if subcategory in description_lower:
                    return subcategory
        
        return "general"
    
    def _extract_merchant(self, description: str) -> Optional[str]:
        """Extract merchant name from description"""
        # Look for known merchants first
        description_lower = description.lower()
        for merchant_name in self.indian_merchants:
            if merchant_name in description_lower:
                return merchant_name.title()
        
        # Extract merchant patterns (e.g., "Payment to XYZ")
        patterns = [
            r"payment to (.+?)(?:\s|$)",
            r"paid (.+?)(?:\s|$)",
            r"(.+?)\s+payment",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description_lower)
            if match:
                return match.group(1).strip().title()
        
        return None
    
    def _extract_payment_method(self, description: str) -> Optional[str]:
        """Extract payment method from description"""
        payment_methods = {
            "upi": ["upi", "gpay", "phonepe", "paytm", "bhim"],
            "card": ["card", "visa", "mastercard", "debit", "credit"],
            "net_banking": ["netbanking", "net banking", "online"],
            "cash": ["cash", "atm"],
            "wallet": ["wallet", "paytm wallet", "mobikwik"]
        }
        
        description_lower = description.lower()
        for method_type, keywords in payment_methods.items():
            if any(keyword in description_lower for keyword in keywords):
                return method_type
        
        return None
    
    async def _learn_from_categorization(self, user_id: str, expense: CategorizedExpense):
        """Learn from user's categorization for future improvements"""
        try:
            if not self.redis_client:
                return
            
            patterns_key = f"user_patterns:{user_id}"
            patterns_data = self.redis_client.get(patterns_key)
            
            if patterns_data:
                patterns = json.loads(patterns_data)
            else:
                patterns = {}
            
            # Store description -> category mapping
            patterns[expense.description.lower()] = expense.category
            
            # Keep only recent patterns (limit to 1000 entries)
            if len(patterns) > 1000:
                # Remove oldest entries (simple approach)
                patterns = dict(list(patterns.items())[-1000:])
            
            # Save back to cache
            self.redis_client.setex(patterns_key, 86400 * 30, json.dumps(patterns))  # 30 days
            
        except Exception as e:
            logger.error(f"Error learning from categorization: {e}")
    
    def _default_categorized_expense(self, expense_id: str, description: str, amount: float, date: datetime) -> CategorizedExpense:
        """Return default categorized expense for error cases"""
        return CategorizedExpense(
            id=expense_id,
            description=description,
            amount=amount,
            category="miscellaneous",
            subcategory="general",
            date=date,
            confidence_score=0.1,
            auto_categorized=False,
            merchant=None,
            location=None,
            payment_method=None
        )
    
    async def batch_categorize_expenses(self, expenses: List[Dict[str, Any]], user_id: str) -> List[CategorizedExpense]:
        """Categorize multiple expenses in batch"""
        categorized_expenses = []
        
        for expense_data in expenses:
            categorized = await self.categorize_expense(
                description=expense_data["description"],
                amount=expense_data["amount"],
                user_id=user_id,
                date=expense_data.get("date"),
                merchant=expense_data.get("merchant")
            )
            categorized_expenses.append(categorized)
        
        return categorized_expenses
    
    def get_category_budget_recommendations(self, monthly_income: float) -> Dict[str, float]:
        """Get recommended budget allocation for categories"""
        recommendations = {}
        
        for category_id, category in self.categories.items():
            recommended_amount = monthly_income * (category.budget_percentage / 100)
            recommendations[category_id] = {
                "name": category.name,
                "recommended_amount": recommended_amount,
                "percentage": category.budget_percentage,
                "color": category.color,
                "icon": category.icon
            }
        
        return recommendations
    
    def get_spending_insights(self, expenses: List[CategorizedExpense], period_days: int = 30) -> Dict[str, Any]:
        """Generate spending insights from categorized expenses"""
        try:
            total_spending = sum(exp.amount for exp in expenses)
            category_spending = defaultdict(float)
            category_counts = defaultdict(int)
            
            for expense in expenses:
                category_spending[expense.category] += expense.amount
                category_counts[expense.category] += 1
            
            # Top categories by spending
            top_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Calculate averages
            avg_daily_spending = total_spending / period_days if period_days > 0 else 0
            avg_transaction_amount = total_spending / len(expenses) if expenses else 0
            
            # Most frequent categories
            frequent_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                "total_spending": total_spending,
                "avg_daily_spending": avg_daily_spending,
                "avg_transaction_amount": avg_transaction_amount,
                "top_categories": [
                    {
                        "category": cat,
                        "amount": amount,
                        "percentage": (amount / total_spending) * 100 if total_spending > 0 else 0,
                        "name": self.categories.get(cat, {}).name if cat in self.categories else cat.title()
                    }
                    for cat, amount in top_categories
                ],
                "frequent_categories": [
                    {
                        "category": cat,
                        "count": count,
                        "name": self.categories.get(cat, {}).name if cat in self.categories else cat.title()
                    }
                    for cat, count in frequent_categories
                ],
                "total_transactions": len(expenses),
                "period_days": period_days
            }
            
        except Exception as e:
            logger.error(f"Error generating spending insights: {e}")
            return {"error": str(e)}

# Helper functions
def format_category_for_display(category_id: str, categories: Dict[str, ExpenseCategory]) -> Dict[str, Any]:
    """Format category information for frontend display"""
    if category_id in categories:
        category = categories[category_id]
        return {
            "id": category.id,
            "name": category.name,
            "color": category.color,
            "icon": category.icon,
            "parent": category.parent_category
        }
    else:
        return {
            "id": category_id,
            "name": category_id.replace("_", " ").title(),
            "color": "#95A5A6",
            "icon": "💰",
            "parent": None
        }
