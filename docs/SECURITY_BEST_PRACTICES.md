# Security Best Practices - Financial Trading Platform

## CRITICAL: This is a Financial Application

Your automated trading system handles **real money**. Security breaches can lead to:
- Unauthorized trades
- Financial losses
- Account compromise
- Regulatory violations
- Data theft

**ZERO TOLERANCE for security shortcuts!**

## 1. Credential Security (HIGHEST PRIORITY)

### 1.1 Never Hardcode Credentials

❌ **NEVER DO THIS:**
```python
api_key = "abc123xyz"  # NEVER hardcode
password = "mypassword"  # NEVER hardcode
```

✅ **ALWAYS DO THIS:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENALGO_API_KEY')
```

### 1.2 Use Environment Variables

```bash
# Create .env file (NEVER commit to git)
OPENALGO_API_KEY=your_key_here
SHOONYA_API_KEY=your_key_here
SHOONYA_PASSWORD=your_password_here
```

### 1.3 Encrypt Sensitive Data

```python
from cryptography.fernet import Fernet

class CredentialManager:
    """Encrypt and store sensitive credentials"""
    
    def __init__(self, key_file='keys/.secret.key'):
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(self.key)
            os.chmod(key_file, 0o600)  # Read/write for owner only
        
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> bytes:
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted: bytes) -> str:
        return self.cipher.decrypt(encrypted).decode()

# Usage
cred_mgr = CredentialManager()
encrypted_password = cred_mgr.encrypt("my_password")
# Store encrypted_password in database
# Later retrieve and decrypt
password = cred_mgr.decrypt(encrypted_password)
```

### 1.4 Git Security

```bash
# Add to .gitignore (CRITICAL)
cat >> .gitignore << 'EOF'
# Credentials and Secrets
.env
*.key
*.pem
config/credentials.yaml
keys/
**/api_credentials*

# Logs (may contain sensitive data)
logs/
*.log

# Database (contains sensitive data)
*.db
*.sqlite
*.duckdb

# Backup files
*.bak
*~

# macOS
.DS_Store

# Python
__pycache__/
*.pyc
venv/
.venv/
EOF

# Verify nothing sensitive is tracked
git status
```

## 2. API Key Management

### 2.1 Rotate Keys Regularly

```python
# Implement key rotation
import datetime

class APIKeyManager:
    def __init__(self, db):
        self.db = db
        self.key_lifetime_days = 90
    
    def is_key_expired(self, key_created_date):
        age = datetime.datetime.now() - key_created_date
        return age.days > self.key_lifetime_days
    
    def rotate_key_if_needed(self, current_key):
        key_info = self.db.get_key_info(current_key)
        if self.is_key_expired(key_info['created_at']):
            # Generate new key from OpenAlgo
            # Update your application config
            # Revoke old key
            logger.warning("API key rotated due to age")
```

### 2.2 Store Keys Securely

```python
# Store API keys with permissions
config = {
    'openalgo_api_key': os.getenv('OPENALGO_API_KEY'),
    'key_permissions': ['read', 'trade'],  # Principle of least privilege
    'key_created': datetime.datetime.now(),
    'key_expires': datetime.datetime.now() + datetime.timedelta(days=90)
}
```

## 3. Network Security

### 3.1 Localhost Only (Development)

```python
# .env configuration
FLASK_HOST_IP = '127.0.0.1'  # NOT 0.0.0.0
WEBSOCKET_HOST = '127.0.0.1'

# Only accessible from your machine
```

### 3.2 Firewall Rules (Production)

```bash
# If you must expose OpenAlgo remotely:

# 1. Use UFW (Ubuntu) or similar firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from YOUR_IP_ADDRESS to any port 5000
sudo ufw enable

# 2. Or use SSH tunnel instead
ssh -L 5000:localhost:5000 user@server
# Access via localhost:5000 on your machine
```

### 3.3 HTTPS/SSL (Production)

```bash
# Use nginx as reverse proxy with SSL
sudo apt install nginx certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Nginx config
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3.4 VPN Access (Recommended for Remote)

```bash
# Set up WireGuard VPN for secure remote access
# Only allow trading system access via VPN
# This is the MOST SECURE approach for remote access
```

## 4. Database Security

### 4.1 Encrypt Sensitive Fields

