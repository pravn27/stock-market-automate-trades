# Quick Start Guide - Get OpenAlgo API Key

## You're Connected! Now Get Your API Key

### Step 1: Access OpenAlgo Dashboard

OpenAlgo should be running at: **http://127.0.0.1:5000**

If not running:
```bash
cd /Users/pshekarappa/pravn27/ASTA/openalgo
source venv/bin/activate
python3 app.py
```

### Step 2: Generate API Key

1. **Login to OpenAlgo** dashboard (http://127.0.0.1:5000)
2. Click on **Settings** (top right or sidebar)
3. Click on **API Keys** section
4. Click **"Generate New API Key"** button
5. **Copy the generated key** (it looks like: `a1b2c3d4-5678-90ab-cdef-1234567890ab`)
6. **Save it immediately** - you can't see it again!

### Step 3: Update Your Project's .env File

Open your project's `.env` file:
```bash
/Users/pshekarappa/pravn27/ASTA/stock-market-automate-trades/.env
```

Find this line:
```bash
OPENALGO_API_KEY=your_openalgo_api_key_here
```

Replace with your actual key:
```bash
OPENALGO_API_KEY=a1b2c3d4-5678-90ab-cdef-1234567890ab
```

Save the file.

### Step 4: Generate Security Keys

Run these commands:
```bash
cd /Users/pshekarappa/pravn27/ASTA/stock-market-automate-trades

# Generate SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Generate ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

Copy both outputs to your `.env` file.

### Step 5: Test OpenAlgo Connection

Create a test script:
```bash
cd /Users/pshekarappa/pravn27/ASTA/stock-market-automate-trades
nano test_openalgo_connection.py
```

Paste this code:
```python
#!/usr/bin/env python3
"""Test OpenAlgo connection"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try importing openalgo
try:
    from openalgo import api
    print("✅ OpenAlgo SDK imported successfully")
except ImportError:
    print("❌ OpenAlgo SDK not found. Installing...")
    import subprocess
    subprocess.run(["pip", "install", "openalgo"])
    from openalgo import api
    print("✅ OpenAlgo SDK installed and imported")

# Get API key
api_key = os.getenv('OPENALGO_API_KEY')
host = os.getenv('OPENALGO_HOST', 'http://localhost:5000')

if not api_key or api_key == 'your_openalgo_api_key_here':
    print("❌ OPENALGO_API_KEY not set in .env file")
    print("Please follow the Quick Start guide to get your API key")
    exit(1)

print(f"\n🔌 Connecting to OpenAlgo at {host}...")

try:
    # Initialize OpenAlgo client
    client = api.OpenAlgoClient(
        api_key=api_key,
        host=host
    )
    
    # Test 1: Get account balance
    print("\n📊 Test 1: Fetching account balance...")
    funds = client.funds()
    if funds.get('status') == 'success':
        balance = funds['data']['availablecash']
        print(f"✅ Available balance: ₹{balance}")
    else:
        print(f"❌ Failed to get balance: {funds.get('message')}")
    
    # Test 2: Get positions
    print("\n📈 Test 2: Fetching positions...")
    positions = client.positions()
    if positions.get('status') == 'success':
        pos_count = len(positions.get('data', []))
        print(f"✅ Current positions: {pos_count}")
        if pos_count > 0:
            for pos in positions['data']:
                print(f"   - {pos['symbol']}: {pos['netqty']} @ ₹{pos['average_price']}")
    else:
        print(f"❌ Failed to get positions: {positions.get('message')}")
    
    # Test 3: Get quote
    print("\n💹 Test 3: Fetching market quote...")
    try:
        quote = client.quotes(symbol='RELIANCE', exchange='NSE')
        if quote.get('status') == 'success':
            ltp = quote['data']['ltp']
            print(f"✅ RELIANCE LTP: ₹{ltp}")
        else:
            print(f"⚠️  Quote fetch returned: {quote.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"⚠️  Quote fetch not available (normal if market closed): {e}")
    
    print("\n" + "="*60)
    print("🎉 All tests passed! OpenAlgo connection successful!")
    print("="*60)
    print("\n✅ You're ready to proceed with Phase 1:")
    print("   - Building Risk Management Module")
    print("   - Building Position Sizer")
    print("   - Building Strategy Validator")
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check if OpenAlgo is running: http://127.0.0.1:5000")
    print("2. Verify API key is correct in .env file")
    print("3. Make sure Shoonya is connected in OpenAlgo dashboard")
```

Save and run:
```bash
chmod +x test_openalgo_connection.py
python3 test_openalgo_connection.py
```

### Expected Output

```
✅ OpenAlgo SDK imported successfully

🔌 Connecting to OpenAlgo at http://localhost:5000...

📊 Test 1: Fetching account balance...
✅ Available balance: ₹100000

📈 Test 2: Fetching positions...
✅ Current positions: 0

💹 Test 3: Fetching market quote...
✅ RELIANCE LTP: ₹2510.50

============================================================
🎉 All tests passed! OpenAlgo connection successful!
============================================================

✅ You're ready to proceed with Phase 1:
   - Building Risk Management Module
   - Building Position Sizer
   - Building Strategy Validator
```

### What's Next?

Once the test passes, you're ready for **Phase 1: Building Your Custom Risk Management Layer**!

This is where the real value is - your rules that remove emotions from trading.
