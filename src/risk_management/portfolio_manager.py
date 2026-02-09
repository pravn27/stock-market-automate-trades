#!/usr/bin/env python3
"""
Portfolio Risk Manager - Portfolio-Level Risk Enforcement

Enforces portfolio-wide risk limits to prevent:
- Overtrading
- Excessive daily losses
- Position concentration
- Correlated exposures

User-specific limits:
- Daily loss: 2% maximum
- Max trades: 3 per day
- Max positions: 3 concurrent
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RejectionReason(Enum):
    """Reasons for trade rejection"""
    MAX_POSITIONS_REACHED = "Maximum positions limit reached"
    DAILY_LOSS_LIMIT = "Daily loss limit exceeded"
    MAX_TRADES_LIMIT = "Maximum trades per day reached"
    INSUFFICIENT_CAPITAL = "Insufficient capital available"
    SECTOR_EXPOSURE_LIMIT = "Sector exposure limit exceeded"
    CORRELATED_POSITION = "Highly correlated position already exists"
    MARKET_CLOSED = "Market is closed"
    INVALID_SIGNAL = "Invalid signal parameters"


@dataclass
class Position:
    """Active position details"""
    symbol: str
    quantity: int
    entry_price: float
    current_price: float
    stop_loss: float
    target: float
    pnl: float
    entry_time: datetime
    sector: Optional[str] = None
    
    @property
    def position_value(self) -> float:
        """Current value of position"""
        return abs(self.quantity) * self.current_price
    
    @property
    def is_profitable(self) -> bool:
        """Check if position is in profit"""
        return self.pnl > 0


@dataclass
class TradeRecord:
    """Record of executed trade"""
    symbol: str
    action: str  # BUY or SELL
    quantity: int
    price: float
    timestamp: datetime
    pnl: Optional[float] = None  # None if still open


class PortfolioRiskManager:
    """
    Manages portfolio-level risk constraints
    
    Enforces:
    - Maximum concurrent positions (3)
    - Daily loss limit (2%)
    - Maximum trades per day (3)
    - Sector exposure limits (optional)
    - Correlation limits (optional)
    """
    
    def __init__(
        self,
        capital: float,
        max_positions: int = 3,
        max_daily_loss_percent: float = 0.02,  # 2%
        max_trades_per_day: int = 3,
        max_sector_exposure_percent: float = 0.50,  # 50% max per sector
        max_correlation: float = 0.70  # 0.70 = 70% correlation
    ):
        """
        Initialize Portfolio Risk Manager
        
        Args:
            capital: Total trading capital
            max_positions: Maximum concurrent positions (default: 3)
            max_daily_loss_percent: Maximum daily loss as % (default: 2%)
            max_trades_per_day: Maximum trades per day (default: 3)
            max_sector_exposure_percent: Max exposure per sector (default: 50%)
            max_correlation: Maximum correlation between positions (default: 0.70)
        """
        if capital <= 0:
            raise ValueError("Capital must be positive")
        
        if max_positions < 1:
            raise ValueError("Max positions must be at least 1")
        
        if not 0 < max_daily_loss_percent <= 0.05:
            raise ValueError("Daily loss limit must be between 0 and 5%")
        
        self.initial_capital = capital
        self.capital = capital
        self.max_positions = max_positions
        self.max_daily_loss_percent = max_daily_loss_percent
        self.max_daily_loss_amount = capital * max_daily_loss_percent
        self.max_trades_per_day = max_trades_per_day
        self.max_sector_exposure_percent = max_sector_exposure_percent
        self.max_correlation = max_correlation
        
        # Daily tracking
        self.current_date = date.today()
        self.daily_loss = 0.0
        self.daily_profit = 0.0
        self.trades_today = 0
        self.active_positions: Dict[str, Position] = {}
        self.todays_trades: List[TradeRecord] = []
        
        logger.info(
            f"PortfolioRiskManager initialized: "
            f"Capital=₹{capital:,.2f}, MaxPos={max_positions}, "
            f"DailyLossLimit={max_daily_loss_percent*100}%, "
            f"MaxTrades={max_trades_per_day}/day"
        )
    
    def _check_and_reset_daily_counters(self):
        """Reset daily counters if new trading day"""
        today = date.today()
        
        if today != self.current_date:
            logger.info(
                f"New trading day: Resetting counters. "
                f"Previous day - Trades: {self.trades_today}, "
                f"P&L: ₹{self.daily_profit - self.daily_loss:,.2f}"
            )
            
            self.current_date = today
            self.daily_loss = 0.0
            self.daily_profit = 0.0
            self.trades_today = 0
            self.todays_trades = []
    
    def can_take_trade(
        self,
        symbol: str,
        estimated_position_value: float,
        sector: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Check if new trade can be taken based on portfolio constraints
        
        Args:
            symbol: Symbol to trade
            estimated_position_value: Expected position value
            sector: Sector of the instrument (optional)
            
        Returns:
            (allowed, reason): Tuple of bool and reason string
        """
        # Reset daily counters if new day
        self._check_and_reset_daily_counters()
        
        # Check 1: Maximum positions limit
        if len(self.active_positions) >= self.max_positions:
            logger.warning(f"Trade rejected: {RejectionReason.MAX_POSITIONS_REACHED.value}")
            return False, f"Maximum {self.max_positions} positions already active"
        
        # Check 2: Daily loss limit
        daily_loss_percent = abs(self.daily_loss) / self.initial_capital
        if daily_loss_percent >= self.max_daily_loss_percent:
            logger.warning(
                f"Trade rejected: Daily loss {daily_loss_percent*100:.2f}% "
                f">= limit {self.max_daily_loss_percent*100}%"
            )
            return False, f"Daily loss limit reached: {daily_loss_percent*100:.2f}%"
        
        # Check 3: Maximum trades per day
        if self.trades_today >= self.max_trades_per_day:
            logger.warning(f"Trade rejected: Max {self.max_trades_per_day} trades/day reached")
            return False, f"Maximum {self.max_trades_per_day} trades per day reached"
        
        # Check 4: Sufficient capital available
        used_capital = sum(pos.position_value for pos in self.active_positions.values())
        available_capital = self.capital - used_capital
        
        if estimated_position_value > available_capital:
            logger.warning(
                f"Trade rejected: Insufficient capital. "
                f"Required: ₹{estimated_position_value:,.2f}, "
                f"Available: ₹{available_capital:,.2f}"
            )
            return False, f"Insufficient capital: Need ₹{estimated_position_value:,.2f}, have ₹{available_capital:,.2f}"
        
        # Check 5: Sector exposure (if sector provided)
        if sector:
            sector_exposure = self._calculate_sector_exposure(sector)
            max_sector_value = self.capital * self.max_sector_exposure_percent
            
            if sector_exposure + estimated_position_value > max_sector_value:
                logger.warning(
                    f"Trade rejected: Sector {sector} exposure limit. "
                    f"Current: ₹{sector_exposure:,.2f}, "
                    f"New would be: ₹{sector_exposure + estimated_position_value:,.2f}, "
                    f"Limit: ₹{max_sector_value:,.2f}"
                )
                return False, f"Sector {sector} exposure limit would be exceeded"
        
        # All checks passed
        logger.info(f"✅ Trade approved for {symbol}")
        return True, "All portfolio risk checks passed"
    
    def add_position(self, position: Position):
        """
        Add new position to portfolio
        
        Args:
            position: Position object
        """
        self._check_and_reset_daily_counters()
        
        if position.symbol in self.active_positions:
            logger.warning(f"Position for {position.symbol} already exists")
            return
        
        self.active_positions[position.symbol] = position
        self.trades_today += 1
        
        # Record trade
        trade_record = TradeRecord(
            symbol=position.symbol,
            action='BUY' if position.quantity > 0 else 'SELL',
            quantity=abs(position.quantity),
            price=position.entry_price,
            timestamp=position.entry_time
        )
        self.todays_trades.append(trade_record)
        
        logger.info(
            f"Position added: {position.symbol} | "
            f"Qty: {position.quantity} | "
            f"Entry: ₹{position.entry_price} | "
            f"Active positions: {len(self.active_positions)}/{self.max_positions}"
        )
    
    def remove_position(self, symbol: str, exit_price: float, exit_reason: str):
        """
        Remove position from portfolio and update P&L
        
        Args:
            symbol: Symbol to remove
            exit_price: Exit price
            exit_reason: Reason for exit (SL_HIT, TARGET_HIT, etc.)
        """
        if symbol not in self.active_positions:
            logger.warning(f"Position {symbol} not found")
            return
        
        position = self.active_positions[symbol]
        
        # Calculate P&L
        if position.quantity > 0:  # Long position
            pnl = (exit_price - position.entry_price) * position.quantity
        else:  # Short position
            pnl = (position.entry_price - exit_price) * abs(position.quantity)
        
        # Update daily P&L
        if pnl < 0:
            self.daily_loss += abs(pnl)
        else:
            self.daily_profit += pnl
        
        # Update trade record
        for trade in self.todays_trades:
            if trade.symbol == symbol and trade.pnl is None:
                trade.pnl = pnl
                break
        
        # Remove position
        del self.active_positions[symbol]
        
        logger.info(
            f"Position closed: {symbol} | "
            f"Exit: ₹{exit_price} | "
            f"P&L: ₹{pnl:,.2f} | "
            f"Reason: {exit_reason} | "
            f"Active: {len(self.active_positions)}"
        )
        
        # Check if daily loss limit reached after exit
        daily_loss_percent = abs(self.daily_loss) / self.initial_capital
        if daily_loss_percent >= self.max_daily_loss_percent:
            logger.critical(
                f"⚠️  DAILY LOSS LIMIT REACHED: {daily_loss_percent*100:.2f}% "
                f"(₹{self.daily_loss:,.2f}). Trading should be stopped for today!"
            )
    
    def update_position_price(self, symbol: str, current_price: float):
        """
        Update current price and P&L for a position
        
        Args:
            symbol: Symbol to update
            current_price: Current market price
        """
        if symbol not in self.active_positions:
            return
        
        position = self.active_positions[symbol]
        position.current_price = current_price
        
        # Update P&L
        if position.quantity > 0:  # Long
            position.pnl = (current_price - position.entry_price) * position.quantity
        else:  # Short
            position.pnl = (position.entry_price - current_price) * abs(position.quantity)
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get current portfolio summary
        
        Returns:
            Dictionary with portfolio metrics
        """
        self._check_and_reset_daily_counters()
        
        # Calculate total P&L
        total_pnl = sum(pos.pnl for pos in self.active_positions.values())
        net_daily_pnl = self.daily_profit - self.daily_loss
        
        # Calculate capital usage
        used_capital = sum(pos.position_value for pos in self.active_positions.values())
        capital_utilization = (used_capital / self.capital) * 100 if self.capital > 0 else 0
        
        # Calculate daily loss percentage
        daily_loss_percent = (abs(self.daily_loss) / self.initial_capital) * 100
        
        summary = {
            'capital': self.capital,
            'used_capital': used_capital,
            'available_capital': self.capital - used_capital,
            'capital_utilization_percent': capital_utilization,
            'active_positions': len(self.active_positions),
            'max_positions': self.max_positions,
            'trades_today': self.trades_today,
            'max_trades_per_day': self.max_trades_per_day,
            'unrealized_pnl': total_pnl,
            'daily_profit': self.daily_profit,
            'daily_loss': self.daily_loss,
            'net_daily_pnl': net_daily_pnl,
            'daily_loss_percent': daily_loss_percent,
            'daily_loss_limit_percent': self.max_daily_loss_percent * 100,
            'risk_remaining_percent': max(0, self.max_daily_loss_percent * 100 - daily_loss_percent),
            'can_trade_more': self.trades_today < self.max_trades_per_day and daily_loss_percent < self.max_daily_loss_percent * 100
        }
        
        return summary
    
    def _calculate_sector_exposure(self, sector: str) -> float:
        """
        Calculate total exposure to a specific sector
        
        Args:
            sector: Sector name
            
        Returns:
            Total value of positions in that sector
        """
        sector_value = sum(
            pos.position_value 
            for pos in self.active_positions.values() 
            if pos.sector == sector
        )
        return sector_value
    
    def check_correlation(self, symbol: str) -> Tuple[bool, str]:
        """
        Check if symbol is correlated with existing positions
        
        Args:
            symbol: Symbol to check
            
        Returns:
            (is_correlated, reason)
        """
        # Simplified correlation check
        # In production, use actual correlation matrix
        
        # Common correlations in Indian markets
        bank_stocks = ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK']
        it_stocks = ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM']
        auto_stocks = ['MARUTI', 'TATAMOTORS', 'M&M', 'BAJAJ-AUTO', 'EICHERMOT']
        
        # Check if we already have position in same group
        for existing_symbol in self.active_positions.keys():
            # Same sector correlation
            if symbol in bank_stocks and existing_symbol in bank_stocks:
                return True, f"Correlated: Both in Banking sector (existing: {existing_symbol})"
            
            if symbol in it_stocks and existing_symbol in it_stocks:
                return True, f"Correlated: Both in IT sector (existing: {existing_symbol})"
            
            if symbol in auto_stocks and existing_symbol in auto_stocks:
                return True, f"Correlated: Both in Auto sector (existing: {existing_symbol})"
        
        return False, "No high correlation detected"
    
    def get_active_positions(self) -> List[Position]:
        """Get list of active positions"""
        return list(self.active_positions.values())
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get specific position by symbol"""
        return self.active_positions.get(symbol)
    
    def has_position(self, symbol: str) -> bool:
        """Check if position exists for symbol"""
        return symbol in self.active_positions
    
    def print_summary(self):
        """Print portfolio summary (for debugging/monitoring)"""
        summary = self.get_portfolio_summary()
        
        print("\n" + "=" * 70)
        print(" PORTFOLIO SUMMARY")
        print("=" * 70)
        print(f"Capital: ₹{summary['capital']:,.2f}")
        print(f"Used: ₹{summary['used_capital']:,.2f} ({summary['capital_utilization_percent']:.1f}%)")
        print(f"Available: ₹{summary['available_capital']:,.2f}")
        print()
        print(f"Positions: {summary['active_positions']}/{summary['max_positions']}")
        print(f"Trades Today: {summary['trades_today']}/{summary['max_trades_per_day']}")
        print()
        print(f"Today's P&L: ₹{summary['net_daily_pnl']:,.2f}")
        print(f"  Profit: ₹{summary['daily_profit']:,.2f}")
        print(f"  Loss: ₹{summary['daily_loss']:,.2f}")
        print()
        print(f"Daily Loss: {summary['daily_loss_percent']:.2f}% / {summary['daily_loss_limit_percent']:.2f}%")
        print(f"Risk Remaining: {summary['risk_remaining_percent']:.2f}%")
        print()
        print(f"Can Trade More: {'✅ Yes' if summary['can_trade_more'] else '❌ No'}")
        print("=" * 70)
        
        if self.active_positions:
            print("\nActive Positions:")
            print("-" * 70)
            for pos in self.active_positions.values():
                status = "🟢" if pos.is_profitable else "🔴"
                print(
                    f"{status} {pos.symbol}: {pos.quantity} @ ₹{pos.entry_price} | "
                    f"Current: ₹{pos.current_price} | "
                    f"P&L: ₹{pos.pnl:,.2f}"
                )
            print("-" * 70)