```python
from sqlalchemy import Column, String, LargeBinary
from cryptography.fernet import Fernet

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String)  # OK to store plain
    entry_price = Column(Float)  # OK to store plain
    
    # Sensitive fields - encrypt
    broker_order_id = Column(LargeBinary)  # Encrypted
    notes = Column(LargeBinary)  # Encrypted (may contain strategy details)
    
    def set_broker_order_id(self, value, cipher):
        self.broker_order_id = cipher.encrypt(value.encode())
    
    def get_broker_order_id(self, cipher):
        return cipher.decrypt(self.broker_order_id).decode()
```

### 4.2 Regular Backups

```bash
#!/bin/bash
# backup_databases.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/Users/pshekarappa/pravn27/ASTA/backups"

mkdir -p "$BACKUP_DIR"

# Backup OpenAlgo database
cp /Users/pshekarappa/pravn27/ASTA/openalgo/db/openalgo.db \
   "$BACKUP_DIR/openalgo_$DATE.db"

# Backup your trading database
cp /Users/pshekarappa/pravn27/ASTA/stock-market-automate-trades/data/trades.db \
   "$BACKUP_DIR/trades_$DATE.db"

# Encrypt backups
openssl enc -aes-256-cbc -salt -pbkdf2 \
    -in "$BACKUP_DIR/openalgo_$DATE.db" \
    -out "$BACKUP_DIR/openalgo_$DATE.db.enc" \
    -k "your_backup_password"

# Delete old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.db.enc" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### 4.3 Database Permissions

```bash
# Restrict database file access
chmod 600 db/openalgo.db
chmod 600 data/trades.db

# Only owner can read/write
```

## 5. Audit Logging (MANDATORY for Financial Apps)

### 5.1 Log Everything

```python
import logging
from datetime import datetime

class AuditLogger:
    """Comprehensive audit trail for all trading activities"""
    
    def __init__(self, log_file='logs/audit.log'):
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)
        
        # File handler with rotation
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=100*1024*1024,  # 100MB
            backupCount=10
        )
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_trade(self, action, details):
        """Log every trade action"""
        self.logger.info(f"TRADE | {action} | {details}")
    
    def log_order(self, order_type, order_details):
        """Log order placement"""
        self.logger.info(f"ORDER | {order_type} | {order_details}")
    
    def log_risk_check(self, result, reason):
        """Log risk management decisions"""
        self.logger.info(f"RISK | {result} | {reason}")
    
    def log_system_event(self, event, details):
        """Log system events"""
        self.logger.info(f"SYSTEM | {event} | {details}")
    
    def log_error(self, error, context):
        """Log errors without exposing sensitive data"""
        sanitized_error = self._sanitize(str(error))
        self.logger.error(f"ERROR | {sanitized_error} | {context}")
    
    def _sanitize(self, message):
        """Remove sensitive data from logs"""
        # Remove API keys, passwords, etc.
        import re
        message = re.sub(r'api[_-]?key[=:]\s*\S+', 'api_key=REDACTED', message, flags=re.IGNORECASE)
        message = re.sub(r'password[=:]\s*\S+', 'password=REDACTED', message, flags=re.IGNORECASE)
        message = re.sub(r'token[=:]\s*\S+', 'token=REDACTED', message, flags=re.IGNORECASE)
        return message

# Usage
audit = AuditLogger()

# Log trade execution
audit.log_trade('BUY', {
    'symbol': 'RELIANCE',
    'quantity': 50,
    'entry': 2500,
    'sl': 2470,
    'target': 2575
})

# Log risk checks
audit.log_risk_check('APPROVED', 'All risk checks passed')
audit.log_risk_check('REJECTED', 'Daily loss limit reached')

# Log system events
audit.log_system_event('STARTUP', 'Trading engine started')
audit.log_system_event('POSITION_MONITOR', 'SL hit for RELIANCE')
```

### 5.2 Log Retention

```bash
# Keep logs for regulatory compliance (minimum 1 year for financial data)
# India: SEBI requires 5 years for trading records

# Automated log rotation and archiving
LOG_RETENTION_DAYS=1825  # 5 years
```

## 6. Input Validation (Prevent Injection Attacks)

### 6.1 Validate All Inputs

```python
import re
from typing import Optional

