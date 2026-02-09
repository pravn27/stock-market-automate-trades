# OpenAlgo Integration Guide

## 1. What is OpenAlgo?

[OpenAlgo](https://www.openalgo.in/) is India's first community-driven, self-hosted algorithmic trading platform that provides:

- ✅ **Unified API** for 25+ Indian brokers
- ✅ **Self-hosted** infrastructure (your server, your control)
- ✅ **Open Source** (AGPL-3.0 licensed)
- ✅ **TradingView Integration** via webhooks
- ✅ **Multi-language SDKs** (Python, Node.js, Java, Go, Rust, .NET)
- ✅ **Built-in Telegram notifications**
- ✅ **90,000+ downloads, 1200+ GitHub stars**

## 2. Architecture Overview

```
Your Custom App ←→ OpenAlgo (localhost:5000) ←→ Shoonya/Finvasia
```

**What OpenAlgo Handles:**
- Broker authentication and session management
- Order placement, modification, cancellation
- Position and order book fetching
- TradingView webhook reception
- Rate limiting and error handling
- Multi-broker abstraction

**What You Build:**
- Risk management logic (1%, 2.5:1 RR, etc.)
- Position sizing calculations
- Pre-trade validation
- Position monitoring
- Trade journal and analytics

## 3. Installation & Setup

### 3.1 Install OpenAlgo (Docker - Recommended)

```bash
# Clone OpenAlgo repository
git clone https://github.com/marketcalls/openalgo.git
cd openalgo

# Start OpenAlgo with Docker
docker-compose up -d

# OpenAlgo will be running at http://localhost:5000
```

### 3.2 Alternative: Manual Installation

```bash
# Clone repository
git clone https://github.com/marketcalls/openalgo.git
cd openalgo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure database
flask db upgrade

# Run OpenAlgo
python app.py
```

### 3.3 Access OpenAlgo Dashboard

1. Open browser: http://localhost:5000
2. Create admin account (first time)
3. Configure broker connection (Shoonya/Finvasia)

## 4. Broker Configuration (Shoonya/Finvasia)

### 4.1 Add Shoonya Broker in OpenAlgo

1. Log in to OpenAlgo dashboard
2. Go to **Settings** → **Broker Configuration**
3. Select **Finvasia (Shoonya)**
4. Enter credentials:
   - User ID
   - Password
   - API Key
   - Vendor Code
   - TOTP Secret (if 2FA enabled)

### 4.2 Test Connection

```bash
# From OpenAlgo dashboard, click "Test Connection"
# Should show: ✅ Connected to Shoonya
```

## 5. OpenAlgo API Reference

### 5.1 Base URL
```
http://localhost:5000/api/v1
```

### 5.2 Authentication

OpenAlgo uses API keys for authentication:

```python
headers = {
    'Authorization': 'Bearer YOUR_OPENALGO_API_KEY',
    'Content-Type': 'application/json'
}
```

**Get API Key:**
- Go to OpenAlgo Dashboard → Settings → API Keys
- Generate new API key
- Save it securely

### 5.3 Key API Endpoints

#### Place Order
```python
POST /api/v1/placeorder

Request:
{
    "apikey": "your_api_key",
    "strategy": "MyStrategy",
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "action": "BUY",          # BUY or SELL
    "quantity": "50",
    "price": "0",             # 0 for market order
    "product": "MIS",         # MIS (intraday) or CNC (delivery)
    "pricetype": "MARKET",    # MARKET or LIMIT
    "ordertype": "REGULAR"    # REGULAR or BRACKET or COVER
}

Response:
{
    "status": "success",
    "orderid": "230523000123456"
}
```

#### Place Bracket Order (with SL & Target)
```python
POST /api/v1/placeorder

Request:
{
    "apikey": "your_api_key",
    "strategy": "MyStrategy",
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "action": "BUY",
    "quantity": "50",
    "price": "2500",
    "product": "MIS",
    "pricetype": "LIMIT",
    "ordertype": "BRACKET",
    "stoploss": "2470",       # Stop loss price
    "target": "2575"          # Target price
}
```

#### Modify Order
```python
POST /api/v1/modifyorder

Request:
{
    "apikey": "your_api_key",
    "orderid": "230523000123456",
    "quantity": "60",
    "price": "2505"
}
```

#### Cancel Order
```python
POST /api/v1/cancelorder

Request:
{
    "apikey": "your_api_key",
    "orderid": "230523000123456"
}
```

#### Get Positions
```python
POST /api/v1/positions

Request:
{
    "apikey": "your_api_key"
}

Response:
{
    "status": "success",
    "data": [
        {
            "symbol": "RELIANCE",
            "exchange": "NSE",
            "product": "MIS",
            "quantity": "50",
            "average_price": "2500.50",
            "ltp": "2510.00",
            "pnl": "475.00",
            "netqty": "50"
        }
    ]
}
```

#### Get Order Book
```python
POST /api/v1/orderbook

Request:
{
    "apikey": "your_api_key"
}

Response:
{
    "status": "success",
    "data": [
        {
            "orderid": "230523000123456",
            "symbol": "RELIANCE",
            "action": "BUY",
            "quantity": "50",
            "price": "2500",
            "status": "COMPLETE",
            "filled_quantity": "50",
            "average_price": "2500.50"
        }
    ]
}
```

#### Get Quote
```python
POST /api/v1/quotes

Request:
{
    "apikey": "your_api_key",
    "symbol": "RELIANCE",
    "exchange": "NSE"
}

Response:
{
    "status": "success",
    "data": {
        "symbol": "RELIANCE",
        "ltp": "2510.00",
        "open": "2490.00",
        "high": "2515.00",
        "low": "2485.00",
        "close": "2495.00",
        "volume": "1234567"
    }
}
```

#### Get Account Balance
```python
POST /api/v1/funds

Request:
{
    "apikey": "your_api_key"
}

Response:
{
    "status": "success",
    "data": {
        "availablecash": "100000.00",
        "usedmargin": "50000.00",
        "collateral": "0.00"
    }
}
```

## 6. Python SDK Usage

### 6.1 Install OpenAlgo Python SDK

```bash
pip install openalgo
```

### 6.2 Basic Usage

```python
from openalgo import api

# Initialize client
client = api.OpenAlgoClient(
    api_key='your_openalgo_api_key',
    host='http://localhost:5000'
)

# Place order
order = client.placeorder(
    strategy='MyStrategy',
    symbol='RELIANCE',
    exchange='NSE',
    action='BUY',
    quantity=50,
    price=0,
    product='MIS',
    pricetype='MARKET',
    ordertype='REGULAR'
)

print(f"Order placed: {order['orderid']}")

# Get positions
positions = client.positions()
for pos in positions['data']:
    print(f"{pos['symbol']}: {pos['quantity']} @ {pos['average_price']}")

# Get quotes
quote = client.quotes(symbol='RELIANCE', exchange='NSE')
print(f"LTP: {quote['data']['ltp']}")

# Cancel order
client.cancelorder(orderid='230523000123456')
```

### 6.3 Complete Example with Error Handling

```python
from openalgo import api
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAlgo client
client = api.OpenAlgoClient(
    api_key='your_api_key',
    host='http://localhost:5000'
)

def place_bracket_order(symbol, action, quantity, entry, sl, target):
    """
    Place bracket order via OpenAlgo
    """
    try:
        order = client.placeorder(
            strategy='AutomatedTrading',
            symbol=symbol,
            exchange='NSE',
            action=action,
            quantity=quantity,
            price=entry,
            product='MIS',
            pricetype='LIMIT',
            ordertype='BRACKET',
            stoploss=sl,
            target=target
        )
        
        if order.get('status') == 'success':
            logger.info(f"Order placed successfully: {order['orderid']}")
            return order['orderid']
        else:
            logger.error(f"Order failed: {order.get('message')}")
            return None
            
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return None

def get_current_positions():
    """
    Fetch current positions from OpenAlgo
    """
    try:
        response = client.positions()
        if response.get('status') == 'success':
            return response.get('data', [])
        return []
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        return []

def exit_position(symbol, quantity):
    """
    Exit a position via market order
    """
    try:
        # Determine action (opposite of position)
        positions = get_current_positions()
        position = next((p for p in positions if p['symbol'] == symbol), None)
        
        if not position:
            logger.warning(f"No position found for {symbol}")
            return False
            
        action = 'SELL' if int(position['netqty']) > 0 else 'BUY'
        
        order = client.placeorder(
            strategy='AutomatedTrading',
            symbol=symbol,
            exchange='NSE',
            action=action,
            quantity=abs(quantity),
            price=0,
            product='MIS',
            pricetype='MARKET',
            ordertype='REGULAR'
        )
        
        if order.get('status') == 'success':
            logger.info(f"Position exited: {symbol}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error exiting position: {e}")
        return False

# Example usage
if __name__ == '__main__':
    # Place bracket order
    order_id = place_bracket_order(
        symbol='RELIANCE',
        action='BUY',
        quantity=50,
        entry=2500,
        sl=2470,
        target=2575
    )
    
    # Check positions
    positions = get_current_positions()
    for pos in positions:
        print(f"{pos['symbol']}: {pos['netqty']} @ {pos['average_price']}, P&L: {pos['pnl']}")
```

## 7. TradingView Webhook Integration

### 7.1 Configure Webhook in OpenAlgo

1. Go to OpenAlgo Dashboard → Settings → Webhooks
2. Copy webhook URL: `http://localhost:5000/api/v1/webhook`
3. Configure allowed strategies

### 7.2 TradingView Alert Setup

Create alert in TradingView with webhook:

**Webhook URL:**
```
http://your-server-ip:5000/api/v1/webhook
```

**Message (JSON):**
```json
{
    "apikey": "your_openalgo_api_key",
    "strategy": "TrendFollowing",
    "symbol": "{{ticker}}",
    "exchange": "NSE",
    "action": "{{strategy.order.action}}",
    "quantity": "50",
    "price": "{{close}}",
    "product": "MIS",
    "pricetype": "LIMIT"
}
```

### 7.3 Process Webhook in Your Application

```python
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/webhook/tradingview', methods=['POST'])
def tradingview_webhook():
    """
    Receive TradingView webhook, validate, and forward to OpenAlgo
    """
    data = request.json
    
    # 1. Validate signal
    if not validate_signal(data):
        return {'status': 'rejected', 'reason': 'Invalid signal'}, 400
    
    # 2. Calculate risk parameters
    entry = float(data['price'])
    sl, target = calculate_sl_target(data['symbol'], entry, data['action'])
    
    # 3. Check risk management rules
    if not check_risk_rules(data['symbol'], entry, sl, target):
        return {'status': 'rejected', 'reason': 'Risk rules not met'}, 400
    
    # 4. Calculate position size
    quantity = calculate_position_size(entry, sl)
    
    # 5. Place order via OpenAlgo
    order = place_order_via_openalgo(
        symbol=data['symbol'],
        action=data['action'],
        quantity=quantity,
        entry=entry,
        sl=sl,
        target=target
    )
    
    return {'status': 'success', 'orderid': order['orderid']}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

## 8. Supported Brokers

OpenAlgo supports 25+ brokers. Check if Shoonya/Finvasia is supported:

- ✅ Finvasia (Shoonya) - **SUPPORTED**
- Zerodha
- Angel One
- Upstox
- 5Paisa
- ICICI Direct
- And 20+ more...

[Full broker list](https://github.com/marketcalls/openalgo#supported-brokers)

## 9. Security Best Practices

### 9.1 API Key Security

```python
# NEVER hardcode API keys
# Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()

OPENALGO_API_KEY = os.getenv('OPENALGO_API_KEY')
OPENALGO_HOST = os.getenv('OPENALGO_HOST', 'http://localhost:5000')
```

### 9.2 Network Security

```bash
# If running OpenAlgo on remote server:
# 1. Use HTTPS (SSL certificate)
# 2. Restrict access with firewall
# 3. Use VPN for additional security

# Example: UFW firewall rules
sudo ufw allow from YOUR_IP to any port 5000
sudo ufw enable
```

### 9.3 Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_second=5):
    """Rate limiter decorator"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=5)
def place_order(symbol, action, quantity):
    return client.placeorder(...)
```

## 10. Testing OpenAlgo Setup

### 10.1 Pre-Flight Checklist

```bash
# 1. Check if OpenAlgo is running
curl http://localhost:5000/api/v1/health

# 2. Test authentication
curl -X POST http://localhost:5000/api/v1/funds \
  -H "Content-Type: application/json" \
  -d '{"apikey": "your_api_key"}'

# 3. Test quote fetch
curl -X POST http://localhost:5000/api/v1/quotes \
  -H "Content-Type: application/json" \
  -d '{"apikey": "your_api_key", "symbol": "RELIANCE", "exchange": "NSE"}'
```

### 10.2 Test Script

```python
from openalgo import api

def test_openalgo_connection():
    """Test OpenAlgo setup"""
    
    client = api.OpenAlgoClient(
        api_key='your_api_key',
        host='http://localhost:5000'
    )
    
    print("Testing OpenAlgo connection...")
    
    # Test 1: Get funds
    try:
        funds = client.funds()
        print(f"✅ Funds: {funds['data']['availablecash']}")
    except Exception as e:
        print(f"❌ Funds test failed: {e}")
        return False
    
    # Test 2: Get quote
    try:
        quote = client.quotes(symbol='RELIANCE', exchange='NSE')
        print(f"✅ Quote: RELIANCE @ {quote['data']['ltp']}")
    except Exception as e:
        print(f"❌ Quote test failed: {e}")
        return False
    
    # Test 3: Get positions
    try:
        positions = client.positions()
        print(f"✅ Positions: {len(positions['data'])} active")
    except Exception as e:
        print(f"❌ Positions test failed: {e}")
        return False
    
    print("\n✅ All tests passed! OpenAlgo is ready.")
    return True

if __name__ == '__main__':
    test_openalgo_connection()
```

## 11. Troubleshooting

### Common Issues

**Issue 1: Connection refused**
```
Solution: Check if OpenAlgo is running
docker ps  # Should show openalgo container
```

**Issue 2: Invalid API key**
```
Solution: Generate new API key from OpenAlgo dashboard
Settings → API Keys → Generate New
```

**Issue 3: Broker not connected**
```
Solution: Check broker configuration in OpenAlgo
Settings → Broker Configuration → Test Connection
```

**Issue 4: Order rejected by broker**
```
Solution: Check:
- Sufficient balance
- Correct symbol format
- Market hours
- Order parameters
```

## 12. Next Steps

1. ✅ Install OpenAlgo
2. ✅ Configure Shoonya broker
3. ✅ Test connection with test script
4. ✅ Get API key
5. ✅ Test placing and canceling orders
6. ➡️ Build your risk management layer on top

## 13. Resources

- **OpenAlgo Website**: https://www.openalgo.in/
- **GitHub Repository**: https://github.com/marketcalls/openalgo
- **Documentation**: https://docs.openalgo.in/
- **Discord Community**: https://discord.gg/openalgo
- **YouTube Tutorials**: Search "OpenAlgo tutorial"

OpenAlgo handles the infrastructure - you focus on the strategy and risk management! 🚀
