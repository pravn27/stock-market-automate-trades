#!/usr/bin/env python3
"""
TradingView Webhook Server

Flask application that receives TradingView webhooks and processes trades.

Endpoints:
- POST /webhook - Receive TradingView alerts
- GET /health - Health check
- GET /status - System status
"""

from flask import Flask, request, jsonify
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from strategy.webhook_handler import WebhookHandler
from strategy.strategy_validator import StrategyValidator
from risk_management import RiskCalculator, PortfolioRiskManager

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize components
capital = float(os.getenv('INITIAL_CAPITAL', 300000))
webhook_api_key = os.getenv('WEBHOOK_API_KEY', 'CHANGE_THIS_KEY')
webhook_secret = os.getenv('WEBHOOK_SECRET', '')

# Risk Calculator
risk_calc = RiskCalculator(capital=capital)

# Portfolio Manager
portfolio = PortfolioRiskManager(
    capital=capital,
    max_positions=int(os.getenv('MAX_POSITIONS', 3)),
    max_daily_loss_percent=float(os.getenv('MAX_DAILY_LOSS_PERCENT', 0.02)),
    max_trades_per_day=int(os.getenv('MAX_TRADES_PER_DAY', 3))
)

# Webhook Handler
webhook_handler = WebhookHandler(
    api_key=webhook_api_key,
    webhook_secret=webhook_secret,
    rate_limit_per_minute=60
)

# Strategy Validator
strategy_validator = StrategyValidator(
    risk_calculator=risk_calc,
    portfolio_manager=portfolio,
    min_rr_ratio=float(os.getenv('MIN_RISK_REWARD_RATIO', 2.5))
)

logger.info("=" * 80)
logger.info(" WEBHOOK SERVER INITIALIZED")
logger.info("=" * 80)
logger.info(f"Capital: ₹{capital:,.2f}")
logger.info(f"Max Positions: {portfolio.max_positions}")
logger.info(f"Daily Loss Limit: {portfolio.max_daily_loss_percent*100}%")
logger.info(f"Max Trades/Day: {portfolio.max_trades_per_day}")
logger.info(f"Min R:R Ratio: {strategy_validator.min_rr_ratio}")
logger.info("=" * 80)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Trading Webhook Server'
    }), 200


@app.route('/status', methods=['GET'])
def system_status():
    """System status endpoint"""
    try:
        portfolio_summary = portfolio.get_portfolio_summary()
        
        return jsonify({
            'status': 'online',
            'timestamp': datetime.now().isoformat(),
            'capital': capital,
            'portfolio': {
                'active_positions': portfolio_summary['active_positions'],
                'max_positions': portfolio_summary['max_positions'],
                'trades_today': portfolio_summary['trades_today'],
                'max_trades_per_day': portfolio_summary['max_trades_per_day'],
                'daily_pnl': portfolio_summary['net_daily_pnl'],
                'daily_loss_percent': portfolio_summary['daily_loss_percent'],
                'daily_loss_limit_percent': portfolio_summary['daily_loss_limit_percent'],
                'can_trade_more': portfolio_summary['can_trade_more']
            },
            'risk_management': {
                'max_risk_percent': 2.0,  # Max 2% risk per trade
                'min_rr_ratio': strategy_validator.min_rr_ratio
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/webhook', methods=['POST'])
def receive_webhook():
    """
    Receive TradingView webhook
    
    Expected JSON payload:
    {
        "symbol": "RELIANCE",
        "exchange": "NSE",
        "action": "BUY",
        "price": 2500.50,
        "stop_loss": 2470.00,
        "target": 2575.00,
        "conviction": "MEDIUM",
        "timeframe": "15m",
        "strategy": "BB_MTF",
        "api_key": "your_webhook_api_key"
    }
    """
    try:
        # Get request data
        payload = request.get_json()
        
        if not payload:
            logger.warning("Empty webhook payload received")
            return jsonify({
                'success': False,
                'error': 'Empty payload'
            }), 400
        
        # Get headers
        api_key = request.headers.get('X-API-Key')
        signature = request.headers.get('X-Signature')
        client_ip = request.remote_addr
        
        logger.info(f"\n{'='*80}")
        logger.info(f" WEBHOOK RECEIVED from {client_ip}")
        logger.info(f"{'='*80}")
        logger.info(f"Payload: {payload}")
        
        # Step 1: Parse and validate webhook
        success, signal, message = webhook_handler.parse_webhook(
            payload=payload,
            provided_api_key=api_key,
            signature=signature,
            ip_address=client_ip
        )
        
        if not success:
            logger.warning(f"❌ Webhook validation failed: {message}")
            return jsonify({
                'success': False,
                'error': message
            }), 403
        
        logger.info(f"✅ Webhook validated: {signal.action.value} {signal.symbol}")
        
        # Step 2: Validate trade through strategy validator
        decision = strategy_validator.validate_trade(signal)
        
        if not decision.approved:
            logger.warning(f"❌ Trade rejected: {decision.reason}")
            return jsonify({
                'success': False,
                'approved': False,
                'reason': decision.reason,
                'signal': signal.to_dict(),
                'timestamp': datetime.now().isoformat()
            }), 200
        
        # Trade approved!
        logger.info(
            f"\n{'='*80}\n"
            f" ✅ TRADE APPROVED FOR EXECUTION\n"
            f"{'='*80}\n"
            f" Symbol: {signal.symbol}\n"
            f" Action: {signal.action.value}\n"
            f" Quantity: {decision.position_size}\n"
            f" Entry: ₹{signal.price}\n"
            f" Stop Loss: ₹{signal.stop_loss}\n"
            f" Target: ₹{signal.target}\n"
            f" Investment: ₹{decision.investment_amount:,.2f}\n"
            f" Risk: ₹{decision.risk_amount:,.2f} ({decision.risk_percent*100:.2f}%)\n"
            f" R:R Ratio: 1:{decision.risk_reward_ratio:.2f}\n"
            f"{'='*80}"
        )
        
        # TODO: Execute trade via OpenAlgo (Component 6)
        # For now, just return approval
        
        return jsonify({
            'success': True,
            'approved': True,
            'reason': decision.reason,
            'signal': signal.to_dict(),
            'trade_details': {
                'position_size': decision.position_size,
                'investment_amount': decision.investment_amount,
                'risk_amount': decision.risk_amount,
                'risk_percent': decision.risk_percent * 100,
                'risk_reward_ratio': decision.risk_reward_ratio
            },
            'note': 'Trade approved - Order execution via OpenAlgo coming in Component 6',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/test', methods=['GET'])
def test_webhook():
    """
    Test endpoint to simulate a webhook
    """
    sample_webhook = {
        "symbol": "TCS",
        "exchange": "NSE",
        "action": "BUY",
        "price": 3500,
        "stop_loss": 3462.5,
        "target": 3593.75,
        "conviction": "MEDIUM",
        "timeframe": "15m",
        "strategy": "BB_MTF_TEST",
        "api_key": webhook_api_key
    }
    
    return jsonify({
        'message': 'Sample webhook payload',
        'webhook': sample_webhook,
        'instructions': 'POST this to /webhook endpoint'
    }), 200


if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Get configuration
    host = os.getenv('WEBHOOK_HOST', '0.0.0.0')
    port = int(os.getenv('WEBHOOK_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"\n{'='*80}")
    logger.info(f" Starting webhook server on {host}:{port}")
    logger.info(f" Debug mode: {debug}")
    logger.info(f"{'='*80}\n")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )
