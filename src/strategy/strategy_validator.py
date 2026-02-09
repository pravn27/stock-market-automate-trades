#!/usr/bin/env python3
"""
Component 5: Strategy Validator

Integrates TradingView signals with Risk Calculator and Portfolio Manager.
Makes the final decision on whether to execute a trade.

Flow:
1. Receive signal from TradingView webhook
2. Validate signal format and authentication
3. Calculate position size (Risk Calculator)
4. Validate risk-reward ratio
5. Check portfolio constraints (Portfolio Manager)
6. Approve or reject trade
"""

import logging
from typing import Tuple, Optional, Dict
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from strategy.webhook_handler import TradingSignal, TradeAction
from risk_management import RiskCalculator, ConvictionLevel, PortfolioRiskManager

logger = logging.getLogger(__name__)


@dataclass
class TradeDecision:
    """
    Final trade decision with all validation results
    """
    approved: bool
    signal: TradingSignal
    reason: str
    
    # Risk calculation results
    position_size: Optional[int] = None
    investment_amount: Optional[float] = None
    risk_amount: Optional[float] = None
    risk_percent: Optional[float] = None
    
    # Risk-reward validation
    risk_reward_ratio: Optional[float] = None
    rr_valid: Optional[bool] = None
    
    # Portfolio checks
    portfolio_check: Optional[bool] = None
    portfolio_reason: Optional[str] = None
    
    # Metadata
    timestamp: datetime = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'approved': self.approved,
            'reason': self.reason,
            'signal': self.signal.to_dict(),
            'position_size': self.position_size,
            'investment_amount': self.investment_amount,
            'risk_amount': self.risk_amount,
            'risk_percent': self.risk_percent,
            'risk_reward_ratio': self.risk_reward_ratio,
            'rr_valid': self.rr_valid,
            'portfolio_check': self.portfolio_check,
            'portfolio_reason': self.portfolio_reason,
            'timestamp': self.timestamp.isoformat()
        }


