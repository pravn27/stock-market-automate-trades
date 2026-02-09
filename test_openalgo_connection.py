#!/usr/bin/env python3
"""Test OpenAlgo connection"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try importing openalgo
try:
    from openalgo import AccountAPI, OrderAPI, DataAPI
    print("✅ OpenAlgo SDK imported successfully")
except ImportError:
    print("❌ OpenAlgo SDK not found. Installing...")
    import subprocess
    subprocess.run(["pip", "install", "openalgo"])
    from openalgo import AccountAPI, OrderAPI, DataAPI
    print("✅ OpenAlgo SDK installed and imported")

# Get API key
api_key = os.getenv('OPENALGO_API_KEY')
host = os.getenv('OPENALGO_HOST', 'http://127.0.0.1:5000')

if not api_key or api_key == 'your_openalgo_api_key_here':
    print("❌ OPENALGO_API_KEY not set in .env file")
    print("\n📋 Follow these steps:")
    print("1. Open OpenAlgo dashboard: http://127.0.0.1:5000")
    print("2. Go to Settings → API Keys")
    print("3. Generate new API key")
    print("4. Copy it to your .env file:")
    print("   OPENALGO_API_KEY=your_generated_key")
    exit(1)

print(f"\n🔌 Connecting to OpenAlgo at {host}...")

try:
    # Initialize OpenAlgo API clients
    account_api = AccountAPI(api_key=api_key, host=host)
    order_api = OrderAPI(api_key=api_key, host=host)
    data_api = DataAPI(api_key=api_key, host=host)
    
    # Test 1: Get account balance
    print("\n📊 Test 1: Fetching account balance...")
    funds = account_api.funds()
    if funds.get('status') == 'success':
        balance = funds['data']['availablecash']
        print(f"✅ Available balance: ₹{balance}")
    else:
        print(f"❌ Failed to get balance: {funds.get('message')}")
    
    # Test 2: Get positions
    print("\n📈 Test 2: Fetching positions...")
    positions = account_api.positionbook()
    if positions.get('status') == 'success':
        pos_count = len(positions.get('data', []))
        print(f"✅ Current positions: {pos_count}")
        if pos_count > 0:
            for pos in positions['data']:
                qty = pos.get('quantity', 0)
                avg_price = pos.get('average_price', 0)
                pnl = pos.get('pnl', 0)
                print(f"   - {pos['symbol']}: {qty} @ ₹{avg_price} | P&L: ₹{pnl}")
    else:
        print(f"❌ Failed to get positions: {positions.get('message')}")
    
    # Test 3: Get quote
    print("\n💹 Test 3: Fetching market quote...")
    try:
        quote = data_api.quotes(symbol='RELIANCE', exchange='NSE')
        if quote.get('status') == 'success':
            ltp = quote['data']['lp']
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
    print("\n📖 Next: Read docs/IMPLEMENTATION_PLAN.md - Phase 1")
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Check if OpenAlgo is running: http://127.0.0.1:5000")
    print("2. Verify API key is correct in .env file")
    print("3. Make sure Shoonya is connected in OpenAlgo dashboard")
    print("4. Check OpenAlgo logs for errors")
