#!/usr/bin/env python3
"""
Risk Calculator - Conviction-Based Risk Allocation

Implements risk calculation based on Technical Analysis probability/conviction levels.
Supports both F&O (lot-based) and Equity (share-based) position sizing.

Based on user's Excel model with 2% max risk allocation.
"""

from enum import Enum
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import logging

# Setup logging
logger = logging.getLogger(__name__)


class ConvictionLevel(Enum):
    """
    Conviction levels based on Technical Analysis probability
    """
    BELOW_LOW = "below_low"      # 0.25% risk
    LOW = "low"                  # 0.50% risk
    MEDIUM = "medium"            # 1.00% risk
    HIGH = "high"                # 1.50% risk
    ABOVE_HIGH = "above_high"    # 1.75% risk
    HIGHEST = "highest"          # 2.00% risk (max)


class InstrumentType(Enum):
    """
    Type of trading instrument
    """
    EQUITY = "equity"           # Stocks (share-based)
    FUTURES = "futures"         # Futures (lot-based)
    OPTIONS = "options"         # Options (lot-based)


@dataclass
class RiskAllocation:
    """
    Risk allocation details for a trade
    """
    capital: float
    conviction_level: ConvictionLevel
    risk_percent: float
    risk_amount: float
    entry_price: float
    stop_loss: float
    risk_per_unit: float  # Per share or per lot
    
    # Position sizing
    max_quantity_by_risk: int    # Based on risk amount
    max_quantity_by_entry: int   # Based on entry price (capital allocation)
    final_quantity: int          # Minimum of above two
    
    # Trade details
    total_investment: float
    actual_risk_amount: float
    actual_risk_percent: float


