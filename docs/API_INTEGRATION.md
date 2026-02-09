# Shoonya API Integration Guide

## 1. Getting Started with Shoonya API

### 1.1 Account Setup
1. Open a trading account with Finvasia (Shoonya platform): https://shoonya.com/
2. Complete KYC verification
3. Get your API credentials from the Shoonya dashboard

### 1.2 API Credentials Required
```yaml
# config/api_credentials.yaml
shoonya:
  user_id: "YOUR_USER_ID"
  password: "YOUR_PASSWORD"  # Encrypted in production
  vendor_code: "YOUR_VENDOR_CODE"
  api_key: "YOUR_API_KEY"
  imei: "abc1234"  # Can be any string for desktop apps
  
  # Optional: For automated login with TOTP
  totp_secret: "YOUR_TOTP_SECRET"  # If 2FA enabled
```

### 1.3 Install Shoonya API Library
```bash
pip install NorenRestApiPy
```

## 2. API Documentation

### 2.1 Official Documentation
- **API Docs**: https://shoonya.finvasia.com/api-documentation
- **GitHub**: https://github.com/Shoonya-Dev/ShoonyaApi-py
- **Support**: support@finvasia.com

### 2.2 Key API Endpoints

#### Authentication
```python
from NorenRestApiPy.NorenApi import NorenApi

api = NorenApi(
    host='https://api.shoonya.com/NorenWClientTP/',
    websocket='wss://api.shoonya.com/NorenWSTP/'
)

# Login
response = api.login(
    userid=user_id,
    password=password,
    twoFA=totp_token,  # Generated from TOTP secret
    vendor_code=vendor_code,
    api_secret=api_key,
    imei=imei
)
```

#### Get Market Quote
```python
# Get quote for a symbol
quote = api.get_quotes(
    exchange='NSE',
    token='2885'  # Reliance token
)

# Response format
{
    'lp': '2500.50',      # Last price
    'h': '2515.00',       # High
    'l': '2485.00',       # Low
    'o': '2490.00',       # Open
    'c': '2495.00',       # Previous close
    'v': '1234567',       # Volume
    'ltt': '15:30:00',    # Last trade time
    'bp1': '2500.00',     # Best bid price
    'bq1': '100',         # Best bid quantity
    'ap1': '2501.00',     # Best ask price
    'aq1': '50'           # Best ask quantity
}
```

#### Search for Symbols
```python
# Search for a symbol to get token
result = api.searchscrip(
    exchange='NSE',
    searchtext='RELIANCE'
)

# Response
{
    'stat': 'Ok',
    'values': [
        {
            'exch': 'NSE',
            'token': '2885',
            'tsym': 'RELIANCE-EQ',
            'instname': 'EQ',
            'pp': '2'
        }
    ]
}
```

#### Place Order
```python
# Place a market order
order = api.place_order(
    buy_or_sell='B',           # 'B' for Buy, 'S' for Sell
    product_type='I',          # 'I' for Intraday, 'C' for Delivery
    exchange='NSE',
    tradingsymbol='RELIANCE-EQ',
    quantity=10,
    discloseqty=0,
    price_type='MKT',          # 'MKT' for Market, 'LMT' for Limit
    price=0,                   # For market orders
    trigger_price=None,
    retention='DAY',
    remarks='Automated trade'
)

# Response
{
    'stat': 'Ok',
    'norenordno': '23052300012345'  # Order number
}
```

#### Place Bracket Order
```python
# Place bracket order with stop loss and target
order = api.place_order(
    buy_or_sell='B',
    product_type='I',
    exchange='NSE',
    tradingsymbol='RELIANCE-EQ',
    quantity=10,
    discloseqty=0,
    price_type='LMT',
    price=2500,
    trigger_price=None,
    retention='DAY',
    amo='NO',
    # Bracket order specific
    book_loss_price=2470,      # Stop loss
    book_profit_price=2575     # Target
)
```

#### Modify Order
```python
# Modify existing order
result = api.modify_order(
    orderno='23052300012345',
    exchange='NSE',
    tradingsymbol='RELIANCE-EQ',
    newquantity=15,            # New quantity
    newprice_type='LMT',
    newprice=2505              # New price
)
```

#### Cancel Order
```python
# Cancel order
result = api.cancel_order(
    orderno='23052300012345'
)

# Response
{
    'stat': 'Ok',
    'result': 'Order cancelled successfully'
}
```

