"""
Risk Management Module

Implements conviction-based risk allocation and position sizing
for both F&O (Futures & Options) and Equity trading.
"""

from .risk_calculator import RiskCalculator, ConvictionLevel, InstrumentType

__all__ = [
    'RiskCalculator',
    'ConvictionLevel',
    'InstrumentType',
]
