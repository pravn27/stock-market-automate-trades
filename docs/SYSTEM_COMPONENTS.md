# System Components Overview

## Complete Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   AUTOMATED TRADING SYSTEM                       │
└─────────────────────────────────────────────────────────────────┘

Layer 1: SIGNAL SOURCES
├── TradingView Webhooks (external)
├── Your Custom Strategies (internal)
└── Manual Signals (optional)
        ↓
Layer 2: YOUR CUSTOM RISK MANAGEMENT (CORE VALUE)
├── 1. Strategy Validator
├── 2. Risk Calculator
├── 3. Position Sizer
├── 4. Portfolio Risk Manager
└── 5. Pre-Trade Validator
        ↓
Layer 3: EXECUTION (OpenAlgo handles this)
├── OpenAlgo API Client
├── Order Placement
├── Order Modification
└── Order Cancellation
        ↓
Layer 4: MONITORING & MANAGEMENT
├── 6. Position Monitor
├── 7. Stop Loss/Target Tracker
├── 8. Auto-Exit Engine
└── 9. Performance Tracker
        ↓
Layer 5: DATA & LOGGING
├── 10. Database Manager
├── 11. Trade Logger
├── 12. Audit Logger
└── 13. Backup Manager
        ↓
Layer 6: USER INTERFACE (Optional)
├── 14. Terminal Dashboard
├── 15. Notification System
└── 16. Web Dashboard (future)
```

---

## Major Components Breakdown

### 🎯 **YOU BUILD (11 Core Components)**

#### **Phase 1: Risk Management (Week 1)** ⭐ HIGHEST PRIORITY

**1. Risk Calculator**
- **Purpose**: Calculate stop loss and targets
- **Input**: Entry price, ATR, market data
- **Output**: Stop loss price, target price
- **Key Features**:
  - ATR-based stop loss
  - Fixed percentage stop loss
  - Support/resistance based stop loss
  - Target calculation (minimum 2.5:1 RR)
  - Risk-reward validation

**Example**:
```python
risk_calc = RiskCalculator()
entry = 2500
atr = 20

sl = risk_calc.calculate_stop_loss(entry, atr, action='BUY')
# Output: 2470 (2500 - 20*1.5)

target = risk_calc.calculate_target(entry, sl, min_rr=2.5)
# Output: 2575 (entry + risk*2.5)
```

---

**2. Position Sizer**
- **Purpose**: Calculate how many shares to buy (1% risk rule)
- **Input**: Account balance, risk %, entry, stop loss
- **Output**: Quantity of shares
- **Key Features**:
  - 1% risk per trade enforcement
  - Maximum position size limit (10%)
  - Minimum position size validation
  - Integer quantity (round down)

**Example**:
```python
sizer = PositionSizer()
balance = 100000
risk_percent = 0.01  # 1%
entry = 2500
stop_loss = 2470

quantity = sizer.calculate_position_size(balance, risk_percent, entry, stop_loss)
# Output: 33 shares
# Calculation: (100000 * 0.01) / (2500 - 2470) = 1000 / 30 = 33
```

---

**3. Portfolio Risk Manager**
- **Purpose**: Enforce portfolio-level risk limits
- **Input**: Current positions, new signal, daily P&L
- **Output**: Approved/Rejected with reason
- **Key Features**:
  - Max 3 concurrent positions
  - 3% daily loss limit
  - Max 5 trades per day
  - Sector exposure limits
  - Correlation checking
  - Daily counter reset

**Example**:
```python
portfolio_mgr = PortfolioRiskManager()

can_trade, reason = portfolio_mgr.can_take_trade(
    current_positions=2,
    daily_loss=0.015,  # 1.5%
    trades_today=3
)
# Output: (True, "Trade allowed")

