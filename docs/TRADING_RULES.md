# Trading Rules & Risk Management

## 1. Core Trading Principles

### 1.1 Risk Management (NON-NEGOTIABLE)
These rules are hard-coded into the system and cannot be overridden:

1. **Risk Per Trade**: Maximum 1% of capital per trade
2. **Minimum Risk-Reward Ratio**: 2.5:1 (minimum)
3. **Daily Loss Limit**: Stop trading if daily loss exceeds 3%
4. **Maximum Positions**: Maximum 3 concurrent positions
5. **Position Size**: Never exceed 10% of capital in single position

### 1.2 Money Management Rules

#### Capital Allocation
```
Total Capital: 100%
├── Active Trading Capital: 30% (maximum in positions at once)
├── Reserved for Opportunities: 50%
└── Safety Buffer: 20% (never trade this)
```

#### Position Sizing Formula
```python
# Risk-based position sizing
Position Size = (Account Balance × Risk%) / |Entry Price - Stop Loss|

Example:
- Account Balance: ₹100,000
- Risk per trade: 1% = ₹1,000
- Entry Price: ₹500
- Stop Loss: ₹490
- Risk per share: ₹10

Position Size = 1,000 / 10 = 100 shares
Total Investment = 100 × 500 = ₹50,000
```

### 1.3 Stop Loss Rules

#### ATR-Based Stop Loss (Recommended)
```python
Stop Loss = Entry Price ± (ATR × Multiplier)

For BUY trades:
Stop Loss = Entry Price - (ATR × 1.5)

For SELL trades:
Stop Loss = Entry Price + (ATR × 1.5)
```

#### Fixed Percentage Stop Loss
```python
Stop Loss = Entry Price × (1 ± Stop Loss %)

For BUY trades:
Stop Loss = Entry Price × 0.98  # 2% below entry

For SELL trades:
Stop Loss = Entry Price × 1.02  # 2% above entry
```

#### Support/Resistance Based Stop Loss
```
For BUY trades:
- Place stop loss slightly below recent support level
- Minimum: 0.5% below support
- Maximum: 3% below entry

For SELL trades:
- Place stop loss slightly above recent resistance level
- Minimum: 0.5% above resistance
- Maximum: 3% above entry
```

### 1.4 Target Setting

#### Minimum Risk-Reward Based
```python
# Calculate minimum target to achieve 2.5:1 RR
Risk = |Entry Price - Stop Loss|
Minimum Reward = Risk × 2.5

For BUY trades:
Target = Entry Price + Minimum Reward

For SELL trades:
Target = Entry Price - Minimum Reward
```

#### Multiple Targets (Optional)
```
Position split into 3 parts:
- Target 1 (30%): Risk-Reward 1.5:1 (Quick profit)
- Target 2 (40%): Risk-Reward 2.5:1 (Primary target)
- Target 3 (30%): Risk-Reward 4:1 (Extended target)

After Target 1 hit: Move stop loss to breakeven
After Target 2 hit: Trail stop loss
```

## 2. Entry Rules (Strategy Dependent)

### 2.1 Pre-Entry Checklist
Before any trade, ALL conditions must be met:

1. ✓ Market is open and liquid
2. ✓ No adverse news pending (earnings, major announcements)
3. ✓ Signal meets minimum confidence threshold
4. ✓ Risk-Reward ratio ≥ 2.5:1
5. ✓ Daily loss limit not reached
6. ✓ Maximum positions not reached
7. ✓ Sufficient capital available
8. ✓ No conflicting positions (same sector/correlated instruments)

### 2.2 Example Strategy: Trend Following Breakout

#### Entry Conditions (ALL must be TRUE)
```yaml
entry_conditions:
  # Trend identification
  - price > ema_21
  - ema_9 > ema_21
  
  # Momentum confirmation
  - rsi > 50 and rsi < 70
  
  # Volume confirmation
  - current_volume > avg_volume_20 * 1.5
  
  # Breakout confirmation
  - price > resistance_level
  - breakout_candle_range > atr * 1.2
  
  # Risk-reward validation
  - calculated_target / calculated_risk >= 2.5
```