class InputValidator:
    """Validate all user inputs to prevent injection attacks"""
    
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """Validate stock symbol"""
        if not symbol or len(symbol) > 20:
            return False
        # Only alphanumeric and dash
        return bool(re.match(r'^[A-Z0-9-]+$', symbol))
    
    @staticmethod
    def validate_quantity(quantity: int) -> bool:
        """Validate order quantity"""
        return isinstance(quantity, int) and 1 <= quantity <= 10000
    
    @staticmethod
    def validate_price(price: float) -> bool:
        """Validate price"""
        return isinstance(price, (int, float)) and 0 < price < 1000000
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 100) -> str:
        """Remove potentially dangerous characters"""
        if not input_str:
            return ""
        # Remove control characters, SQL injection attempts
        sanitized = re.sub(r'[^\w\s-]', '', input_str)
        return sanitized[:max_length]

# Usage
validator = InputValidator()

def place_order(symbol, quantity, price):
    # Validate before processing
    if not validator.validate_symbol(symbol):
        raise ValueError(f"Invalid symbol: {symbol}")
    
    if not validator.validate_quantity(quantity):
        raise ValueError(f"Invalid quantity: {quantity}")
    
    if not validator.validate_price(price):
        raise ValueError(f"Invalid price: {price}")
    
    # Safe to proceed
    return openalgo.place_order(...)
```

## 7. Error Handling (Don't Leak Sensitive Info)

### 7.1 Safe Error Messages

```python
class SafeErrorHandler:
    """Handle errors without exposing sensitive information"""
    
    @staticmethod
    def handle_error(error: Exception, context: str) -> dict:
        """Return safe error message to user, log details internally"""
        
        # Log full error internally
        logger.error(f"{context}: {str(error)}", exc_info=True)
        
        # Return generic message to user
        if isinstance(error, ValueError):
            return {
                'status': 'error',
                'message': 'Invalid input provided',
                'code': 'INVALID_INPUT'
            }
        elif isinstance(error, PermissionError):
            return {
                'status': 'error',
                'message': 'Insufficient permissions',
                'code': 'PERMISSION_DENIED'
            }
        else:
            # Never expose internal error details
            return {
                'status': 'error',
                'message': 'An error occurred. Please contact support.',
                'code': 'INTERNAL_ERROR',
                'reference': generate_error_id()  # For support tracking
            }
```

## 8. Rate Limiting & Abuse Prevention

### 8.1 Implement Circuit Breakers

```python
class TradingCircuitBreaker:
    """Prevent runaway trading and abuse"""
    
    def __init__(self):
        self.max_orders_per_minute = 10
        self.max_daily_loss = 0.03  # 3%
        self.max_position_value = 0.30  # 30% of capital
        self.order_timestamps = []
        self.daily_loss = 0.0
    
    def check_order_rate(self) -> Tuple[bool, str]:
        """Prevent order spam"""
        now = datetime.datetime.now()
        # Remove old timestamps
        self.order_timestamps = [
            ts for ts in self.order_timestamps
            if (now - ts).seconds < 60
        ]
        
        if len(self.order_timestamps) >= self.max_orders_per_minute:
            return False, "Order rate limit exceeded"
        
        return True, "OK"
    
    def check_daily_loss(self, account_balance) -> Tuple[bool, str]:
        """Stop trading if daily loss limit reached"""
        loss_percent = abs(self.daily_loss) / account_balance
        
        if loss_percent >= self.max_daily_loss:
            return False, f"Daily loss limit reached: {loss_percent:.2%}"
        
        return True, "OK"
    
    def emergency_stop(self):
        """Emergency stop all trading"""
        logger.critical("EMERGENCY STOP TRIGGERED")
        # Close all positions
        # Cancel all pending orders
        # Disable new orders
        # Send alerts
```

## 9. Two-Factor Authentication (2FA)

### 9.2 Implement TOTP for Critical Operations

```python
import pyotp

class TwoFactorAuth:
    """Require 2FA for critical operations"""
    
    def __init__(self, secret):
        self.totp = pyotp.TOTP(secret)
    
    def verify_totp(self, token: str) -> bool:
        """Verify TOTP token"""
        return self.totp.verify(token, valid_window=1)
    
    def require_2fa(self, func):
        """Decorator to require 2FA for function"""
        def wrapper(*args, **kwargs):
            token = input("Enter 2FA code: ")
            if not self.verify_totp(token):
                raise PermissionError("Invalid 2FA code")
            return func(*args, **kwargs)
        return wrapper

