#!/usr/bin/env python3
"""
Component 5: Strategy Validator - TradingView Webhook Handler

Receives and validates trading signals from TradingView webhooks.
Integrates with Risk Calculator and Portfolio Manager for trade approval.

Security features:
- API key authentication
- Request signature validation
- IP whitelisting (optional)
- Rate limiting
- Input sanitization
"""

import json
import hmac
import hashlib
import logging
from datetime import datetime
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import os

logger = logging.getLogger(__name__)


class TradeAction(Enum):
    """Trading actions"""
    BUY = "BUY"
    SELL = "SELL"
    CLOSE = "CLOSE"
    CLOSE_ALL = "CLOSE_ALL"


class OrderType(Enum):
    """Order types"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"


@dataclass
class TradingSignal:
    """
    Trading signal from TradingView
    
    Expected webhook JSON format:
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
        "timestamp": "2026-02-09T10:30:00",
        "api_key": "your_webhook_api_key"
    }
    """
    symbol: str
    exchange: str
    action: TradeAction
    price: float
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    conviction: str = "MEDIUM"
    timeframe: str = "15m"
    strategy: str = "UNKNOWN"
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate signal data"""
        if not self.symbol or len(self.symbol) == 0:
            raise ValueError("Symbol is required")
        
        if self.price <= 0:
            raise ValueError("Price must be positive")
        
        if self.stop_loss and self.stop_loss <= 0:
            raise ValueError("Stop loss must be positive")
        
        if self.target and self.target <= 0:
            raise ValueError("Target must be positive")
        
        # Validate conviction level
        valid_convictions = ['BELOW_LOW', 'LOW', 'MEDIUM', 'HIGH', 'ABOVE_HIGH', 'HIGHEST']
        if self.conviction.upper() not in valid_convictions:
            logger.warning(f"Invalid conviction {self.conviction}, defaulting to MEDIUM")
            self.conviction = "MEDIUM"
        
        # Normalize
        self.symbol = self.symbol.upper().strip()
        self.exchange = self.exchange.upper().strip()
        self.conviction = self.conviction.upper()
    
    @classmethod
    def from_json(cls, data: Dict) -> 'TradingSignal':
        """Create TradingSignal from JSON webhook data"""
        try:
            # Parse action
            action_str = data.get('action', '').upper()
            action = TradeAction[action_str] if action_str in TradeAction.__members__ else TradeAction.BUY
            
            # Parse timestamp
            timestamp_str = data.get('timestamp')
            timestamp = None
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()
            
            return cls(
                symbol=data['symbol'],
                exchange=data.get('exchange', 'NSE'),
                action=action,
                price=float(data['price']),
                stop_loss=float(data['stop_loss']) if data.get('stop_loss') else None,
                target=float(data['target']) if data.get('target') else None,
                conviction=data.get('conviction', 'MEDIUM'),
                timeframe=data.get('timeframe', '15m'),
                strategy=data.get('strategy', 'UNKNOWN'),
                timestamp=timestamp
            )
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid value in webhook data: {e}")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'exchange': self.exchange,
            'action': self.action.value,
            'price': self.price,
            'stop_loss': self.stop_loss,
            'target': self.target,
            'conviction': self.conviction,
            'timeframe': self.timeframe,
            'strategy': self.strategy,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class WebhookHandler:
    """
    Handles TradingView webhook requests
    
    Security:
    - API key authentication
    - Request signature validation (HMAC-SHA256)
    - Rate limiting (max requests per minute)
    - IP whitelisting (optional)
    """
    
    def __init__(
        self,
        api_key: str,
        webhook_secret: Optional[str] = None,
        allowed_ips: Optional[list] = None,
        rate_limit_per_minute: int = 60,
        validate_signatures: bool = True
    ):
        """
        Initialize webhook handler
        
        Args:
            api_key: API key for authentication
            webhook_secret: Secret for HMAC signature validation
            allowed_ips: List of allowed IP addresses (None = allow all)
            rate_limit_per_minute: Max requests per minute
            validate_signatures: Enable signature validation
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.webhook_secret = webhook_secret or os.getenv('WEBHOOK_SECRET', '')
        self.allowed_ips = allowed_ips or []
        self.rate_limit_per_minute = rate_limit_per_minute
        self.validate_signatures = validate_signatures
        
        # Rate limiting tracking
        self.request_timestamps = []
        
        logger.info(
            f"WebhookHandler initialized: "
            f"Signature validation: {validate_signatures}, "
            f"Rate limit: {rate_limit_per_minute}/min"
        )
    
    def validate_api_key(self, provided_key: str) -> bool:
        """
        Validate API key
        
        Args:
            provided_key: API key from request
            
        Returns:
            True if valid, False otherwise
        """
        return hmac.compare_digest(self.api_key, provided_key)
    
    def validate_signature(self, payload: str, signature: str) -> bool:
        """
        Validate HMAC-SHA256 signature
        
        Args:
            payload: Request payload (JSON string)
            signature: Provided signature
            
        Returns:
            True if valid, False otherwise
        """
        if not self.validate_signatures or not self.webhook_secret:
            return True
        
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def check_rate_limit(self) -> Tuple[bool, str]:
        """
        Check if request is within rate limit
        
        Returns:
            (allowed, reason)
        """
        now = datetime.now()
        
        # Remove timestamps older than 1 minute
        self.request_timestamps = [
            ts for ts in self.request_timestamps
            if (now - ts).total_seconds() < 60
        ]
        
        if len(self.request_timestamps) >= self.rate_limit_per_minute:
            return False, f"Rate limit exceeded: {self.rate_limit_per_minute} requests/minute"
        
        # Add current timestamp
        self.request_timestamps.append(now)
        return True, "OK"
    
    def check_ip_whitelist(self, ip_address: str) -> Tuple[bool, str]:
        """
        Check if IP is whitelisted
        
        Args:
            ip_address: Client IP address
            
        Returns:
            (allowed, reason)
        """
        if not self.allowed_ips:
            return True, "OK"
        
        if ip_address in self.allowed_ips:
            return True, "OK"
        
        return False, f"IP {ip_address} not whitelisted"
    
    def validate_request(
        self,
        payload: Dict,
        provided_api_key: Optional[str] = None,
        signature: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Validate incoming webhook request
        
        Args:
            payload: Request payload (dict)
            provided_api_key: API key from request
            signature: Request signature
            ip_address: Client IP address
            
        Returns:
            (valid, reason)
        """
        # Check 1: Rate limit
        allowed, reason = self.check_rate_limit()
        if not allowed:
            logger.warning(f"Rate limit check failed: {reason}")
            return False, reason
        
        # Check 2: IP whitelist
        if ip_address:
            allowed, reason = self.check_ip_whitelist(ip_address)
            if not allowed:
                logger.warning(f"IP whitelist check failed: {reason}")
                return False, reason
        
        # Check 3: API key
        api_key = provided_api_key or payload.get('api_key')
        if not api_key:
            logger.warning("API key missing in request")
            return False, "API key required"
        
        if not self.validate_api_key(api_key):
            logger.warning("Invalid API key provided")
            return False, "Invalid API key"
        
        # Check 4: Signature (if enabled)
        if self.validate_signatures and signature:
            payload_str = json.dumps(payload, sort_keys=True)
            if not self.validate_signature(payload_str, signature):
                logger.warning("Invalid signature")
                return False, "Invalid signature"
        
        return True, "OK"
    
    def parse_webhook(
        self,
        payload: Dict,
        provided_api_key: Optional[str] = None,
        signature: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[bool, Optional[TradingSignal], str]:
        """
        Parse and validate webhook payload
        
        Args:
            payload: Webhook payload
            provided_api_key: API key from header
            signature: Request signature from header
            ip_address: Client IP
            
        Returns:
            (success, signal, message)
        """
        try:
            # Validate request
            valid, reason = self.validate_request(payload, provided_api_key, signature, ip_address)
            if not valid:
                return False, None, reason
            
            # Parse signal
            signal = TradingSignal.from_json(payload)
            
            logger.info(
                f"✅ Webhook parsed: {signal.action.value} {signal.symbol} @ ₹{signal.price} "
                f"(Conviction: {signal.conviction}, Strategy: {signal.strategy})"
            )
            
            return True, signal, "Signal parsed successfully"
            
        except ValueError as e:
            logger.error(f"Invalid webhook data: {e}")
            return False, None, f"Invalid data: {str(e)}"
        except Exception as e:
            logger.error(f"Error parsing webhook: {e}")
            return False, None, f"Error: {str(e)}"
    
    def create_sample_webhook(self) -> Dict:
        """
        Create sample webhook payload for testing
        
        Returns:
            Sample webhook JSON
        """
        return {
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "action": "BUY",
            "price": 2500.50,
            "stop_loss": 2470.00,
            "target": 2575.00,
            "conviction": "MEDIUM",
            "timeframe": "15m",
            "strategy": "BB_MTF",
            "timestamp": datetime.now().isoformat(),
            "api_key": self.api_key
        }


if __name__ == "__main__":
    # Demo webhook handler
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 80)
    print(" WEBHOOK HANDLER DEMO")
    print("=" * 80)
    
    # Initialize handler
    handler = WebhookHandler(
        api_key="test_api_key_12345",
        webhook_secret="test_secret",
        rate_limit_per_minute=10
    )
    
    print("\n📋 Configuration:")
    print(f"  API Key: {handler.api_key}")
    print(f"  Rate Limit: {handler.rate_limit_per_minute}/min")
    print(f"  Signature Validation: {handler.validate_signatures}")
    
    # Test 1: Valid webhook
    print("\n" + "=" * 80)
    print(" TEST 1: Valid Webhook")
    print("=" * 80)
    
    sample_webhook = handler.create_sample_webhook()
    print(f"\n📥 Incoming webhook:")
    print(json.dumps(sample_webhook, indent=2))
    
    success, signal, message = handler.parse_webhook(sample_webhook)
    
    print(f"\n✅ Result: {message}")
    if signal:
        print(f"\n📊 Parsed Signal:")
        print(f"  Symbol: {signal.symbol}")
        print(f"  Action: {signal.action.value}")
        print(f"  Entry: ₹{signal.price}")
        print(f"  Stop Loss: ₹{signal.stop_loss}")
        print(f"  Target: ₹{signal.target}")
        print(f"  Conviction: {signal.conviction}")
        print(f"  Strategy: {signal.strategy}")
    
    # Test 2: Invalid API key
    print("\n" + "=" * 80)
    print(" TEST 2: Invalid API Key")
    print("=" * 80)
    
    invalid_webhook = sample_webhook.copy()
    invalid_webhook['api_key'] = "wrong_key"
    
    success, signal, message = handler.parse_webhook(invalid_webhook)
    print(f"\n❌ Result: {message}")
    
    # Test 3: Missing required field
    print("\n" + "=" * 80)
    print(" TEST 3: Missing Required Field")
    print("=" * 80)
    
    incomplete_webhook = sample_webhook.copy()
    del incomplete_webhook['symbol']
    
    success, signal, message = handler.parse_webhook(incomplete_webhook)
    print(f"\n❌ Result: {message}")
    
    # Test 4: Rate limiting
    print("\n" + "=" * 80)
    print(" TEST 4: Rate Limiting")
    print("=" * 80)
    
    print(f"\nSending {handler.rate_limit_per_minute + 5} requests...")
    blocked_count = 0
    
    for i in range(handler.rate_limit_per_minute + 5):
        success, signal, message = handler.parse_webhook(sample_webhook)
        if not success and "Rate limit" in message:
            blocked_count += 1
    
    print(f"\n✅ Blocked {blocked_count} requests due to rate limiting")
    
    # Test 5: Different actions
    print("\n" + "=" * 80)
    print(" TEST 5: Different Actions")
    print("=" * 80)
    
    for action in ['BUY', 'SELL', 'CLOSE']:
        test_webhook = sample_webhook.copy()
        test_webhook['action'] = action
        test_webhook['symbol'] = f"TEST_{action}"
        
        success, signal, message = handler.parse_webhook(test_webhook)
        if success:
            print(f"\n✅ {action}: {signal.symbol} @ ₹{signal.price}")
    
    print("\n" + "=" * 80)
    print(" ✅ WEBHOOK HANDLER DEMO COMPLETE")
    print("=" * 80)
