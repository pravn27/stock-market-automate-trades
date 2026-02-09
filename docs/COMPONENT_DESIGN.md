# Component Design - Low Level Design

## 1. Module Structure

```
src/
├── api/
│   ├── __init__.py
│   ├── shoonya_client.py      # Shoonya API wrapper
│   ├── market_data.py          # Market data fetcher
│   └── websocket_feed.py       # Real-time data feed
├── strategy/
│   ├── __init__.py
│   ├── base_strategy.py        # Abstract strategy class
│   ├── signal_generator.py     # Signal generation logic
│   ├── indicators.py           # Technical indicators
│   └── rules_engine.py         # Rule evaluation engine
├── risk_management/
│   ├── __init__.py
│   ├── risk_calculator.py      # Risk calculations
│   ├── position_sizer.py       # Position sizing
│   ├── stop_loss_manager.py    # SL/Target management
│   └── portfolio_manager.py    # Portfolio-level risk
├── execution/
│   ├── __init__.py
│   ├── order_executor.py       # Order execution
│   ├── order_manager.py        # Order tracking
│   └── execution_engine.py     # Main execution engine
├── monitoring/
│   ├── __init__.py
│   ├── logger.py               # Logging setup
│   ├── notifier.py             # Alert notifications
│   ├── performance_tracker.py  # Performance metrics
│   └── dashboard.py            # Optional web dashboard
├── database/
│   ├── __init__.py
│   ├── models.py               # Database models
│   └── repository.py           # Data access layer
└── utils/
    ├── __init__.py
    ├── config_loader.py        # Configuration management
    ├── validators.py           # Input validation
    └── helpers.py              # Utility functions
```

## 2. Core Classes and Interfaces

### 2.1 API Layer

#### ShoonyaClient
```python
class ShoonyaClient:
    """
    Wrapper for Shoonya API interactions
    """
    def __init__(self, credentials: dict):
        """Initialize with API credentials"""
        
    def login(self) -> bool:
        """Authenticate with Shoonya"""
        
    def get_quote(self, symbol: str, exchange: str) -> dict:
        """Get current market quote"""
        
    def place_order(self, order: Order) -> str:
        """Place an order, returns order_id"""
        
    def modify_order(self, order_id: str, **kwargs) -> bool:
        """Modify existing order"""
        
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        
    def get_positions(self) -> List[Position]:
        """Get current positions"""
        
    def get_order_book(self) -> List[Order]:
        """Get order book"""
        
    def get_account_balance(self) -> float:
        """Get available balance"""
```

#### MarketDataFeed
```python
class MarketDataFeed:
    """
    Manages market data collection
    """
    def __init__(self, client: ShoonyaClient):
        """Initialize with Shoonya client"""
        
    def get_historical_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime,
        interval: str = '5min'
    ) -> pd.DataFrame:
        """Fetch historical OHLCV data"""
        
    def subscribe_realtime(
        self, 
        symbols: List[str], 
        callback: Callable
    ):
        """Subscribe to real-time price updates"""
        
    def calculate_indicators(
        self, 
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate technical indicators"""
```

### 2.2 Strategy Layer

#### BaseStrategy (Abstract)
```python
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies
    """
    def __init__(self, config: dict):
        """Initialize strategy with configuration"""
        self.config = config
        
    @abstractmethod
    def generate_signal(
        self, 
        data: pd.DataFrame
    ) -> Signal:
        """
        Generate trading signal based on market data
        Returns: Signal object with action, entry, sl, target
        """
        pass
        
    @abstractmethod
    def validate_signal(
        self, 
        signal: Signal
    ) -> bool:
        """Validate signal meets strategy criteria"""
        pass
```

#### Signal
```python
from dataclasses import dataclass
from enum import Enum

class Action(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    EXIT = "EXIT"

@dataclass
class Signal:
    symbol: str
    action: Action
    entry_price: float
    stop_loss: float
    target_price: float
    timestamp: datetime
    confidence: float  # 0.0 to 1.0
    reason: str  # Description of why signal generated
    
    @property
    def risk_reward_ratio(self) -> float:
        """Calculate R:R ratio"""
        risk = abs(self.entry_price - self.stop_loss)
        reward = abs(self.target_price - self.entry_price)
        return reward / risk if risk > 0 else 0
```

#### RulesEngine
```python
class RulesEngine:
    """
    Evaluates trading rules and conditions
    """
    def __init__(self, rules_config: dict):
        """Load rules from configuration"""
        self.rules = self._parse_rules(rules_config)
        
    def evaluate(
        self, 
        data: pd.DataFrame, 
        context: dict
    ) -> List[Signal]:
        """
        Evaluate all rules against current data
        Returns list of signals generated
        """
        
    def check_entry_conditions(
        self, 
        data: pd.DataFrame
    ) -> bool:
        """Check if entry conditions are met"""
        
    def check_exit_conditions(
        self, 
        position: Position, 
        current_price: float
    ) -> bool:
        """Check if exit conditions are met"""
```