#### Entry Execution
```
1. Wait for breakout candle to close
2. Calculate stop loss (below breakout level or ATR-based)
3. Calculate target (minimum 2.5:1 RR)
4. Calculate position size
5. Place bracket order (Entry + SL + Target)
6. Log trade details
```

## 3. Exit Rules

### 3.1 Stop Loss Exit (Highest Priority)
```
Trigger: Price hits stop loss level
Action: Exit entire position immediately (Market order)
Reason: Protect capital, accept the loss
Log: Record trade details, analyze what went wrong
```

### 3.2 Target Exit
```
Trigger: Price hits target level
Action: Exit position (can be partial or full)
Reason: Book profits as per plan
Log: Record trade details, celebrate disciplined exit
```

### 3.3 Time-Based Exit
```
If position held for > 2 days without reaching target:
  - Review trade setup
  - If losing: Exit if down > 0.5%
  - If slightly profitable: Consider trailing stop
  - If flat: Exit at breakeven
```

### 3.4 Trailing Stop Loss (Optional)
```
Activate after: Target 1 reached or profit > 1.5% Risk

Trailing method:
- Trail by ATR: New SL = Current High - (ATR × 1.5)
- Trail by percentage: New SL = Current High × 0.98
- Trail by swing low: New SL = Recent swing low

Update frequency: Every 5-minute candle close
```

### 3.5 Emergency Exit Conditions
Exit ALL positions immediately if:
- Daily loss limit reached (3%)
- System error detected
- Market circuit breaker triggered
- API connection lost for > 1 minute
- Unusual volatility (VIX spike > threshold)

## 4. Portfolio Management

### 4.1 Correlation Management
```
Rule: Maximum 2 positions in correlated instruments

Correlation matrix:
- Nifty50 stocks: Check sector correlation
- Bank stocks: High correlation with Bank Nifty
- IT stocks: High correlation with Nifty IT

Action: If new signal is highly correlated (>0.7) with 
existing position, skip the trade
```

### 4.2 Sector Exposure
```
Maximum exposure per sector: 40% of active capital

Sectors:
- Banking/Finance
- IT
- Pharma
- Auto
- Energy
- FMCG

Track: Sum of position values by sector
```

### 4.3 Daily Trade Limit
```
Maximum trades per day: 5

Why: Prevent over-trading and emotional decisions

Exception: Exit trades don't count toward limit
```

## 5. Emotion Control Mechanisms

### 5.1 Forced Breaks
```
After 2 consecutive losses:
- Take 30-minute break
- Review what went wrong
- Recalibrate if needed

After 3 consecutive losses:
- Stop trading for the day
- Review trading system
- Check if market conditions changed
```

### 5.2 No Revenge Trading
```
Rules:
1. Never increase position size after a loss
2. Never remove stop loss after entry
3. Never average down on losing position
4. Stick to calculated position size
```

### 5.3 Profit Protection
```
After reaching daily profit target (2%):
- Tighten stop losses on remaining positions
- Reduce position size for new trades by 50%
- Consider stopping for the day
```

## 6. System Parameters Configuration

### 6.1 Risk Parameters (config/risk_management.yaml)
```yaml
risk_management:
  # Position sizing
  risk_per_trade_percent: 1.0
  max_position_size_percent: 10.0
  
  # Risk-reward
  min_risk_reward_ratio: 2.5
  
  # Portfolio limits
  max_concurrent_positions: 3
  max_daily_loss_percent: 3.0
  max_trades_per_day: 5
  daily_profit_target_percent: 2.0
  
  # Correlation
  max_correlation: 0.7
  max_sector_exposure_percent: 40.0
  
  # Stop loss settings
  stop_loss_method: "atr_based"  # atr_based, fixed_percent, support_resistance
  atr_multiplier: 1.5
  fixed_sl_percent: 2.0
  
  # Trailing stop
  enable_trailing_stop: true
  trailing_trigger_rr: 1.5
  trailing_stop_atr_multiplier: 1.5
```

