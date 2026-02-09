#!/usr/bin/env python3
"""
Unit Tests for Portfolio Risk Manager
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, date

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from risk_management.portfolio_manager import (
    PortfolioRiskManager,
    Position,
    RejectionReason
)


class TestPortfolioRiskManager:
    """Test Portfolio Risk Manager functionality"""
    
    def test_initialization(self):
        """Test manager initialization with user parameters"""
        manager = PortfolioRiskManager(
            capital=300000,
            max_positions=3,
            max_daily_loss_percent=0.02,  # 2%
            max_trades_per_day=3
        )
        
        assert manager.capital == 300000
        assert manager.max_positions == 3
        assert manager.max_daily_loss_percent == 0.02
        assert manager.max_trades_per_day == 3
        assert manager.max_daily_loss_amount == 6000  # 300000 * 0.02
    
    def test_first_trade_allowed(self):
        """Test that first trade is allowed"""
        manager = PortfolioRiskManager(
            capital=300000,
            max_positions=3,
            max_daily_loss_percent=0.02,
            max_trades_per_day=3
        )
        
        can_trade, reason = manager.can_take_trade(
            symbol='RELIANCE',
            estimated_position_value=125000
        )
        
        assert can_trade == True
        assert "passed" in reason.lower()
    
    def test_max_positions_limit(self):
        """Test that max 3 positions limit is enforced"""
        manager = PortfolioRiskManager(
            capital=300000,
            max_positions=3,
            max_daily_loss_percent=0.02,
            max_trades_per_day=3
        )
        
        # Add 3 positions
        for i, symbol in enumerate(['RELIANCE', 'TCS', 'INFY']):
            position = Position(
                symbol=symbol,
                quantity=50,
                entry_price=2500,
                current_price=2500,
                stop_loss=2470,
                target=2575,
                pnl=0,
                entry_time=datetime.now()
            )
            manager.add_position(position)
        
        # Try 4th position - should be rejected
        can_trade, reason = manager.can_take_trade(
            symbol='SBIN',
            estimated_position_value=50000
        )
        
        assert can_trade == False
        assert "3 positions" in reason
    
    def test_max_trades_per_day(self):
        """Test max trades per day limit (3)"""
        manager = PortfolioRiskManager(
            capital=300000,
            max_positions=3,
            max_daily_loss_percent=0.02,
            max_trades_per_day=3
        )
        
        # Execute 3 trades (add and close immediately)
        for i, symbol in enumerate(['RELIANCE', 'TCS', 'INFY']):
            position = Position(
                symbol=symbol,
                quantity=50,
                entry_price=2500,
                current_price=2500,
                stop_loss=2470,
                target=2575,
                pnl=0,
                entry_time=datetime.now()
            )
            manager.add_position(position)
            manager.remove_position(symbol, 2575, 'TARGET_HIT')  # Close with profit
        
        # Try 4th trade - should be rejected
        can_trade, reason = manager.can_take_trade(
            symbol='SBIN',
            estimated_position_value=50000
        )
        
        assert can_trade == False
        assert "3 trades per day" in reason
    
    def test_daily_loss_limit(self):
        """Test 2% daily loss limit"""
        manager = PortfolioRiskManager(
            capital=300000,
            max_positions=3,
            max_daily_loss_percent=0.02,
            max_trades_per_day=3
        )
        
        # Add position
        position = Position(
            symbol='RELIANCE',
            quantity=50,
            entry_price=2500,
            current_price=2500,
            stop_loss=2470,
            target=2575,
            pnl=0,
            entry_time=datetime.now()
        )
        manager.add_position(position)
        
        # Simulate big loss (2.5% > 2% limit)
        manager.remove_position('RELIANCE', 2350, 'SL_HIT')  # Loss = 7500
        
        # Daily loss should be 2.5% now
        daily_loss_pct = abs(manager.daily_loss) / manager.initial_capital
        assert daily_loss_pct > 0.02
        
        # Try new trade - should be rejected
        can_trade, reason = manager.can_take_trade(
            symbol='TCS',
            estimated_position_value=100000
        )
        
        assert can_trade == False
        assert "Daily loss limit" in reason
    
    def test_insufficient_capital(self):
        """Test insufficient capital check"""
        manager = PortfolioRiskManager(
            capital=100000,
            max_positions=3,
            max_daily_loss_percent=0.02,
            max_trades_per_day=3
        )
        
        # Try to take position worth 120% of capital
        can_trade, reason = manager.can_take_trade(
            symbol='RELIANCE',
            estimated_position_value=120000
        )
        
        assert can_trade == False
        assert "Insufficient capital" in reason
    
    def test_position_tracking(self):
        """Test position add/remove tracking"""
        manager = PortfolioRiskManager(capital=300000)
        
        # Initially no positions
        assert len(manager.get_active_positions()) == 0
        
        # Add position
        position = Position(
            symbol='RELIANCE',
            quantity=50,
            entry_price=2500,
            current_price=2500,
            stop_loss=2470,
            target=2575,
            pnl=0,
            entry_time=datetime.now()
        )
        manager.add_position(position)
        
        assert len(manager.get_active_positions()) == 1
        assert manager.has_position('RELIANCE') == True
        assert manager.get_position('RELIANCE').symbol == 'RELIANCE'
        
        # Remove position
        manager.remove_position('RELIANCE', 2575, 'TARGET_HIT')
        
        assert len(manager.get_active_positions()) == 0
        assert manager.has_position('RELIANCE') == False
    
    def test_pnl_calculation_long(self):
        """Test P&L calculation for long position"""
        manager = PortfolioRiskManager(capital=300000)
        
        position = Position(
            symbol='RELIANCE',
            quantity=50,
            entry_price=2500,
            current_price=2500,
            stop_loss=2470,
            target=2575,
            pnl=0,
            entry_time=datetime.now()
        )
        manager.add_position(position)
        
        # Exit with profit
        manager.remove_position('RELIANCE', 2575, 'TARGET_HIT')
        
        # P&L should be (2575 - 2500) * 50 = 3750
        assert manager.daily_profit == 3750
        assert manager.daily_loss == 0
    
    def test_pnl_calculation_loss(self):
        """Test P&L calculation for losing trade"""
        manager = PortfolioRiskManager(capital=300000)
        
        position = Position(
            symbol='RELIANCE',
            quantity=50,
            entry_price=2500,
            current_price=2500,
            stop_loss=2470,
            target=2575,
            pnl=0,
            entry_time=datetime.now()
        )
        manager.add_position(position)
        
        # Exit with loss
        manager.remove_position('RELIANCE', 2470, 'SL_HIT')
        
        # Loss should be (2500 - 2470) * 50 = 1500
        assert manager.daily_loss == 1500
        assert manager.daily_profit == 0
    
    def test_portfolio_summary(self):
        """Test portfolio summary generation"""
        manager = PortfolioRiskManager(
            capital=300000,
            max_positions=3,
            max_daily_loss_percent=0.02,
            max_trades_per_day=3
        )
        
        summary = manager.get_portfolio_summary()
        
        assert 'capital' in summary
        assert 'active_positions' in summary
        assert 'trades_today' in summary
        assert 'daily_loss_percent' in summary
        assert 'can_trade_more' in summary
        
        assert summary['capital'] == 300000
        assert summary['max_positions'] == 3
        assert summary['max_trades_per_day'] == 3
    
    def test_correlation_check(self):
        """Test correlation checking between positions"""
        manager = PortfolioRiskManager(capital=300000)
        
        # Add ICICI Bank position
        position = Position(
            symbol='ICICIBANK',
            quantity=50,
            entry_price=1000,
            current_price=1000,
            stop_loss=980,
            target=1050,
            pnl=0,
            entry_time=datetime.now(),
            sector='Banking'
        )
        manager.add_position(position)
        
        # Try to add another bank stock (should detect correlation)
        is_correlated, reason = manager.check_correlation('HDFCBANK')
        
        assert is_correlated == True
        assert 'Banking' in reason or 'Correlated' in reason


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