# Usage: Require 2FA for emergency stops, withdrawals, etc.
```

## 10. Monitoring & Alerting

### 10.1 Real-time Security Monitoring

```python
class SecurityMonitor:
    """Monitor for suspicious activities"""
    
    def __init__(self):
        self.failed_login_attempts = {}
        self.unusual_order_patterns = []
    
    def detect_brute_force(self, ip_address):
        """Detect brute force login attempts"""
        if ip_address not in self.failed_login_attempts:
            self.failed_login_attempts[ip_address] = []
        
        # Add timestamp
        self.failed_login_attempts[ip_address].append(datetime.datetime.now())
        
        # Check if >5 attempts in last 5 minutes
        recent_attempts = [
            t for t in self.failed_login_attempts[ip_address]
            if (datetime.datetime.now() - t).seconds < 300
        ]
        
        if len(recent_attempts) > 5:
            # Block IP, send alert
            logger.warning(f"Brute force detected from {ip_address}")
            self.send_alert(f"Security: Brute force attack from {ip_address}")
    
    def detect_unusual_trading(self, order):
        """Detect unusual trading patterns"""
        # Check for:
        # - Orders outside normal trading hours
        # - Unusually large orders
        # - Rapid order modifications
        # - Orders to unusual symbols
        pass
```

## 11. Testing in Sandbox First

### 11.1 Never Test with Real Money

```python
class TradingMode(Enum):
    SANDBOX = "sandbox"  # Test mode, no real orders
    PAPER = "paper"      # Simulated with real market data
    LIVE = "live"        # Real money

# Configuration
config = {
    'mode': TradingMode.SANDBOX,  # Start here
    'allow_live_trading': False    # Require explicit enable
}

def place_order(order):
    if config['mode'] == TradingMode.SANDBOX:
        logger.info("SANDBOX MODE: Order simulated")
        return simulate_order(order)
    
    elif config['mode'] == TradingMode.PAPER:
        logger.info("PAPER TRADING: Order simulated with real prices")
        return paper_trade(order)
    
    elif config['mode'] == TradingMode.LIVE:
        if not config['allow_live_trading']:
            raise PermissionError("Live trading not enabled")
        
        # Require confirmation
        confirm = input("LIVE TRADING: Execute real order? (yes/no): ")
        if confirm.lower() != 'yes':
            return None
        
        return execute_real_order(order)
```

## 12. Security Checklist

### Pre-Deployment Checklist

- [ ] All credentials stored in environment variables
- [ ] `.gitignore` configured (no credentials in git)
- [ ] Strong random keys generated (not default values)
- [ ] Database encrypted and backed up
- [ ] Audit logging enabled (5-year retention)
- [ ] Rate limiting configured
- [ ] CSRF protection enabled
- [ ] Input validation on all user inputs
- [ ] Error handling doesn't leak sensitive info
- [ ] Network restricted (localhost or VPN)
- [ ] HTTPS enabled (if remote access)
- [ ] 2FA enabled for Shoonya account
- [ ] Circuit breakers implemented
- [ ] Emergency stop tested
- [ ] Tested in sandbox mode first
- [ ] Monitoring and alerts configured
- [ ] Backup and recovery tested
- [ ] Incident response plan documented

### Regular Security Maintenance

**Daily:**
- [ ] Review audit logs
- [ ] Check for unauthorized access
- [ ] Verify system health

**Weekly:**
- [ ] Review trade logs for anomalies
- [ ] Test backup restoration
- [ ] Check for software updates

**Monthly:**
- [ ] Rotate API keys
- [ ] Review and update firewall rules
- [ ] Security audit
- [ ] Test disaster recovery

**Quarterly:**
- [ ] Full security assessment
- [ ] Penetration testing
- [ ] Review and update security policies

## 13. Compliance & Regulations

### 13.1 Data Retention (India - SEBI)

```python
# SEBI Requirements for Indian markets:
# - Trade records: 5 years
# - Account statements: 5 years
# - Audit trails: 5 years

LOG_RETENTION_DAYS = 1825  # 5 years
BACKUP_RETENTION_DAYS = 1825
```

### 13.2 Risk Disclosures

Always include risk disclaimers:
- Trading involves substantial risk of loss
- Past performance doesn't guarantee future results
- Only trade with risk capital
- Understand the risks before trading

## Final Words

**Security is NOT optional for financial applications!**

- Always assume you're a target
- Defense in depth (multiple security layers)
- Principle of least privilege
- Test everything twice
- When in doubt, be conservative
- **NEVER skip security for convenience**

Remember: One security breach can wipe out years of profits!
