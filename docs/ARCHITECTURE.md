# System Architecture - High Level Design (with OpenAlgo)

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│              AUTOMATED TRADING SYSTEM (with OpenAlgo)            │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────────────────────┐
│   TradingView    │         │  YOUR CUSTOM RISK MANAGEMENT     │
│   (Signals)      │ Webhook │         LAYER                    │
└────────┬─────────┘         │                                  │
         │                   │  ┌────────────────────────────┐  │
         │                   │  │   Strategy Validator       │  │
         └──────────────────►│  │   (Entry/Exit Rules)       │  │
                             │  └──────────┬─────────────────┘  │
                             │             │                    │
                             │  ┌──────────▼─────────────────┐  │
                             │  │   Risk Manager             │  │
                             │  │   - 1% per trade           │  │
                             │  │   - 2.5:1 RR minimum       │  │
                             │  │   - Daily loss limits      │  │
                             │  └──────────┬─────────────────┘  │
                             │             │                    │
                             │  ┌──────────▼─────────────────┐  │
                             │  │   Position Sizer           │  │
                             │  │   Calculate quantity       │  │
                             │  └──────────┬─────────────────┘  │
                             │             │                    │
                             │  ┌──────────▼─────────────────┐  │
                             │  │   Pre-Trade Validator      │  │
                             │  │   Final checks before exec │  │
                             │  └──────────┬─────────────────┘  │
                             └─────────────┼────────────────────┘
                                           │ Approved Order
                                           ▼
                             ┌─────────────────────────────────┐
                             │      OpenAlgo Platform          │
                             │  (Self-Hosted Infrastructure)   │
                             │                                 │
                             │  - Authentication               │
                             │  - Order Routing                │
                             │  - Webhook Receiver             │
                             │  - Multi-broker Support         │
                             │  - Telegram Notifications       │
                             └────────┬──────────┬─────────────┘
                                      │          │
                    ┌─────────────────┘          └──────────────┐
                    │                                           │
         ┌──────────▼──────────┐                   ┌───────────▼────────┐
         │  Shoonya (Finvasia) │                   │  25+ Other Brokers │
         │  Trading Platform   │                   │  (Future proof)    │
         └─────────────────────┘                   └────────────────────┘
                    │
                    │ Positions, Orders, Balance
                    │
                    ▼
         ┌──────────────────────────────────────────┐
         │     Your Monitoring & Logging Layer      │
         │  - Position Tracking                     │
         │  - SL/Target Monitoring                  │
         │  - Performance Analytics                 │
         │  - Trade Journal (Database)              │
         └──────────────────────────────────────────┘
```

## 2. Core Components (Your Custom Layer)

### 2.1 OpenAlgo Client Wrapper
**Purpose**: Interface with OpenAlgo API
- **Input**: Order requests, configuration
- **Output**: Order confirmations, position data
- **Responsibilities**:
  - Authentication with OpenAlgo
  - Place/modify/cancel orders via OpenAlgo
  - Fetch positions and order book
  - Handle OpenAlgo API errors
  - WebSocket connection for real-time updates

### 2.2 Strategy Validator
**Purpose**: Validate TradingView signals against your rules
- **Input**: TradingView webhook signals
- **Output**: Validated signals
- **Responsibilities**:
  - Parse TradingView alerts
  - Validate signal format
  - Check if signal matches your strategy rules
  - Calculate initial stop loss and target
  - Add context and metadata

### 2.3 Risk Management Module (YOUR CORE VALUE)
**Purpose**: Enforce strict risk and money management rules
- **Input**: Validated signals, account balance, current positions
- **Output**: Approved/Rejected signals with position sizing
- **Responsibilities**:
  - Stop loss calculation (ATR-based, S/R, fixed %)
  - Target calculation (min 1:2.5 RR enforcement)
  - Position sizing based on risk per trade
  - Portfolio-level risk checks:
    - Maximum positions (3)
    - Daily loss limit (3%)
    - Max trades per day (5)
    - Sector exposure limits
  - Correlation checks
  - **This is where emotions are removed!**

### 2.4 Position Size Calculator
**Purpose**: Calculate optimal position size for each trade
- **Input**: Account balance, risk percentage, stop loss distance
- **Output**: Number of shares/quantity to trade
- **Formula**: 
  ```
  Position Size = (Account Balance × Risk %) / Stop Loss Distance
  ```

### 2.5 Pre-Trade Validator
**Purpose**: Final validation before sending to OpenAlgo
- **Input**: Risk-approved signal with position size
- **Output**: Final approved order or rejection
- **Responsibilities**:
  - Verify all risk checks passed
  - Confirm sufficient balance
  - Check market hours
  - Validate order parameters
  - Log pre-trade details

### 2.6 Position Monitor
**Purpose**: Monitor active positions for SL/Target hits
- **Input**: Current positions from OpenAlgo, real-time prices
- **Output**: Exit orders when SL/Target hit
- **Responsibilities**:
  - Track active positions
  - Monitor stop loss levels
  - Monitor target levels
  - Auto-exit on SL/Target hit via OpenAlgo
  - Trailing stop loss (optional)
  - Update position status in database

### 2.7 Monitoring & Logging System
**Purpose**: Track system performance and generate alerts
- **Components**:
  - Database for trade history
  - Performance analytics
  - Trade journal
  - System health monitoring
  - Custom alerts (beyond OpenAlgo's built-in Telegram)

## 2.8 OpenAlgo Platform (Managed Separately)

**What OpenAlgo Handles:**
- ✅ Broker API integration (Shoonya and 25+ others)
- ✅ Order execution and routing
- ✅ Authentication and session management
- ✅ TradingView webhook receiver
- ✅ Basic Telegram notifications
- ✅ WebSocket connections
- ✅ Multi-account support
- ✅ Rate limiting and error handling

**What You Don't Need to Build:**
- ❌ Shoonya API wrapper
- ❌ Order placement logic
- ❌ Session management
- ❌ Broker-specific error handling
- ❌ TradingView webhook parser (basic)

## 3. Data Flow (with OpenAlgo)

### 3.1 Trade Entry Flow (TradingView Signal)
```
1. TradingView → Generate alert (price crosses EMA, etc.)
   
