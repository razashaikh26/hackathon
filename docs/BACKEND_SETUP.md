# FinVoice Backend Setup Guide

## 🗄️ Database Setup

### PostgreSQL with pgvector

1. **Install PostgreSQL** (if not already installed):
   ```bash
   # macOS
   brew install postgresql@15
   brew services start postgresql@15
   
   # Or use Docker
   docker run --name finvoice-postgres -e POSTGRES_PASSWORD=your_password -p 5432:5432 -d postgres:15
   ```

2. **Install pgvector extension**:
   ```bash
   # macOS
   brew install pgvector
   
   # Or if using Docker:
   docker run --name finvoice-postgres -e POSTGRES_PASSWORD=your_password -p 5432:5432 -d pgvector/pgvector:pg15
   ```

3. **Create database and user**:
   ```sql
   -- Connect to PostgreSQL
   psql postgres
   
   -- Create user
   CREATE USER finvoice_user WITH PASSWORD 'secure_password_123';
   
   -- Create database
   CREATE DATABASE finvoice OWNER finvoice_user;
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE finvoice TO finvoice_user;
   
   -- Connect to finvoice database
   \c finvoice
   
   -- Enable pgvector extension
   CREATE EXTENSION IF NOT EXISTS vector;
   
   -- Grant usage on schema
   GRANT USAGE ON SCHEMA public TO finvoice_user;
   GRANT CREATE ON SCHEMA public TO finvoice_user;
   ```

## 🔧 Environment Configuration

Create `.env` file in the backend directory:

```bash
# Copy the example file
cp .env.example .env
```

### Essential Database Variables:
```bash
# Database URLs
DATABASE_URL=postgresql://finvoice_user:secure_password_123@localhost:5432/finvoice
ASYNC_DATABASE_URL=postgresql+asyncpg://finvoice_user:secure_password_123@localhost:5432/finvoice

# Redis (for caching and background tasks)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-make-it-at-least-32-characters-long
DEBUG=True
```

### API Keys (Optional for testing):
```bash
# OpenAI (for AI insights)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Plaid (for bank connections)
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox

# Google Cloud (for speech-to-text)
GOOGLE_CLOUD_CREDENTIALS=/path/to/credentials.json
```

### Blockchain Configuration:
```bash
# Polygon Amoy Testnet
POLYGON_RPC_URL=https://rpc-amoy.polygon.technology/
POLYGON_CHAIN_ID=80002
PRIVATE_KEY=your_metamask_private_key_for_testnet
```

## 🚀 Backend Startup Commands

### 1. Install Dependencies:
```bash
cd "backend"
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Migration:
```bash
# Initialize Alembic (if not done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 3. Start the Backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🐳 Docker Alternative

If you prefer Docker:

```bash
# Start all services
docker-compose up -d

# Or just database
docker-compose up -d postgres redis
```

## 🧪 Test Database Connection

Create a test script to verify database connectivity:

```python
# test_db.py
import asyncpg
import asyncio

async def test_connection():
    try:
        conn = await asyncpg.connect(
            "postgresql://finvoice_user:secure_password_123@localhost:5432/finvoice"
        )
        result = await conn.fetchval("SELECT version()")
        print(f"✅ Database connected: {result}")
        await conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
```

## 📊 Redis Setup

### Install Redis:
```bash
# macOS
brew install redis
brew services start redis

# Or Docker
docker run --name finvoice-redis -p 6379:6379 -d redis:7-alpine
```

### Test Redis:
```bash
redis-cli ping
# Should return: PONG
```

## 🔐 Security Setup

### Generate Secret Key:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Create JWT tokens for authentication:
The backend will handle user authentication automatically.

## 🌐 External Services (Optional)

### OpenAI API:
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

### Plaid API (for bank connections):
1. Sign up at https://plaid.com/
2. Get sandbox credentials
3. Add to `.env`

### Google Cloud Speech (for voice input):
1. Create Google Cloud project
2. Enable Speech-to-Text API
3. Create service account key
4. Download JSON credentials

## 🚦 Ready-to-Use .env Template

```bash
# ===== ESSENTIAL CONFIGURATION =====
DEBUG=True
SECRET_KEY=your-32-character-secret-key-here-make-it-random-and-secure

# Database
DATABASE_URL=postgresql://finvoice_user:secure_password_123@localhost:5432/finvoice
ASYNC_DATABASE_URL=postgresql+asyncpg://finvoice_user:secure_password_123@localhost:5432/finvoice

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
ALLOWED_HOSTS=["http://localhost:3000", "http://127.0.0.1:3000"]

# ===== OPTIONAL API KEYS =====
# Uncomment and configure as needed

# OPENAI_API_KEY=sk-your-key-here
# PLAID_CLIENT_ID=your-client-id
# PLAID_SECRET=your-secret
# PLAID_ENV=sandbox
# GOOGLE_CLOUD_CREDENTIALS=/path/to/credentials.json

# ===== BLOCKCHAIN (TESTNET) =====
POLYGON_RPC_URL=https://rpc-amoy.polygon.technology/
POLYGON_CHAIN_ID=80002
# PRIVATE_KEY=your-metamask-private-key-for-testnet-only

# ===== SYSTEM CONFIGURATION =====
LOG_LEVEL=INFO
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
MODEL_PATH=./ml_models
```

## ✅ Verification Steps

1. **Database**: `psql -h localhost -U finvoice_user -d finvoice -c "SELECT version()"`
2. **Redis**: `redis-cli ping`
3. **Backend**: Visit http://localhost:8000/docs
4. **Health Check**: http://localhost:8000/health

Your backend will be ready to serve your frontend! 🚀