### 2.3 Risk Management Layer

#### RiskCalculator
```python
class RiskCalculator:
    """
    Calculates risk parameters for trades
    """
    def __init__(self, config: dict):
        self.risk_per_trade = config['risk_per_trade']  # e.g., 0.01 for 1%
        self.min_rr_ratio = config['min_risk_reward']  # e.g., 2.5
        
    def calculate_stop_loss(
        self, 
        entry_price: float, 
        signal_type: Action,
        atr: float = None,
        support_resistance: float = None
    ) -> float:
        """Calculate stop loss based on technical factors"""
        
    def calculate_target(
        self, 
        entry_price: float, 
        stop_loss: float,
        min_rr: float = None
    ) -> float:
        """Calculate target to meet minimum R:R ratio"""
        
    def validate_risk_reward(
        self, 
        signal: Signal
    ) -> bool:
        """Validate signal meets minimum R:R ratio"""
        return signal.risk_reward_ratio >= self.min_rr_ratio
```

#### PositionSizer
```python
class PositionSizer:
    """
    Calculates position size based on risk parameters
    """
    def calculate_position_size(
        self,
        account_balance: float,
        risk_per_trade: float,
        entry_price: float,
        stop_loss: float,
        max_position_value: float = None
    ) -> int:
        """
        Calculate number of shares/quantity to trade
        
        Formula:
        Position Size = (Account Balance × Risk %) / (Entry - Stop Loss)
        
        Returns: Number of shares (integer)
        """
        risk_amount = account_balance * risk_per_trade
        risk_per_share = abs(entry_price - stop_loss)
        
        if risk_per_share == 0:
            return 0
            
        quantity = int(risk_amount / risk_per_share)
        
        # Apply maximum position size constraint
        if max_position_value:
            max_quantity = int(max_position_value / entry_price)
            quantity = min(quantity, max_quantity)
            
        return quantity
```

#### PortfolioRiskManager
```python
class PortfolioRiskManager:
    """
    Manages portfolio-level risk constraints
    """
    def __init__(self, config: dict):
        self.max_positions = config['max_positions']
        self.max_daily_loss = config['max_daily_loss']
        self.max_trades_per_day = config['max_trades_per_day']
        self.daily_loss = 0.0
        self.trades_today = 0
        
    def can_take_trade(
        self, 
        current_positions: int,
        signal: Signal
    ) -> Tuple[bool, str]:
        """
        Check if new trade can be taken
        Returns: (allowed, reason)
        """
        # Check max positions
        if current_positions >= self.max_positions:
            return False, "Maximum positions reached"
            
        # Check daily loss limit
        if self.daily_loss >= self.max_daily_loss:
            return False, "Daily loss limit reached"
            
        # Check max trades per day
        if self.trades_today >= self.max_trades_per_day:
            return False, "Maximum trades per day reached"
            
        return True, "Trade allowed"
        
    def update_daily_pnl(self, pnl: float):
        """Update daily profit/loss tracking"""
        self.daily_loss += abs(pnl) if pnl < 0 else 0
        
    def reset_daily_counters(self):
        """Reset daily counters (call at start of trading day)"""
        self.daily_loss = 0.0
        self.trades_today = 0
```

### 2.4 Execution Layer

#### Order
```python
@dataclass
class Order:
    symbol: str
    exchange: str
    action: Action  # BUY/SELL
    quantity: int
    order_type: str  # MARKET, LIMIT
    price: float = None  # For LIMIT orders
    stop_loss: float = None
    target: float = None
    order_id: str = None
    status: str = None  # PENDING, FILLED, CANCELLED, REJECTED
    filled_price: float = None
    filled_quantity: int = 0
    timestamp: datetime = None
```

#### OrderExecutor
```python
class OrderExecutor:
    """
    Handles order execution with Shoonya
    """
    def __init__(self, client: ShoonyaClient):
        self.client = client
        
    def execute_order(
        self, 
        order: Order,
        retry_count: int = 3
    ) -> Order:
        """
        Execute order with retry logic
        Returns updated Order object with execution details
        """
        
    def place_bracket_order(
        self,
        order: Order
    ) -> Tuple[str, str, str]:
        """
        Place bracket order (entry + SL + target)
        Returns: (entry_order_id, sl_order_id, target_order_id)
        """
        
    def modify_stop_loss(
        self,
        position: Position,
        new_sl: float
    ) -> bool:
        """Modify stop loss for existing position"""
```