class StrategyValidator:
    """
    Validates trading signals and makes trade decisions
    
    Integrates:
    - Risk Calculator (Component 1)
    - Portfolio Manager (Component 3)
    - Webhook Handler (Component 5)
    """
    
    def __init__(
        self,
        risk_calculator: RiskCalculator,
        portfolio_manager: PortfolioRiskManager,
        min_rr_ratio: float = 2.5,
        require_stop_loss: bool = True,
        require_target: bool = True
    ):
        """
        Initialize strategy validator
        
        Args:
            risk_calculator: Risk Calculator instance
            portfolio_manager: Portfolio Manager instance
            min_rr_ratio: Minimum risk:reward ratio
            require_stop_loss: Require stop loss in signal
            require_target: Require target in signal
        """
        self.risk_calc = risk_calculator
        self.portfolio = portfolio_manager
        self.min_rr_ratio = min_rr_ratio
        self.require_stop_loss = require_stop_loss
        self.require_target = require_target
        
        logger.info(
            f"StrategyValidator initialized: "
            f"Min R:R={min_rr_ratio}, "
            f"Require SL={require_stop_loss}, "
            f"Require Target={require_target}"
        )
    
    def validate_signal_completeness(self, signal: TradingSignal) -> Tuple[bool, str]:
        """
        Validate that signal has all required fields
        
        Args:
            signal: Trading signal
            
        Returns:
            (valid, reason)
        """
        if self.require_stop_loss and not signal.stop_loss:
            return False, "Stop loss is required but missing"
        
        if self.require_target and not signal.target:
            return False, "Target is required but missing"
        
        if signal.action == TradeAction.BUY:
            if signal.stop_loss and signal.stop_loss >= signal.price:
                return False, f"For BUY, stop loss (₹{signal.stop_loss}) must be below entry (₹{signal.price})"
            
            if signal.target and signal.target <= signal.price:
                return False, f"For BUY, target (₹{signal.target}) must be above entry (₹{signal.price})"
        
        elif signal.action == TradeAction.SELL:
            if signal.stop_loss and signal.stop_loss <= signal.price:
                return False, f"For SELL, stop loss (₹{signal.stop_loss}) must be above entry (₹{signal.price})"
            
            if signal.target and signal.target >= signal.price:
                return False, f"For SELL, target (₹{signal.target}) must be below entry (₹{signal.price})"
        
        return True, "Signal complete"
    
    def calculate_position(
        self,
        signal: TradingSignal
    ) -> Tuple[bool, Optional[object], str]:
        """
        Calculate position size using Risk Calculator
        
        Args:
            signal: Trading signal
            
        Returns:
            (success, allocation, message)
        """
        try:
            # Map conviction string to enum
            conviction_map = {
                'BELOW_LOW': ConvictionLevel.BELOW_LOW,
                'LOW': ConvictionLevel.LOW,
                'MEDIUM': ConvictionLevel.MEDIUM,
                'HIGH': ConvictionLevel.HIGH,
                'ABOVE_HIGH': ConvictionLevel.ABOVE_HIGH,
                'HIGHEST': ConvictionLevel.HIGHEST
            }
            
            conviction = conviction_map.get(signal.conviction, ConvictionLevel.MEDIUM)
            
            # Calculate position size (assuming equity for now)
            allocation = self.risk_calc.calculate_position_size_equity(
                entry_price=signal.price,
                stop_loss=signal.stop_loss,
                conviction=conviction
            )
            
            if allocation.final_quantity == 0:
                return False, None, "Calculated position size is 0 (risk too high for capital)"
            
            logger.info(
                f"Position calculated: {allocation.final_quantity} shares, "
                f"Investment: ₹{allocation.total_investment:,.2f}, "
                f"Risk: ₹{allocation.actual_risk_amount:,.2f} ({allocation.actual_risk_percent*100:.2f}%)"
            )
            
            return True, allocation, "Position calculated"
            
        except Exception as e:
            logger.error(f"Error calculating position: {e}")
            return False, None, f"Calculation error: {str(e)}"
    
    def validate_risk_reward(
        self,
        signal: TradingSignal
    ) -> Tuple[bool, float, str]:
        """
        Validate risk:reward ratio
        
        Args:
            signal: Trading signal
            
        Returns:
            (valid, ratio, message)
        """
        try:
            is_valid, rr_ratio, message = self.risk_calc.validate_risk_reward(
                entry_price=signal.price,
                stop_loss=signal.stop_loss,
                target_price=signal.target,
                min_rr_ratio=self.min_rr_ratio
            )
            
            if is_valid:
                logger.info(f"✅ Risk:Reward validated: 1:{rr_ratio:.2f} (min: 1:{self.min_rr_ratio})")
            else:
                logger.warning(f"❌ Risk:Reward invalid: 1:{rr_ratio:.2f} < 1:{self.min_rr_ratio}")
            
            return is_valid, rr_ratio, message
            
        except Exception as e:
            logger.error(f"Error validating R:R: {e}")
            return False, 0.0, f"R:R validation error: {str(e)}"
    
    def check_portfolio_constraints(
        self,
        signal: TradingSignal,
        allocation: object
    ) -> Tuple[bool, str]:
        """
        Check portfolio-level constraints
        
        Args:
            signal: Trading signal
            allocation: Position allocation from Risk Calculator
            
        Returns:
            (allowed, reason)
        """
        try:
            # Determine sector (simplified - in production, use a sector mapping service)
            sector = self._get_sector(signal.symbol)
            
            can_trade, reason = self.portfolio.can_take_trade(
                symbol=signal.symbol,
                estimated_position_value=allocation.total_investment,
                sector=sector
            )
            
            if can_trade:
                logger.info(f"✅ Portfolio check passed: {reason}")
            else:
                logger.warning(f"❌ Portfolio check failed: {reason}")
            
            return can_trade, reason
            
        except Exception as e:
            logger.error(f"Error checking portfolio: {e}")
            return False, f"Portfolio check error: {str(e)}"
    
    def _get_sector(self, symbol: str) -> Optional[str]:
        """
        Get sector for symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Sector name or None
        """
        # Simplified sector mapping for demo
        sector_map = {
            'RELIANCE': 'Energy',
            'TCS': 'IT',
            'INFY': 'IT',
            'WIPRO': 'IT',
            'HCLTECH': 'IT',
            'TECHM': 'IT',
            'HDFCBANK': 'Banking',
            'ICICIBANK': 'Banking',
            'SBIN': 'Banking',
            'KOTAKBANK': 'Banking',
            'AXISBANK': 'Banking',
            'TATAMOTORS': 'Auto',
            'MARUTI': 'Auto',
            'M&M': 'Auto',
        }
        
        return sector_map.get(symbol.upper())
    
    def validate_trade(
        self,
        signal: TradingSignal
    ) -> TradeDecision:
        """
        Complete trade validation pipeline
        
        Args:
            signal: Trading signal from TradingView
            
        Returns:
            TradeDecision with approval status and details
        """
        logger.info(
            f"\n{'='*80}\n"
            f" VALIDATING TRADE: {signal.action.value} {signal.symbol}\n"
            f"{'='*80}"
        )
        
        # Step 1: Validate signal completeness
        logger.info("\n📋 STEP 1: Signal Completeness Check")
        valid, reason = self.validate_signal_completeness(signal)
        if not valid:
            logger.warning(f"❌ Signal incomplete: {reason}")
            return TradeDecision(
                approved=False,
                signal=signal,
                reason=reason
            )
        logger.info(f"✅ {reason}")
        
        # Step 2: Calculate position size
        logger.info("\n📐 STEP 2: Position Size Calculation")
        success, allocation, msg = self.calculate_position(signal)
        if not success:
            logger.warning(f"❌ Position calculation failed: {msg}")
            return TradeDecision(
                approved=False,
                signal=signal,
                reason=msg
            )
        
        # Step 3: Validate risk:reward
        logger.info("\n✅ STEP 3: Risk:Reward Validation")
        rr_valid, rr_ratio, rr_msg = self.validate_risk_reward(signal)
        if not rr_valid:
            logger.warning(f"❌ R:R validation failed: {rr_msg}")
            return TradeDecision(
                approved=False,
                signal=signal,
                reason=rr_msg,
                position_size=allocation.final_quantity,
                investment_amount=allocation.total_investment,
                risk_amount=allocation.actual_risk_amount,
                risk_percent=allocation.actual_risk_percent,
                risk_reward_ratio=rr_ratio,
                rr_valid=False
            )
        
        # Step 4: Check portfolio constraints
        logger.info("\n🛡️  STEP 4: Portfolio Constraints Check")
        portfolio_ok, portfolio_reason = self.check_portfolio_constraints(signal, allocation)
        if not portfolio_ok:
            logger.warning(f"❌ Portfolio check failed: {portfolio_reason}")
            return TradeDecision(
                approved=False,
                signal=signal,
                reason=portfolio_reason,
                position_size=allocation.final_quantity,
                investment_amount=allocation.total_investment,
                risk_amount=allocation.actual_risk_amount,
                risk_percent=allocation.actual_risk_percent,
                risk_reward_ratio=rr_ratio,
                rr_valid=True,
                portfolio_check=False,
                portfolio_reason=portfolio_reason
            )
        
        # All checks passed - APPROVE TRADE
        logger.info(
            f"\n{'='*80}\n"
            f" ✅ TRADE APPROVED\n"
            f"{'='*80}\n"
            f" Symbol: {signal.symbol}\n"
            f" Action: {signal.action.value}\n"
            f" Entry: ₹{signal.price}\n"
            f" Stop Loss: ₹{signal.stop_loss}\n"
            f" Target: ₹{signal.target}\n"
            f" Conviction: {signal.conviction}\n"
            f" Position Size: {allocation.final_quantity} shares\n"
            f" Investment: ₹{allocation.total_investment:,.2f}\n"
            f" Risk: ₹{allocation.actual_risk_amount:,.2f} ({allocation.actual_risk_percent*100:.2f}%)\n"
            f" Risk:Reward: 1:{rr_ratio:.2f}\n"
            f"{'='*80}"
        )
        
        return TradeDecision(
            approved=True,
            signal=signal,
            reason="All validations passed - trade approved",
            position_size=allocation.final_quantity,
            investment_amount=allocation.total_investment,
            risk_amount=allocation.actual_risk_amount,
            risk_percent=allocation.actual_risk_percent,
            risk_reward_ratio=rr_ratio,
            rr_valid=True,
            portfolio_check=True,
            portfolio_reason=portfolio_reason
        )


