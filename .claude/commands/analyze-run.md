# Analyze Trading Strategy Run

---
description: Process existing run data into canonical outputs
argument-hint: [run_id or config_path universe_id date_range]
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-analyzer** agent to process backtest data into canonical artifacts and visualizations.

## Run Specification
$ARGUMENTS

## Analysis Tasks

### 1. Data Processing & Validation
- **Input Validation**: Verify data quality, UTC timestamps, no duplicates
- **Missing Bar Policy**: Ensure missing-bar policy is respected
- **Data Integrity**: Check for non-negative prices/volumes, monotonic timestamps

### 2. Artifact Generation
Create canonical outputs in `/data/runs/{run_id}/`:

- **`manifest.json`**: Run metadata including:
  - run_id, universe_id, date_start, date_end
  - config_path, config_hash, data_hash
  - engine_version, strat_version, seed, fees_model
  - parent_run_id (if applicable)

- **`metrics.json`**: Performance metrics including:
  - CAGR, Sortino, Sharpe, MaxDD
  - exposure, n_trades, win_rate
  - avg_gain, avg_loss, avg_win
  - avg_trade_dur_days, avg_monitor_dur_days
  - start_utc, end_utc

- **`trades.csv`**: Individual fill records with:
  - side, qty, price, fees, realizedPnL
  - open/close timestamps, symbol, batch_id

- **`events.csv`**: Signal and action timestamps:
  - filter_pass, buy_signal, tp_signal, tp_sell
  - sl_signal, sl_sell with UTC timestamps

- **`series.csv`**: Time series data:
  - Daily equity, monitored_count, open_trades_count
  - Optional cash, gross_exposure

### 3. Visualization Generation
Create figures in `/data/runs/{run_id}/figs/`:

- **Main Equity Plot**:
  - Equity curve with trade bars grouped by symbol
  - Color coding: blues/greens for gains, reds/oranges for losses
  - Intensity encodes number of trades in batch
  - Side panel with config hash and headline stats

- **Monitoring Subplot**:
  - monitored_count and open_trades_count lines
  - Daily dots or continuous lines

- **Per-Symbol Charts**:
  - Candlestick + volume charts
  - Vertical event lines with color coding:
    - Grey: filter pass
    - Black: buy signal
    - Blue: TP signal, Green: TP sell
    - Orange: SL signal, Red: SL sell
  - Shaded spans for open trades
  - Monthly event bar with ticks and labels

### 4. Validation Protocol
Run comprehensive validators (block on failure):

1. **No-Lookahead Check**: Features use data ≤ t, actions at next-bar open
2. **Accounting Identity**: `Equity_{t+1} = Equity_t + realizedPnL - fees`
3. **Sanity Thresholds**: Flag extreme ratios (high Sortino, zero DD)
4. **Data Quality**: Verify timestamps, duplicates, missing-bar compliance

### 5. Registry Update
- Use lockfile protocol (`/docs/runs/.registry.lock`)
- Check for stale locks (>5min) and proceed with warning
- Atomically append run to `/docs/runs/run_registry.csv`
- Include validation status and anomaly flags

### 6. Progress Reporting
- Update `progress.json` every 30 seconds during long phases
- Include percent complete, current phase, ETA, current symbol

### 7. Resource Management
- Monitor RAM usage, fail if drops below 2GB
- Clean up partial artifacts on failure
- Generate SHA256 checksums for data integrity

## Expected Outputs
- Complete artifact set in `/data/runs/{run_id}/`
- Validation report with pass/fail status
- Updated run registry entry
- High-quality visualizations following best practices
- Progress tracking and resource usage reports

The analysis will focus on data integrity, comprehensive metrics generation, and professional visualizations suitable for strategy evaluation.