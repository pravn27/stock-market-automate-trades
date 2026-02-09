# Stock Market Automated Trading System

## Overview
An emotion-free, rule-based automated trading system that uses **OpenAlgo** as the infrastructure layer for broker connectivity, with custom risk management and strategy logic.

## Core Objectives
1. **Strict Risk Management**: Enforce stop loss and minimum 1:2.5 Risk-Reward ratio
2. **Emotion-Free Trading**: Automated execution based on predefined rules
3. **Money Management**: Strict position sizing and capital allocation rules

## Key Features
- **OpenAlgo Integration**: Unified API for multi-broker support (Shoonya/Finvasia and 25+ others)
- **Custom Risk Management Layer**: Enforces strict risk and money management rules
- **TradingView Integration**: Webhook-based signal reception via OpenAlgo
- **Rule-based Trade Validation**: Pre-trade checks before execution
- **Automatic Stop Loss & Target Management**: ATR-based and custom methods
- **Real-time Monitoring**: Position tracking and alerts
- **Comprehensive Logging**: Trade journal and performance analytics
- **Position Sizing Calculator**: Risk-based position sizing

## Documentation
- [System Architecture](docs/ARCHITECTURE.md) - High-level system design with OpenAlgo
- [Component Design](docs/COMPONENT_DESIGN.md) - Low-level component details
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) - Step-by-step implementation guide
- [Trading Rules](docs/TRADING_RULES.md) - Risk and money management rules
- [OpenAlgo Integration](docs/OPENALGO_INTEGRATION.md) - OpenAlgo setup and usage

## Technology Stack
- **Language**: Python 3.10+
- **Infrastructure**: OpenAlgo (Self-hosted, Open Source)
- **Trading Platform**: Shoonya (Finvasia) via OpenAlgo (supports 25+ brokers)
- **Technical Analysis**: TradingView via webhooks / pandas-ta
- **Database**: SQLite (development) / PostgreSQL (production)
- **Monitoring**: Logging + Telegram notifications (via OpenAlgo)

## Project Structure
```
stock-market-automate-trades/
├── src/
│   ├── openalgo/         # OpenAlgo API client wrapper
│   ├── strategy/         # Trading strategies and rules
│   ├── risk_management/  # Risk and money management (CORE)
│   ├── validation/       # Pre-trade validation engine
│   ├── monitoring/       # System monitoring and alerts
│   └── utils/            # Helper utilities
├── config/               # Configuration files
├── tests/                # Unit and integration tests
├── docs/                 # Documentation
├── logs/                 # Application logs
└── data/                 # Historical data and backtests
```

## Why OpenAlgo?

✅ **Saves 2-3 weeks** of API integration development  
✅ **Battle-tested** broker integrations used by 90,000+ traders  
✅ **Multi-broker support** - Switch from Shoonya to any of 25+ brokers easily  
✅ **TradingView Ready** - Built-in webhook receiver  
✅ **Self-hosted** - Complete control and privacy  
✅ **Open Source** - Transparent, community-driven  
✅ **Active Community** - 1200+ GitHub stars, Discord support

## Getting Started
See [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) for detailed setup instructions.

## Safety & Disclaimer
- Always test with paper trading first
- Start with small position sizes
- Monitor the system continuously
- Have manual override capabilities
- This system does not guarantee profits
- Trading involves substantial risk