2. TradingView → Send webhook to OpenAlgo
   Payload: {
     "symbol": "RELIANCE",
     "action": "BUY",
     "price": 2500
   }
   
3. OpenAlgo → Forward webhook to Your Custom Endpoint
   
4. Strategy Validator → Parse and validate signal
   - Check signal format
   - Verify symbol is tradeable
   - Extract entry price
   
5. Risk Calculator → Calculate SL and Target
   - Fetch ATR for the symbol
   - Calculate SL = Entry - (ATR × 1.5)
   - Calculate Target = Entry + (Risk × 2.5)
   - Verify R:R ratio ≥ 2.5
   
6. Position Sizer → Calculate quantity
   - Get account balance from OpenAlgo
   - Risk amount = Balance × 1%
   - Quantity = Risk / (Entry - SL)
   
7. Portfolio Risk Manager → Validate portfolio rules
   - Check current positions < 3
   - Check daily loss < 3%
   - Check trades today < 5
   - Check sector exposure
   
8. Pre-Trade Validator → Final checks
   - All rules passed?
   - Sufficient balance?
   - Market open?
   
9. Your System → Send order to OpenAlgo API
   POST /api/v1/placeorder
   {
     "symbol": "RELIANCE",
     "exchange": "NSE",
     "action": "BUY",
     "quantity": 50,
     "price": 2500,
     "product": "MIS",
     "stoploss": 2470,
     "target": 2575
   }
   
10. OpenAlgo → Execute order with Shoonya
    
11. OpenAlgo → Return order confirmation
    
12. Your System → Save trade to database
    
13. Your System → Update active positions
    
14. OpenAlgo → Send Telegram notification (built-in)
```

### 3.2 Trade Exit Flow (Stop Loss / Target Hit)
```
1. Position Monitor → Fetch positions from OpenAlgo API
   GET /api/v1/positions
   
2. Position Monitor → Get current market prices
   GET /api/v1/quotes?symbol=RELIANCE
   
3. Position Monitor → Check each position
   For RELIANCE position:
   - Entry: 2500
   - SL: 2470
   - Target: 2575
   - Current Price: 2468
   
4. Position Monitor → SL hit detected!
   
5. Your System → Place exit order via OpenAlgo
   POST /api/v1/placeorder
   {
     "symbol": "RELIANCE",
     "exchange": "NSE",
     "action": "SELL",
     "quantity": 50,
     "product": "MIS",
     "order_type": "MARKET"
   }
   
6. OpenAlgo → Execute exit order with Shoonya
   
7. Your System → Update position status to "CLOSED"
   
8. Your System → Calculate P&L
   - Entry: 2500
   - Exit: 2468
   - Quantity: 50
   - P&L: (2468 - 2500) × 50 = -₹1,600
   
9. Your System → Update trade in database
   
10. Risk Manager → Update daily loss counter
    
11. Your System → Log trade result
    
12. OpenAlgo → Send exit notification via Telegram
```

### 3.3 Manual Entry Flow (Your Custom Logic)
```
1. Your Strategy → Analyze market data
   - Fetch historical data
   - Calculate indicators
   - Evaluate entry conditions
   
2. Your Strategy → Generate signal internally
   
