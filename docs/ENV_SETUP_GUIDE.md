# Environment Variables Setup Guide

## Quick Start Checklist

Complete these steps in order:

- [ ] Step 1: Get OpenAlgo API Key
- [ ] Step 2: Configure Trading Mode
- [ ] Step 3: Set Risk Parameters
- [ ] Step 4: Configure Logging
- [ ] Step 5: Test Configuration

## Step 1: Get OpenAlgo API Key (REQUIRED)

### 1.1 Start OpenAlgo
```bash
cd /Users/pshekarappa/pravn27/ASTA/openalgo
source venv/bin/activate
python3 app.py
```

### 1.2 Access Dashboard
- Open browser: `http://127.0.0.1:5000`
- Create admin account (first time)
- Login

### 1.3 Generate API Key
1. Go to **Settings** → **API Keys**
2. Click **"Generate New API Key"**
3. Copy the API key
4. Paste it in your `.env` file:
   ```
   OPENALGO_API_KEY=paste_your_key_here
   ```

## Step 2: Configure Trading Mode (CRITICAL)

### 2.1 Trading Modes Explained

**sandbox** (RECOMMENDED FOR TESTING):
```bash
TRADING_MODE=sandbox
ALLOW_LIVE_TRADING=false
```
- Simulates trades locally
- No real orders placed
- No broker connection needed
- Perfect for testing logic

**paper** (NEXT STEP):
```bash
TRADING_MODE=paper
ALLOW_LIVE_TRADING=false
```
- Simulates with real market data
- Uses OpenAlgo data feeds
- No real money
- Tests execution timing

**live** (ONLY AFTER THOROUGH TESTING):
```bash
TRADING_MODE=live
ALLOW_LIVE_TRADING=true
```
- Real orders placed
- Real money at risk
- Requires OpenAlgo + broker connection
- **DO NOT use until fully tested!**

### 2.2 Start in Sandbox Mode

Edit `.env`:
```bash
TRADING_MODE=sandbox
ALLOW_LIVE_TRADING=false
```

## Step 3: Configure Risk Parameters

These are YOUR trading rules. Review and adjust:

### 3.1 Risk Per Trade
```bash
RISK_PER_TRADE=0.01  # 1% of capital per trade
```

**Example**:
- Capital: ₹100,000
- Risk per trade: 1% = ₹1,000
- If SL is ₹10 away, quantity = 1,000/10 = 100 shares

### 3.2 Risk-Reward Ratio
```bash
MIN_RISK_REWARD_RATIO=2.5  # Minimum 2.5:1
```

**Example**:
- Risk: ₹1,000 (to stop loss)
- Minimum Reward: ₹2,500 (to target)
- If trade doesn't meet 2.5:1, it's rejected

### 3.3 Daily Limits
```bash
MAX_DAILY_LOSS_PERCENT=0.03  # 3% max daily loss
MAX_TRADES_PER_DAY=5         # Max 5 trades per day
MAX_POSITIONS=3              # Max 3 concurrent positions
```

### 3.4 Position Size Limit
```bash
MAX_POSITION_SIZE_PERCENT=0.10  # Max 10% of capital per position
```

**Example**:
- Capital: ₹100,000
- Max position: 10% = ₹10,000
- Even if risk calc says 150 shares, limit to ₹10,000 worth

## Step 4: Configure Stop Loss Method

### 4.1 ATR-Based (RECOMMENDED)
```bash
STOP_LOSS_METHOD=atr_based
ATR_MULTIPLIER=1.5
```

**How it works**:
- Stop Loss = Entry Price ± (ATR × 1.5)
- Adjusts to volatility
- Tighter for less volatile stocks
- Wider for more volatile stocks

### 4.2 Fixed Percentage
```bash
STOP_LOSS_METHOD=fixed_percent
FIXED_SL_PERCENT=2.0
```

**How it works**:
- Stop Loss = Entry Price × (1 ± 2%)
- Simple and consistent
- Doesn't adapt to market conditions

### 4.3 Support/Resistance Based
```bash
STOP_LOSS_METHOD=support_resistance
```

**How it works**:
- Places SL below support (for longs)
- Places SL above resistance (for shorts)
- Requires support/resistance detection logic

## Step 5: Configure Logging (MANDATORY)

### 5.1 Basic Logging
```bash
LOG_LEVEL=INFO
LOG_TO_FILE=True
LOG_DIR=logs
```

### 5.2 Compliance Logging (5-year retention)
```bash
LOG_RETENTION_DAYS=1825  # 5 years (SEBI requirement)
```

**What's logged**:
- All trade decisions
- Order placements
- Risk checks (passed/failed)
- System events
- Errors

## Step 6: Configure Trading Hours

