# Phase 2 Complete: TradingView Integration ✅

## What We Built

### Component 5: Strategy Validator with TradingView Webhooks ✅

Complete webhook receiver system that connects TradingView alerts to your automated trading system.

---

## Architecture

```
┌─────────────────┐
│  TradingView    │
│  Pine Script    │
│  Alert Fired    │
└────────┬────────┘
         │ HTTPS Webhook
         ▼
┌─────────────────────────────────────────────┐
│     YOUR WEBHOOK SERVER (localhost:5001)    │
├─────────────────────────────────────────────┤
│                                             │
│  Step 1: Webhook Handler                   │
│  • Parse JSON                               │
│  • Validate API key                         │
│  • Rate limiting (60/min)                   │
│  • Optional signature check                 │
│         ↓                                   │
│  Step 2: Strategy Validator                 │
│  • Signal completeness                      │
│         ↓                                   │
│  Step 3: Risk Calculator (Component 1)      │
│  • Position sizing (conviction-based)       │
│  • Risk:Reward validation (≥ 2.5:1)         │
│         ↓                                   │
│  Step 4: Portfolio Manager (Component 3)    │
│  • Max positions (3)                        │
│  • Daily loss limit (2%)                    │
│  • Max trades/day (3)                       │
│  • Capital availability                     │
│  • Sector exposure                          │
│         ↓                                   │
│  Decision: ✅ APPROVE or ❌ REJECT          │
│                                             │
└─────────────────────────────────────────────┘
         │
         ▼
   [Ready for Component 6: Order Executor]
         │
         ▼
   OpenAlgo → Shoonya → 🎯 Trade Executed
```

---

## Components Breakdown

### 1. Webhook Handler (`src/strategy/webhook_handler.py`)

**Purpose:** Receive and validate TradingView webhook requests

**Features:**
- ✅ JSON payload parsing
- ✅ API key authentication (HMAC-safe comparison)
- ✅ Rate limiting (60 requests/minute)
- ✅ Optional HMAC-SHA256 signature validation
- ✅ Optional IP whitelisting
- ✅ Input sanitization and validation
- ✅ Comprehensive error handling

**Security:**
```python
WebhookHandler(
    api_key="your_secure_key",
    webhook_secret="optional_secret",
    allowed_ips=["1.2.3.4"],  # Optional
    rate_limit_per_minute=60
)
```

**Classes:**
- `TradingSignal` - Data class for parsed signals
- `TradeAction` - Enum (BUY, SELL, CLOSE, CLOSE_ALL)
- `WebhookHandler` - Main handler class

---

### 2. Strategy Validator (`src/strategy/strategy_validator.py`)

**Purpose:** Multi-layer trade validation pipeline

**Validation Steps:**

#### Step 1: Signal Completeness ✅
```python
- Stop loss present (if required)
- Target present (if required)
- Stop loss < Entry (for BUY)
- Target > Entry (for BUY)
- Opposite for SELL
```

#### Step 2: Position Sizing 📐
```python
- Map conviction level to risk %
- Calculate shares/lots
- Ensure position > 0
- Log position details
```

#### Step 3: Risk:Reward Validation ✅
```python
- Calculate risk per share
- Calculate reward per share
- Validate R:R ≥ 2.5:1
- Reject if below minimum
```

#### Step 4: Portfolio Constraints 🛡️
```python
- Max 3 positions check
- Max 3 trades/day check
- 2% daily loss limit
- Capital availability
- Sector exposure limits
- Correlation check
```

**Output:** `TradeDecision` object with:
- `approved` (bool)
- `reason` (string)
- `position_size` (int)
- `investment_amount` (float)
- `risk_amount` (float)
- `risk_percent` (float)
- `risk_reward_ratio` (float)

---

### 3. Flask Webhook Server (`src/webhook_server.py`)

**Purpose:** HTTP server to receive webhooks

**Endpoints:**

#### `POST /webhook`
Receive TradingView alerts

**Request:**
```json
{
  "symbol": "TCS",
  "exchange": "NSE",
  "action": "BUY",
  "price": 3500,
  "stop_loss": 3462.5,
  "target": 3593.75,
  "conviction": "MEDIUM",
  "timeframe": "15m",
  "strategy": "BB_MTF",
  "api_key": "your_webhook_api_key"
}
```

