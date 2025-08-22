# Project Requirements and Implementation Guidelines

## Core Features to Implement

### 1. Portfolio Accuracy System
- **Real-time Portfolio Computation:**
  1. Retrieve holdings from Neon database
  2. Fetch latest price quotes (use configurable market price provider)
  3. Convert prices to INR (use currency conversion API or maintained INR price feed)
  4. Compute per-holding value, aggregated value, P/L, and snapshot
  5. Persist snapshot to Neon and cache with short TTL in Redis

- **API Endpoints:**
  - `GET /api/v1/portfolio?user_id=...` - Returns computed portfolio and latest snapshot meta
  - `POST /api/v1/portfolio/snapshot` - Force snapshot + optional blockchain log (ACL controlled)

### 2. AI Chatbot & Voice Agent Integration
- **Technology Stack:** OpenRouter (or OpenAI) + Vapi
- **Context Injection:** Always prefix chat/voice requests with user's financial context:
  - Current balances
  - Holdings summary
  - Last snapshot timestamp
  - Active goals
  - Recent transactions (sanitized, last 30 days)
- **Data Source:** Use real stored data only; NO demo/random data in production
- **Multi-language Support:**
  - Default: English (en-IN), Hindi (hi-IN)
  - Support other Indian languages
  - Provide language code mapping frontend → backend
- **Audio Output:** All AI responses must include:
  - Text response
  - Audio TTS payload or reference URL
  - Frontend fetches and plays through browser audio element

### 3. Clean-up & Production Readiness
- **Demo Data Removal:**
  - Gate demo/random data behind `DEMO_MODE` flag
  - When `DEMO_MODE=false`, use only Neon/Upstash/blockchain data
  - Delete local temp files and cache directories
  - Migrate relevant data to Neon

### 4. Testing & Error Handling
- **Unit Tests:**
  - Portfolio compute logic
  - Blockchain logging stub
- **Integration Tests:**
  - End-to-end portfolio compute: DB → price fetch → compute → DB → blockchain log
- **Error Handling:**
  - Robust handling for external provider failures (AI/TTS/market/chain)
  - Graceful degradation with helpful error payloads
  - Comprehensive logging

## Deliverables & Acceptance Criteria

1. **Backend:**
   - Clean FastAPI app on uvicorn
   - Environment-driven configuration
   - All endpoints documented in `/docs`
   - No import errors or warnings

2. **Frontend:**
   - React app using only cloud-backed endpoints
   - Portfolio page queries `GET /api/v1/portfolio`
   - Shows live computed INR values
   - Voice assistant plays audio through browser audio element

3. **Blockchain Integration:**
   - Web3 integration signs and sends transactions correctly
   - Transaction hash persisted in Neon
   - Transaction status shown in portfolio audit

4. **Security:**
   - Private keys and API keys only in backend environment
   - Frontend receives only public keys (e.g., Vapi public key)

5. **Documentation:**
   - Exact commands to start backend and frontend
   - Final checklist of changed files with explanations

## Important Implementation Rules

### Web3 Signing
- Check returned signed object keys
- Use `signed.rawTransaction` or `signed.raw_transaction` accordingly
- Execute: `w3.eth.send_raw_transaction(signed_raw)`

### Database Engine
- Use AsyncEngine for app operations:
```python
create_async_engine(ASYNC_DATABASE_URL, future=True)
```

### TTS Endpoint
- Return `StreamingResponse` with correct `Content-Type`
- Frontend implementation:
```javascript
fetch(endpoint)
  .then(res => res.blob())
  .then(blob => new Audio(URL.createObjectURL(blob)))
  .then(audio => audio.play())
```

### AI Prompt Context
- Always inject JSON `user_context` block before user question:
```json
{
  "user_context": {
    "balances": {},
    "holdings_summary": {},
    "goals": [],
    "recent_transactions": []
  }
}
```

### TTS Fallback
- Primary: Vapi
- Fallback: Google TTS or pyttsx3 server-side generation

## Advanced Features

### Real-time Features
- **Live Ticker:** WebSocket (FastAPI + Redis pub/sub) for portfolio P&L updates
- **Optimistic UI:** React updates for better UX

### Blockchain Features
- **Proof-of-Snapshot:** Hash portfolio JSON → store tx_hash → verify later
- **Audit Trail:** Complete blockchain logs table

### Voice Features
- **Quick Actions:** Map intents to actions (Add expense, Snapshot, Hedge)
- **Multi-lingual Tutor:** Budget tips in user's language
- **Personalization:** Store interactions in Neon

### Security & Monitoring
- **Anomaly Detection:** Background job for transaction rating
- **Alerts:** In-app, email, SMS notifications
- **Fraud Prevention:** Real-time monitoring

### Social & Gamification
- **Shareable Goals:** Export progress cards, read-only portfolio links
- **Achievements:** Badges for savings streaks, SIP consistency
- **Animations:** UI celebrations for milestones

### Market Intelligence
- **Sentiment Feed:** RSS + simple NLP for crisis signals
- **Advisory Context:** Inject market sentiment into AI prompts

### Mobile & Offline
- **PWA Support:** Progressive Web App capabilities
- **Offline Mode:** Service worker caching, sync when online
- **Expense Capture:** Offline expense logging

### Architecture
- **Microservices Design:**
  - AI Service
  - Blockchain Service
  - Pricing Service
  - Voice Service
  - Each independently deployable

## Implementation Priority

1. **Critical (Do First):**
   - Remove demo data
   - Fix database async engine
   - Implement real portfolio computation
   - Fix web3 signing

2. **High Priority:**
   - Add portfolio endpoints
   - Integrate AI context injection
   - Implement TTS with fallback
   - Add error handling

3. **Medium Priority:**
   - Multi-language support
   - WebSocket real-time updates
   - Blockchain logging
   - Testing suite

4. **Nice to Have:**
   - Gamification
   - Social features
   - Market sentiment
   - PWA support

## Next Steps
1. Inspect entire repository
2. Create prioritized patch list (files and lines)
3. Implement changes systematically
4. Run comprehensive tests
5. Provide runbook and verification checklist

## Notes
- Ensure all changes maintain backward compatibility
- Document any breaking changes
- Update API documentation
- Add migration scripts if needed
