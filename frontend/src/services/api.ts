/**
 * API Service for FinVoice Backend
 * Handles all API calls to the FastAPI backend with database integration
 */

// Base configuration
const API_BASE_URL = 'http://localhost:8000';
const DB_API_BASE_URL = `${API_BASE_URL}/api/v1/db`;

// Authentication interfaces
interface LoginResponse {
  user: DbUser;
  message: string;
  success: boolean;
}

interface DbUser {
  id: string;
  email: string;
  full_name: string | null;
  risk_tolerance: string | null;
  currency_preference: string;
  is_active: boolean;
  created_at: string;
}

export interface DashboardData {
  totalBalance: number;
  monthlyIncome: number;
  monthlyExpenses: number;
  savingsRate: number;
  portfolioValue: number;
  portfolioGrowth: number;
  currency: string;
  recentTransactions: Transaction[];
}

export interface Transaction {
  id: string;
  account_id: string;
  amount: number;
  description: string;
  category: string;
  transaction_type: 'debit' | 'credit';
  transaction_date: string;
  currency: string;
  created_at: string;
}

export interface Portfolio {
  totalValue: number;
  todayChange: number;
  todayChangePercent: number;
  totalGainLoss: number;
  gainLossPercentage: number;
  currency: string;
  holdings: Holding[];
}

export interface Holding {
  id: string;
  user_id: string;
  symbol: string;
  name: string;
  asset_type: string;
  quantity: number;
  average_price: number;
  current_price: number;
  market_value: number;
  total_gain_loss: number;
  total_gain_loss_percentage: number;
  purchase_date: string;
  currency: string;
  is_active: boolean;
  created_at: string;
}

export interface ExpenseData {
  totalMonthly: number;
  currency: string;
  categories: ExpenseCategory[];
}

export interface ExpenseCategory {
  name: string;
  amount: number;
  percentage: number;
  currency: string;
}

export interface Goal {
  id: string;
  user_id: string;
  goal_name: string; // For frontend compatibility 
  name: string; // Backend field
  goal_type: string;
  target_amount: number;
  current_amount: number;
  target_date: string;
  monthly_contribution: number;
  priority: string;
  is_active: boolean;
  progress_percentage: number;
  months_remaining: number;
  required_monthly_amount: number;
  currency: string;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  risk_tolerance: string;
  currency_preference: string;
  is_active: boolean;
  created_at: string;
}

export interface Account {
  id: string;
  user_id: string;
  account_type: string;
  account_name: string;
  institution_name: string;
  current_balance: number;
  currency: string;
  is_active: boolean;
  created_at: string;
}

export interface VoiceLanguage {
  [key: string]: string;
}

export interface VoiceTestRequest {
  text: string;
  language: string;
  user_id?: string;
}

export interface VoiceExpenseRequest {
  text: string;
  user_id?: string;
}

export interface FinancialOverview {
  portfolio: {
    total_value: number;
    total_gain_loss: number;
    total_gain_loss_percentage: number;
  };
  cash_balance: number;
  net_worth: number;
  recent_transactions: Transaction[];
  expense_summary: {
    total: number;
    categories: any[];
  };
  goals: Goal[];
  accounts_count: number;
  goals_count: number;
}

class ApiService {
  // =============== AUTHENTICATION METHODS ===============
  
  async loginUser(email: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${DB_API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error(`Login failed: ${response.statusText}`);
    }

    return response.json();
  }

