# Implementation Plan - Step by Step Guide (with OpenAlgo)

**TOTAL TIMELINE: ~3 weeks** (vs 5-6 weeks building from scratch)

OpenAlgo eliminates 2-3 weeks of broker API integration work, allowing you to focus on what matters: **risk management and strategy logic**.

## Phase 0: OpenAlgo Setup & Testing (Day 1-2)

### Step 0.1: Install OpenAlgo (Infrastructure Layer)
```bash
# Clone OpenAlgo repository
git clone https://github.com/marketcalls/openalgo.git
cd openalgo

# Start OpenAlgo with Docker (recommended)
docker-compose up -d

# OpenAlgo will run at http://localhost:5000

# Verify it's running
curl http://localhost:5000
```

### Step 0.2: Configure OpenAlgo with Shoonya
1. Open browser: http://localhost:5000
2. Create admin account
3. Go to Settings → Broker Configuration
4. Select "Finvasia (Shoonya)"
5. Enter your Shoonya credentials:
   - User ID
   - Password
   - API Key
   - Vendor Code
   - TOTP Secret
6. Click "Test Connection" → Should show ✅ Connected

### Step 0.3: Get OpenAlgo API Key
1. In OpenAlgo Dashboard → Settings → API Keys
2. Click "Generate New API Key"
3. Save the key securely
4. You'll use this to communicate with OpenAlgo from your app

### Step 0.4: Setup Your Custom Application
```bash
# Navigate to your project directory
cd /path/to/stock-market-automate-trades

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 0.5: Test OpenAlgo Connection
```python
# test_openalgo.py
from openalgo import api

client = api.OpenAlgoClient(
    api_key='your_openalgo_api_key',
    host='http://localhost:5000'
)

# Test 1: Get account balance
funds = client.funds()
print(f"Available balance: {funds['data']['availablecash']}")

# Test 2: Get quote
quote = client.quotes(symbol='RELIANCE', exchange='NSE')
print(f"RELIANCE LTP: {quote['data']['ltp']}")

# Test 3: Get positions (should be empty initially)
positions = client.positions()
print(f"Current positions: {len(positions['data'])}")

print("✅ OpenAlgo setup successful!")
```

**Time Saved**: ~1 week (no need to build Shoonya API wrapper)

## Phase 1: OpenAlgo Client Wrapper (Day 3)

**MUCH SIMPLER**: Instead of building complex API wrapper, just create thin wrapper around OpenAlgo SDK

### Step 1.1: OpenAlgo Client Wrapper
**File**: `src/openalgo/client.py`

**Tasks**:
- [ ] Create OpenAlgoClient wrapper class
- [ ] Implement place_order() with retry logic
- [ ] Implement cancel_order()
- [ ] Implement get_positions()
- [ ] Implement get_quote()
- [ ] Implement get_balance()
- [ ] Add logging for all operations

**Code**:
```python
from openalgo import api
import logging

class TradingClient:
    def __init__(self, api_key, host='http://localhost:5000'):
        self.client = api.OpenAlgoClient(api_key=api_key, host=host)
        self.logger = logging.getLogger(__name__)
    
    def place_bracket_order(self, symbol, action, quantity, entry, sl, target):
        """Place bracket order with SL and target"""
        try:
            order = self.client.placeorder(
                strategy='AutomatedTrading',
                symbol=symbol,
                exchange='NSE',
                action=action,
                quantity=quantity,
                price=entry,
                product='MIS',
                pricetype='LIMIT',
                ordertype='BRACKET',
                stoploss=sl,
                target=target
            )
            self.logger.info(f"Order placed: {order.get('orderid')}")
            return order
        except Exception as e:
            self.logger.error(f"Order placement failed: {e}")
            raise
    
    def get_positions(self):
        """Get current positions"""
        return self.client.positions()
    
    # ... other methods