class RiskCalculator:
    """
    Calculate risk and position sizing based on conviction levels
    
    Features:
    - Variable risk allocation (0.25% to 2% based on conviction)
    - Support for F&O (lot-based) and Equity (share-based)
    - Dual position sizing (risk-based and entry-based)
    - Risk amount calculation
    """
    
    # Risk percentages for each conviction level (from user's Excel)
    CONVICTION_RISK_MAP = {
        ConvictionLevel.BELOW_LOW: 0.0025,   # 0.25%
        ConvictionLevel.LOW: 0.0050,         # 0.50%
        ConvictionLevel.MEDIUM: 0.0100,      # 1.00%
        ConvictionLevel.HIGH: 0.0150,        # 1.50%
        ConvictionLevel.ABOVE_HIGH: 0.0175,  # 1.75%
        ConvictionLevel.HIGHEST: 0.0200,     # 2.00%
    }
    
    def __init__(self, capital: float, max_risk_percent: float = 0.02):
        """
        Initialize Risk Calculator
        
        Args:
            capital: Total trading capital
            max_risk_percent: Maximum risk per trade (default 2%)
        """
        if capital <= 0:
            raise ValueError("Capital must be positive")
        
        if not 0 < max_risk_percent <= 0.02:
            raise ValueError("Max risk must be between 0 and 2%")
        
        self.capital = capital
        self.max_risk_percent = max_risk_percent
        
        logger.info(f"RiskCalculator initialized: Capital=₹{capital:,.2f}, MaxRisk={max_risk_percent*100}%")
    
    def get_risk_percent(self, conviction: ConvictionLevel) -> float:
        """
        Get risk percentage for a conviction level
        
        Args:
            conviction: Conviction level
            
        Returns:
            Risk percentage (as decimal, e.g., 0.01 for 1%)
        """
        return self.CONVICTION_RISK_MAP[conviction]
    
    def get_risk_amount(self, conviction: ConvictionLevel) -> float:
        """
        Calculate risk amount based on conviction level
        
        Args:
            conviction: Conviction level
            
        Returns:
            Risk amount in INR
        """
        risk_percent = self.get_risk_percent(conviction)
        risk_amount = self.capital * risk_percent
        
        logger.debug(f"Risk amount for {conviction.value}: ₹{risk_amount:,.2f} ({risk_percent*100}%)")
        return risk_amount
    
    def calculate_position_size_equity(
        self,
        entry_price: float,
        stop_loss: float,
        conviction: ConvictionLevel,
        max_position_percent: float = 0.30  # Max 30% capital in single position
    ) -> RiskAllocation:
        """
        Calculate position size for EQUITY (share-based)
        
        Args:
            entry_price: Entry price per share
            stop_loss: Stop loss price per share
            conviction: Conviction level
            max_position_percent: Maximum % of capital in single position
            
        Returns:
            RiskAllocation with all details
        """
        # Input validation
        if entry_price <= 0:
            raise ValueError("Entry price must be positive")
        
        if stop_loss <= 0:
            raise ValueError("Stop loss must be positive")
        
        if entry_price == stop_loss:
            raise ValueError("Entry price and stop loss cannot be equal")
        
        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_loss)
        
        # Get risk amount based on conviction
        risk_percent = self.get_risk_percent(conviction)
        risk_amount = self.capital * risk_percent
        
        # Calculate max shares based on RISK
        max_shares_by_risk = int(risk_amount / risk_per_share)
        
        # Calculate max shares based on ENTRY (capital allocation)
        max_investment = self.capital * max_position_percent
        max_shares_by_entry = int(max_investment / entry_price)
        
        # Final quantity = minimum of both
        final_quantity = min(max_shares_by_risk, max_shares_by_entry)
        
        if final_quantity == 0:
            logger.warning(f"Position size calculated as 0 shares. Risk per share too high or entry price too high.")
        
        # Calculate actual values
        total_investment = final_quantity * entry_price
        actual_risk_amount = final_quantity * risk_per_share
        actual_risk_percent = actual_risk_amount / self.capital if self.capital > 0 else 0
        
        allocation = RiskAllocation(
            capital=self.capital,
            conviction_level=conviction,
            risk_percent=risk_percent,
            risk_amount=risk_amount,
            entry_price=entry_price,
            stop_loss=stop_loss,
            risk_per_unit=risk_per_share,
            max_quantity_by_risk=max_shares_by_risk,
            max_quantity_by_entry=max_shares_by_entry,
            final_quantity=final_quantity,
            total_investment=total_investment,
            actual_risk_amount=actual_risk_amount,
            actual_risk_percent=actual_risk_percent
        )
        
        logger.info(
            f"EQUITY Position: {final_quantity} shares @ ₹{entry_price} | "
            f"Investment: ₹{total_investment:,.2f} | "
            f"Risk: ₹{actual_risk_amount:,.2f} ({actual_risk_percent*100:.2f}%)"
        )
        
        return allocation
    
    def calculate_position_size_fo(
        self,
        entry_price: float,
        stop_loss_points: float,
        lot_size: int,
        conviction: ConvictionLevel,
        instrument_type: InstrumentType = InstrumentType.FUTURES
    ) -> RiskAllocation:
        """
        Calculate position size for F&O (lot-based)
        
        Args:
            entry_price: Entry price per lot
            stop_loss_points: Stop loss in points (not price)
            lot_size: Standard lot size for the instrument
            conviction: Conviction level
            instrument_type: FUTURES or OPTIONS
            
        Returns:
            RiskAllocation with all details
        """
        # Input validation
        if entry_price <= 0:
            raise ValueError("Entry price must be positive")
        
        if stop_loss_points <= 0:
            raise ValueError("Stop loss points must be positive")
        
        if lot_size <= 0:
            raise ValueError("Lot size must be positive")
        
        # Calculate risk per lot
        risk_per_lot = stop_loss_points * lot_size
        
        # Get risk amount based on conviction
        risk_percent = self.get_risk_percent(conviction)
        risk_amount = self.capital * risk_percent
        
        # Calculate max lots based on RISK
        max_lots_by_risk = int(risk_amount / risk_per_lot)
        
        # For F&O, we typically don't limit by entry price
        # (margin requirements are different)
        # But we can add a max lots limit
        max_lots_by_entry = 999  # Placeholder, can be customized
        
        # Final lots = minimum of both
        final_lots = min(max_lots_by_risk, max_lots_by_entry)
        
        if final_lots == 0:
            logger.warning(f"Position size calculated as 0 lots. Risk per lot too high.")
        
        # Calculate quantity (lots * lot_size)
        final_quantity = final_lots * lot_size
        
        # Calculate actual values
        total_investment = entry_price * final_quantity  # Approximate
        actual_risk_amount = final_lots * risk_per_lot
        actual_risk_percent = actual_risk_amount / self.capital if self.capital > 0 else 0
        
        allocation = RiskAllocation(
            capital=self.capital,
            conviction_level=conviction,
            risk_percent=risk_percent,
            risk_amount=risk_amount,
            entry_price=entry_price,
            stop_loss=entry_price - stop_loss_points,  # Approximate SL price
            risk_per_unit=risk_per_lot,
            max_quantity_by_risk=max_lots_by_risk,
            max_quantity_by_entry=max_lots_by_entry,
            final_quantity=final_quantity,
            total_investment=total_investment,
            actual_risk_amount=actual_risk_amount,
            actual_risk_percent=actual_risk_percent
        )
        
        logger.info(
            f"F&O Position: {final_lots} lots ({final_quantity} qty) @ ₹{entry_price} | "
            f"Risk: ₹{actual_risk_amount:,.2f} ({actual_risk_percent*100:.2f}%)"
        )
        
        return allocation
    
    def get_conviction_summary(self) -> Dict[ConvictionLevel, Dict[str, float]]:
        """
        Get risk amounts for all conviction levels
        
        Returns:
            Dictionary with conviction levels and their risk details
        """
        summary = {}
        for conviction in ConvictionLevel:
            risk_percent = self.get_risk_percent(conviction)
            risk_amount = self.capital * risk_percent
            
            summary[conviction] = {
                'risk_percent': risk_percent * 100,  # Convert to percentage
                'risk_amount': risk_amount,
            }
        
        return summary
    
    def validate_risk_reward(
        self,
        entry_price: float,
        stop_loss: float,
        target_price: float,
        min_rr_ratio: float = 2.5
    ) -> Tuple[bool, float, str]:
        """
        Validate if trade meets minimum risk-reward ratio
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            target_price: Target price
            min_rr_ratio: Minimum acceptable risk-reward ratio
            
        Returns:
            (is_valid, actual_rr_ratio, message)
        """
        risk = abs(entry_price - stop_loss)
        reward = abs(target_price - entry_price)
        
        if risk == 0:
            return False, 0, "Risk cannot be zero"
        
        rr_ratio = reward / risk
        
        is_valid = rr_ratio >= min_rr_ratio
        message = (
            f"R:R ratio {rr_ratio:.2f}:1 {'meets' if is_valid else 'below'} "
            f"minimum {min_rr_ratio:.2f}:1"
        )
        
        logger.debug(message)
        return is_valid, rr_ratio, message


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("Risk Calculator - Conviction-Based Position Sizing")
    print("=" * 60)
    
    # Initialize calculator
    capital = 300000  # 3 lakhs
    calc = RiskCalculator(capital, max_risk_percent=0.02)
    
    print(f"\nCapital: ₹{capital:,}")
    print(f"Max Risk per Trade: 2%\n")
    
    # Show conviction levels and risk amounts
    print("Conviction Levels & Risk Allocation:")
    print("-" * 60)
    summary = calc.get_conviction_summary()
    for conviction, details in summary.items():
        print(f"{conviction.value:12s}: {details['risk_percent']:5.2f}% = ₹{details['risk_amount']:8,.2f}")
    
    print("\n" + "=" * 60)
    print("Example 1: EQUITY Position (Medium Conviction)")
    print("=" * 60)
    
    # Example: Equity trade with Medium conviction
    equity_allocation = calc.calculate_position_size_equity(
        entry_price=2500,
        stop_loss=2470,
        conviction=ConvictionLevel.MEDIUM
    )
    
    print(f"Entry: ₹{equity_allocation.entry_price}")
    print(f"Stop Loss: ₹{equity_allocation.stop_loss}")
    print(f"Risk per share: ₹{equity_allocation.risk_per_unit}")
    print(f"Conviction: {equity_allocation.conviction_level.value} ({equity_allocation.risk_percent*100}%)")
    print(f"Max shares (by risk): {equity_allocation.max_quantity_by_risk}")
    print(f"Max shares (by entry): {equity_allocation.max_quantity_by_entry}")
    print(f"Final quantity: {equity_allocation.final_quantity} shares")
    print(f"Total investment: ₹{equity_allocation.total_investment:,.2f}")
    print(f"Actual risk: ₹{equity_allocation.actual_risk_amount:,.2f} ({equity_allocation.actual_risk_percent*100:.2f}%)")
    
    print("\n" + "=" * 60)
    print("Example 2: F&O Position (High Conviction)")
    print("=" * 60)
    
    # Example: F&O trade with High conviction
    fo_allocation = calc.calculate_position_size_fo(
        entry_price=7780,
        stop_loss_points=10,
        lot_size=250,
        conviction=ConvictionLevel.HIGH,
        instrument_type=InstrumentType.FUTURES
    )
    
    print(f"Entry: ₹{fo_allocation.entry_price}")
    print(f"SL Points: 10")
    print(f"Lot Size: 250")
    print(f"Conviction: {fo_allocation.conviction_level.value} ({fo_allocation.risk_percent*100}%)")
    print(f"Risk per lot: ₹{fo_allocation.risk_per_unit:,.2f}")
    print(f"Max lots: {fo_allocation.max_quantity_by_risk}")
    print(f"Final quantity: {fo_allocation.final_quantity}")
    print(f"Actual risk: ₹{fo_allocation.actual_risk_amount:,.2f} ({fo_allocation.actual_risk_percent*100:.2f}%)")
    
    print("\n" + "=" * 60)
    print("Example 3: Risk-Reward Validation")
    print("=" * 60)
    
    # Validate R:R ratio
    is_valid, rr_ratio, message = calc.validate_risk_reward(
        entry_price=2500,
        stop_loss=2470,
        target_price=2575,
        min_rr_ratio=2.5
    )
    
    print(f"Entry: ₹2500, SL: ₹2470, Target: ₹2575")
    print(f"R:R Ratio: {rr_ratio:.2f}:1")
    print(f"Valid: {'✅ Yes' if is_valid else '❌ No'}")
    print(f"Message: {message}")