**Response (Approved):**
```json
{
  "success": true,
  "approved": true,
  "reason": "All validations passed",
  "signal": {...},
  "trade_details": {
    "position_size": 25,
    "investment_amount": 87500.0,
    "risk_amount": 937.5,
    "risk_percent": 0.31,
    "risk_reward_ratio": 2.5
  },
  "timestamp": "2026-02-09T13:32:23.537348"
}
```

**Response (Rejected):**
```json
{
  "success": false,
  "approved": false,
  "reason": "Risk:Reward ratio 1.8:1 below minimum 2.5:1",
  "signal": {...},
  "timestamp": "..."
}
```

#### `GET /health`
Health check

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-09T13:31:49.892086",
  "service": "Trading Webhook Server"
}
```

#### `GET /status`
System status

**Response:**
```json
{
  "status": "online",
  "capital": 300000.0,
  "portfolio": {
    "active_positions": 1,
    "max_positions": 3,
    "trades_today": 2,
    "max_trades_per_day": 3,
    "daily_pnl": 1500.0,
    "daily_loss_percent": 0.5,
    "can_trade_more": true
  },
  "risk_management": {
    "max_risk_percent": 2.0,
    "min_rr_ratio": 2.5
  }
}
```

#### `GET /test`
Sample webhook payload for testing

---

## Configuration

### Environment Variables (`.env`)

```bash
# Webhook Server
WEBHOOK_API_KEY=your_secure_key_here
WEBHOOK_SECRET=optional_for_signature_validation
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=5001
FLASK_DEBUG=False

# Risk Management (from Phase 1)
INITIAL_CAPITAL=300000
MAX_DAILY_LOSS_PERCENT=0.02
MAX_POSITIONS=3
MAX_TRADES_PER_DAY=3
MIN_RISK_REWARD_RATIO=2.5
```

### Generate Secure Keys

```bash
# Webhook API key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Webhook secret (optional)
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Testing Results

### Test 1: Valid Trade (TCS) ✅

**Webhook:**
```json
{
  "symbol": "TCS",
  "price": 3500,
  "stop_loss": 3462.5,
  "target": 3593.75,
  "conviction": "MEDIUM"
}
```

**Result:**
```
✅ TRADE APPROVED
Position: 25 shares
Investment: ₹87,500
Risk: ₹937.50 (0.31%)
R:R: 1:2.50
```

### Test 2: Valid Trade (RELIANCE) ✅

**Webhook:**
```json
{
  "symbol": "RELIANCE",
  "price": 2500,
  "stop_loss": 2462.5,
  "target": 2593.75,
  "conviction": "HIGH"
}
```

**Result:**
```
✅ TRADE APPROVED
Position: 36 shares
Investment: ₹90,000
Risk: ₹1,350 (0.45%)
R:R: 1:2.50
```

### Test 3: Invalid R:R ❌

**Webhook:**
```json
{
  "symbol": "INFY",
  "price": 1600,
  "stop_loss": 1580,
  "target": 1620  // Only 1:1 R:R
}
```

**Result:**
```
❌ TRADE REJECTED
Reason: Risk:Reward ratio 1.00:1 below minimum 2.50:1
```

### Test 4: Missing Stop Loss ❌

**Result:**
```
❌ TRADE REJECTED
Reason: Stop loss is required but missing
```

### Test 5: Invalid API Key ❌

**Result:**
```
❌ REJECTED (403 Forbidden)
Reason: Invalid API key
```

---

## Real-World Usage

### Start Webhook Server

```bash
cd /Users/pshekarappa/pravn27/ASTA/stock-market-automate-trades
python3 src/webhook_server.py
```

### Expose to Internet (ngrok)

```bash
ngrok http 5001
```

Gives you: `https://abc123.ngrok.io/webhook`

### Configure TradingView Alert

**Alert Message:**
```json
{
  "symbol": "{{ticker}}",
  "exchange": "NSE",
  "action": "{{strategy.order.action}}",
  "price": {{close}},
  "stop_loss": YOUR_SL_CALCULATION,
  "target": YOUR_TARGET_CALCULATION,
  "conviction": "MEDIUM",
  "timeframe": "{{interval}}",
  "strategy": "MY_STRATEGY",
  "api_key": "your_webhook_api_key"
}
```

