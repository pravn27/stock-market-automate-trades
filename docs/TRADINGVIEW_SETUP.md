# TradingView Webhook Setup Guide

## Overview

This guide shows you how to connect TradingView alerts to your automated trading system. When TradingView detects your strategy signal, it will send a webhook to your server, which will automatically validate and execute the trade.

## Architecture

```
TradingView Alert
       ↓
   (Webhook)
       ↓
Your Webhook Server (localhost:5001)
       ↓
   Validation Pipeline:
   1. Webhook Handler → Parse & Authenticate
   2. Risk Calculator → Position Sizing
   3. Portfolio Manager → Check Limits
       ↓
   Decision: APPROVE or REJECT
       ↓
   (If approved)
       ↓
OpenAlgo → Shoonya → Trade Executed
```

## Prerequisites

1. **TradingView Premium Account** (required for webhooks)
2. **Webhook Server Running** on your machine
3. **OpenAlgo Setup** (completed in Phase 0)
4. **Shoonya API Credentials** configured in OpenAlgo

## Step 1: Configure Webhook API Key

### Generate Secure API Key

```bash
# Generate a secure webhook API key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Update `.env` File

Edit `/Users/pshekarappa/pravn27/ASTA/stock-market-automate-trades/.env`:

```bash
# Replace this with your generated key
WEBHOOK_API_KEY=your_generated_secure_key_here

# Optional: Add webhook secret for signature validation
WEBHOOK_SECRET=your_optional_secret_here

# Server configuration
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=5001
```

## Step 2: Start Webhook Server

### Start Server

```bash
cd /Users/pshekarappa/pravn27/ASTA/stock-market-automate-trades
python3 src/webhook_server.py
```

You should see:

```
================================================================================
 WEBHOOK SERVER INITIALIZED
================================================================================
Capital: ₹300,000.00
Max Positions: 3
Daily Loss Limit: 2.0%
Max Trades/Day: 3
Min R:R Ratio: 2.5
================================================================================

 * Running on http://127.0.0.1:5001
```

### Test Server (Optional)

```bash
# Health check
curl http://localhost:5001/health

# System status
curl http://localhost:5001/status

# Test webhook
curl -X POST http://localhost:5001/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "TCS",
    "exchange": "NSE",
    "action": "BUY",
    "price": 3500,
    "stop_loss": 3462.5,
    "target": 3593.75,
    "conviction": "MEDIUM",
    "api_key": "your_webhook_api_key"
  }'
```

## Step 3: Expose Webhook to Internet

Your webhook server needs to be accessible from TradingView's servers. You have several options:

### Option A: ngrok (Recommended for Testing)

```bash
# Install ngrok
brew install ngrok

# Start ngrok tunnel
ngrok http 5001
```

You'll get a public URL like: `https://abc123.ngrok.io`

Your webhook URL will be: `https://abc123.ngrok.io/webhook`

### Option B: Port Forwarding (For Home Network)

1. Log into your router
2. Forward external port 5001 to your machine's IP:5001
3. Get your public IP: `curl ifconfig.me`
4. Webhook URL: `http://YOUR_PUBLIC_IP:5001/webhook`

⚠️ **Security Note:** Use HTTPS in production!

### Option C: Cloud Server (Production)

Deploy to DigitalOcean, AWS, or similar:
- Upload your code
- Start webhook server
- Use domain with SSL certificate
- Webhook URL: `https://your-domain.com/webhook`

## Step 4: Configure TradingView Pine Script

### Your Strategy Code

Add this to your TradingView Pine Script:

```pine
//@version=5
strategy("Your Strategy", overlay=true)

// Your strategy logic here
// ...

// When buy signal
if (buyCondition)
    strategy.entry("Long", strategy.long)
    
    // Calculate levels
    entryPrice = close
    stopLoss = entryPrice - (atr * 1.5)  // ATR-based SL
    target = entryPrice + ((entryPrice - stopLoss) * 2.5)  // 2.5:1 R:R
    
    // Send webhook
    alert('{"symbol":"{{ticker}}", "exchange":"NSE", "action":"BUY", "price":' + str.tostring(entryPrice) + ', "stop_loss":' + str.tostring(stopLoss) + ', "target":' + str.tostring(target) + ', "conviction":"MEDIUM", "timeframe":"{{interval}}", "strategy":"YOUR_STRATEGY", "api_key":"YOUR_WEBHOOK_API_KEY"}', alert.freq_once_per_bar)

// When sell signal
if (sellCondition)
    strategy.entry("Short", strategy.short)
    
    // Similar calculation for short
    alert('{"symbol":"{{ticker}}", "exchange":"NSE", "action":"SELL", ...}', alert.freq_once_per_bar)
```

## Step 5: Create TradingView Alert

### In TradingView Chart:

1. **Click Alert Button** (clock icon, top right)

2. **Configure Alert:**
   - **Condition:** Your Strategy → Order fills only
   - **Alert name:** "Your Strategy - {{ticker}}"
   - **Message:** (Use JSON format below)

3. **Webhook URL:** `https://your-ngrok-url.ngrok.io/webhook` (or your server URL)

### Alert Message Format:

```json
{
    "symbol": "{{ticker}}",
    "exchange": "NSE",
    "action": "{{strategy.order.action}}",
    "price": {{close}},
    "stop_loss": YOUR_CALCULATED_SL,
    "target": YOUR_CALCULATED_TARGET,
    "conviction": "MEDIUM",
    "timeframe": "{{interval}}",
    "strategy": "YOUR_STRATEGY_NAME",
    "api_key": "your_webhook_api_key_here"
}
```

**Important:** Replace `your_webhook_api_key_here` with your actual API key from `.env`

4. **Notifications:** Enable "Webhook URL"