if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print(" PORTFOLIO RISK MANAGER DEMO")
    print("=" * 70)
    
    # Initialize manager with user's limits
    manager = PortfolioRiskManager(
        capital=300000,
        max_positions=3,
        max_daily_loss_percent=0.02,  # 2%
        max_trades_per_day=3
    )
    
    print("\n📋 Configuration:")
    print(f"  Capital: ₹300,000")
    print(f"  Max Positions: 3")
    print(f"  Daily Loss Limit: 2%")
    print(f"  Max Trades/Day: 3")
    
    # Scenario 1: First trade
    print("\n" + "=" * 70)
    print(" Scenario 1: First Trade")
    print("=" * 70)
    
    can_trade, reason = manager.can_take_trade(
        symbol='RELIANCE',
        estimated_position_value=125000
    )
    print(f"Can trade RELIANCE? {can_trade}")
    print(f"Reason: {reason}")
    
    if can_trade:
        # Add position
        position = Position(
            symbol='RELIANCE',
            quantity=50,
            entry_price=2500,
            current_price=2500,
            stop_loss=2470,
            target=2575,
            pnl=0,
            entry_time=datetime.now(),
            sector='Energy'
        )
        manager.add_position(position)
    
    manager.print_summary()
    
    # Scenario 2: Second trade
    print("\n" + "=" * 70)
    print(" Scenario 2: Second Trade")
    print("=" * 70)
    
    can_trade, reason = manager.can_take_trade(
        symbol='TCS',
        estimated_position_value=105000
    )
    print(f"Can trade TCS? {can_trade}")
    print(f"Reason: {reason}")
    
    if can_trade:
        position = Position(
            symbol='TCS',
            quantity=30,
            current_price=3500,
            entry_price=3500,
            stop_loss=3465,
            target=3587,
            pnl=0,
            entry_time=datetime.now(),
            sector='IT'
        )
        manager.add_position(position)
    
    manager.print_summary()
    
    # Scenario 3: Third trade
    print("\n" + "=" * 70)
    print(" Scenario 3: Third Trade (Should be Last)")
    print("=" * 70)
    
    can_trade, reason = manager.can_take_trade(
        symbol='INFY',
        estimated_position_value=80000
    )
    print(f"Can trade INFY? {can_trade}")
    print(f"Reason: {reason}")
    
    if can_trade:
        position = Position(
            symbol='INFY',
            quantity=50,
            entry_price=1600,
            current_price=1600,
            stop_loss=1580,
            target=1650,
            pnl=0,
            entry_time=datetime.now(),
            sector='IT'
        )
        manager.add_position(position)
    
    manager.print_summary()
    
    # Scenario 4: Fourth trade (Should be REJECTED - max 3 positions)
    print("\n" + "=" * 70)
    print(" Scenario 4: Fourth Trade (Should be REJECTED)")
    print("=" * 70)
    
    can_trade, reason = manager.can_take_trade(
        symbol='HDFCBANK',
        estimated_position_value=100000
    )
    print(f"Can trade HDFCBANK? {can_trade}")
    print(f"Reason: {reason}")
    
    # Scenario 5: Simulate loss and check daily limit
    print("\n" + "=" * 70)
    print(" Scenario 5: Simulate Loss and Daily Limit Check")
    print("=" * 70)
    
    # Close RELIANCE with loss
    manager.update_position_price('RELIANCE', 2460)  # Hit SL
    manager.remove_position('RELIANCE', 2460, 'SL_HIT')
    
    # Close TCS with loss
    manager.update_position_price('TCS', 3450)  # Hit SL
    manager.remove_position('TCS', 3450, 'SL_HIT')
    
    manager.print_summary()
    
    # Try to take another trade after losses
    print("\n" + "=" * 70)
    print(" Scenario 6: Try Trade After Losses")
    print("=" * 70)
    
    can_trade, reason = manager.can_take_trade(
        symbol='SBIN',
        estimated_position_value=50000
    )
    print(f"Can trade SBIN? {can_trade}")
    print(f"Reason: {reason}")
    
    print("\n" + "=" * 70)
    print(" ✅ PORTFOLIO RISK MANAGER DEMO COMPLETE")
    print("=" * 70)