```

**Time Saved**: ~1 week (OpenAlgo handles all broker communication)

## Phase 2: Risk Management (Day 4-7) - YOUR CORE VALUE

### Step 2.1: Risk Calculator
**File**: `src/risk_management/risk_calculator.py`

**Tasks**:
- [ ] Create RiskCalculator class
- [ ] Implement ATR-based stop loss
- [ ] Implement support/resistance-based stop loss
- [ ] Implement fixed percentage stop loss
- [ ] Implement target calculation (min 2.5 R:R)
- [ ] Add risk-reward validation

**Validation**:
```python
# Test risk calculations
calc = RiskCalculator(config)
sl = calc.calculate_stop_loss(2500, Action.BUY, atr=20)
target = calc.calculate_target(2500, sl)
print(f"Entry: 2500, SL: {sl}, Target: {target}")
print(f"R:R Ratio: {calc.calculate_rr_ratio(2500, sl, target)}")
```

### Step 2.2: Position Sizer
**File**: `src/risk_management/position_sizer.py`

**Tasks**:
- [ ] Create PositionSizer class
- [ ] Implement calculate_position_size()
- [ ] Add maximum position value constraint
- [ ] Add minimum position size validation
- [ ] Handle fractional shares (round down)

**Validation**:
```python
# Test position sizing
sizer = PositionSizer()
qty = sizer.calculate_position_size(
    account_balance=100000,
    risk_per_trade=0.01,
    entry_price=2500,
    stop_loss=2470
)
print(f"Position size: {qty} shares")
print(f"Capital required: {qty * 2500}")
```

### Step 2.3: Portfolio Risk Manager
**File**: `src/risk_management/portfolio_manager.py`

**Tasks**:
- [ ] Create PortfolioRiskManager class
- [ ] Implement max positions check
- [ ] Implement daily loss limit tracking
- [ ] Implement max trades per day
- [ ] Add correlation checking
- [ ] Add sector exposure tracking
- [ ] Implement daily counter reset

**Validation**:
```python
# Test portfolio constraints
manager = PortfolioRiskManager(config)
can_trade, reason = manager.can_take_trade(current_positions=2, signal)
print(f"Can trade: {can_trade}, Reason: {reason}")
```

## Phase 3: Strategy Engine (Day 8-10)

### Step 3.1: Base Strategy Framework
**File**: `src/strategy/base_strategy.py`

**Tasks**:
- [ ] Create BaseStrategy abstract class
- [ ] Define Signal dataclass
- [ ] Define Action enum
- [ ] Create strategy interface

### Step 3.2: Rules Engine
**File**: `src/strategy/rules_engine.py`

**Tasks**:
- [ ] Create RulesEngine class
- [ ] Implement rule parsing from YAML
- [ ] Implement condition evaluation
- [ ] Support multiple conditions (AND/OR)
- [ ] Add confidence scoring

**Example rules**:
```yaml
entry_conditions:
  - field: "close"
    operator: ">"
    compare_to: "ema_21"
  - field: "rsi"
    operator: ">"
    value: 50
```

### Step 3.3: Example Strategy Implementation
**File**: `src/strategy/breakout_strategy.py`

**Tasks**:
- [ ] Create BreakoutStrategy class (extends BaseStrategy)
- [ ] Implement generate_signal()
- [ ] Implement entry logic
- [ ] Implement exit logic
- [ ] Add parameter configuration

**Validation**:
```python
# Test strategy
strategy = BreakoutStrategy(config)
signal = strategy.generate_signal(market_data)
print(f"Signal: {signal.action}, Entry: {signal.entry_price}")
print(f"SL: {signal.stop_loss}, Target: {signal.target_price}")
print(f"R:R: {signal.risk_reward_ratio}")
```

## Phase 4: Position Monitoring (Day 11-12)

**SIMPLIFIED**: OpenAlgo handles order execution, you just monitor positions

### Step 4.1: Position Monitor
**File**: `src/monitoring/position_monitor.py`

**Tasks**:
- [ ] Create PositionMonitor class
- [ ] Fetch positions from OpenAlgo periodically
- [ ] Check if stop loss hit
- [ ] Check if target hit
- [ ] Place exit order via OpenAlgo when SL/Target hit
- [ ] Update database with trade results

**Code**:
```python
class PositionMonitor:
    def __init__(self, openalgo_client, db):
        self.client = openalgo_client
        self.db = db
        
    def monitor_positions(self):
        """Check all positions for SL/Target hits"""
        positions = self.client.get_positions()
        
        for position in positions['data']:
            # Get stored SL/Target from database
            trade = self.db.get_active_trade(position['symbol'])
            
            if not trade:
                continue
                
            current_price = float(position['ltp'])
            
            # Check stop loss
            if self._is_sl_hit(trade, current_price):
                self._exit_position(trade, 'SL_HIT', current_price)
                
            # Check target
            elif self._is_target_hit(trade, current_price):
                self._exit_position(trade, 'TARGET_HIT', current_price)
    
    def _exit_position(self, trade, reason, price):
        """Exit position via OpenAlgo"""
        action = 'SELL' if trade['action'] == 'BUY' else 'BUY'
        
        self.client.place_order(
            symbol=trade['symbol'],
            action=action,
            quantity=trade['quantity'],
            order_type='MARKET'
        )
        
        # Update database
        self.db.close_trade(trade['id'], reason, price)