  async createUser(userData: {
    email: string;
    password: string;
    full_name?: string;
    risk_tolerance?: string;
    currency_preference?: string;
    annual_income?: number;
  }): Promise<DbUser> {
    const response = await fetch(`${DB_API_BASE_URL}/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      throw new Error(`User creation failed: ${response.statusText}`);
    }

    return response.json();
  }

  async createDemoUsers(): Promise<any> {
    const response = await fetch(`${DB_API_BASE_URL}/demo/create-users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Demo users creation failed: ${response.statusText}`);
    }

    return response.json();
  }

  // =============== USER DATA METHODS ===============
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // =============== DATABASE API METHODS ===============

  // User Management

  async getUser(userId: string): Promise<User> {
    return this.request<User>(`/api/v1/db/users/${userId}`);
  }

  async updateUser(userId: string, userData: Partial<User>): Promise<User> {
    return this.request<User>(`/api/v1/db/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  // Account Management
  async createAccount(userId: string, accountData: { account_type: string; account_name: string; institution_name?: string; current_balance?: number; currency?: string }): Promise<Account> {
    return this.request<Account>(`/api/v1/db/accounts?user_id=${userId}`, {
      method: 'POST',
      body: JSON.stringify(accountData),
    });
  }

  async getUserAccounts(userId: string): Promise<Account[]> {
    return this.request<Account[]>(`/api/v1/db/accounts?user_id=${userId}`);
  }

  async updateAccount(accountId: string, accountData: Partial<Account>): Promise<Account> {
    return this.request<Account>(`/api/v1/db/accounts/${accountId}`, {
      method: 'PUT',
      body: JSON.stringify(accountData),
    });
  }

  async deleteAccount(accountId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/v1/db/accounts/${accountId}`, {
      method: 'DELETE',
    });
  }

  // Transaction Management
  async createTransaction(transactionData: { account_id: string; amount: number; description: string; category: string; transaction_type: string; currency?: string }): Promise<Transaction> {
    return this.request<Transaction>('/api/v1/db/transactions', {
      method: 'POST',
      body: JSON.stringify(transactionData),
    });
  }

  async getAccountTransactions(accountId: string): Promise<Transaction[]> {
    return this.request<Transaction[]>(`/api/v1/db/accounts/${accountId}/transactions`);
  }

  async getUserTransactions(userId: string): Promise<Transaction[]> {
    return this.request<Transaction[]>(`/api/v1/db/transactions?user_id=${userId}`);
  }

  async updateTransaction(transactionId: string, transactionData: Partial<Transaction>): Promise<Transaction> {
    return this.request<Transaction>(`/api/v1/db/transactions/${transactionId}`, {
      method: 'PUT',
      body: JSON.stringify(transactionData),
    });
  }

  async deleteTransaction(transactionId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/v1/db/transactions/${transactionId}`, {
      method: 'DELETE',
    });
  }

  // Holdings Management (Portfolio)
  async createHolding(userId: string, holdingData: { symbol: string; name: string; asset_type: string; quantity: number; average_price: number; currency?: string }): Promise<Holding> {
    return this.request<Holding>(`/api/v1/db/holdings?user_id=${userId}`, {
      method: 'POST',
      body: JSON.stringify(holdingData),
    });
  }

  async getUserHoldings(userId: string): Promise<Holding[]> {
    return this.request<Holding[]>(`/api/v1/db/holdings?user_id=${userId}`);
  }

  async updateHolding(holdingId: string, holdingData: Partial<Holding>): Promise<Holding> {
    return this.request<Holding>(`/api/v1/db/holdings/${holdingId}`, {
      method: 'PUT',
      body: JSON.stringify(holdingData),
    });
  }

  async deleteHolding(holdingId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/v1/db/holdings/${holdingId}`, {
      method: 'DELETE',
    });
  }

  // Goals Management
  async createGoal(userId: string, goalData: { name: string; goal_type: string; target_amount: number; target_date: string; monthly_contribution?: number; priority?: string; currency?: string }): Promise<Goal> {
    const response = await this.request<any>(`/api/v1/db/goals?user_id=${userId}`, {
      method: 'POST',
      body: JSON.stringify(goalData),
    });

    // Transform backend response to frontend format
    return {
      id: response.id,
      user_id: userId,
      goal_name: response.name, // Map backend 'name' to frontend 'goal_name'
      name: response.name,
      goal_type: response.goal_type,
      target_amount: response.target_amount,
      current_amount: response.current_amount || 0,
      target_date: response.target_date,
      monthly_contribution: response.monthly_contribution || 0,
      priority: response.priority || 'medium',
      is_active: !response.is_achieved, // Map is_achieved to is_active
      progress_percentage: response.progress_percent || 0, // Map progress_percent to progress_percentage
      months_remaining: this.calculateMonthsRemaining(response.target_date),
      required_monthly_amount: this.calculateRequiredMonthly(response.target_amount, response.current_amount || 0, response.target_date),
      currency: response.currency || 'INR',
      created_at: response.created_at || new Date().toISOString()
    };
  }

  async getUserGoals(userId: string): Promise<Goal[]> {
    const response = await this.request<any[]>(`/api/v1/db/goals?user_id=${userId}`);
    
    // Transform backend response to frontend format
    return response.map(goal => ({
      id: goal.id,
      user_id: userId,
      goal_name: goal.name, // Map backend 'name' to frontend 'goal_name'
      name: goal.name,
      goal_type: goal.goal_type,
      target_amount: goal.target_amount,
      current_amount: goal.current_amount || 0,
      target_date: goal.target_date,
      monthly_contribution: goal.monthly_contribution || 0,
      priority: goal.priority || 'medium',
      is_active: !goal.is_achieved, // Map is_achieved to is_active
      progress_percentage: goal.progress_percent || 0, // Map progress_percent to progress_percentage
      months_remaining: this.calculateMonthsRemaining(goal.target_date),
      required_monthly_amount: this.calculateRequiredMonthly(goal.target_amount, goal.current_amount || 0, goal.target_date),
      currency: goal.currency || 'INR',
      created_at: goal.created_at || new Date().toISOString()
    }));
  }

  private calculateMonthsRemaining(targetDate: string): number {
    const target = new Date(targetDate);
    const now = new Date();
    const diffTime = target.getTime() - now.getTime();
    const diffMonths = Math.ceil(diffTime / (1000 * 60 * 60 * 24 * 30));
    return Math.max(0, diffMonths);
  }

  private calculateRequiredMonthly(targetAmount: number, currentAmount: number, targetDate: string): number {
    const remaining = targetAmount - currentAmount;
    const monthsRemaining = this.calculateMonthsRemaining(targetDate);
    return monthsRemaining > 0 ? remaining / monthsRemaining : 0;
  }

  async updateGoal(goalId: string, goalData: Partial<Goal>): Promise<Goal> {
    // Transform frontend data to backend format for sending
    const backendData: any = { ...goalData };
    if (goalData.goal_name) {
      backendData.name = goalData.goal_name;
      delete backendData.goal_name;
    }
    if (goalData.progress_percentage !== undefined) {
      backendData.progress_percent = goalData.progress_percentage;
      delete backendData.progress_percentage;
    }

    const response = await this.request<any>(`/api/v1/db/goals/${goalId}`, {
      method: 'PUT',
      body: JSON.stringify(backendData),
    });

    // Transform backend response to frontend format
    return {
      id: response.id,
      user_id: response.user_id,
      goal_name: response.name, // Map backend 'name' to frontend 'goal_name'
      name: response.name,
      goal_type: response.goal_type,
      target_amount: response.target_amount,
      current_amount: response.current_amount || 0,
      target_date: response.target_date,
      monthly_contribution: response.monthly_contribution || 0,
      priority: response.priority || 'medium',
      is_active: !response.is_achieved, // Map is_achieved to is_active
      progress_percentage: response.progress_percent || 0, // Map progress_percent to progress_percentage
      months_remaining: this.calculateMonthsRemaining(response.target_date),
      required_monthly_amount: this.calculateRequiredMonthly(response.target_amount, response.current_amount || 0, response.target_date),
      currency: response.currency || 'INR',
      created_at: response.created_at || new Date().toISOString()
    };
  }

  async deleteGoal(goalId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/v1/db/goals/${goalId}`, {
      method: 'DELETE',
    });
  }