#### Get Order Book
```python
# Get all orders for the day
orders = api.get_order_book()

# Response - list of orders
[
    {
        'norenordno': '23052300012345',
        'status': 'COMPLETE',
        'tsym': 'RELIANCE-EQ',
        'qty': '10',
        'filledqty': '10',
        'avgprc': '2500.50',
        'exch': 'NSE',
        'trantype': 'B',
        'prctyp': 'LMT',
        'prc': '2500.00',
        'rejreason': ''
    }
]
```

#### Get Positions
```python
# Get current positions
positions = api.get_positions()

# Response - list of positions
[
    {
        'exch': 'NSE',
        'tsym': 'RELIANCE-EQ',
        'netqty': '10',           # Net quantity
        'netavgprc': '2500.50',   # Average price
        'lp': '2510.00',          # Last price
        'urmtom': '95.00',        # Unrealized MTM
        'rpnl': '0.00',           # Realized P&L
        'prd': 'I'                # Product type
    }
]
```

#### Get Account Balance
```python
# Get available margin/balance
limits = api.get_limits()

# Response
{
    'stat': 'Ok',
    'cash': '100000.00',      # Available cash
    'payin': '0.00',
    'payout': '0.00',
    'brkcollamt': '0.00',
    'unclearedcash': '0.00',
    'daycash': '100000.00'
}
```

#### Get Historical Data
```python
# Get historical data
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=10)

historical_data = api.get_time_price_series(
    exchange='NSE',
    token='2885',  # Reliance
    starttime=start_date.strftime('%d-%m-%Y 09:15:00'),
    endtime=end_date.strftime('%d-%m-%Y 15:30:00'),
    interval='5'  # 1, 3, 5, 10, 15, 30, 60, etc.
)

# Response - list of candles
[
    {
        'time': '1621843200',
        'into': '1621843500',
        'inth': '2510.00',
        'intl': '2505.00',
        'intc': '2508.00',
        'intvwap': '2507.50',
        'intv': '12345',
        'intoi': '0'
    }
]
```

## 3. WebSocket for Real-Time Data

### 3.1 Subscribe to Real-Time Quotes
```python
from NorenRestApiPy.NorenApi import NorenApi

def on_open():
    print("WebSocket connected")

def on_error(error):
    print(f"Error: {error}")

def on_message(message):
    print(f"Received: {message}")
    # message format:
    # {
    #     'lp': '2500.50',  # Last price
    #     't': 'tk',        # Touchline
    #     'tk': '2885',     # Token
    #     'e': 'NSE'        # Exchange
    # }

def on_close():
    print("WebSocket closed")

# Connect to WebSocket
api.start_websocket(
    order_update_callback=on_message,
    subscribe_callback=on_open,
    socket_error_callback=on_error,
    socket_close_callback=on_close
)

# Subscribe to symbol
api.subscribe(['NSE|2885'])  # Reliance

# Subscribe to multiple symbols
api.subscribe([
    'NSE|2885',   # Reliance
    'NSE|3045',   # SBIN
    'NSE|1594'    # INFY
])

# Unsubscribe
api.unsubscribe(['NSE|2885'])
```

## 4. Common Token Numbers

```python
# NSE popular stocks
TOKENS = {
    'RELIANCE': '2885',
    'TCS': '11536',
    'INFY': '1594',
    'HDFC': '1333',
    'ICICIBANK': '4963',
    'SBIN': '3045',
    'BHARTIARTL': '10604',
    'ITC': '1660',
    'LT': '11483',
    'HDFCBANK': '1333'
}

# To get token for any symbol, use searchscrip API
```

## 5. Error Handling

### 5.1 Common Errors
```python
# 1. Session expired
if response['stat'] == 'Not_Ok' and 'session' in response['emsg'].lower():
    # Re-login
    api.login(...)

# 2. Insufficient funds
if 'insufficient' in response.get('emsg', '').lower():
    # Handle insufficient balance

# 3. Rate limit exceeded
if response['stat'] == 'Not_Ok' and 'rate limit' in response['emsg'].lower():
    # Wait and retry
    time.sleep(1)
    
# 4. Invalid order
if response['stat'] == 'Not_Ok':
    print(f"Order failed: {response['emsg']}")
```