```

**Time Saved**: ~1 week (no complex order management needed)

## Phase 5: Database & Logging (Day 13-14)

### Step 5.1: Database Setup
**File**: `src/database/models.py`

**Tasks**:
- [ ] Install SQLAlchemy
- [ ] Define Trade model
- [ ] Define Position model
- [ ] Define SystemMetrics model
- [ ] Create database initialization script

**File**: `src/database/repository.py`

**Tasks**:
- [ ] Create Database class
- [ ] Implement save_trade()
- [ ] Implement get_trades()
- [ ] Implement save_metrics()
- [ ] Add query helpers

### Step 5.2: Logging Setup
**File**: `src/monitoring/logger.py`

**Tasks**:
- [ ] Configure Python logging
- [ ] Set up file rotation
- [ ] Create separate logs for:
  - System events (info.log)
  - Errors (error.log)
  - Trades (trades.log)
- [ ] Add structured logging format

## Phase 6: Performance Tracking (Day 15)

**SIMPLIFIED**: OpenAlgo has built-in Telegram alerts, you just track performance

### Step 6.1: Performance Tracker (OpenAlgo handles notifications)
**File**: `src/monitoring/performance_tracker.py`

**Tasks**:
- [ ] Create PerformanceTracker class
- [ ] Calculate daily P&L
- [ ] Calculate win rate
- [ ] Calculate average R:R
- [ ] Calculate maximum drawdown
- [ ] Generate daily summary

## Phase 7: Main Application (Day 16-17)

### Step 7.1: Configuration Management
**File**: `src/utils/config_loader.py`

**Tasks**:
- [ ] Create ConfigLoader class
- [ ] Load YAML configurations
- [ ] Validate configuration parameters
- [ ] Handle environment variables for secrets

**Create config files**:
- `config/api_credentials.yaml` (template)
- `config/trading_rules.yaml`
- `config/risk_management.yaml`
- `config/system_settings.yaml`

### Step 7.2: Trading Engine
**File**: `src/main.py`

**Tasks**:
- [ ] Create TradingEngine class
- [ ] Implement initialization
- [ ] Implement main loop
- [ ] Add startup checks
- [ ] Add graceful shutdown
- [ ] Add state persistence
- [ ] Implement mode switching (backtest/paper/live)

**Main loop logic**:
```python
def run(self):
    while self.is_running:
        # 1. Check if market is open
        if not self.is_market_open():
            continue
            
        # 2. Get latest market data
        data = self.market_data.get_latest()
        
        # 3. Generate signals
        signal = self.strategy.generate_signal(data)
        
        # 4. If signal, validate and execute
        if signal.action in [BUY, SELL]:
            self.validate_and_execute(signal)
            
        # 5. Monitor active positions
        self.monitor_positions()
        
        # 6. Sleep
        time.sleep(self.update_interval)
