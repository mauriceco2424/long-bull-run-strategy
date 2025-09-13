# Parameter Configuration - RSI Mean Reversion Test Strategy
> Auto-generated from docs/test/test_SMR.md
> Fill in parameter values before running backtest

## Strategy Parameters

### RSI Indicator Settings
- **RSI Period**: `14` (Number of periods for RSI calculation)
- **Oversold Threshold**: `30` (RSI value below which to enter long)
- **Overbought Threshold**: `70` (RSI value above which to exit)

### Risk Management
- **Stop Loss Percentage**: `5` (Maximum loss per trade in %)
- **Position Size**: `10` (Percentage of equity per trade in %)
- **Min Notional**: `50` (Minimum order size in USD)
- **Max Positions Per Symbol**: `1` (Maximum concurrent positions per asset)

## Market Configuration

### Universe Settings
- **Exchange**: `binance`
- **Quote Currency**: `USDT`
- **Symbols**: `BTCUSDT,ETHUSDT,ADAUSDT` (Comma-separated list)
- **Timeframe**: `1h` (Bar interval: 1m, 5m, 15m, 1h, 4h, 1d)

### Data Requirements
- **Min History Bars**: `50` (Minimum bars needed for indicators)
- **Warmup Period**: `14` (Bars needed before first trade)

## Backtest Configuration

### Date Range
- **Start Date**: `2023-01-01` (YYYY-MM-DD format)
- **End Date**: `2023-06-30` (YYYY-MM-DD format)

### Execution Settings
- **Initial Capital**: `10000` (Starting equity in USD)
- **Slippage Model**: `fixed` (fixed or percentage)
- **Slippage Value**: `0.001` (0.1% for percentage model)
- **Fee Model**: `percentage` (fixed or percentage)
- **Fee Value**: `0.001` (0.1% trading fee)

### Portfolio Settings
- **Accounting Mode**: `mark_to_market` (mark_to_market or realized_only)
- **Rebalance Frequency**: `none` (none, daily, weekly, monthly)
- **Cash Reserve**: `0` (Minimum cash to maintain in USD)

## Run Configuration

### Output Settings
- **Run ID**: `test_run_001` (Unique identifier for this run)
- **Output Directory**: `/data/test_runs/` (Where to save results)
- **Generate Reports**: `true` (Generate PDF/HTML reports)
- **Save Trades**: `true` (Save detailed trade log)
- **Save Metrics**: `true` (Save performance metrics)

### Visualization Settings
- **Chart Level**: `enhanced` (basic, enhanced, advanced)
- **Benchmark Symbol**: `BTC` (Symbol for benchmark comparison)
- **Show Per Symbol**: `true` (Generate per-symbol analysis)

## Validation Rules
All parameters above must be filled with valid values before running.
Parameters are validated against the ranges specified in the strategy template.