### 6.2 Trading Hours
```yaml
trading_hours:
  market_open: "09:15"
  market_close: "15:30"
  
  # Avoid first 15 minutes (high volatility)
  start_trading_at: "09:30"
  
  # Avoid last 15 minutes (erratic moves)
  stop_new_trades_at: "15:15"
  
  # Close all positions before market close
  force_exit_time: "15:25"
```

## 7. Pre-Trade Validation Checklist

```python
class PreTradeValidator:
    def validate_trade(self, signal: Signal) -> Tuple[bool, str]:
        """
        Validate trade against all rules
        Returns: (is_valid, reason)
        """
        checks = [
            self._check_risk_reward(signal),
            self._check_position_size(signal),
            self._check_daily_limits(),
            self._check_position_limits(),
            self._check_correlation(signal),
            self._check_sector_exposure(signal),
            self._check_market_hours(),
            self._check_account_balance(signal),
        ]
        
        for passed, reason in checks:
            if not passed:
                return False, reason
                
        return True, "All validations passed"
```

## 8. Post-Trade Analysis

### 8.1 Trade Journal (Auto-generated)
```
For each trade, record:
- Entry date/time
- Exit date/time
- Symbol
- Entry price
- Exit price
- Stop loss
- Target
- Quantity
- P&L (₹ and %)
- Risk-Reward (planned vs actual)
- Exit reason
- Strategy used
- Market conditions
- Mistakes (if any)
```

### 8.2 Performance Metrics
```
Daily:
- Total trades
- Win rate
- Average R:R
- P&L
- Maximum drawdown

Weekly:
- Cumulative P&L
- Best/worst day
- Strategy performance
- Rule violations (if any)

Monthly:
- Return %
- Sharpe ratio
- Win rate trend
- Capital growth
```

## 9. Rule Violation Handling

### 9.1 System Enforced (Cannot be violated)
- Stop loss hit → Automatic exit
- Daily loss limit → Trading disabled
- Max positions → New trades blocked
- Insufficient capital → Trade rejected

### 9.2 Logged Warnings
- Position size exceeds recommendation
- Risk-reward below optimal
- High correlation detected
- Unusual market conditions

### 9.3 Learning from Violations
```
Track:
- How many times risk was exceeded
- How many times stop loss was widened
- Average holding period vs planned
- Emotional decision count

Review monthly and adjust system
```

## 10. Example Trade Workflow

```
1. SIGNAL GENERATION
   - System detects breakout in RELIANCE
   - Entry: ₹2,500
   - ATR: ₹20
   
2. STOP LOSS CALCULATION
   - SL = 2,500 - (20 × 1.5) = ₹2,470
   - Risk per share = ₹30
   
3. TARGET CALCULATION
   - Minimum reward = 30 × 2.5 = ₹75
   - Target = 2,500 + 75 = ₹2,575
   - Risk-Reward = 75/30 = 2.5 ✓
   
4. POSITION SIZE CALCULATION
   - Account balance = ₹100,000
   - Risk per trade = 1% = ₹1,000
   - Position size = 1,000 / 30 = 33 shares
   - Investment = 33 × 2,500 = ₹82,500 (< 10% ✓)
   
5. PRE-TRADE VALIDATION
   ✓ Risk-reward ≥ 2.5
   ✓ Current positions = 2 (< 3)
   ✓ Daily loss = 1.5% (< 3%)
   ✓ Trades today = 3 (< 5)
   ✓ Sector exposure OK
   ✓ Market hours OK
   
6. ORDER EXECUTION
   - Place bracket order
   - Entry: 33 shares @ ₹2,500
   - Stop loss: ₹2,470
   - Target: ₹2,575
   
7. MONITORING
   - Track price every 5 seconds
   - Check for SL/Target hit
   
8. EXIT SCENARIOS
   
   A. Target Hit (₹2,575)
      - P&L = 33 × (2,575 - 2,500) = ₹2,475
      - Return = 2,475 / 82,500 = 3%
      - Actual R:R = 2.5 ✓
      
   B. Stop Loss Hit (₹2,470)
      - P&L = 33 × (2,470 - 2,500) = -₹990
      - Loss = -0.99% of capital ✓
      - Accept the loss, move on
```

This trading rules document ensures disciplined, emotion-free trading with strict risk management!
