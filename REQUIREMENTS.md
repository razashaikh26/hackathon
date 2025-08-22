# Project Requirements and Implementation Plan

## Portfolio Accuracy
- When requested, always compute portfolio values by:
  1. Retrieving holdings from Neon
  2. Fetching latest price quotes (use configurable market price provider)
  3. Convert prices to INR (use currency conversion API or maintained INR price feed)
  4. Compute per-holding value, aggregated value, P/L, and snapshot
  5. Persist snapshot to Neon and cache short TTL in Redis
- Add endpoint: GET /api/v1/portfolio?user_id=... that returns computed portfolio and latest snapshot meta
- Add endpoint POST /api/v1/portfolio/snapshot to force snapshot + optional blockchain log (controlled by ACL)

## AI Chatbot & Voice Agent
- Use OpenRouter (or OpenAI) and Vapi as configured. But always prefix every chat and voice request by injecting the user's current financial context:
  - Current balances, holdings summary, last snapshot timestamp, active goals, and recent transactions (sanitized)
- Ensure chatbot answers can reference real stored data; do NOT use demo/random data in production mode
- Allow multi-language support for STT/TTS. Default English (en-IN) + Hindi (hi-IN) + other Indian languages. Provide mapping language codes frontend → backend
- All AI responses must include text and an audio TTS payload (or reference URL) that the frontend will fetch and play to the computer speaker

## Clean-up & Remove Demo
- Remove or gate demo/random data behind DEMO_MODE flag
- If DEMO_MODE=false, all API responses must come from Neon/Upstash/blockchain only
- Delete local temp files and directories used as caches; migrate relevant data to Neon

## Tests & Error Handling
- Add unit tests for portfolio compute logic and blockchain logging stub
- Add integration test that runs a portfolio compute end-to-end (DB → price fetch stub → compute → DB → optional blockchain log)
- Add robust error handling & logging when external AI/TTS/market/chain providers fail; always degrade gracefully with helpful error payloads

## Deliverables & Acceptance Criteria
1. **Backend**: Clean FastAPI app running on uvicorn with env-driven config. All endpoints documented in /docs. No import errors/warnings
2. **Frontend**: React app uses only cloud-backed endpoints. Portfolio page queries GET /api/v1/portfolio and shows live computed INR values. Voice assistant plays audio through browser audio element (not a chatbox sound only)
3. **Blockchain**: web3 integration signs and sends transactions correctly; tx hash persisted in Neon. Show tx status in portfolio audit
4. **Security**: Private keys and private API keys used only in backend env. Frontend gets only public key for Vapi
5. **Run steps**: Provide exact commands to start backend and frontend in two terminals
6. **Final checklist** of files changed and why

## Important Code Rules and Fix Hints
- **Web3 signing**: Check returned signed object keys; use signed.rawTransaction or signed.raw_transaction accordingly, then w3.eth.send_raw_transaction(signed_raw)
- **DB engine**: Use AsyncEngine for app operations: create_async_engine(ASYNC_DATABASE_URL, future=True)
- **For TTS endpoint**: Return StreamingResponse with correct Content-Type; frontend fetch as blob → new Audio(URL.createObjectURL(blob)) → play()
- **Prepend AI prompt**: Always include an injected JSON "user_context" block with balances, holdings summary, goals, recent txns (last 30 days) before user question
- **Provide fallback TTS**: If Vapi fails: Google TTS or pyttsx3 server-side generation and return audio

## Advanced Features

### Real-time Demo Mode (Live Ticker)
Show live portfolio P&L updates with WebSocket (FastAPI + Redis pub/sub) and optimistic UI updates in React

### On-chain Proof-of-snapshot
Hash portfolio snapshot JSON → store tx_hash in blockchain_logs table → verify later

### Voice-first Quick Actions (Vapi)
Map spoken intents to quick actions (Add expense, Snapshot portfolio, Hedge) and return TTS confirmation

### Multi-lingual Voice Tutor
Short budget tips in user language; store interactions in Neon for personalization

### Anomaly & Fraud Detector
Background job that rates transactions' anomalies; push alerts via in-app, email, or SMS

### Social/Shareable Financial Goals
Export goal progress card (image) or share read-only portfolio view link (secure token)

### Gamification & Achievements
Badges for savings streaks, SIP consistency; store achievements in Neon; animate in UI

### Aggregated Market Sentiment Feed
Light-weight news + sentiment (free RSS + simple NLP) for crisis signals injected into advisor prompts

### Mobile PWA + Offline Support
Cache last snapshot with service worker; allow offline expense capture synced when online

### Microservices Demo Split (for judges)
Show modular design: AI service, Blockchain service, Pricing service, Voice service — each deployable

## Next Steps
Now inspect entire repo, create a prioritized patch list (files and lines), implement changes, run tests, and provide a short runbook and verification checklist.