### 5.2 Retry Logic
```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    if result.get('stat') == 'Ok':
                        return result
                    elif attempt < max_retries - 1:
                        time.sleep(delay)
                        continue
                    else:
                        return result
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        continue
                    else:
                        raise e
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=1)
def place_order_with_retry(api, **order_params):
    return api.place_order(**order_params)
```

## 6. Paper Trading / Simulation

### 6.1 Test Environment
Shoonya doesn't provide a separate paper trading environment. Options:

1. **Simulation Mode**: Track orders locally without sending to broker
2. **Small Position Size**: Trade with minimum quantity for testing
3. **Third-party simulators**: Use backtesting frameworks

### 6.2 Simulation Implementation
```python
class SimulatedShoonyaClient:
    """
    Simulated client for paper trading
    """
    def __init__(self):
        self.orders = {}
        self.positions = {}
        self.balance = 100000  # Starting capital
        
    def place_order(self, **kwargs):
        order_id = str(uuid.uuid4())
        self.orders[order_id] = {
            'order_id': order_id,
            'status': 'PENDING',
            **kwargs
        }
        return {'stat': 'Ok', 'norenordno': order_id}
        
    def get_positions(self):
        return list(self.positions.values())
        
    # ... implement other methods
```

## 7. Rate Limits

### 7.1 Shoonya API Rate Limits
- **Order APIs**: ~10 requests/second
- **Market data**: ~5 requests/second
- **WebSocket**: No limit, but use efficiently

### 7.2 Best Practices
```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()
        
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()
                
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                time.sleep(sleep_time)
                
            result = func(*args, **kwargs)
            self.calls.append(time.time())
            return result
        return wrapper

# Usage
rate_limiter = RateLimiter(max_calls=10, period=1)

@rate_limiter
def get_quote(symbol):
    return api.get_quotes(...)
```

## 8. Security Best Practices

### 8.1 Credential Storage
```python
# NEVER hardcode credentials
# NEVER commit credentials to git

# Option 1: Environment variables
import os

user_id = os.getenv('SHOONYA_USER_ID')
password = os.getenv('SHOONYA_PASSWORD')

# Option 2: Encrypted config file
from cryptography.fernet import Fernet

def load_encrypted_credentials():
    key = load_encryption_key()
    cipher = Fernet(key)
    with open('config/credentials.enc', 'rb') as f:
        encrypted = f.read()
    decrypted = cipher.decrypt(encrypted)
    return json.loads(decrypted)
```

### 8.2 TOTP for 2FA
```python
import pyotp

def generate_totp(secret):
    """Generate TOTP token from secret"""
    totp = pyotp.TOTP(secret)
    return totp.now()

# Usage
totp_token = generate_totp(totp_secret)
api.login(..., twoFA=totp_token)
```

## 9. Testing Checklist

Before going live:

- [ ] Successfully login with API
- [ ] Fetch market quotes
- [ ] Place test order (with minimum quantity)
- [ ] Cancel order
- [ ] Fetch order book
- [ ] Fetch positions
- [ ] Check account balance
- [ ] Subscribe to WebSocket feed
- [ ] Handle WebSocket disconnections
- [ ] Test error scenarios
- [ ] Test rate limiting
- [ ] Verify position reconciliation

## 10. Troubleshooting

### 10.1 Login Issues
```
Error: "Invalid credentials"
- Verify user_id, password, api_key
- Check if 2FA token is correct
- Ensure account is active

Error: "Session expired"
- Re-login before making requests
- Implement automatic re-login on session expiry
```

### 10.2 Order Issues
```
Error: "Insufficient funds"
- Check available balance with get_limits()
- Reduce position size

Error: "Symbol not found"
- Verify symbol format (e.g., 'RELIANCE-EQ')
- Use searchscrip to get correct symbol and token

Error: "Order rejected"
- Check order parameters
- Verify exchange is open
- Check for circuit limits
```

### 10.3 WebSocket Issues
```
Error: Connection drops
- Implement reconnection logic
- Re-subscribe to symbols after reconnect
- Log WebSocket errors for debugging
```

## 11. Next Steps

1. Set up Shoonya account and get API credentials
2. Test API connection with sample script
3. Implement ShoonyaClient wrapper class
4. Test all critical API endpoints
5. Implement WebSocket for real-time data
6. Add error handling and retry logic
7. Proceed with strategy implementation

For support: support@finvasia.com or Shoonya API documentation
