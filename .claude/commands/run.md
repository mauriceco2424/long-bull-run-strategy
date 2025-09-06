# Run Trading Strategy Backtest

---
description: Execute backtest using parameter configuration file
argument-hint: 
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-single-runner** agent to execute the trading strategy backtest using the configured parameters from `parameter_config.md`.

## Backtest Execution Tasks

### 1. **Parameter Configuration Validation**
- Read and validate `parameter_config.md` completeness
- Verify all required parameters have values assigned
- Check parameter values are within valid ranges (per strategy schema)
- Validate market/universe and date range specifications
- Confirm configuration consistency and logical coherence

### 2. **Resource Validation & Preparation**
- Verify ≥2GB available RAM before execution
- Check sufficient disk space for output artifacts
- Validate data availability for specified universe and date range
- Confirm engine build is current and compatible
- Prepare run directory structure

### 3. **Backtest Execution**
- Execute engine with parameters from `parameter_config.md`
- Monitor resource usage and auto-throttle if needed
- **Display unified progress bar** with ETA estimation
- **Update progress every 30 seconds** during execution phases
- Handle execution errors gracefully with detailed logging

### 4. **Progress Reporting Standards**
- **Single progress bar format**: `Running backtest... ████████░░░░ 75% (~2 min remaining)`
- **Clear phases**: data loading → signal generation → trade execution → validation
- **ETA integration** based on processing speed and remaining work
- **No micro-progress**: one unified view of major execution progress

### 5. **Artifact Generation**
- Generate run artifacts in `/data/runs/{run_id}/`:
  - `manifest.json` - Run metadata and configuration
  - `metrics.json` - Performance metrics (CAGR, Sortino, Sharpe, MaxDD, etc.)
  - `trades.csv` - Individual trade fill records
  - `events.csv` - Signal and action timestamps
  - `series.csv` - Daily equity and position counts
  - `progress.json` - Real-time progress tracking
- Compute SHA256 checksums for data integrity

### 6. **Data Validation & Quality Checks**
- Run comprehensive data validation suite:
  - No lookahead bias validation
  - Accounting identity verification
  - Timestamp monotonicity and UTC compliance
  - No missing or NaN values in essential columns
  - Trade execution realism checks
- Flag any anomalies or suspicious patterns for escalation

### 7. **Run Registry Update**
- Atomically append run to `/docs/runs/run_registry.csv`
- Use lockfile protocol (`/docs/runs/.registry.lock`) with 5min timeout
- Include run status, metadata, and validation results
- Generate run summary with key metrics and any warnings

## Parameter Configuration Format
The `parameter_config.md` file should contain:
```markdown
# Trading Strategy Parameters

## Strategy Parameters
[All strategy-specific parameters from template]

## Market Configuration  
universe: binance_usdt
timeframe: 4h

## Date Range
start_date: 2021-01-01
end_date: 2023-12-31

## Risk Management
[Risk and position sizing parameters]

## Execution Settings
[Execution timing and conflict resolution settings]
```

## Expected Outputs
- Complete backtest artifacts in `/data/runs/{run_id}/`
- Updated run registry with new entry
- Validation report confirming data integrity
- Performance summary with key metrics
- Ready for analysis phase with `/analyze-run`

## Success Criteria
- Backtest completes without critical errors
- All required artifacts generated successfully  
- Data validation passes all checks
- Run registry updated successfully
- Progress reporting provides clear visibility throughout execution

## Error Handling
- **P0 failures**: Stop execution, log detailed error, escalate to Builder
- **P1 failures**: Complete current phase, flag for review
- **P2 failures**: Log warnings, continue execution
- **Resource failures**: Clean up partial artifacts, report system state

Please use the trading-single-runner agent to execute the backtest with unified progress reporting and comprehensive validation.