  // Financial Overview
  async getFinancialOverview(userId: string): Promise<FinancialOverview> {
    return this.request<FinancialOverview>(`/api/v1/db/overview?user_id=${userId}`);
  }

  async getPortfolioPerformance(userId: string) {
    return this.request(`/api/v1/db/portfolio/performance?user_id=${userId}`);
  }

  // =============== LEGACY API METHODS (for backwards compatibility) ===============
  
  // Dashboard API
  async getDashboard(): Promise<DashboardData> {
    return this.request<DashboardData>('/api/v1/dashboard');
  }

  // Portfolio API
  async getPortfolio(): Promise<Portfolio> {
    return this.request<Portfolio>('/api/v1/portfolio');
  }

  async addPortfolioHolding(holding: { symbol: string; shares: number; purchase_price: number }) {
    return this.request('/api/v1/portfolio/holdings', {
      method: 'POST',
      body: JSON.stringify(holding),
    });
  }

  async getBlockchainStatus() {
    return this.request('/api/v1/blockchain/status');
  }

  async getAuditTrail(userId: string) {
    return this.request(`/api/v1/blockchain/audit/${userId}`);
  }

  // Expenses API
  async getExpenses(): Promise<ExpenseData> {
    return this.request<ExpenseData>('/api/v1/expenses');
  }