**Webhook URL:** `https://abc123.ngrok.io/webhook`

---

## Files Created

### Core Implementation
1. `src/strategy/__init__.py` - Module init
2. `src/strategy/webhook_handler.py` (476 lines)
3. `src/strategy/strategy_validator.py` (491 lines)
4. `src/webhook_server.py` (276 lines)

### Documentation
5. `docs/TRADINGVIEW_SETUP.md` - Complete setup guide
6. `docs/PHASE_1_COMPLETE.md` - Phase 1 summary
7. `docs/PHASE_2_TRADINGVIEW_INTEGRATION.md` - This file

**Total:** 1,243 new lines of production code

---

## Security Features

### 1. Authentication ✅
- API key required on every request
- HMAC-safe key comparison (timing attack resistant)

### 2. Rate Limiting ✅
- 60 requests per minute per IP
- Automatic cleanup of old timestamps
- Configurable limits

### 3. Input Validation ✅
- JSON schema validation
- Symbol sanitization
- Price/SL/Target validation
- Conviction level validation

### 4. Optional Features ✅
- HMAC-SHA256 signature validation
- IP whitelisting
- Webhook secret support

### 5. Logging & Audit ✅
- All webhooks logged
- All trade decisions logged
- Comprehensive error logging

---

## Integration Points

### With Component 1 (Risk Calculator)
```python
allocation = risk_calc.calculate_position_size_equity(
    entry_price=signal.price,
    stop_loss=signal.stop_loss,
    conviction=conviction_level
)
```

### With Component 3 (Portfolio Manager)
```python
can_trade, reason = portfolio.can_take_trade(
    symbol=signal.symbol,
    estimated_position_value=allocation.total_investment,
    sector=sector
)
```

### Ready for Component 6 (Order Executor)
```python
if decision.approved:
    # Execute via OpenAlgo
    order_result = openalgo_client.placeorder(
        symbol=signal.symbol,
        action=signal.action.value,
        quantity=decision.position_size,
        ...
    )
```

---

## What's Working

✅ **End-to-End Webhook Flow**
- TradingView → Your Server → Validation → Decision

✅ **Multi-Layer Protection**
- Authentication → Parsing → Position Sizing → R:R Check → Portfolio Limits

✅ **Real-Time Decisions**
- Instant approval/rejection with detailed reasons
- All based on YOUR rules (2% loss limit, 3 positions max, 3 trades/day)

✅ **Production-Ready**
- Error handling
- Logging
- Rate limiting
- Security features

---

## Next Steps

### Component 6: Order Executor (Next Up!)
Integrate with OpenAlgo to actually execute approved trades:
- Convert `TradeDecision` to OpenAlgo order
- Place order via OpenAlgo API
- Handle order status
- Error handling & retries

### Component 7: Position Monitor
Real-time position tracking:
- Monitor open positions
- Check stop loss / target hits
- Auto-close on triggers
- Update Portfolio Manager

### Component 8: Performance Tracker
Track and analyze:
- Win rate
- Average R:R achieved
- Daily/weekly/monthly P&L
- Drawdown analysis

---

## Summary

You now have:

1. ✅ **Risk Calculator** (Component 1) - Conviction-based sizing
2. ✅ **Portfolio Manager** (Component 3) - Multi-layer protection
3. ✅ **Strategy Validator** (Component 5) - TradingView webhook receiver

**Trade Flow:**
```
TradingView Alert
    → Webhook (authenticated)
    → 4-step validation
    → Instant decision (approve/reject)
    → [Ready for execution via OpenAlgo]
```

**Your Rules Enforced:**
- ✅ 2% daily loss limit
- ✅ Max 3 positions
- ✅ Max 3 trades/day
- ✅ Min 2.5:1 Risk:Reward
- ✅ Conviction-based position sizing (0.25% to 2%)

**Status:** Ready to connect to TradingView and start receiving alerts!

---

**Phase 2 Status:** ✅ **COMPLETE**

**Next:** Component 6 (Order Executor) - Execute approved trades via OpenAlgo! 🚀