### 6.1 Default Settings (Recommended)
```bash
MARKET_OPEN_TIME=09:15
MARKET_CLOSE_TIME=15:30
START_TRADING_AT=09:30      # Avoid first 15 min
STOP_NEW_TRADES_AT=15:15    # Avoid last 15 min
FORCE_EXIT_TIME=15:25        # Exit all positions
```

**Why these times?**
- First 15 minutes: High volatility, erratic moves
- Last 15 minutes: Closing volatility, squaring off

## Step 7: Configure Database

### 7.1 Database Location
```bash
DATABASE_URL=sqlite:///data/trades.db
```

This creates: `/Users/pshekarappa/pravn27/ASTA/stock-market-automate-trades/data/trades.db`

### 7.2 Backups
```bash
DATABASE_BACKUP_DIR=/Users/pshekarappa/pravn27/ASTA/backups
```

Create the directory:
```bash
mkdir -p /Users/pshekarappa/pravn27/ASTA/backups
```

## Step 8: Configure Symbols to Trade

### 8.1 Default Symbols
```bash
TRADEABLE_SYMBOLS=RELIANCE,TCS,INFY,HDFCBANK,ICICIBANK
DEFAULT_EXCHANGE=NSE
```

**Start with liquid stocks**:
- High volume
- Tight spreads
- Well-known behavior

## Step 9: Security Keys (Generate New Ones)

### 9.1 Generate Secret Key
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy output to:
```bash
SECRET_KEY=paste_generated_key_here
```

### 9.2 Generate Encryption Key
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy output to:
```bash
ENCRYPTION_KEY=paste_generated_key_here
```

## Step 10: Notifications (Optional - Configure Later)

### 10.1 Skip for Now
Leave these as default:
```bash
TELEGRAM_ENABLED=false
EMAIL_ENABLED=false
```

### 10.2 Configure Later (After System Works)

**Telegram Setup** (when ready):
1. Create bot with @BotFather on Telegram
2. Get bot token
3. Get your chat ID
4. Update `.env`:
   ```bash
   TELEGRAM_ENABLED=true
   TELEGRAM_BOT_TOKEN=your_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

## Complete Example `.env` (Minimal to Start)

```bash
# OpenAlgo Connection
OPENALGO_API_KEY=your_key_from_openalgo_dashboard
OPENALGO_HOST=http://127.0.0.1:5000

# Trading Mode
TRADING_MODE=sandbox
ALLOW_LIVE_TRADING=false

# Risk Management (Your Rules)
RISK_PER_TRADE=0.01
MIN_RISK_REWARD_RATIO=2.5
MAX_DAILY_LOSS_PERCENT=0.03
MAX_POSITIONS=3
MAX_TRADES_PER_DAY=5

# Stop Loss
STOP_LOSS_METHOD=atr_based
ATR_MULTIPLIER=1.5

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=True
LOG_RETENTION_DAYS=1825

# Database
DATABASE_URL=sqlite:///data/trades.db

# Symbols
TRADEABLE_SYMBOLS=RELIANCE,TCS,INFY

# Security (Generate new keys!)
SECRET_KEY=generate_with_command_above
ENCRYPTION_KEY=generate_with_command_above
```

## Verification Steps

### Verify Configuration
```python
# test_config.py
import os
from dotenv import load_dotenv

load_dotenv()

print("Configuration Check:")
print(f"✓ OpenAlgo API Key: {'Set' if os.getenv('OPENALGO_API_KEY') else 'MISSING'}")
print(f"✓ Trading Mode: {os.getenv('TRADING_MODE')}")
print(f"✓ Risk Per Trade: {os.getenv('RISK_PER_TRADE')}")
print(f"✓ Min RR Ratio: {os.getenv('MIN_RISK_REWARD_RATIO')}")
print(f"✓ Database: {os.getenv('DATABASE_URL')}")
```

Run:
```bash
cd /Users/pshekarappa/pravn27/ASTA/stock-market-automate-trades
python3 test_config.py
```

## Common Mistakes to Avoid

❌ **Don't commit `.env` to git** - Already in `.gitignore`
❌ **Don't use production mode without testing**
❌ **Don't skip log retention** - Required for compliance
❌ **Don't use default security keys** - Generate new ones
❌ **Don't start with live trading** - Always start sandbox

## What's Next?

Once your `.env` is configured:

1. ✅ OpenAlgo API key set
2. ✅ Risk parameters configured
3. ✅ Logging enabled
4. ✅ Security keys generated

**You're ready for Phase 1**: Building the risk management layer!

## Need Help?

- **Can't get OpenAlgo API key**: See [OPENALGO_INTEGRATION.md](OPENALGO_INTEGRATION.md)
- **Vendor code issues**: See [SHOONYA_SETUP.md](SHOONYA_SETUP.md)
- **Security questions**: See [SECURITY_BEST_PRACTICES.md](SECURITY_BEST_PRACTICES.md)
- **Compliance questions**: See [COMPLIANCE.md](COMPLIANCE.md)