#### OrderManager
```python
class OrderManager:
    """
    Tracks and manages all orders and positions
    """
    def __init__(self, client: ShoonyaClient, db: Database):
        self.client = client
        self.db = db
        self.active_orders: Dict[str, Order] = {}
        self.active_positions: Dict[str, Position] = {}
        
    def add_order(self, order: Order):
        """Add order to tracking"""
        
    def update_order_status(self, order_id: str):
        """Update order status from broker"""
        
    def check_stop_loss_hit(
        self, 
        position: Position, 
        current_price: float
    ) -> bool:
        """Check if stop loss is hit"""
        
    def check_target_hit(
        self, 
        position: Position, 
        current_price: float
    ) -> bool:
        """Check if target is hit"""
        
    def exit_position(
        self, 
        position: Position,
        reason: str
    ) -> Order:
        """Exit a position"""
```

### 2.5 Database Layer

#### Database Models
```python
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    action = Column(String)  # BUY/SELL
    entry_price = Column(Float)
    exit_price = Column(Float)
    quantity = Column(Integer)
    stop_loss = Column(Float)
    target = Column(Float)
    pnl = Column(Float)
    risk_reward_actual = Column(Float)
    entry_time = Column(DateTime)
    exit_time = Column(DateTime)
    exit_reason = Column(String)  # TARGET_HIT, SL_HIT, MANUAL, etc.
    strategy_name = Column(String)
    
class SystemMetrics(Base):
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    win_rate = Column(Float)
    total_pnl = Column(Float)
    max_drawdown = Column(Float)
    active_positions = Column(Integer)
```

## 3. Main Application Flow

### TradingEngine
```python
class TradingEngine:
    """
    Main orchestrator for the trading system
    """
    def __init__(self, config: dict):
        # Initialize all components
        self.client = ShoonyaClient(config['api'])
        self.market_data = MarketDataFeed(self.client)
        self.strategy = self._load_strategy(config['strategy'])
        self.risk_manager = PortfolioRiskManager(config['risk'])
        self.position_sizer = PositionSizer()
        self.executor = OrderExecutor(self.client)
        self.order_manager = OrderManager(self.client, database)
        
    def run(self):
        """Main execution loop"""
        while self.is_running:
            try:
                # 1. Get market data
                data = self.market_data.get_latest_data()
                
                # 2. Generate signals
                signal = self.strategy.generate_signal(data)
                
                if signal.action in [Action.BUY, Action.SELL]:
                    # 3. Validate signal
                    if self._validate_and_execute_signal(signal):
                        logger.info(f"Trade executed: {signal}")
                
                # 4. Monitor active positions
                self._monitor_positions()
                
                # 5. Sleep until next iteration
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                
    def _validate_and_execute_signal(self, signal: Signal) -> bool:
        """Validate and execute a trading signal"""
        # Check portfolio-level constraints
        can_trade, reason = self.risk_manager.can_take_trade(
            len(self.order_manager.active_positions),
            signal
        )
        if not can_trade:
            logger.warning(f"Trade rejected: {reason}")
            return False
            
        # Calculate position size
        balance = self.client.get_account_balance()
        quantity = self.position_sizer.calculate_position_size(
            balance,
            self.config['risk_per_trade'],
            signal.entry_price,
            signal.stop_loss
        )
        
        if quantity == 0:
            logger.warning("Position size calculated as 0")
            return False
            
        # Create and execute order
        order = Order(
            symbol=signal.symbol,
            action=signal.action,
            quantity=quantity,
            stop_loss=signal.stop_loss,
            target=signal.target
        )
        
        executed_order = self.executor.execute_order(order)
        self.order_manager.add_order(executed_order)
        
        return executed_order.status == "FILLED"
```

## 4. Configuration Schema

### trading_rules.yaml
```yaml
strategy:
  name: "breakout_strategy"
  timeframe: "5min"
  indicators:
    - name: "RSI"
      period: 14
      overbought: 70
      oversold: 30
    - name: "EMA"
      fast: 9
      slow: 21
  
  entry_rules:
    - condition: "price > ema_21"
    - condition: "rsi > 50"
    - condition: "volume > avg_volume * 1.5"
    
  exit_rules:
    - type: "stop_loss"
      method: "atr_based"
      multiplier: 1.5
    - type: "target"
      method: "risk_reward"
      ratio: 2.5
```

### risk_management.yaml
```yaml
risk_management:
  # Position level
  risk_per_trade_percent: 1.0  # 1% of capital
  min_risk_reward_ratio: 2.5
  max_position_size_percent: 10.0
  
  # Portfolio level
  max_concurrent_positions: 3
  max_daily_loss_percent: 3.0
  max_trades_per_day: 5
  
  # Stop loss methods
  stop_loss:
    method: "atr_based"  # atr_based, fixed_percent, support_resistance
    atr_multiplier: 1.5
    fixed_percent: 2.0
```

This completes the low-level component design. Would you like me to continue with the implementation plan?
