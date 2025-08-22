/**
 * Configuration constants for FinVoice Frontend
 */

// Demo user ID for testing (replace with actual authentication)
// Demo User Configuration - will be set dynamically after login
export let DEMO_USER_ID = 'd4d3d413-0a8f-43a1-8ad7-687282b9b5fb';

export const setCurrentUserId = (userId: string) => {
  DEMO_USER_ID = userId;
};

// API Base URL
export const API_BASE_URL = "http://localhost:8000";

// Database API endpoints
export const DB_ENDPOINTS = {
  USERS: "/api/v1/db/users",
  ACCOUNTS: "/api/v1/db/accounts", 
  TRANSACTIONS: "/api/v1/db/transactions",
  HOLDINGS: "/api/v1/db/holdings",
  GOALS: "/api/v1/db/goals",
  OVERVIEW: "/api/v1/db/overview",
  PORTFOLIO_PERFORMANCE: "/api/v1/db/portfolio/performance"
};

// Default currency
export const DEFAULT_CURRENCY = "INR";

// Asset types
export const ASSET_TYPES = [
  "stock",
  "etf", 
  "mutual_fund",
  "bond",
  "crypto"
];

// Goal types
export const GOAL_TYPES = [
  "savings",
  "investment",
  "retirement",
  "education",
  "travel",
  "emergency_fund",
  "debt_payoff",
  "other"
];

// Priority levels
export const PRIORITY_LEVELS = [
  "low",
  "medium", 
  "high",
  "critical"
];

// Risk tolerance levels
export const RISK_TOLERANCE_LEVELS = [
  "conservative",
  "moderate",
  "aggressive"
];

// Account types
export const ACCOUNT_TYPES = [
  "checking",
  "savings", 
  "investment",
  "credit",
  "loan"
];

// Transaction categories
export const TRANSACTION_CATEGORIES = [
  "groceries",
  "dining",
  "transportation",
  "utilities",
  "entertainment",
  "healthcare",
  "shopping",
  "education",
  "travel",
  "investment",
  "salary",
  "bonus",
  "freelance",
  "rental_income",
  "dividends",
  "other"
];

export default {
  DEMO_USER_ID,
  API_BASE_URL,
  DB_ENDPOINTS,
  DEFAULT_CURRENCY,
  ASSET_TYPES,
  GOAL_TYPES,
  PRIORITY_LEVELS,
  RISK_TOLERANCE_LEVELS,
  ACCOUNT_TYPES,
  TRANSACTION_CATEGORIES
};
