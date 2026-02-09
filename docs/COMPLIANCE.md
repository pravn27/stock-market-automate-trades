# Compliance & Regulatory Requirements - Indian Markets

## SEBI (Securities and Exchange Board of India) Compliance

### 1. Record Keeping Requirements

#### 1.1 Trade Records
**Requirement**: All trade records must be maintained for **5 years**

Records to maintain:
- Date and time of trade
- Symbol/Security name
- Quantity
- Price (entry and exit)
- Order ID from broker
- Trade reason/strategy
- P&L
- Stop loss and targets

```python
# Implementation
class TradeRecord:
    retention_period_days = 1825  # 5 years
    
    def __init__(self):
        self.trade_data = {
            'timestamp': datetime.datetime.now(),
            'symbol': 'RELIANCE',
            'action': 'BUY',
            'quantity': 50,
            'entry_price': 2500.0,
            'exit_price': 2575.0,
            'broker_order_id': 'ORD123456',
            'strategy': 'BreakoutStrategy',
            'pnl': 3750.0,
            'stop_loss': 2470.0,
            'target': 2575.0
        }
    
    def archive_old_trades(self):
        """Archive trades older than 5 years"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(
            days=self.retention_period_days
        )
        # Move to archive, don't delete
```

#### 1.2 Order Audit Trail
**Requirement**: Complete audit trail of all orders

Must log:
- Order placement time
- Order modification time
- Order cancellation time
- Order execution time
- Rejection reasons
- IP address of system
- User ID

#### 1.3 System Logs
**Requirement**: Maintain system logs for **5 years**

Include:
- All API calls to broker
- System start/stop times
- Error logs
- Security events
- Configuration changes

### 2. Risk Management Requirements

#### 2.1 Position Limits
**SEBI Guideline**: Individual traders should not concentrate risk

Implementation:
- Maximum 30% of capital in any single position
- Maximum 3-5 concurrent positions
- Sector-wise exposure limits

#### 2.2 Stop Loss Mandate
**Best Practice**: Always use stop loss orders

- Hard stop loss (broker level) preferred
- Software stop loss as backup
- Never remove stop loss after entry

#### 2.3 Leverage Limits
**SEBI Regulation**: 

For Equity Intraday (MIS):
- Generally up to 5x leverage for liquid stocks
- Varies by broker and stock

For Options:
- Margin as per SPAN + Exposure margin
- Real-time margin monitoring required

```python
class LeverageCompliance:
    def __init__(self):
        self.max_leverage_equity = 5.0
        self.max_leverage_options = 1.0  # No leverage on options
    
    def check_leverage(self, position_value, available_margin):
        effective_leverage = position_value / available_margin
        return effective_leverage <= self.max_leverage_equity
```

### 3. Algorithmic Trading Compliance

#### 3.1 SEBI Circular on Algo Trading (2024)

**Requirements for Individual Algo Traders:**

1. **Order-to-Trade Ratio**: 
   - Maintain reasonable OTR (typically <20:1)
   - Avoid excessive order modifications/cancellations

2. **Risk Controls**:
   - Order value limits
   - Order quantity limits
   - Daily loss limits
   - Position limits

3. **System Testing**:
   - Mandatory testing in test environment
   - No direct production deployment

4. **Approval**:
   - Currently, retail algo trading through registered platforms only
   - Requires broker approval

```python
class AlgoTradingCompliance:
    def __init__(self):
        self.max_order_value = 1000000  # ₹10 lakhs per order
        self.max_order_quantity = 1000  # Adjust per stock
        self.max_daily_orders = 100
        self.max_otr_ratio = 20.0  # Orders to trades ratio
    
    def check_order_compliance(self, order):
        """Validate order against SEBI guidelines"""
        
        # Check order value
        order_value = order.quantity * order.price
        if order_value > self.max_order_value:
            return False, "Order value exceeds limit"
        
        # Check quantity
        if order.quantity > self.max_order_quantity:
            return False, "Order quantity exceeds limit"
        
        return True, "Compliant"
```

### 4. Tax Compliance

#### 4.1 Capital Gains Tax

**Short Term Capital Gains (STCG)** - Equity:
- Holding period: < 1 year
- Tax rate: 20% (as of 2024)

**Long Term Capital Gains (LTCG)** - Equity:
- Holding period: ≥ 1 year
- Tax rate: 12.5% on gains > ₹1.25 lakh/year

**Intraday Trading**:
- Treated as business income
- Taxed as per income tax slab

```python
class TaxCalculator:
    def __init__(self):
        self.stcg_rate = 0.20  # 20%
        self.ltcg_rate = 0.125  # 12.5%
        self.ltcg_exemption = 125000  # ₹1.25 lakhs
    
    def calculate_tax(self, trades):
        """Calculate tax liability"""
        stcg = sum(t.pnl for t in trades if t.holding_days < 365 and t.pnl > 0)
        ltcg = sum(t.pnl for t in trades if t.holding_days >= 365 and t.pnl > 0)
        
        # LTCG exemption
        ltcg_taxable = max(0, ltcg - self.ltcg_exemption)
        
        tax = (stcg * self.stcg_rate) + (ltcg_taxable * self.ltcg_rate)
        return tax
```