  async getCategorizedExpenses() {
    return this.request('/api/v1/expenses/categorized');
  }

  // Goals API
  async getGoals() {
    return this.request('/api/v1/goals');
  }

  async analyzeGoal(goalId: string) {
    return this.request(`/api/v1/goals/analyze/${goalId}`);
  }

  // Voice API
  async getSupportedLanguages(): Promise<{ supported_languages: VoiceLanguage }> {
    return this.request<{ supported_languages: VoiceLanguage }>('/api/v1/voice/languages');
  }

  async testVoiceInput(data: VoiceTestRequest) {
    return this.request('/api/v1/voice/test', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async processVoiceExpense(data: VoiceExpenseRequest) {
    return this.request('/api/v1/voice/expense', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // SIP Recommendations
  async getSipRecommendations() {
    return this.request('/api/v1/sip/recommendations');
  }

  // AI Advisory
  async getAiAdvisory(advisoryType: string, userProfile: any, financialData?: any) {
    return this.request('/api/v1/ai/advisory', {
      method: 'POST',
      body: JSON.stringify({
        advisory_type: advisoryType,
        user_profile: userProfile,
        financial_data: financialData,
      }),
    });
  }

  async getAiChatResponse(userId: string, query: string) {
    return this.request(`/api/v1/ai/chat/${userId}?query=${encodeURIComponent(query)}`);
  }

  // Health check
  async getHealth() {
    return this.request('/health');
  }

  // AI Advisory API
  async getAIAdvice(advisoryRequest: { advisory_type: string; user_profile: any; financial_data?: any }) {
    return this.request('/api/v1/ai/advice', {
      method: 'POST',
      body: JSON.stringify(advisoryRequest),
    });
  }

  // Crisis monitoring
  async getCrisisEvents() {
    return this.request('/api/v1/crisis/monitor');
  }

  // Portfolio optimization
  async optimizePortfolio() {
    return this.request('/api/v1/portfolio/optimize');
  }

  // Risk analysis
  async analyzeRisk() {
    return this.request('/api/v1/risk/analysis');
  }

  // AI Summary
  async getAiSummary() {
    return this.request('/api/v1/ai/summary');
  }

  // Insights API
  async getUserInsights(userId: string, limit?: number) {
    const params = limit ? `?limit=${limit}` : '';
    return this.request(`/api/v1/insights/${userId}${params}`);
  }
}

export const apiService = new ApiService();
export default apiService;
