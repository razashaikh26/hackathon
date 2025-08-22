# FinVoice: Complete System Workflow

## 🎯 System Overview
FinVoice is an AI-powered financial management platform with voice input capabilities, blockchain integration, and comprehensive financial analysis. The system supports 12 Indian languages and provides real-time financial insights.

## 🏗️ Architecture Components

### 1. Backend (FastAPI - Python)
**Location**: `/backend/`
**Main Entry**: `app/simple_main.py`
**Port**: 8000

#### Core Services:
- **Voice Service** (`services/voice_service.py`)
  - Multi-engine speech recognition (Google, Wit.ai, Azure, OpenAI Whisper, Sphinx)
  - 12 Indian language support
  - Audio processing with pydub
  
- **AI Advisory** (`services/ai_advisory.py`)
  - OpenAI GPT-4 integration
  - Personal financial advisor chatbot
  - Indian market context

- **Expense Categorization** (`services/expense_categorization.py`)
  - ML-based transaction categorization
  - Indian merchant recognition
  - Anomaly detection

- **Blockchain Service** (`services/blockchain_service.py`)
  - Ethereum integration
  - Transaction recording
  - Smart contract interactions

- **Financial Engine** (`services/financial_engine.py`)
  - Portfolio optimization
  - Risk analysis
  - Goal planning with SIP recommendations

### 2. Frontend (React + TypeScript)
**Location**: `/frontend/`
**Main Entry**: `src/App.tsx`
**Port**: 3000

#### Key Components:
- **Dashboard** (`pages/Dashboard/Dashboard.tsx`)
  - Real-time financial overview
  - INR currency formatting
  - Chart.js visualizations

- **Voice Input** (`pages/VoiceInput/VoiceInput.tsx`)
  - Web Speech API integration
  - 12 Indian languages
  - Real-time voice command processing

- **Expenses** (`pages/Expenses/Expenses.tsx`)
  - Transaction management
  - Categorization and analytics
  - Budget tracking

- **Portfolio** (`pages/Portfolio/Portfolio.tsx`)
  - Indian stock market integration (NSE/BSE)
  - Investment tracking
  - Performance analysis

### 3. Database Layer
**Technology**: PostgreSQL (configurable in `core/config.py`)

#### Schema Structure:
```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    merchant VARCHAR(255),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_anomaly BOOLEAN DEFAULT FALSE
);

-- Portfolio holdings
CREATE TABLE holdings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    symbol VARCHAR(20) NOT NULL,
    shares DECIMAL(10,4) NOT NULL,
    purchase_price DECIMAL(10,2) NOT NULL,
    current_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Voice commands log
CREATE TABLE voice_commands (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    command_text TEXT NOT NULL,
    language VARCHAR(20) DEFAULT 'en-IN',
    confidence DECIMAL(3,2),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Blockchain Integration
**Technology**: Ethereum (Web3.py)
**Smart Contracts**: Deployed on testnet

#### Features:
- Transaction immutability
- Audit trail for financial records
- Smart contract for automated compliance
- Gas optimization for Indian market

## 🚀 Complete Startup Workflow

### Method 1: Docker Compose (Recommended)
```bash
# Start entire system with one command
cd /Users/razashaikh/Desktop/final\ ro
docker-compose up -d

# Services will be available at:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - PostgreSQL: localhost:5432
```

### Method 2: Manual Setup

#### Step 1: Database Setup
```bash
# Install PostgreSQL (if not installed)
brew install postgresql
brew services start postgresql

# Create database
createdb finvoice_db

# Set environment variables
export DATABASE_URL="postgresql://username:password@localhost/finvoice_db"
```

#### Step 2: Backend Setup
```bash
cd /Users/razashaikh/Desktop/final\ ro/backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
export OPENAI_API_KEY="your_openai_key"
export WIT_AI_TOKEN="your_wit_token"
export AZURE_SPEECH_KEY="your_azure_key"
export AZURE_SPEECH_REGION="your_region"

# Start backend server
uvicorn app.simple_main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 3: Frontend Setup
```bash
cd /Users/razashaikh/Desktop/final\ ro/frontend

# Install Node.js dependencies
npm install

# Start development server
npm start

# Or build for production
npm run build
npx serve -s build -l 3000
```

## 🎤 Voice Input Workflow

### 1. Voice Command Processing
```
User speaks → Web Speech API → Backend processing → Action execution → UI update
```

### 2. Supported Languages
- Hindi (hi-IN)
- Tamil (ta-IN)
- Telugu (te-IN)
- Bengali (bn-IN)
- Marathi (mr-IN)
- Gujarati (gu-IN)
- Kannada (kn-IN)
- Malayalam (ml-IN)
- Punjabi (pa-IN)
- Urdu (ur-IN)
- Odia (or-IN)
- English (en-IN)

