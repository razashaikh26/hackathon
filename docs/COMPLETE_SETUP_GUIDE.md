# Complete Cloud Setup Guide for FinVoice

This guide will walk you through setting up all required cloud services for FinVoice.

## 🎯 Services We'll Set Up:
1. **Neon Database** (PostgreSQL with pgvector)
2. **Upstash Redis** (Cache & Sessions)  
3. **OpenAI API** (AI/ML Features)

---

## 1. 🗄️ Neon Database Setup (PostgreSQL)

### Step 1: Create Neon Account
1. Go to: https://neon.tech
2. Click "Sign Up" (free)
3. Sign up with GitHub/Google or email
4. Verify your email if needed

### Step 2: Create Database
1. After login, click "Create Project"
2. Choose:
   - **Project Name**: `finvoice-db`
   - **Database Name**: `finvoice`
   - **Region**: Choose closest to you
   - **PostgreSQL Version**: 15 (default)
3. Click "Create Project"

### Step 3: Get Connection String
1. In your project dashboard, click "Connection Details"
2. Copy the connection string that looks like:
   ```
   postgresql://username:password@ep-xxxxx.us-east-1.aws.neon.tech/finvoice?sslmode=require
   ```
3. **Save this connection string** - you'll need it for the .env file

### Step 4: Enable pgvector Extension
1. In Neon dashboard, go to "SQL Editor"
2. Run this command:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Click "Run" - you should see "CREATE EXTENSION"

---

## 2. 🚀 Upstash Redis Setup

### Step 1: Create Upstash Account  
1. Go to: https://upstash.com
2. Click "Sign Up" (free)
3. Sign up with GitHub/Google or email
4. Complete verification

### Step 2: Create Redis Database
1. Click "Create Database" 
2. Choose:
   - **Name**: `finvoice-cache`
   - **Type**: Regional (free tier)
   - **Region**: Choose closest to you
3. Click "Create"

### Step 3: Get Redis URL
1. In your database dashboard, click "Details"
2. Copy the "UPSTASH_REDIS_REST_URL" that looks like:
   ```
   https://us1-xxxxx.upstash.io
   ```
3. Also copy the "UPSTASH_REDIS_REST_TOKEN"
4. **Save both values** - you'll need them for the .env file

---

## 3. 🤖 OpenAI API Setup

### Step 1: Create OpenAI Account
1. Go to: https://platform.openai.com
2. Click "Sign Up" or "Log In"
3. Complete account setup
4. Add a payment method (required for API access)
   - **Note**: You get $5 free credits for new accounts

### Step 2: Create API Key
1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Choose:
   - **Name**: `finvoice-api-key`
   - **Permissions**: All (default)
4. Click "Create secret key"
5. **Copy the API key** (starts with `sk-...`)
   - ⚠️ **Important**: You can only see this once!

### Step 3: Set Usage Limits (Optional but Recommended)
1. Go to: https://platform.openai.com/usage-limits
2. Set monthly usage limit: $10-20 (recommended)
3. This prevents unexpected charges

---

## 4. 🔧 Environment Configuration

After getting all the credentials above, we'll update your `.env` file with the actual values.

### Your Credentials Checklist:
- [ ] Neon PostgreSQL connection string
- [ ] Upstash Redis URL  
- [ ] Upstash Redis Token
- [ ] OpenAI API Key

---

## 5. 🧪 Testing Your Setup

Once configured, we'll test each service:

1. **Database Connection**: Test PostgreSQL connection
2. **Redis Cache**: Test cache operations
3. **OpenAI API**: Test AI model access
4. **Full Integration**: Test complete backend

---

## 💰 Cost Breakdown (All Free Tiers):

| Service | Free Tier Limits | Cost After Free Tier |
|---------|-----------------|---------------------|
| **Neon** | 10GB storage, 100 compute hours | $0.102/GB-month |
| **Upstash** | 10K commands/day | $0.2/100K commands |
| **OpenAI** | $5 credit for new users | $0.002/1K tokens (GPT-4o-mini) |

**Total Monthly Cost**: $0-5 for development usage

---

## 🚨 Security Notes:

1. **Never commit credentials** to version control
2. **Use environment variables** for all secrets
3. **Rotate API keys** regularly
4. **Set usage limits** on OpenAI to prevent unexpected charges

---

## Next Steps:

1. Complete the signups for all three services
2. Collect all the credentials
3. We'll update your `.env` file together
4. Test the complete integration

Ready to start? Let's begin with the first service!