3. [Follow same flow as 3.1 from step 4 onwards]
```

## 4. System Modes

### 4.1 Backtesting Mode
- Test strategies on historical data
- Validate risk/reward ratios
- Calculate expected returns
- No real orders placed

### 4.2 Paper Trading Mode
- Real-time simulation
- All components active except actual order placement
- Virtual portfolio tracking
- Risk-free testing

### 4.3 Live Trading Mode
- Full system active
- Real orders placed
- Real money at risk
- Continuous monitoring required

## 5. Safety Mechanisms

### 5.1 Circuit Breakers
- **Daily Loss Limit**: Stop trading if daily loss exceeds X%
- **Max Positions**: Limit number of concurrent positions
- **Max Trade Frequency**: Prevent over-trading
- **Connection Loss**: Safe shutdown if API disconnects

### 5.2 Manual Override
- Emergency stop button
- Manual order cancellation
- System pause/resume
- Parameter adjustment interface

### 5.3 Validation Layers
1. **Pre-trade validation**: Check before order placement
2. **Post-execution validation**: Verify order confirmation
3. **Position reconciliation**: Match system vs broker positions
4. **Balance verification**: Check account balance regularly

## 6. Configuration Management

### 6.1 Configuration Files
- `config/trading_rules.yaml` - Trading strategy rules
- `config/risk_management.yaml` - Risk parameters
- `config/api_credentials.yaml` - API keys (encrypted)
- `config/system_settings.yaml` - System parameters

### 6.2 Key Parameters
```yaml
risk_management:
  risk_per_trade: 1.0  # 1% of capital per trade
  min_risk_reward: 2.5  # Minimum RR ratio
  max_daily_loss: 3.0  # 3% max daily loss
  max_positions: 3  # Maximum concurrent positions
  max_trades_per_day: 5  # Maximum trades per day

position_sizing:
  default_capital: 100000  # Default capital
  min_position_size: 1  # Minimum shares
  max_position_size_percent: 10  # Max 10% of capital per trade
```

## 7. Technology Stack (Updated for OpenAlgo)

### 7.1 Core Technologies
- **Language**: Python 3.10+
- **Infrastructure**: OpenAlgo (Self-hosted, Docker)
- **Your Layer**: Custom Python application
- **API Communication**: OpenAlgo REST API + Python SDK
- **Technical Analysis**: pandas-ta, TA-Lib (for custom strategies)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Scheduling**: APScheduler
- **Logging**: Python logging + file rotation

### 7.2 Key Libraries
```python
# OpenAlgo Integration
- openalgo-python  # OpenAlgo Python SDK
- requests         # HTTP client for OpenAlgo API

# Your Custom Layer
- pandas           # Data manipulation
- pandas-ta        # Technical indicators (optional)
- pyyaml           # Configuration
- sqlalchemy       # Database ORM
- apscheduler      # Task scheduling
- flask            # Webhook receiver (if needed)

# Utilities
- python-dotenv    # Environment variables
- loguru           # Better logging
```

### 7.3 Architecture Layers

```
┌─────────────────────────────────────────┐
│     Your Custom Python Application      │
│  (Risk Management + Strategy Logic)     │
│  - Running on your machine              │
│  - Communicates with OpenAlgo via API   │
└──────────────┬──────────────────────────┘
               │ REST API / Python SDK
               │
┌──────────────▼──────────────────────────┐
│         OpenAlgo Platform               │
│  (Infrastructure Layer)                 │
│  - Running in Docker (self-hosted)      │
│  - Port: 5000 (default)                 │
│  - Handles broker communication         │
└──────────────┬──────────────────────────┘
               │ Broker APIs
               │
┌──────────────▼──────────────────────────┐
│    Shoonya / 25+ Other Brokers          │
└─────────────────────────────────────────┘
```

## 8. Security Considerations

### 8.1 Credential Management
- API keys stored encrypted
- Never commit credentials to git
- Use environment variables
- Secure key rotation

### 8.2 Data Protection
- Encrypted database for sensitive data
- Secure API communication (HTTPS)
- Access logs and audit trails
- Regular security updates

## 9. Scalability & Performance

### 9.1 Performance Requirements
- Order execution latency: < 500ms
- Market data update frequency: 1-5 seconds
- Strategy evaluation: < 100ms per symbol
- Database writes: Asynchronous, non-blocking

### 9.2 Scalability Considerations
- Start with single symbol trading
- Expand to multiple symbols gradually
- Consider microservices architecture for scale
- Implement caching for frequently accessed data

## 10. Monitoring & Alerting

### 10.1 System Metrics
- System uptime
- API response times
- Order success rate
- Data feed reliability
- Error rates

### 10.2 Trading Metrics
- Daily P&L
- Win rate
- Average R:R ratio
- Maximum drawdown
- Number of active positions
- Capital utilization

### 10.3 Alert Triggers
- Trade executed
- Stop loss hit
- Target achieved
- Daily loss limit approaching
- System error
- API connection lost
- Unusual market conditions