### 3. Voice Commands Examples
```
"Add dinner 7300" → Creates expense entry
"Show portfolio" → Displays investment summary
"Budget analysis" → Shows spending breakdown
"Investment suggestions" → AI recommendations
"Risk assessment" → Portfolio risk analysis
```

## 💰 Financial Data Flow

### 1. Expense Logging
```
Voice Input → Speech Recognition → NLP Processing → Category Assignment → Database Storage → Real-time UI Update
```

### 2. AI Categorization
```python
# Example categorization logic
categories = {
    'Food': ['restaurant', 'swiggy', 'zomato', 'dinner', 'lunch'],
    'Transport': ['uber', 'ola', 'metro', 'bus', 'fuel'],
    'Shopping': ['amazon', 'flipkart', 'mall', 'clothing'],
    'Bills': ['electricity', 'water', 'internet', 'mobile'],
    'Entertainment': ['movie', 'netflix', 'games', 'concert']
}
```

### 3. Investment Tracking
```
Indian Stocks (NSE/BSE) → Real-time Price Updates → Portfolio Valuation → Performance Analytics → AI Insights
```

## 🔐 Security & Blockchain

### 1. Data Security
- JWT token authentication
- Password hashing with bcrypt
- HTTPS encryption
- Environment variable protection

### 2. Blockchain Integration
```python
# Transaction recording on blockchain
def record_transaction(amount, category, hash):
    contract.functions.recordTransaction(
        amount * 100,  # Convert to paisa
        category.encode('utf-8'),
        hash
    ).transact({'from': account})
```

## 📊 Analytics & AI Features

### 1. Spending Analysis
- Monthly trends visualization
- Category-wise breakdown
- Anomaly detection
- Budget vs actual comparison

### 2. AI Advisory
```python
# Personal finance advisor
def get_financial_advice(user_data):
    prompt = f"""
    Based on spending: ₹{user_data['monthly_spending']}
    Categories: {user_data['categories']}
    Goals: {user_data['goals']}
    
    Provide personalized financial advice for Indian context.
    """
    return openai_service.get_completion(prompt)
```

### 3. Investment Recommendations
- SIP calculations
- Risk assessment
- Indian mutual fund suggestions
- Tax optimization (80C, ELSS)

## 🔗 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

### Voice Processing
- `POST /voice/process` - Process voice command
- `GET /voice/languages` - Supported languages

### Financial Data
- `GET /dashboard` - Dashboard data
- `POST /transactions` - Add transaction
- `GET /transactions` - Get transactions
- `GET /portfolio` - Portfolio data
- `POST /portfolio/holdings` - Add holding

### AI Services
- `POST /ai/advice` - Get financial advice
- `POST /ai/categorize` - Categorize expense
- `GET /ai/insights` - Financial insights

## 📱 Mobile Integration

### Progressive Web App (PWA)
- Offline capability
- Voice input on mobile
- Native app experience
- Push notifications for budget alerts

## 🌐 Deployment Architecture

### Production Setup
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/finvoice
      - REDIS_URL=redis://redis:6379
    
  frontend:
    build: ./frontend
    environment:
      - REACT_APP_API_URL=https://api.finvoice.com
    
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=finvoice
      - POSTGRES_USER=finvoice_user
      - POSTGRES_PASSWORD=secure_password
    
  redis:
    image: redis:7-alpine
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
```

## 🔄 Real-time Features

### WebSocket Integration
- Real-time expense updates
- Live portfolio tracking
- Instant voice command feedback
- Collaborative budget planning

## 📈 Performance Monitoring

### Metrics Tracked
- Voice recognition accuracy
- API response times
- Database query performance
- User engagement analytics

## 🛠️ Development Tools

### Backend
- FastAPI with automatic OpenAPI docs
- Pytest for testing
- Black for code formatting
- SQLAlchemy ORM

### Frontend
- React with TypeScript
- Material-UI components
- Chart.js for visualizations
- Jest for testing

## 🚀 Getting Started (Quick Launch)

1. **Clone and Navigate**
```bash
cd /Users/razashaikh/Desktop/final\ ro
```

2. **Start Backend**
```bash
cd backend
uvicorn app.simple_main:app --host 0.0.0.0 --port 8000 --reload
```

3. **Start Frontend** (in new terminal)
```bash
cd frontend
npm start
```

4. **Access Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🎯 Key Features Summary

### Voice-Driven Financial Management
- "Add dinner 7300" → Instant expense logging
- Multi-language support for Indian users
- Voice-to-expense categorization

### AI-Powered Insights
- Personal financial advisor chatbot
- Expense categorization with ML
- Investment recommendations
- Risk analysis and optimization

### Indian Market Integration
- INR currency throughout
- NSE/BSE stock symbols
- Indian merchant recognition
- Tax-saving instrument suggestions

### Real-time Analytics
- Live portfolio tracking
- Spending trend analysis
- Budget vs actual monitoring
- Anomaly detection alerts

This complete workflow ensures a production-ready voice-driven financial management system with comprehensive Indian market integration.
