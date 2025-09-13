# Long Bull Run Strategy

## 1) Strategy Overview
- **Name**: Long Bull Run Strategy  
- **Market/Universe**: Binance USDT pairs  
- **Asset Selection**: Scan all eligible pairs passing filters  
- **Timeframe**: 1D (daily candles)  
- **Scope**: Long-only  

---

## 1a) Strategy Description (Narrative)
The strategy operates on daily Binance USDT pairs.  
Every 5 days, it applies liquidity and trend filters to define eligible symbols.  
Eligible symbols are then monitored daily for a combined price-and-volume awakening trigger.  
When a trigger occurs, the strategy enters a position at the next bar open with fixed capital allocation.  
While in position, exits are monitored daily via stop-loss and take-profit rules.  
If a take-profit is reached, the strategy schedules a delayed exit; if a stop-loss is hit, it exits immediately.  
All exits are executed at the next bar open after the condition (or delay) is satisfied.  
Equity is tracked mark-to-market, and position caps enforce diversification across symbols.  

---

## 2) Entry Logic — *When do we BUY?*
- **Information / Markers Used**: Volume trend averages, price averages, short-term vs long-term ratios, awakening volume and price increases  
- **Parameters**:  
  - Minimum history: 365 daily bars  
  - Minimum daily volume: $250,000  
  - Volume trend: 36d vs 360d, decline ≤ 45%  
  - Price position: 8d vs 600d, ratio ≥ 1.5  
  - Volume awakening: 3d vs 25d average, ≥ 1.2× increase  
  - Price awakening: 3d high vs 25d average, ≥ 1.03  
  - Awakening persistence: ≥ 3 consecutive days  
- **Mechanic / Condition**: Symbol must pass all filters, then show both volume and price awakening within 50 days of the filter date  
- **Trigger Evaluation Time**: Bar close (daily)  
- **Execution Rule**: Buy executes at the next bar open  

---

## 3) Exit Logic — *When do we SELL?*
- **Information / Markers Used**: Profit target multiple, stop-loss multiple, time-delay after TP  
- **Parameters**:  
  - Profit target: 2.3× entry price (130%)  
  - Stop-loss: 0.5× entry price (−50%)  
  - Time delay: 20% of trade duration (minimum 1 bar) after TP  
- **Mechanic / Condition**:  
  1. Exit immediately if price ≤ 0.5× entry (stop-loss).  
  2. If price ≥ 2.3× entry, mark TP and schedule delayed exit.  
- **Collision Handling**: Stop-loss takes precedence; otherwise TP + delay applies.  
- **Execution Rule**: Exit executes at the next bar open after the condition is met (or delayed TP exit date).  

---

## 4) Position Management

### 4.1 Portfolio Accounting Mode
- **Mark-to-market** — Equity = cash + current value of open positions  

### 4.2 Position Sizing Strategy
- **Fixed % of Equity** — 5% of equity per trade  
- **Caps / Constraints**:  
  - Max concurrent positions: 100  
  - Max per symbol: 20  
  - No pyramiding; one active position per symbol  
- **Re-entry / Cooldown**: Symbol must re-pass filter/awakening after exit before a new entry is allowed  

---

## 5) Filters & Eligibility
- **Data Requirements**: At least 365 daily bars of history  
- **Tradability Filters**: Minimum daily volume $250,000  
- **Run Boundaries**: Backtests start from the earliest date with sufficient history; strategy applies continuously forward with no explicit end date  

---

## 6) Conflict Handling
- **Buy vs Sell same bar**: Exit signals take precedence  
- **Exit Collisions (TP vs SL vs Trailing)**: Stop-loss overrides take-profit; TP delay applies only if no stop-loss is triggered  

---

## 7) Visualization Configuration (Optional)

### 7.1 Visualization Level
- **Enhanced** — Equity curve + drawdowns + per-symbol candlestick charts with event overlays  

### 7.2 Display Options
- **Benchmark Symbol**: BTC  
- **Per-Symbol Analysis**: Yes  
- **Trade Markers**: Major only  
- **Time Period Shading**: Yes  

### 7.3 Custom Analysis Preferences
- **Strategy-Specific Metrics**: Awakening frequency, delay-hold vs immediate exit comparison  

### 7.4 Other Strategy Notes
- **Implementation Notes**: Runs on Binance USDT daily OHLCV data  
- **Risk Considerations**: High volatility; large drawdowns possible due to wide stop-loss  
- **Optimization Priorities**: Refine TP delay logic and volume thresholds  

---

## Checklist
- [x] Market/Universe defined  
- [x] Asset Selection method specified  
- [x] Timeframe specified  
- [x] Entry logic (markers, parameters, condition, trigger time, execution) defined  
- [x] Exit logic (markers, parameters, condition, collisions, execution) defined  
- [x] **Portfolio Accounting Mode chosen**  
- [x] **Position Sizing Strategy chosen**  
- [x] Data Requirements specified  
- [x] Filters & Eligibility defined  
- [x] Conflict Handling defined  
- [x] (Optional) Extras considered  
