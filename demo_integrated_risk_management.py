#!/usr/bin/env python3
"""
Integrated Risk Management Demo

Demonstrates how Risk Calculator and Portfolio Manager work together
to enforce comprehensive risk controls for automated trading.

Shows:
1. Risk Calculator: Conviction-based position sizing
2. Portfolio Manager: Portfolio-level limits enforcement
3. Integration: End-to-end trade workflow with multi-layer risk checks
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from risk_management import (
    RiskCalculator,
    ConvictionLevel,
    PortfolioRiskManager,
    Position
)


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_trade_details(trade_num: int, symbol: str, entry: float, sl: float, target: float):
    """Print trade details"""
    print(f"\n📊 Trade #{trade_num}: {symbol}")
    print(f"   Entry: ₹{entry}")
    print(f"   Stop Loss: ₹{sl}")
    print(f"   Target: ₹{target}")


def main():
    print_header("INTEGRATED RISK MANAGEMENT SYSTEM DEMO")
    print("\n🎯 User Configuration:")
    print("   Capital: ₹3,00,000")
    print("   Max Daily Loss: 2%")
    print("   Max Positions: 3")
    print("   Max Trades/Day: 3")
    print("   Min Risk:Reward: 1:2.5")
    
    # Initialize components with user's parameters
    capital = 300000
    risk_calc = RiskCalculator(capital=capital)
    portfolio = PortfolioRiskManager(
        capital=capital,
        max_positions=3,
        max_daily_loss_percent=0.02,  # 2%
        max_trades_per_day=3
    )
    
    # ========================================================================
    # TRADE 1: RELIANCE - High Conviction F&O Trade
    # ========================================================================
    print_header("TRADE 1: RELIANCE FEB FUTURES - HIGH CONVICTION")
    
    trade1 = {
        'symbol': 'RELIANCE FEB FUT',
        'entry_price': 2500,
        'stop_loss_points': 20,  # ATR-based (tighter SL for demo)
        'lot_size': 100,  # Smaller lot size for demo
        'conviction': ConvictionLevel.HIGH,
        'sector': 'Energy'
    }
    
    print_trade_details(1, trade1['symbol'], trade1['entry_price'], 
                       trade1['entry_price'] - trade1['stop_loss_points'],
                       trade1['entry_price'] + (trade1['stop_loss_points'] * 2.5))
    
    # Step 1: Calculate position size
    print("\n📐 STEP 1: Risk Calculator - Position Sizing")
    allocation = risk_calc.calculate_position_size_fo(
        entry_price=trade1['entry_price'],
        stop_loss_points=trade1['stop_loss_points'],
        lot_size=trade1['lot_size'],
        conviction=trade1['conviction']
    )
    
    print(f"   Conviction: {trade1['conviction'].value.upper()} → {allocation.risk_percent*100}% risk")
    print(f"   Risk Amount: ₹{allocation.risk_amount:,.2f}")
    lots = allocation.final_quantity // trade1['lot_size'] if allocation.final_quantity > 0 else 0
    print(f"   Lots: {lots}")
    print(f"   Quantity: {allocation.final_quantity}")
    print(f"   Position Value: ₹{allocation.total_investment:,.2f}")
    
    # Step 2: Validate risk-reward
    print("\n✅ STEP 2: Validate Risk-Reward Ratio")
    target_price = trade1['entry_price'] + (trade1['stop_loss_points'] * 2.5)
    is_valid_rr, actual_rr_ratio, rr_message = risk_calc.validate_risk_reward(
        entry_price=trade1['entry_price'],
        stop_loss=trade1['entry_price'] - trade1['stop_loss_points'],
        target_price=target_price
    )
    risk_per_unit = abs(trade1['entry_price'] - (trade1['entry_price'] - trade1['stop_loss_points']))
    reward_per_unit = abs(target_price - trade1['entry_price'])
    print(f"   Risk: ₹{risk_per_unit:.2f}")
    print(f"   Reward: ₹{reward_per_unit:.2f}")
    print(f"   Risk:Reward = 1:{actual_rr_ratio:.2f}")
    print(f"   Valid: {'✅ YES' if is_valid_rr else '❌ NO'}")
    
    # Step 3: Portfolio-level checks
    print("\n🛡️  STEP 3: Portfolio Manager - Pre-Trade Checks")
    can_trade, reason = portfolio.can_take_trade(
        symbol=trade1['symbol'],
        estimated_position_value=allocation.total_investment,
        sector=trade1['sector']
    )
    print(f"   Can Trade: {'✅ YES' if can_trade else '❌ NO'}")
    print(f"   Reason: {reason}")
    
    # Step 4: Execute trade
    if can_trade and is_valid_rr and allocation.final_quantity > 0:
        print("\n✅ TRADE APPROVED - Executing...")
        position1 = Position(
            symbol=trade1['symbol'],
            quantity=allocation.final_quantity,
            entry_price=trade1['entry_price'],
            current_price=trade1['entry_price'],
            stop_loss=trade1['entry_price'] - trade1['stop_loss_points'],
            target=target_price,
            pnl=0,
            entry_time=datetime.now(),
            sector=trade1['sector']
        )
        portfolio.add_position(position1)
        print(f"   Order placed: BUY {allocation.final_quantity} {trade1['symbol']} @ ₹{trade1['entry_price']}")
    
    # Show portfolio status
    portfolio.print_summary()
    
    # ========================================================================
    # TRADE 2: TCS - Medium Conviction Equity Trade
    # ========================================================================
    print_header("TRADE 2: TCS EQUITY - MEDIUM CONVICTION")
    
    trade2 = {
        'symbol': 'TCS',
        'entry_price': 3500,
        'stop_loss': 3465,  # Support-based
        'target': 3587,
        'conviction': ConvictionLevel.MEDIUM,
        'sector': 'IT'
    }
    
    print_trade_details(2, trade2['symbol'], trade2['entry_price'], 
                       trade2['stop_loss'], trade2['target'])
    
    # Step 1: Calculate position size
    print("\n📐 STEP 1: Risk Calculator - Position Sizing")
    allocation2 = risk_calc.calculate_position_size_equity(
        entry_price=trade2['entry_price'],
        stop_loss=trade2['stop_loss'],
        conviction=trade2['conviction']
    )
    
    print(f"   Conviction: {trade2['conviction'].value.upper()} → {allocation2.risk_percent*100}% risk")
    print(f"   Risk Amount: ₹{allocation2.risk_amount:,.2f}")
    print(f"   Shares: {allocation2.final_quantity}")
    print(f"   Position Value: ₹{allocation2.total_investment:,.2f}")
    
    # Step 2: Validate risk-reward
    print("\n✅ STEP 2: Validate Risk-Reward Ratio")
    is_valid_rr2, actual_rr_ratio2, rr_message2 = risk_calc.validate_risk_reward(
        entry_price=trade2['entry_price'],
        stop_loss=trade2['stop_loss'],
        target_price=trade2['target']
    )
    risk_per_unit2 = abs(trade2['entry_price'] - trade2['stop_loss'])
    reward_per_unit2 = abs(trade2['target'] - trade2['entry_price'])
    print(f"   Risk: ₹{risk_per_unit2:.2f}")
    print(f"   Reward: ₹{reward_per_unit2:.2f}")
    print(f"   Risk:Reward = 1:{actual_rr_ratio2:.2f}")
    print(f"   Valid: {'✅ YES' if is_valid_rr2 else '❌ NO'}")
    
    # Step 3: Portfolio-level checks
    print("\n🛡️  STEP 3: Portfolio Manager - Pre-Trade Checks")
    can_trade2, reason2 = portfolio.can_take_trade(
        symbol=trade2['symbol'],
        estimated_position_value=allocation2.total_investment,
        sector=trade2['sector']
    )
    print(f"   Can Trade: {'✅ YES' if can_trade2 else '❌ NO'}")
    print(f"   Reason: {reason2}")
    
    # Step 4: Execute trade
    if can_trade2 and is_valid_rr2:
        print("\n✅ TRADE APPROVED - Executing...")
        position2 = Position(
            symbol=trade2['symbol'],
            quantity=allocation2.final_quantity,
            entry_price=trade2['entry_price'],
            current_price=trade2['entry_price'],
            stop_loss=trade2['stop_loss'],
            target=trade2['target'],
            pnl=0,
            entry_time=datetime.now(),
            sector=trade2['sector']
        )
        portfolio.add_position(position2)
        print(f"   Order placed: BUY {allocation2.final_quantity} {trade2['symbol']} @ ₹{trade2['entry_price']}")
    
    # Show portfolio status
    portfolio.print_summary()
    
    # ========================================================================
    # TRADE 3: INFY - Try Third Trade (Should be limited by capital or hit max)
    # ========================================================================
    print_header("TRADE 3: INFY EQUITY - LOW CONVICTION")
    
    trade3 = {
        'symbol': 'INFY',
        'entry_price': 1600,
        'stop_loss': 1580,
        'target': 1650,
        'conviction': ConvictionLevel.LOW,
        'sector': 'IT'
    }
    
    print_trade_details(3, trade3['symbol'], trade3['entry_price'], 
                       trade3['stop_loss'], trade3['target'])
    
    # Step 1: Calculate position size
    print("\n📐 STEP 1: Risk Calculator - Position Sizing")
    allocation3 = risk_calc.calculate_position_size_equity(
        entry_price=trade3['entry_price'],
        stop_loss=trade3['stop_loss'],
        conviction=trade3['conviction']
    )
    
    print(f"   Conviction: {trade3['conviction'].value.upper()} → {allocation3.risk_percent*100}% risk")
    print(f"   Risk Amount: ₹{allocation3.risk_amount:,.2f}")
    print(f"   Shares: {allocation3.final_quantity}")
    print(f"   Position Value: ₹{allocation3.total_investment:,.2f}")
    
    # Step 2: Validate risk-reward
    print("\n✅ STEP 2: Validate Risk-Reward Ratio")
    is_valid_rr3, actual_rr_ratio3, rr_message3 = risk_calc.validate_risk_reward(
        entry_price=trade3['entry_price'],
        stop_loss=trade3['stop_loss'],
        target_price=trade3['target']
    )
    risk_per_unit3 = abs(trade3['entry_price'] - trade3['stop_loss'])
    reward_per_unit3 = abs(trade3['target'] - trade3['entry_price'])
    print(f"   Risk: ₹{risk_per_unit3:.2f}")
    print(f"   Reward: ₹{reward_per_unit3:.2f}")
    print(f"   Risk:Reward = 1:{actual_rr_ratio3:.2f}")
    print(f"   Valid: {'✅ YES' if is_valid_rr3 else '❌ NO'}")
    
    # Step 3: Portfolio-level checks (likely to fail - insufficient capital or correlation)
    print("\n🛡️  STEP 3: Portfolio Manager - Pre-Trade Checks")
    can_trade3, reason3 = portfolio.can_take_trade(
        symbol=trade3['symbol'],
        estimated_position_value=allocation3.total_investment,
        sector=trade3['sector']
    )
    print(f"   Can Trade: {'✅ YES' if can_trade3 else '❌ NO'}")
    print(f"   Reason: {reason3}")
    
    if can_trade3 and is_valid_rr3:
        # Check correlation before trade
        is_correlated, corr_reason = portfolio.check_correlation(trade3['symbol'])
        if is_correlated:
            print(f"\n⚠️  CORRELATION WARNING: {corr_reason}")
            print("   Trade blocked due to correlation risk")
        else:
            print("\n✅ TRADE APPROVED - Executing...")
            position3 = Position(
                symbol=trade3['symbol'],
                quantity=allocation3.final_quantity,
                entry_price=trade3['entry_price'],
                current_price=trade3['entry_price'],
                stop_loss=trade3['stop_loss'],
                target=trade3['target'],
                pnl=0,
                entry_time=datetime.now(),
                sector=trade3['sector']
            )
            portfolio.add_position(position3)
            print(f"   Order placed: BUY {allocation3.final_quantity} {trade3['symbol']} @ ₹{trade3['entry_price']}")
    else:
        print(f"\n❌ TRADE REJECTED: {reason3}")
    
    # Show final portfolio status
    portfolio.print_summary()
    
    # ========================================================================
    # TRADE 4: Attempt Fourth Trade (Should be REJECTED)
    # ========================================================================
    print_header("TRADE 4: HDFCBANK - Should be REJECTED")
    
    trade4 = {
        'symbol': 'HDFCBANK',
        'entry_price': 1650,
        'stop_loss': 1630,
        'target': 1700,
        'conviction': ConvictionLevel.HIGH,
        'sector': 'Banking'
    }
    
    print_trade_details(4, trade4['symbol'], trade4['entry_price'], 
                       trade4['stop_loss'], trade4['target'])
    
    print("\n🛡️  Portfolio Manager - Pre-Trade Checks")
    allocation4 = risk_calc.calculate_position_size_equity(
        entry_price=trade4['entry_price'],
        stop_loss=trade4['stop_loss'],
        conviction=trade4['conviction']
    )
    
    can_trade4, reason4 = portfolio.can_take_trade(
        symbol=trade4['symbol'],
        estimated_position_value=allocation4.total_investment,
        sector=trade4['sector']
    )
    
    print(f"   Can Trade: {'✅ YES' if can_trade4 else '❌ NO'}")
    print(f"   Reason: {reason4}")
    
    if not can_trade4:
        print(f"\n❌ TRADE REJECTED: {reason4}")
        print("   Protection working as designed!")
    
    # ========================================================================
    # SIMULATE TRADE EXIT: Close RELIANCE with loss
    # ========================================================================
    print_header("SIMULATE EXIT: RELIANCE Hits Stop Loss")
    
    print(f"\n📉 Market moves against us - RELIANCE hits stop loss")
    print(f"   Entry: ₹{trade1['entry_price']}")
    print(f"   Exit: ₹{trade1['entry_price'] - trade1['stop_loss_points']}")
    
    portfolio.update_position_price(
        trade1['symbol'], 
        trade1['entry_price'] - trade1['stop_loss_points']
    )
    portfolio.remove_position(
        trade1['symbol'], 
        trade1['entry_price'] - trade1['stop_loss_points'],
        'SL_HIT'
    )
    
    portfolio.print_summary()
    
    # Check if can still trade after loss
    print("\n🔍 Can we take another trade after this loss?")
    can_trade_after_loss, reason_after_loss = portfolio.can_take_trade(
        symbol='SBIN',
        estimated_position_value=50000
    )
    print(f"   Result: {'✅ YES' if can_trade_after_loss else '❌ NO'}")
    print(f"   Reason: {reason_after_loss}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_header("RISK MANAGEMENT SYSTEM SUMMARY")
    
    print("\n✅ MULTI-LAYER RISK PROTECTION DEMONSTRATED:")
    print("\n1️⃣  Risk Calculator Layer:")
    print("   ✓ Conviction-based position sizing (0.25% to 2% risk)")
    print("   ✓ Separate calculations for Equity (shares) and F&O (lots)")
    print("   ✓ Risk-Reward validation (min 1:2.5)")
    print("   ✓ Dynamic position size based on stop loss distance")
    
    print("\n2️⃣  Portfolio Manager Layer:")
    print("   ✓ Maximum 3 concurrent positions enforced")
    print("   ✓ Maximum 3 trades per day enforced")
    print("   ✓ 2% daily loss limit monitoring")
    print("   ✓ Capital availability checks")
    print("   ✓ Sector exposure limits")
    print("   ✓ Correlation detection")
    
    print("\n3️⃣  Automated Protection:")
    print("   ✓ Emotions eliminated - rules enforced automatically")
    print("   ✓ Overtrading prevented")
    print("   ✓ Capital preserved")
    print("   ✓ Consistent risk per trade")
    
    final_summary = portfolio.get_portfolio_summary()
    print(f"\n📊 Final Stats:")
    print(f"   Trades Taken: {final_summary['trades_today']}/{final_summary['max_trades_per_day']}")
    print(f"   Active Positions: {final_summary['active_positions']}/{final_summary['max_positions']}")
    print(f"   Daily P&L: ₹{final_summary['net_daily_pnl']:,.2f}")
    print(f"   Daily Loss: {final_summary['daily_loss_percent']:.2f}% / {final_summary['daily_loss_limit_percent']:.2f}%")
    print(f"   Risk Remaining: {final_summary['risk_remaining_percent']:.2f}%")
    
    print("\n" + "=" * 80)
    print(" ✅ INTEGRATED RISK MANAGEMENT DEMO COMPLETE")
    print(" 🎯 Your trading is now emotionless and rule-based!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