5. **Options:**
   - ✅ Webhook URL
   - ⏱️ Once Per Bar Close (recommended)
   - ♾️ Unlimited alerts

6. **Click "Create"**

## Step 6: Test Your Setup

### Manual Test from TradingView

1. Go to your TradingView chart
2. Wait for your strategy to generate a signal
3. Alert should trigger
4. Check your webhook server logs

### Check Server Logs

```bash
# View webhook server logs
tail -f logs/webhook.log

# Or check Flask output
# Look for:
# ✅ TRADE APPROVED FOR EXECUTION
```

### Expected Webhook Flow:

```
TradingView Alert Triggered
       ↓
Webhook Received: BUY TCS @ ₹3,500
       ↓
Step 1: Signal Completeness ✅
Step 2: Position Sizing → 25 shares
Step 3: Risk:Reward → 1:2.50 ✅
Step 4: Portfolio Check ✅
       ↓
✅ TRADE APPROVED
Position: 25 shares
Investment: ₹87,500
Risk: ₹937.50 (0.31%)
```

## Webhook JSON Format

### Required Fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `symbol` | string | Stock symbol | "TCS", "RELIANCE" |
| `exchange` | string | Exchange | "NSE", "BSE" |
| `action` | string | Trade action | "BUY", "SELL" |
| `price` | number | Entry price | 3500 |
| `stop_loss` | number | Stop loss price | 3465 |
| `target` | number | Target price | 3587 |
| `api_key` | string | Your webhook API key | "your_key" |

### Optional Fields:

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `conviction` | string | BELOW_LOW, LOW, MEDIUM, HIGH, ABOVE_HIGH, HIGHEST | "MEDIUM" |
| `timeframe` | string | Chart timeframe | "15m" |
| `strategy` | string | Strategy name | "UNKNOWN" |
| `timestamp` | string | ISO timestamp | Auto-generated |

## Validation Pipeline

Your webhook goes through 4 validation steps:

### 1. Authentication & Rate Limiting
- API key validation
- Rate limit: 60 requests/minute
- IP whitelisting (optional)

### 2. Signal Completeness
- All required fields present
- Stop loss below entry (for BUY)
- Target above entry (for BUY)
- Opposite for SELL

### 3. Risk Calculation
- Position sizing based on conviction
- Risk amount calculation
- Risk:Reward validation (min 2.5:1)

### 4. Portfolio Constraints
- Max 3 positions check
- Max 3 trades/day check
- 2% daily loss limit check
- Capital availability check
- Sector exposure check

## Troubleshooting

### Webhook Not Received

**Check:**
1. Is webhook server running? `curl http://localhost:5001/health`
2. Is ngrok running? Check ngrok dashboard
3. Is URL correct in TradingView alert?
4. Check firewall settings

**Logs:**
```bash
tail -f logs/webhook.log
```

### Trade Rejected

**Common reasons:**
1. **Invalid API key** → Check `.env` WEBHOOK_API_KEY
2. **Risk:Reward < 2.5:1** → Adjust stop loss or target
3. **Max positions reached** → Close a position first
4. **Max trades/day** → Wait for next trading day
5. **Daily loss limit** → Stop trading for today

**Check logs:**
```bash
grep "REJECTED" logs/webhook.log
```

### Server Errors

**Check logs:**
```bash
# Full error details
cat logs/webhook.log | tail -50

# Python errors
tail -f logs/webhook_server.log
```

## Security Best Practices

### 1. Strong API Key
```bash
# Generate cryptographically secure key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. HTTPS Only (Production)
- Never use HTTP in production
- Use Let's Encrypt for free SSL certificates
- Configure SSL in nginx/Apache

### 3. IP Whitelisting (Optional)
Edit `src/webhook_server.py`:
```python
webhook_handler = WebhookHandler(
    api_key=webhook_api_key,
    allowed_ips=['TradingView_IP_1', 'TradingView_IP_2']
)
```

### 4. Signature Validation (Optional)
```bash
# In .env
WEBHOOK_SECRET=your_secret_here
```

### 5. Rate Limiting
Default: 60 requests/minute per IP

### 6. Monitor Logs
```bash
# Set up log monitoring
tail -f logs/audit.log
```

## Production Deployment

### Recommended Stack:

```
Internet → Cloudflare (DDoS protection)
         ↓
       nginx (SSL, reverse proxy)
         ↓
    gunicorn (WSGI server)
         ↓
Your Flask app (webhook_server.py)
         ↓
OpenAlgo → Shoonya
```

### Sample nginx config:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /webhook {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Sample systemd service:

```ini
[Unit]
Description=Trading Webhook Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/python src/webhook_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Testing Checklist

- [ ] Webhook server starts without errors
- [ ] Health endpoint responds: `curl http://localhost:5001/health`
- [ ] Status endpoint shows correct config
- [ ] Test webhook succeeds with valid data
- [ ] Test webhook fails with invalid API key
- [ ] Test webhook rejects trades with bad R:R
- [ ] ngrok/tunnel working (if used)
- [ ] TradingView alert configured correctly
- [ ] Alert message format is valid JSON
- [ ] API key in alert matches `.env`
- [ ] Test alert triggers successfully
- [ ] Server logs show trade approval
- [ ] All validations pass correctly

## Next Steps

Once webhooks are working:
1. **Component 6:** Build Order Executor (OpenAlgo integration)
2. **Component 7:** Add Position Monitor
3. **Component 8:** Add Performance Tracker
4. **Component 9:** Set up notifications (Telegram/Email)

## Support

Check logs for detailed error messages:
- Webhook logs: `logs/webhook.log`
- Audit logs: `logs/audit.log`
- Server logs: `logs/webhook_server.log`

---

**Status: Phase 2 - Component 5 Complete ✅**

Your TradingView alerts are now connected to your automated trading system!
