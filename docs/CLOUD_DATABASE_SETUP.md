# Free Cloud Database Setup Guide

## 🐘 Neon Database (PostgreSQL + pgvector)

### Step 1: Create Neon Account
1. Go to https://neon.tech/
2. Sign up with GitHub/Google (free tier: 10GB storage, 100 hours compute)
3. Create a new project named "finvoice"
4. Select region closest to you

### Step 2: Enable pgvector Extension
1. In Neon console, go to "SQL Editor"
2. Run this command:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Step 3: Get Connection String
1. In Neon dashboard, click "Connection Details"
2. Copy the connection string (looks like):
```
postgresql://username:password@ep-xyz.region.neon.tech/neondb?sslmode=require
```

### Your Database URL will be:
```
DATABASE_URL=postgresql://username:password@ep-xyz.region.neon.tech/neondb?sslmode=require
ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@ep-xyz.region.neon.tech/neondb?sslmode=require
```

## ⚡ Upstash Redis (Free Redis Cloud)

### Step 1: Create Upstash Account
1. Go to https://upstash.com/
2. Sign up (free tier: 10K commands/day)
3. Create new Redis database
4. Select region closest to you

### Step 2: Get Redis URL
1. Copy the Redis URL from dashboard:
```
REDIS_URL=rediss://default:password@region.upstash.io:6379
```

## 🔐 Other Free Services

### Railway (Alternative to local services)
- Free tier: 500 execution hours/month
- Can host PostgreSQL + Redis together

### PlanetScale (MySQL alternative)
- Free tier: 1 database, 1GB storage, 1 billion reads/month

### Aiven (Multiple database options)
- Free tier: 1 month trial for PostgreSQL, Redis, etc.

## 🌟 Recommended: Neon + Upstash Combo
- ✅ Both have generous free tiers
- ✅ No credit card required for sign-up
- ✅ Easy to scale later
- ✅ Built-in SSL/security
- ✅ Global CDN for better performance

## Quick Setup Commands

1. Sign up for both services
2. Get your connection strings
3. Update your .env file
4. Start backend - no local installations needed!

```bash
# No PostgreSQL installation needed
# No Redis installation needed
# Just update .env and run:
pip install -r requirements.txt
uvicorn app.main:app --reload
```
