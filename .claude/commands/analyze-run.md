# Analyze Trading Run Results

---
description: Process run data into comprehensive metrics and professional visualizations
argument-hint: [run_id]
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-analyzer** agent to process the backtest data into comprehensive analysis artifacts including metrics calculation and professional visualizations.

## Run Analysis Parameters
- **Run ID**: $ARGUMENTS (defaults to most recent run if not specified)

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

### 4. **Embedded Validation & Quality Checks**
- **No Lookahead Validation**: Verify all features use data ≤ t for actions at t+1
- **Accounting Identity**: Confirm `Equity_{t+1} = Equity_t + realizedPnL - fees`
- **Sanity Thresholds**: Flag extreme ratios (Sortino >3, zero drawdown periods)
- **Data Quality**: UTC timestamps, no duplicates, non-negative prices/volumes
- **Execution Realism**: Validate trade execution feasibility and liquidity

### 5. **Anomaly Detection & Reporting**
- Identify unusual patterns or suspicious performance metrics
- Flag potential overfitting indicators
- Detect data quality issues or missing information
- Generate anomaly report with severity classifications
- Escalate critical issues to appropriate agents

### 6. **Professional Visualization Standards**
- **Publication-ready quality**: High-resolution PNG and SVG formats
- **Professional formatting**: Clear labels, legends, and captions
- **Consistent styling**: Standard color schemes and typography
- **Figure descriptions**: Auto-generated captions explaining each visualization
- **Ready for PDF inclusion**: Proper sizing and quality for reports

### 7. **Registry Update & Progress Reporting**
- Use lockfile protocol (`/docs/runs/.registry.lock`)
- Check for stale locks (>5min) and proceed with warning
- Atomically append run to `/docs/runs/run_registry.csv`
- **Unified progress bar**: `Analyzing run... ████████░░░░ 75% (~1 min remaining)`
- **Clear phases**: validation → metrics → visualization → quality checks
- **ETA integration**: Based on data size and processing complexity

### 8. **Resource Management & Output Organization**
- Monitor RAM usage, fail if drops below 2GB
- Generate SHA256 checksums for data integrity
- Save all outputs to `/data/runs/{run_id}/analysis/`:
  - Enhanced metrics.json with expanded statistics
  - Professional visualizations in `/figs/` directory
  - Validation reports and quality check results
  - Analysis summary with key findings

## Expected Outputs
- **Enhanced metrics.json** with comprehensive performance statistics
- **Professional visualization suite** ready for report inclusion:
  - Main equity chart with trade markers and statistics panel
  - Position monitoring subplot with clear timeline
  - Per-symbol OHLCV charts with event overlays
- **Validation report** confirming data integrity and realism
- **Anomaly detection report** with any concerns flagged
- **Analysis summary** highlighting key findings and insights
- **Ready for evaluation** with `/evaluate-run`

## Success Criteria
- All validation checks pass without critical errors
- Professional visualizations generated successfully
- Comprehensive metrics calculated and validated
- No critical anomalies detected in analysis
- All artifacts ready for evaluator consumption

Please use the trading-analyzer agent to perform comprehensive data analysis with embedded validation and professional visualization generation.