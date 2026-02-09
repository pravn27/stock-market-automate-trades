# Shoonya (Finvasia) API Setup Guide

## Error: "Invalid Vendor code"

This error occurs when the vendor code is incorrect or not configured properly.

## Getting Shoonya API Credentials

### Step 1: Enable API Access

1. **Login to Shoonya**: https://shoonya.com/
2. Go to **Settings** → **API Settings**
3. Click **"Enable API Access"**
4. You'll receive:
   - User ID (your login ID)
   - API Key
   - **Vendor Code** (Important!)
   - API Secret

### Step 2: Vendor Code Information

**For Shoonya/Finvasia:**

The vendor code depends on your account type:

1. **If you have API access enabled**:
   - Check your API documentation email from Finvasia
   - Vendor code is usually: `SHOONYA_API` or similar
   - Some accounts may have custom vendor codes

2. **If you're a retail trader**:
   - You may need to contact Finvasia support to get API access
   - Email: support@finvasia.com
   - Subject: "Request API Access for Algo Trading"

### Step 3: Common Shoonya Vendor Codes

Try these vendor codes (one at a time):

```
SHOONYA_API
NA
SHOONYA_U
```

**Note**: The exact vendor code is provided when you enable API access.

### Step 4: Required Credentials

You need all of these:

```yaml
User ID: FA68946  # Your login ID (you have this)
Password: •••••••  # Your password (you have this)
API Key: •••••••   # From API settings
API Secret: ••••••• # From API settings (if required)
Vendor Code: ••••••• # THIS IS WHAT'S MISSING
TOTP Secret: ••••••• # For 2FA (if enabled)
```

## Alternative: Check if Shoonya is Supported in OpenAlgo

### Verify Broker Support

OpenAlgo mentions "shoonya" in supported brokers, but Finvasia may have specific requirements.

**Check OpenAlgo Documentation:**
- https://github.com/marketcalls/openalgo
- Look for Shoonya/Finvasia specific setup

## Contact Finvasia Support

If vendor code is not clear:

**Email**: support@finvasia.com  
**Phone**: +91 80 4719 7777  
**Website**: https://www.finvasia.com/

**What to ask:**
1. "What is the Vendor Code for API access?"
2. "How do I enable algorithmic trading API?"
3. "What are the complete API credentials I need?"

## Temporary Solution: Try Other Brokers

If Shoonya setup is complex, OpenAlgo supports 25+ brokers:

### Easier Alternatives:
1. **Zerodha** (Kite Connect) - Most popular, good documentation
2. **Angel One** - Easy API setup
3. **Upstox** - Simple API integration
4. **Fyers** - Good for algo trading

All use similar risk management logic, so your trading system will work the same!

## Next Steps

**Once you get the correct vendor code:**

1. Update OpenAlgo broker configuration with correct vendor code
2. Test authentication
3. Proceed with Phase 1 of implementation

**If vendor code is still unclear:**
- Contact Finvasia support (they respond within 24 hours)
- Or switch to a more algo-friendly broker like Zerodha

## Important Security Note

Never share your:
- User ID
- Password  
- API Keys
- Vendor Code
- TOTP Secret

These credentials give full access to your trading account!