```

### Step 7.3: Command Line Interface
**File**: `src/cli.py`

**Tasks**:
- [ ] Create CLI with argparse
- [ ] Add commands:
  - `start` - Start trading
  - `stop` - Stop trading
  - `status` - Show status
  - `backtest` - Run backtest
  - `paper` - Paper trading mode
  - `live` - Live trading mode

## Phase 8: Testing (Day 18-19)

### Step 8.1: Unit Tests
**Directory**: `tests/`

**Tasks**:
- [ ] Test RiskCalculator
- [ ] Test PositionSizer
- [ ] Test PortfolioRiskManager
- [ ] Test Strategy signal generation
- [ ] Test OrderExecutor (mocked)
- [ ] Test database operations

### Step 8.2: Integration Tests
**Tasks**:
- [ ] Test end-to-end signal to execution
- [ ] Test position monitoring
- [ ] Test stop loss triggers
- [ ] Test daily limit enforcement

### Step 8.3: Backtesting
**File**: `src/backtest/backtester.py`

**Tasks**:
- [ ] Create Backtester class
- [ ] Load historical data
- [ ] Simulate trades
- [ ] Calculate performance metrics
- [ ] Generate backtest report

**Validation**:
```python
# Run backtest
backtester = Backtester(strategy, data)
results = backtester.run(start_date, end_date)
print(results.summary())
# Output: Win rate, Total trades, P&L, Max DD, etc.
```

## Phase 9: Paper Trading (Day 20-25) - 1 Week Minimum

### Step 9.1: Setup Paper Trading
**Tasks**:
- [ ] Configure paper trading mode
- [ ] Set up virtual portfolio
- [ ] Track virtual trades
- [ ] Monitor system behavior

### Step 9.2: Run Paper Trading
**Duration**: 5 days minimum

**Objectives**:
- Verify all components work together
- Test during different market conditions
- Validate risk management rules
- Check for edge cases and bugs
- Monitor system stability

**Daily checklist**:
- [ ] System starts successfully
- [ ] Signals generated correctly
- [ ] Risk checks enforced
- [ ] Orders tracked properly
- [ ] Stop loss/targets work
- [ ] Logs are clean
- [ ] No crashes or errors

## Phase 10: Live Trading Preparation (Day 26+)

### Step 10.1: Final Safety Checks
**Checklist**:
- [ ] Stop loss always enforced
- [ ] Position sizing correct
- [ ] Daily loss limit works
- [ ] Max positions enforced
- [ ] Emergency stop works
- [ ] Manual override available
- [ ] Logs comprehensive
- [ ] Notifications working

### Step 10.2: Start Small
**Day 1-5 of Live Trading**:
- [ ] Start with 1 position max
- [ ] Use minimum position size
- [ ] Reduce risk per trade to 0.5%
- [ ] Monitor every trade closely
- [ ] Review each trade manually

### Step 10.3: Gradual Scale-Up
**Week 2-4**:
- [ ] Increase to 2 positions if all good
- [ ] Increase risk to 0.75%
- [ ] Monitor for 2 weeks

**Week 4+**:
- [ ] Increase to 3 positions
- [ ] Increase risk to 1%
- [ ] Continue monitoring

## Phase 11: Ongoing Maintenance

### Daily Tasks
- [ ] Check system logs
- [ ] Review trades taken
- [ ] Verify P&L matches broker
- [ ] Check for errors
- [ ] Monitor system health

### Weekly Tasks
- [ ] Calculate weekly performance
- [ ] Review strategy performance
- [ ] Check for rule violations
- [ ] Backup database
- [ ] Update strategy if needed

### Monthly Tasks
- [ ] Full performance review
- [ ] Strategy optimization
- [ ] Risk parameter tuning
- [ ] System updates
- [ ] Security audit

## Timeline Summary (With OpenAlgo - MUCH FASTER!)

```
Week 1 (Days 1-7):
├── Day 1-2: OpenAlgo setup & Shoonya configuration
├── Day 3: OpenAlgo client wrapper
├── Day 4-7: Risk management modules (YOUR CORE VALUE)
└── Time saved: ~1 week vs building from scratch

Week 2 (Days 8-14):
├── Day 8-10: Strategy engine & rules
├── Day 11-12: Position monitoring
├── Day 13-14: Database & logging
├── Day 15: Performance tracking
└── Time saved: ~1 week (no complex order execution)

Week 3 (Days 16-21):
├── Day 16-17: Main application & integration
├── Day 18-19: Unit & integration tests
├── Day 20-21: Initial testing & bug fixes
└── Ready for paper trading!

Week 4+ (Day 22+):
├── Paper trading (minimum 1 week)
├── Monitor, validate, fix issues
└── Go live when confident

TOTAL: ~3 weeks to paper trading (vs 5-6 weeks)
        ~4 weeks to live trading (vs 6-7 weeks)
```

## Key Benefits of Using OpenAlgo

✅ **2-3 weeks faster** development time  
✅ **No broker API complexity** - battle-tested integration  
✅ **Switch brokers easily** - same code works with 25+ brokers  
✅ **Active community** - 90,000+ users, Discord support  
✅ **Built-in features** - TradingView webhooks, Telegram alerts  
✅ **Focus on value** - Spend time on risk management, not API plumbing

## Success Criteria

### Before Paper Trading
- ✓ All unit tests pass
- ✓ Integration tests pass
- ✓ Backtest shows positive results
- ✓ Risk management enforced
- ✓ Logging comprehensive

### Before Live Trading
- ✓ 1 week successful paper trading
- ✓ Zero crashes
- ✓ All risk rules enforced
- ✓ Manual override tested
- ✓ Emergency stop tested
- ✓ Comfortable with system behavior

### Ongoing Success
- ✓ Following risk management rules
- ✓ No emotional overrides
- ✓ Regular monitoring
- ✓ Continuous improvement
- ✓ Positive R:R over time

## Common Pitfalls to Avoid

1. **Don't skip paper trading** - Essential for validation
2. **Don't over-optimize** - Keep strategy simple
3. **Don't ignore losses** - Analyze and learn
4. **Don't increase risk too fast** - Scale gradually
5. **Don't remove stop losses** - Never
6. **Don't trade without logs** - Always keep records
7. **Don't rely 100% on system** - Monitor actively
8. **Don't ignore system errors** - Fix immediately

## Next Steps

1. Review this implementation plan
2. Confirm understanding of each phase
3. Start with Phase 0: Environment Setup
4. Follow the plan step by step
5. Test thoroughly at each phase
6. Don't rush to live trading

Ready to start implementing? Let's begin with Phase 0!