# If daily loss = 3.5%
# Output: (False, "Daily loss limit exceeded")
```

---

**4. Pre-Trade Validator**
- **Purpose**: Final validation before sending order to OpenAlgo
- **Input**: Fully prepared order with all risk checks
- **Output**: Final approval or rejection
- **Key Features**:
  - Verify all risk checks passed
  - Confirm sufficient balance
  - Check market hours
  - Validate order parameters
  - Log validation decision

**Example**:
```python
validator = PreTradeValidator()

result = validator.validate_trade({
    'symbol': 'RELIANCE',
    'quantity': 50,
    'entry': 2500,
    'sl': 2470,
    'target': 2575,
    'rr_ratio': 2.5
})
# Output: {'approved': True, 'reason': 'All checks passed'}
```

---

#### **Phase 2: Strategy Engine (Week 2)**

**5. Strategy Validator**
- **Purpose**: Validate TradingView signals or generate custom signals
- **Input**: Webhook from TradingView or market data
- **Output**: Validated signal with entry, SL, target
- **Key Features**:
  - Parse TradingView webhooks
  - Validate signal format
  - Check if symbol is tradeable
  - Extract entry, SL, target from signal
  - Add confidence score

**Example**:
```python
validator = StrategyValidator()

# From TradingView webhook
signal = validator.parse_webhook({
    'symbol': 'RELIANCE',
    'action': 'BUY',
    'price': 2500
})
# Output: Signal(symbol='RELIANCE', action='BUY', entry=2500, ...)
```

---

**6. Rules Engine** (Optional - if building custom strategies)
- **Purpose**: Evaluate custom trading rules
- **Input**: Market data, indicators
- **Output**: Trading signals
- **Key Features**:
  - Load rules from YAML
  - Evaluate conditions (AND/OR logic)
  - Support multiple indicators
  - Generate signals based on rules

---

#### **Phase 3: Position Monitoring (Week 2)**

**7. Position Monitor**
- **Purpose**: Track active positions and check for SL/Target hits
- **Input**: Positions from OpenAlgo, current prices
- **Output**: Exit orders when conditions met
- **Key Features**:
  - Fetch positions every 5 seconds
  - Check stop loss hit
  - Check target hit
  - Auto-exit via OpenAlgo
  - Update database

**Example**:
```python
monitor = PositionMonitor(openalgo_client, db)

# Runs continuously
while trading_hours:
    monitor.check_positions()
    # If SL hit: Places exit order
    # If Target hit: Places exit order
    time.sleep(5)
