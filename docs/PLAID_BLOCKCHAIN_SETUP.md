# Plaid & Blockchain Setup Guide

## 🏦 Plaid API Setup (Bank Account Integration)

### Step 1: Create Plaid Developer Account
1. Go to: https://dashboard.plaid.com/signup
2. Sign up for a free developer account
3. Complete email verification
4. Fill out the developer questionnaire

### Step 2: Get API Credentials
1. After signup, go to your Plaid Dashboard
2. Navigate to "Team Settings" → "Keys"
3. Copy your credentials:
   - **Client ID**: `your_client_id_here`
   - **Sandbox Secret**: `your_sandbox_secret_here`
   - **Development Secret**: `your_development_secret_here` (optional)

### Step 3: Configure Environment
- **Sandbox**: For testing with fake bank accounts
- **Development**: For testing with real bank accounts (limited)
- **Production**: For live bank data (requires approval)

---

## ⛓️ Blockchain Setup (Polygon Amoy Testnet)

### Step 1: Create MetaMask Wallet
1. Install MetaMask: https://metamask.io/
2. Create a new wallet or import existing
3. **Save your seed phrase securely!**

### Step 2: Add Polygon Amoy Testnet
1. Open MetaMask
2. Click network dropdown → "Add Network"
3. Add these details:
   - **Network Name**: Polygon Amoy Testnet
   - **RPC URL**: https://rpc-amoy.polygon.technology/
   - **Chain ID**: 80002
   - **Currency**: POL
   - **Explorer**: https://amoy.polygonscan.com

### Step 3: Get Test POL Tokens
1. Copy your wallet address from MetaMask
2. Go to: https://faucet.polygon.technology/
3. Select "Polygon Amoy"
4. Paste your address and request test tokens

### Step 4: Export Private Key (FOR DEVELOPMENT ONLY)
⚠️ **SECURITY WARNING**: Never share or commit private keys!

1. In MetaMask, click the 3 dots → "Account Details"
2. Click "Export Private Key"
3. Enter your password
4. Copy the private key (starts with 0x...)

---

## 🔧 Environment Configuration Commands

I'll help you update your .env file with the actual values once you get them.

### What You'll Need:
- [ ] Plaid Client ID
- [ ] Plaid Sandbox Secret  
- [ ] Your wallet address (for receiving tokens)
- [ ] Your private key (for signing transactions)

---

## 💰 Cost Breakdown:

| Service | Free Tier | Cost After |
|---------|-----------|------------|
| **Plaid Sandbox** | Unlimited testing | Free forever |
| **Plaid Development** | 100 live accounts | $0.60/account/month |
| **Polygon Amoy** | Test network | Free forever |
| **MetaMask** | Wallet software | Free forever |

---

## 🚨 Security Best Practices:

### For Plaid:
- ✅ Use Sandbox for development
- ✅ Never expose API keys in frontend
- ✅ Implement proper user consent flows

### For Blockchain:
- ⚠️ **NEVER** use real private keys in development
- ✅ Use testnet for development
- ✅ Keep private keys in environment variables only
- ✅ Use separate wallets for development vs production

---

## 📝 Next Steps:

1. **Sign up for Plaid** and get your credentials
2. **Set up MetaMask** and get testnet tokens
3. **Update your .env** with real values
4. **Test the integration**

Ready to start? Which service would you like to set up first?
