# STRAT_TEMPLATE.md — Template for trading_strat.md

> Purpose: Define **what the strategy does** (mechanics only).  
> Note: Global engine rules (no-lookahead, realistic fills, fee model, outputs schema) are handled by the skeleton.

---

## 1) Strategy Overview
- **Name**: `<Strategy Name>`
- **Market/Universe**: `<e.g., Binance USDT pairs | S&P500 stocks | single asset BTCUSDT>`
- **Asset Selection**: `<scan all | fixed list | ranking/filtering method>`
- **Timeframe**: `<e.g., 1D | 1h | 15m>`
- **Scope**: `<long-only | short-only | long-short>`

---

## 1a) Strategy Description (Narrative)
Write in **full sentences** how the strategy operates from start to finish.  
Describe the trading flow step by step, including exotic features if present.  
Do not explain *why* it might work — only *what it does*.  

Example structure:  
- First, the strategy applies its filters to define eligible symbols.  
- Next, eligible symbols are monitored for a trigger/awakening event.  
- When a trigger occurs, the strategy enters at the next bar open.  
- While in position, exits are monitored via stop-loss, take-profit, or other rules.  
- Exits are executed at the next bar open after the condition is met.  

---

## 2) Entry Logic — *When do we BUY?*
- **Information / Markers Used**: `<indicators, price patterns, breadth, custom features>`  
- **Parameters**: `<specific values: RSI(14), SMA(20), ATR(10), thresholds, etc.>`  
- **Mechanic / Condition**: `<precise condition that defines a buy signal>`  
- **Trigger Evaluation Time**: `<bar close | bar open | other>`  
- **Execution Rule**: `<when the order is actually placed: next bar open | same bar close | other>`  

---

## 3) Exit Logic — *When do we SELL?*
- **Information / Markers Used**: `<TP/SL, trailing stop, time exit, reversal signals, etc.>`  
- **Parameters**: `<specific values: TP 3x ATR, SL 2x ATR, max hold 30 bars, etc.>`  
- **Mechanic / Condition**: `<precise condition that defines a sell>`  
- **Collision Handling**: `<priority/ordering rule>`  
- **Execution Rule**: `<when the sell executes: next bar open after hit | same bar close | other>`  

---

## 4) Position Management
> Pick one **Portfolio Accounting Mode** and one **Position Sizing Strategy** below.  
> You MAY specify a custom/exotic method instead, but must describe it clearly.

### 4.1 Portfolio Accounting Mode (choose one)
1. **Cash-only** — Equity = account cash only (ignore open trades until they close).  
2. **Mark-to-market** — Equity = cash + live market value of open positions.  
3. **Frozen-notional** — Equity = cash + invested amounts at entry prices (unchanged until exit).  

### 4.2 Position Sizing Strategy (choose one)
1. **Fixed % of Equity** — Invest a constant percentage of "Equity" (as defined by the chosen accounting mode).  
2. **Fixed Notional** — Invest a fixed currency amount per trade (no compounding).  
3. **Volatility-Adjusted (Risk Targeting)** — Size inversely to volatility (e.g., ATR), to equalize risk per trade.  

- **Caps / Constraints**: `<max concurrent positions, min notional per order, symbol caps, daily buy caps>`  
- **Re-entry / Cooldown / Scaling**: `<cooldown after exit, allow pyramiding yes/no, partial exits yes/no>`  

---

## 5) Filters & Eligibility
- **Data Requirements**: `<minimum bars of history, required indicators>`  
- **Tradability Filters**: `<minimum history, liquidity/volume thresholds, black/allow lists>`  
- **Run Boundaries**: `<backtest/live start date, end date if any>`  

---

## 6) Conflict Handling
- **Buy vs Sell same bar**: `<which action takes precedence>`  
- **Exit Collisions (TP vs SL vs Trailing)**: `<explicit precedence rule>`  

---

## 7) Visualization Configuration (Optional)
*(leave empty to use professional defaults)*

### 7.1 Visualization Level (choose one)
1. **Basic** — Default 3-panel layout: equity curve + drawdown + activity summary  
2. **Enhanced** — Basic + per-symbol candlestick charts with event overlays  
3. **Advanced** — Enhanced + custom strategy-specific visualizations  

### 7.2 Display Options
- **Benchmark Symbol**: `<SPY | QQQ | BTC | custom symbol>` *(default: SPY)*  
- **Per-Symbol Analysis**: `<yes | no>` *(default: no, enables enhanced visualization)*  
- **Trade Markers**: `<all | major | none>` *(default: major - only significant trades shown)*  
- **Time Period Shading**: `<yes | no>` *(default: yes - subtle winning/losing period backgrounds)*  

### 7.3 Custom Analysis Preferences  
- **Strategy-Specific Metrics**: `<e.g., sector rotation analysis, momentum persistence>`  
- **Additional Overlays**: `<e.g., volatility bands, custom indicators>`  
- **Report Sections**: `<any additional analysis sections for LaTeX report>`  

### 7.4 Other Strategy Notes
- **Implementation Notes**: `<any strategy-specific execution details>`  
- **Risk Considerations**: `<known limitations or edge cases>`  
- **Optimization Priorities**: `<areas for future enhancement>`  

---

## Checklist (must be ticked before running)
- [ ] Market/Universe defined  
- [ ] Asset Selection method specified  
- [ ] Timeframe specified  
- [ ] Entry logic (markers, parameters, condition, trigger time, execution) defined  
- [ ] Exit logic (markers, parameters, condition, collisions, execution) defined  
- [ ] **Portfolio Accounting Mode chosen**  
- [ ] **Position Sizing Strategy chosen**  
- [ ] Data Requirements specified  
- [ ] Filters & Eligibility defined  
- [ ] Conflict Handling defined  
- [ ] (Optional) Extras considered