```

---

**8. Stop Loss/Target Tracker**
- **Purpose**: Track and manage stop loss/target orders
- **Input**: Active positions with SL/Target levels
- **Output**: Modified SL orders (trailing stop)
- **Key Features**:
  - Store SL/Target in database
  - Track order IDs
  - Modify SL for trailing stop (optional)
  - Handle partial exits

---

#### **Phase 4: Data & Logging (Week 3)**

**9. Database Manager**
- **Purpose**: Store all trading data
- **Tables**:
  - `trades` - All trade history
  - `positions` - Active positions
  - `orders` - Order book
  - `system_metrics` - Performance data
- **Key Features**:
  - Trade history (5 years)
  - Position tracking
  - Performance metrics
  - Query helpers

**Example Schema**:
```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    action TEXT,
    entry_price REAL,
    exit_price REAL,
    quantity INTEGER,
    stop_loss REAL,
    target REAL,
    pnl REAL,
    entry_time DATETIME,
    exit_time DATETIME,
    exit_reason TEXT
);
```

---

**10. Trade Logger**
- **Purpose**: Log every trading action
- **Output**: Structured logs in files
- **Key Features**:
  - Trade execution logs
  - Risk check logs
  - System event logs
  - Error logs
  - 5-year retention

**Example Log**:
```
2026-02-09 10:15:30 | TRADE | BUY | RELIANCE | Entry: 2500 | SL: 2470 | Target: 2575 | Qty: 50
2026-02-09 10:15:31 | RISK | APPROVED | RR: 2.5:1 | Risk: 1.0% | All checks passed
2026-02-09 10:15:32 | ORDER | PLACED | OrderID: ORD123456 | Status: COMPLETE
```

---

**11. Audit Logger**
- **Purpose**: Comprehensive audit trail (SEBI compliance)
- **Key Features**:
  - All API calls logged
  - User actions logged
  - Configuration changes logged
  - Security events logged
  - Immutable logs

---

#### **Phase 5: User Interface (Week 3-4) - Optional**

**12. Terminal Dashboard**
- **Purpose**: Real-time monitoring in terminal
- **Key Features**:
  - Live position display
  - Today's P&L
  - Risk metrics
  - System status
  - Recent trades

**Example Display**:
```
╔══════════════════════════════════════════════════╗
║  Trading Dashboard - 2026-02-09 10:15:30        ║
╠══════════════════════════════════════════════════╣
║  Balance: ₹100,000 | Today's P&L: +₹1,200      ║
║  Trades: 2/5 | Positions: 2/3 | Risk: 1.5%     ║
╠══════════════════════════════════════════════════╣
║  Active Positions:                              ║
║  RELIANCE | BUY | 50 @ 2500 | SL: 2470         ║
║  Current: 2510 | P&L: +₹500 | Status: 🟢       ║
╚══════════════════════════════════════════════════╝
```

---

**13. Notification System**
- **Purpose**: Send alerts for important events
- **Channels**:
  - Telegram (via OpenAlgo)
  - Email (optional)
  - SMS (optional)
- **Alerts**:
  - Trade executed
  - Stop loss hit
  - Target achieved
  - Daily loss limit approaching
  - System errors

---

**14. Performance Tracker**
- **Purpose**: Track and analyze trading performance
- **Metrics**:
  - Daily/Weekly/Monthly P&L
  - Win rate
  - Average R:R ratio
  - Maximum drawdown
  - Sharpe ratio
  - Best/worst trades
- **Reports**:
  - Daily summary
  - Weekly analysis
  - Monthly report

---

### 🏗️ **OpenAlgo Handles (You DON'T Build)**

**15. OpenAlgo API Client** ✅
- Order placement
- Order modification
- Order cancellation
- Position fetching
- Balance checking
- Market data access

**16. Broker Communication** ✅
- Shoonya API integration
- Authentication & session management
- WebSocket connections
- Rate limiting
- Error handling

**17. TradingView Webhook Receiver** ✅
- Webhook endpoint
- Signal parsing
- Alert management

---

## Component Priority Matrix

### 🔴 Critical (Must Build First)
**Phase 1 - Risk Management**:
1. Risk Calculator ⭐
2. Position Sizer ⭐
3. Portfolio Risk Manager ⭐
4. Pre-Trade Validator ⭐

**Without these, you can't trade safely!**

---

### 🟡 Important (Build Second)
**Phase 2 - Strategy**:
5. Strategy Validator
6. OpenAlgo Client Wrapper

**Phase 3 - Monitoring**:
7. Position Monitor
8. Stop Loss Tracker

**Without these, you can't automate!**

---

### 🟢 Nice to Have (Build Later)
**Phase 4 - Data**:
9. Database Manager
10. Trade Logger
11. Audit Logger

**Phase 5 - UI**:
12. Terminal Dashboard
13. Notification System
14. Performance Tracker

**These improve experience but not critical for trading.**

---

## Component Dependencies

```
Risk Calculator (no dependencies)
    ↓
Position Sizer (needs Risk Calculator)
    ↓
Portfolio Risk Manager (needs Position Sizer)
    ↓
Pre-Trade Validator (needs all above)
    ↓
OpenAlgo Client (needs validation)
    ↓
Position Monitor (needs OpenAlgo Client)
    ↓
Database Manager (needs all trading data)
    ↓
