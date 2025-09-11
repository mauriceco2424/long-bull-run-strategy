# Test Strategy Specification - RSI Mean Reversion

> Purpose: Define **what the strategy does** (mechanics only).  
> Note: Global engine rules (no-lookahead, realistic fills, fee model, outputs schema) are handled by the skeleton.

---

## 1) Strategy Overview
- **Name**: `RSI Mean Reversion Test Strategy`
- **Market/Universe**: `Binance USDT pairs`
- **Asset Selection**: `Fixed list: BTCUSDT, ETHUSDT, ADAUSDT`
- **Timeframe**: `1h`
- **Scope**: `long-only`

---

## 1a) Strategy Description (Narrative)
The RSI Mean Reversion Test Strategy operates on a simple contrarian principle using the Relative Strength Index indicator. First, the strategy monitors three major cryptocurrency pairs (BTCUSDT, ETHUSDT, ADAUSDT) on 1-hour timeframes. When the 14-period RSI drops below 30 (oversold condition), indicating potential buying opportunity, the strategy triggers a long entry signal. The entry is executed at the next bar's opening price. While holding the position, the strategy continuously monitors two exit conditions: either the RSI rises above 70 (overbought condition) signaling mean reversion completion, or the position hits a 5% stop loss to limit downside risk. When either exit condition is met, the position is closed at the next bar's opening price. The strategy employs fixed position sizing of 10% equity per trade with mark-to-market portfolio accounting.

---

## 2) Entry Logic — *When do we BUY?*
- **Information / Markers Used**: `RSI(14) - 14-period Relative Strength Index`  
- **Parameters**: `RSI Period: 14, Oversold Threshold: 30`  
- **Mechanic / Condition**: `RSI(14) < 30`  
- **Trigger Evaluation Time**: `bar close`  
- **Execution Rule**: `next bar open`  

---

## 3) Exit Logic — *When do we SELL?*
- **Information / Markers Used**: `RSI(14) for mean reversion exit, Entry price for stop loss`  
- **Parameters**: `Overbought Threshold: 70, Stop Loss: 5%`  
- **Mechanic / Condition**: `RSI(14) > 70 OR price < entry_price * 0.95`  
- **Collision Handling**: `Stop loss takes precedence over RSI exit`  
- **Execution Rule**: `next bar open after condition is met`  

---

## 4) Position Management

### 4.1 Portfolio Accounting Mode (choose one)
2. **Mark-to-market** — Equity = cash + live market value of open positions.

### 4.2 Position Sizing Strategy (choose one)
1. **Fixed % of Equity** — Invest a constant percentage of "Equity" (as defined by the chosen accounting mode).

- **Position Size**: `10% of current equity per trade`
- **Caps / Constraints**: `Maximum 1 position per symbol, minimum $50 notional per order`  
- **Re-entry / Cooldown / Scaling**: `No cooldown period, no pyramiding, no partial exits`  

---

## 5) Filters & Eligibility
- **Data Requirements**: `Minimum 50 bars of history for RSI calculation`  
- **Tradability Filters**: `Fixed symbol list (BTCUSDT, ETHUSDT, ADAUSDT), minimum $50 notional`  
- **Run Boundaries**: `2023-01-01 to 2023-06-30 (6 months for testing)`  

---

## 6) Conflict Handling
- **Buy vs Sell same bar**: `Sell takes precedence (exit existing position before new entry)`  
- **Exit Collisions (TP vs SL vs Trailing)**: `Stop loss takes precedence over RSI overbought exit`  

---

## 7) Visualization Configuration (Optional)

### 7.1 Visualization Level (choose one)
2. **Enhanced** — Basic + per-symbol candlestick charts with event overlays  

### 7.2 Display Options
- **Benchmark Symbol**: `BTC` 
- **Per-Symbol Analysis**: `yes` 
- **Trade Markers**: `all` 
- **Time Period Shading**: `yes` 

### 7.3 Custom Analysis Preferences  
- **Strategy-Specific Metrics**: `RSI distribution analysis, mean reversion timing analysis`  
- **Additional Overlays**: `RSI(14) with 30/70 threshold lines`  
- **Report Sections**: `RSI effectiveness analysis, mean reversion success rate`  

### 7.4 Other Strategy Notes
- **Implementation Notes**: `Simple test strategy for skeleton validation, fast execution on small universe`  
- **Risk Considerations**: `Limited to 3 symbols, 6-month backtest period for speed`  
- **Optimization Priorities**: `Test framework performance, not strategy optimization`  

---

## Checklist (must be ticked before running)
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