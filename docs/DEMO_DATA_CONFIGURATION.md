# Demo Data Configuration for FinVoice

## 🎯 **Demo Mode Configuration**

Your FinVoice app is now configured to use realistic demo data without any external banking APIs.

### **✅ What's Enabled:**
- **Mock Bank Accounts**: Checking, Savings, Credit, Investment
- **Demo Transactions**: 12 months of realistic transaction history
- **Portfolio Data**: Sample investment portfolio with real stock symbols
- **Expense Categories**: Realistic spending patterns
- **Income Tracking**: Monthly salary and income sources
- **Financial Goals**: Sample savings and investment goals

### **🚫 What's Disabled:**
- All external banking APIs (Plaid, Teller, Nordigen, etc.)
- CSV upload functionality
- Manual transaction entry
- Real bank connections

---

## 📊 **Demo Data Included**

### **Bank Accounts**
```json
{
  "accounts": [
    {
      "id": "acc_1",
      "name": "Primary Checking",
      "type": "checking",
      "balance": 5420.50,
      "institution": "Demo Bank",
      "account_number": "****1234"
    },
    {
      "id": "acc_2", 
      "name": "High Yield Savings",
      "type": "savings",
      "balance": 28750.00,
      "institution": "Demo Credit Union",
      "account_number": "****5678"
    },
    {
      "id": "acc_3",
      "name": "Travel Rewards Card",
      "type": "credit",
      "balance": -1250.30,
      "institution": "Demo Credit Card",
      "account_number": "****9012"
    },
    {
      "id": "acc_4",
      "name": "Investment Portfolio",
      "type": "investment", 
      "balance": 89500.00,
      "institution": "Demo Brokerage",
      "account_number": "****3456"
    }
  ]
}
```

### **Sample Transactions (Last 30 Days)**
```json
{
  "transactions": [
    {
      "id": "txn_1",
      "account_id": "acc_1",
      "amount": 3200.00,
      "description": "Salary Deposit - Tech Corp",
      "category": "Income",
      "date": "2025-08-15",
      "type": "income"
    },
    {
      "id": "txn_2",
      "account_id": "acc_1", 
      "amount": -1200.00,
      "description": "Rent Payment",
      "category": "Housing",
      "date": "2025-08-01",
      "type": "expense"
    },
    {
      "id": "txn_3",
      "account_id": "acc_1",
      "amount": -85.50,
      "description": "Grocery Store",
      "category": "Food & Dining",
      "date": "2025-08-20",
      "type": "expense"
    },
    {
      "id": "txn_4",
      "account_id": "acc_2",
      "amount": 500.00,
      "description": "Monthly Savings Transfer",
      "category": "Transfer",
      "date": "2025-08-15",
      "type": "transfer"
    }
  ]
}
```

### **Investment Portfolio**
```json
{
  "holdings": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "shares": 50,
      "avg_price": 185.00,
      "current_price": 192.50,
      "value": 9625.00,
      "gain_loss": 375.00,
      "gain_loss_percent": 4.05
    },
    {
      "symbol": "MSFT", 
      "name": "Microsoft Corporation",
      "shares": 25,
      "avg_price": 380.00,
      "current_price": 395.20,
      "value": 9880.00,
      "gain_loss": 380.00,
      "gain_loss_percent": 4.00
    },
    {
      "symbol": "GOOGL",
      "name": "Alphabet Inc.",
      "shares": 15,
      "avg_price": 145.00,
      "current_price": 142.80,
      "value": 2142.00,
      "gain_loss": -33.00,
      "gain_loss_percent": -1.52
    }
  ]
}
```

### **Monthly Expenses by Category**
```json
{
  "expenses": [
    {"category": "Housing", "amount": 1200.00, "percentage": 40.0},
    {"category": "Food & Dining", "amount": 450.00, "percentage": 15.0},
    {"category": "Transportation", "amount": 350.00, "percentage": 11.7},
    {"category": "Utilities", "amount": 180.00, "percentage": 6.0},
    {"category": "Entertainment", "amount": 200.00, "percentage": 6.7},
    {"category": "Healthcare", "amount": 150.00, "percentage": 5.0},
    {"category": "Shopping", "amount": 300.00, "percentage": 10.0},
    {"category": "Other", "amount": 170.00, "percentage": 5.6}
  ]
}
```

---

## 🎯 **Benefits of Demo Mode**

### **✅ Advantages:**
- **Instant Setup**: No API keys or external accounts needed
- **Consistent Data**: Same data every time for testing
- **Full Features**: All app features work immediately  
- **No Rate Limits**: Unlimited testing and development
- **Offline Capable**: Works without internet connection
- **Privacy Friendly**: No real financial data involved

### **🔧 Perfect For:**
- **Development**: Building and testing features
- **Demos**: Showing the app to investors/clients
- **UI/UX Testing**: Consistent data for design testing
- **Performance Testing**: Predictable data for optimization
- **Education**: Learning financial management concepts

---

## 🚀 **Your App Features (Demo Mode)**

### **Dashboard**
- ✅ Account balances and overview
- ✅ Monthly income vs expenses  
- ✅ Savings rate calculation
- ✅ Recent transactions feed

### **Portfolio**
- ✅ Investment holdings with real stock symbols
- ✅ Portfolio performance charts
- ✅ Asset allocation breakdown
- ✅ Gain/loss tracking

### **Expenses**
- ✅ Spending by category
- ✅ Monthly trends and patterns
- ✅ Budget vs actual comparisons
- ✅ Expense analytics

### **Goals**
- ✅ Savings goal tracking
- ✅ Investment milestones
- ✅ Progress visualization
- ✅ Goal recommendations

### **Voice Features**
- ✅ Voice-activated balance queries
- ✅ Expense logging by voice
- ✅ Financial advice through AI

---

## 🧪 **Test Your Demo Setup**

Your backend is now optimized for demo data. Test these endpoints:

1. **Dashboard**: `GET /api/v1/dashboard` 
2. **Portfolio**: `GET /api/v1/portfolio`
3. **Expenses**: `GET /api/v1/expenses`
4. **Transactions**: `GET /api/v1/transactions`

All endpoints will return realistic, consistent demo data perfect for development and demonstrations!

**Result**: A fully functional financial management app with zero external dependencies! 🎉