#### 4.2 ITR Filing

**Requirements**:
- F&O traders: ITR-3 (Business Income)
- Equity delivery traders: ITR-2 (Capital Gains)
- Maintain detailed trade records for audit

#### 4.3 TDS on Securities

**TDS Rate**: 0.1% on sale value (if turnover > ₹1 crore)

### 5. Know Your Client (KYC) Compliance

#### 5.1 Periodic KYC Update
**Requirement**: Update KYC every 2 years

- Submit updated documents to broker
- Update PAN, address, bank details

#### 5.2 Financial Details
**Requirement**: Declare annual income, net worth

- Required for derivatives trading
- Update periodically

### 6. Data Protection & Privacy

#### 6.1 Personal Data
**IT Act 2000**: Protect personal information

- Encrypt sensitive data
- Secure storage
- Limited access

#### 6.2 Trading Data
**Proprietary**: Your trading strategy is confidential

- Don't share API keys
- Secure your system
- Use encrypted connections

### 7. Broker Compliance

#### 7.1 Authorized Algo Trading
**Check with Broker**:
- Is algo trading allowed?
- Any restrictions?
- Need approval?

#### 7.2 API Usage Terms
**Broker Terms**:
- Rate limits
- Prohibited activities
- Liability clauses

### 8. Risk Disclosures (Mandatory)

#### 8.1 Standard Disclosure

```
RISK DISCLOSURE

Trading in securities market is subject to market risks. 
Past performance is not indicative of future returns.

Risks involved in algorithmic trading:
1. System failures and technical glitches
2. Market volatility and slippage
3. Connectivity issues
4. Order execution delays
5. Incorrect strategy logic
6. Over-optimization and curve fitting

Please read all risk disclosures carefully before trading.
Invest only surplus funds that you can afford to lose.

Seek professional advice if unsure.
```

### 9. Reporting Requirements

#### 9.1 Internal Reports (Recommended)

Generate monthly:
- Trade summary
- P&L statement
- Risk metrics
- System performance
- Compliance violations (if any)

#### 9.2 Broker Statements

Download and reconcile:
- Daily contract notes
- Monthly ledger
- Tax P&L statement (for ITR)

### 10. Audit Readiness

#### 10.1 Documents to Maintain

✅ Trade logs (5 years)
✅ Order confirmations (5 years)
✅ Bank statements (6 years)
✅ Contract notes (5 years)
✅ System logs (5 years)
✅ Strategy documentation
✅ Risk management policies
✅ Compliance procedures

#### 10.2 Audit Trail

Maintain complete audit trail:
```python
# Example audit log entry
{
    'timestamp': '2026-02-09 10:15:30',
    'action': 'ORDER_PLACED',
    'symbol': 'RELIANCE',
    'order_id': 'ORD123456',
    'quantity': 50,
    'price': 2500.0,
    'strategy': 'BreakoutStrategy',
    'system_id': 'ALGO001',
    'ip_address': '127.0.0.1',
    'pre_trade_checks': {
        'risk_check': 'PASSED',
        'position_limit_check': 'PASSED',
        'margin_check': 'PASSED'
    }
}
```

### 11. Compliance Checklist

#### Before Going Live

- [ ] Read SEBI guidelines on algo trading
- [ ] Understand broker's algo trading policy
- [ ] Set up proper risk controls
- [ ] Implement audit logging (5-year retention)
- [ ] Test thoroughly in sandbox/paper trading
- [ ] Document your trading strategy
- [ ] Set up backup and recovery
- [ ] Understand tax implications
- [ ] Update KYC if needed
- [ ] Review and accept risk disclosures

#### Ongoing Compliance

**Daily**:
- [ ] Reconcile trades with broker
- [ ] Review system logs for errors
- [ ] Check risk limits not breached

**Monthly**:
- [ ] Download broker statements
- [ ] Generate P&L report
- [ ] Backup trade data
- [ ] Review compliance metrics

**Annually**:
- [ ] File Income Tax Return (ITR)
- [ ] Update KYC (if due)
- [ ] System security audit
- [ ] Review and update risk policies

### 12. Penalties for Non-Compliance

**SEBI Penalties**:
- Fines up to ₹25 crores
- Trading ban
- Criminal prosecution (in severe cases)

**Income Tax Penalties**:
- 50% to 200% of tax evaded
- Interest at 1% per month
- Prosecution for willful default

**Broker Actions**:
- Account suspension
- Margin calls
- Position liquidation

### 13. Resources

**SEBI**:
- Website: www.sebi.gov.in
- Circulars: Check regularly for updates

**Income Tax**:
- Website: www.incometax.gov.in
- e-Filing: www.incometaxindiaefiling.gov.in

**NSE/BSE**:
- NSE: www.nseindia.com
- BSE: www.bseindia.com

### 14. Disclaimer

This document provides general guidance on compliance requirements in India. 
It is NOT legal or financial advice.

**Consult with:**
- Chartered Accountant (CA) for tax matters
- Securities lawyer for legal compliance
- SEBI registered investment advisor
- Your broker's compliance team

Regulations change frequently. Stay updated!

**Last Updated**: February 2026