if __name__ == "__main__":
    # Demo strategy validator
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 80)
    print(" STRATEGY VALIDATOR DEMO")
    print("=" * 80)
    
    # Initialize components
    risk_calc = RiskCalculator(capital=300000)
    portfolio = PortfolioRiskManager(
        capital=300000,
        max_positions=3,
        max_daily_loss_percent=0.02,
        max_trades_per_day=3
    )
    
    validator = StrategyValidator(
        risk_calculator=risk_calc,
        portfolio_manager=portfolio,
        min_rr_ratio=2.5
    )
    
    # Test 1: Valid signal
    print("\n" + "=" * 80)
    print(" TEST 1: Valid Signal - Should APPROVE")
    print("=" * 80)
    
    signal1 = TradingSignal(
        symbol='TCS',
        exchange='NSE',
        action=TradeAction.BUY,
        price=3500,
        stop_loss=3462.5,  # 37.5 points risk
        target=3593.75,    # 93.75 points reward = 2.5:1 R:R
        conviction='MEDIUM',
        strategy='BB_MTF'
    )
    
    decision1 = validator.validate_trade(signal1)
    print(f"\n{'✅ APPROVED' if decision1.approved else '❌ REJECTED'}")
    print(f"Reason: {decision1.reason}")
    
    # Test 2: Invalid R:R
    print("\n" + "=" * 80)
    print(" TEST 2: Invalid Risk:Reward - Should REJECT")
    print("=" * 80)
    
    signal2 = TradingSignal(
        symbol='RELIANCE',
        exchange='NSE',
        action=TradeAction.BUY,
        price=2500,
        stop_loss=2470,
        target=2530,  # Only 1:1 R:R
        conviction='HIGH',
        strategy='BB_MTF'
    )
    
    decision2 = validator.validate_trade(signal2)
    print(f"\n{'✅ APPROVED' if decision2.approved else '❌ REJECTED'}")
    print(f"Reason: {decision2.reason}")
    
    # Test 3: Missing stop loss
    print("\n" + "=" * 80)
    print(" TEST 3: Missing Stop Loss - Should REJECT")
    print("=" * 80)
    
    signal3 = TradingSignal(
        symbol='INFY',
        exchange='NSE',
        action=TradeAction.BUY,
        price=1600,
        stop_loss=None,  # Missing SL
        target=1650,
        conviction='LOW',
        strategy='BB_MTF'
    )
    
    decision3 = validator.validate_trade(signal3)
    print(f"\n{'✅ APPROVED' if decision3.approved else '❌ REJECTED'}")
    print(f"Reason: {decision3.reason}")
    
    print("\n" + "=" * 80)
    print(" ✅ STRATEGY VALIDATOR DEMO COMPLETE")
    print("=" * 80)
