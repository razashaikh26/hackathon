# Polygon Amoy Testnet Setup Guide
cd "/Users/razashaikh/Desktop/final ro/frontend" && DANGEROUSLY_DISABLE_HOST_CHECK=true WDS_SOCKET_HOST=localhost WDS_SOCKET_PORT=3000 npm start

## Overview
FinVoice uses Polygon Amoy Testnet for blockchain audit trails and immutable financial data logging.

## Network Details
- **Network Name**: Polygon Amoy Testnet
- **RPC URL**: https://rpc-amoy.polygon.technology/
- **Chain ID**: 80002
- **Currency Symbol**: POL
- **Block Explorer**: https://amoy.polygonscan.com

## Setup Instructions

### 1. Add Network to MetaMask

1. Open MetaMask and click on the network dropdown
2. Select "Add Network" or "Custom RPC"
3. Enter the following details:
   - Network Name: `Polygon Amoy Testnet`
   - New RPC URL: `https://rpc-amoy.polygon.technology/`
   - Chain ID: `80002`
   - Currency Symbol: `POL`
   - Block Explorer URL: `https://amoy.polygonscan.com`

### 2. Get Test POL Tokens

1. Visit the [Polygon Faucet](https://faucet.polygon.technology/)
2. Select "Amoy Testnet"
3. Enter your wallet address
4. Request test POL tokens

### 3. Configure FinVoice

1. Copy your private key from MetaMask (for testnet only!)
2. Update your `.env` file:
   ```env
   POLYGON_RPC_URL=https://rpc-amoy.polygon.technology/
   POLYGON_CHAIN_ID=80002
   PRIVATE_KEY=your_private_key_here
   ```

## Features

### Audit Logging
- Financial analysis results are hashed and logged to the blockchain
- Transaction summaries are stored as immutable records
- Portfolio changes are tracked with timestamps

### Data Privacy
- Only hashed summaries are stored on-chain
- Personal financial data never leaves the application
- Blockchain provides audit trail without exposing sensitive information

### Verification
- All blockchain transactions can be verified on Amoy PolygonScan
- Data integrity can be cryptographically verified
- Audit trails are permanent and tamper-proof

## Gas Estimation

Typical gas costs on Amoy:
- Financial Analysis Log: ~100,000 gas (~0.001 POL)
- Transaction Summary: ~80,000 gas (~0.0008 POL)
- Portfolio Update: ~90,000 gas (~0.0009 POL)

## Development vs Production

### Testnet (Development)
- Use Amoy testnet for development and testing
- Free test tokens from faucet
- All transactions are public but have no real value

### Mainnet (Production)
- Switch to Polygon mainnet for production deployment
- Use real MATIC/POL tokens
- Consider gas optimization and cost management

## Security Notes

⚠️ **Important Security Guidelines:**

1. **Never use mainnet private keys in development**
2. **Use environment variables for private keys**
3. **Rotate keys regularly in production**
4. **Monitor transaction costs and set limits**
5. **Implement proper error handling for network issues**

## Troubleshooting

### Common Issues

1. **RPC Connection Failed**
   - Check network connectivity
   - Verify RPC URL is correct
   - Try alternative RPC endpoints if needed

2. **Insufficient Gas**
   - Ensure wallet has enough POL for gas fees
   - Increase gas limit if transactions fail

3. **Transaction Stuck**
   - Check transaction status on PolygonScan
   - Wait for network congestion to clear
   - Consider increasing gas price for faster confirmation

### Monitoring

- Monitor blockchain logs in application logs
- Check transaction receipts for confirmation
- Use PolygonScan to verify transaction details

## Resources

- [Polygon Documentation](https://docs.polygon.technology/)
- [Amoy Testnet Faucet](https://faucet.polygon.technology/)
- [PolygonScan Amoy](https://amoy.polygonscan.com)
- [Web3.py Documentation](https://web3py.readthedocs.io/)

## Integration Examples

### Logging a Financial Analysis
```python
# Hash sensitive data
data_hash = hashlib.sha256(analysis_data.encode()).hexdigest()

# Log to blockchain
tx_hash = await blockchain_service.log_analysis(user_id, data_hash)

# Store transaction hash for verification
await db.store_audit_record(user_id, tx_hash, data_hash)
```

### Verifying Data Integrity
```python
# Retrieve stored hash and transaction
stored_hash = await db.get_audit_hash(user_id, timestamp)
tx_hash = await db.get_transaction_hash(user_id, timestamp)

# Verify on blockchain
is_valid = await blockchain_service.verify_data_integrity(
    user_id, stored_hash, tx_hash
)
```