Dashboard (needs Database + Monitor)
```

---

## Estimated Development Time

| Component | Time | Difficulty |
|-----------|------|------------|
| Risk Calculator | 1 day | Easy |
| Position Sizer | 1 day | Easy |
| Portfolio Risk Manager | 2 days | Medium |
| Pre-Trade Validator | 1 day | Easy |
| Strategy Validator | 1 day | Easy |
| OpenAlgo Client Wrapper | 1 day | Easy |
| Position Monitor | 2 days | Medium |
| Database Manager | 1 day | Easy |
| Trade Logger | 1 day | Easy |
| Terminal Dashboard | 2 days | Medium |
| **Total** | **13 days** | **~3 weeks** |

---

## Component Files Structure

```
src/
├── risk_management/
│   ├── __init__.py
│   ├── risk_calculator.py      # Component 1
│   ├── position_sizer.py       # Component 2
│   ├── portfolio_manager.py    # Component 3
│   └── stop_loss_manager.py    # Component 8
├── validation/
│   ├── __init__.py
│   ├── strategy_validator.py   # Component 5
│   └── pre_trade_validator.py  # Component 4
├── openalgo/
│   ├── __init__.py
│   └── client.py               # Component 6 (wrapper)
├── monitoring/
│   ├── __init__.py
│   ├── position_monitor.py     # Component 7
│   ├── performance_tracker.py  # Component 14
│   └── logger.py               # Component 10, 11
├── database/
│   ├── __init__.py
│   ├── models.py               # Component 9
│   └── repository.py           # Component 9
└── ui/
    ├── __init__.py
    ├── dashboard.py            # Component 12
    └── notifier.py             # Component 13
```

---

## What Makes This System Valuable?

### 🎯 Your Competitive Advantage (Components 1-4)
**Risk Management Layer**:
- Enforces discipline (removes emotion)
- Prevents over-risking
- Ensures proper position sizing
- Maintains portfolio limits

**This is 80% of your value!**

### 🔧 Automation Layer (Components 5-8)
**Strategy & Monitoring**:
- Executes trades automatically
- Monitors positions 24/7
- Never misses stop loss
- Consistent execution

**This saves time and reduces errors.**

### 📊 Analytics Layer (Components 9-14)
**Data & Insights**:
- Tracks performance
- Provides insights
- Helps improve strategy
- Compliance (SEBI)

**This helps you improve over time.**

---

## Testing Strategy

Each component needs:
1. **Unit Tests** - Test individual functions
2. **Integration Tests** - Test with other components
3. **Sandbox Tests** - Test with fake data
4. **Paper Trading Tests** - Test with real market data (no money)
5. **Live Tests** - Start small, scale up

---

## Success Criteria

### Phase 1 Complete:
- ✅ Can calculate stop loss and targets
- ✅ Can calculate position size (1% rule)
- ✅ Can enforce portfolio limits
- ✅ Can validate trades before execution
- ✅ All unit tests pass

### Phase 2 Complete:
- ✅ Can receive TradingView signals
- ✅ Can place orders via OpenAlgo
- ✅ Can monitor positions
- ✅ Can exit on SL/Target hit

### Phase 3 Complete:
- ✅ All trades logged
- ✅ Performance tracked
- ✅ Dashboard showing status
- ✅ Successfully paper trading

### Ready for Live:
- ✅ 1 week successful paper trading
- ✅ Zero crashes
- ✅ All risk rules enforced
- ✅ Comfortable with system behavior

---

## Next Steps

**Week 1 (This Week)**: Build Components 1-4
- Risk Calculator
- Position Sizer
- Portfolio Risk Manager
- Pre-Trade Validator

**Week 2**: Build Components 5-8
- Strategy Validator
- OpenAlgo Client
- Position Monitor
- Stop Loss Tracker

**Week 3**: Build Components 9-11
- Database Manager
- Trade Logger
- Integration tests

**Week 4+**: Polish & Test
- Terminal Dashboard
- Paper trading
- Bug fixes
- Go live!

---

## Questions to Think About

1. **Which components are most critical for YOUR trading style?**
2. **Do you want to use TradingView or build custom strategies?**
3. **How important is the dashboard vs just logging?**
4. **What notifications do you need?**

We can adjust priorities based on your answers!

Ready to start building Component 1 (Risk Calculator)?
