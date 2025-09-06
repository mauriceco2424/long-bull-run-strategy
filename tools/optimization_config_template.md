# Trading Strategy - Parameter Optimization Configuration Template

<!-- This template defines parameter ranges for optimization sweeps -->
<!-- Used by /optimize command to perform systematic parameter exploration -->

## Instructions
Fill in all required optimization parameters below. Remove the [REQUIRED] markers when you provide values.
All parameter ranges must be defined before running `/optimize` command.

---

## Optimization Study Configuration
study_name: [REQUIRED: descriptive name, e.g., "RSI_MA_Optimization_Q1_2024"]
search_strategy: [REQUIRED: choose from grid, random, bayesian]
max_combinations: [REQUIRED: integer 50-10000, e.g., 1000] # Maximum parameter combinations to test
random_seed: [REQUIRED: integer, e.g., 42] # For reproducible random/Bayesian searches

## Walk-Forward Analysis Configuration
training_period_months: [REQUIRED: integer 12-36, e.g., 24] # In-sample training period
validation_period_months: [REQUIRED: integer 6-12, e.g., 6] # Out-of-sample validation period
rolling_step_months: [REQUIRED: integer 1-6, e.g., 3] # How far to advance each window
min_validation_windows: [REQUIRED: integer 3-10, e.g., 5] # Minimum number of validation periods

## Market Configuration
universe: [REQUIRED: e.g., binance_usdt, crypto_majors, equity_sp500]
timeframe: [REQUIRED: e.g., 1h, 4h, 1d]

## Date Range for Full Dataset
start_date: [REQUIRED: YYYY-MM-DD, e.g., 2020-01-01] # Full dataset start
end_date: [REQUIRED: YYYY-MM-DD, e.g., 2024-12-31] # Full dataset end

## Optimization Target
primary_metric: [REQUIRED: choose from sortino_ratio, sharpe_ratio, cagr, max_drawdown_adj_return]
minimize_metric: [REQUIRED: boolean true/false] # true if lower is better (e.g., max_drawdown)

## Parameter Ranges for Optimization

### Entry Parameters
# RSI Configuration
rsi_period_min: [REQUIRED: integer 5-25, e.g., 10]
rsi_period_max: [REQUIRED: integer 15-50, e.g., 20] 
rsi_period_step: [REQUIRED: integer 1-5, e.g., 2]

rsi_threshold_min: [REQUIRED: float 20-35, e.g., 25]
rsi_threshold_max: [REQUIRED: float 30-45, e.g., 35]
rsi_threshold_step: [REQUIRED: float 0.5-2.5, e.g., 1.0]

# Volume Filter Configuration
volume_filter_min: [REQUIRED: float 0.8-1.2, e.g., 1.0]
volume_filter_max: [REQUIRED: float 1.2-2.5, e.g., 1.8]
volume_filter_step: [REQUIRED: float 0.1-0.3, e.g., 0.2]

### Exit Parameters
# Stop Loss Configuration  
stop_loss_pct_min: [REQUIRED: float 0.005-0.02, e.g., 0.01]
stop_loss_pct_max: [REQUIRED: float 0.02-0.08, e.g., 0.04]
stop_loss_pct_step: [REQUIRED: float 0.0025-0.01, e.g., 0.005]

# Take Profit Configuration
take_profit_pct_min: [REQUIRED: float 0.015-0.04, e.g., 0.02]
take_profit_pct_max: [REQUIRED: float 0.04-0.15, e.g., 0.08]
take_profit_pct_step: [REQUIRED: float 0.005-0.02, e.g., 0.01]

# Maximum Hold Period Configuration
max_hold_days_min: [REQUIRED: integer 3-10, e.g., 5]
max_hold_days_max: [REQUIRED: integer 10-25, e.g., 15]
max_hold_days_step: [REQUIRED: integer 1-3, e.g., 2]

### Portfolio Parameters (Fixed for Optimization)
# These parameters remain constant across all optimization runs
accounting_mode: [REQUIRED: choose from cash-only, mark-to-market, frozen-notional]
position_sizing_strategy: [REQUIRED: choose from fixed-percent, fixed-notional, volatility-adjusted]
position_size_pct: [REQUIRED: float 0.02-0.10, e.g., 0.05] # Fixed position size
max_concurrent_positions: [REQUIRED: integer 3-10, e.g., 5] # Fixed max positions

### Risk Parameters (Fixed for Optimization)
max_daily_trades: [REQUIRED: integer 5-20, e.g., 10] # Fixed daily trade limit
cooldown_bars: [REQUIRED: integer 2-10, e.g., 5] # Fixed cooldown period

## Overfitting Prevention Configuration
min_trades_per_combination: [REQUIRED: integer 30-100, e.g., 50] # Minimum trades for statistical significance
max_parameters_optimized: [REQUIRED: integer 3-5, e.g., 5] # Maximum parameters to optimize simultaneously
out_of_sample_decay_threshold: [REQUIRED: float 0.15-0.30, e.g., 0.20] # Maximum allowed performance decay
statistical_significance_p: [REQUIRED: float 0.01-0.10, e.g., 0.05] # p-value threshold for significance

## Resource Management
max_parallel_runs: [REQUIRED: integer 1-8, e.g., 4] # Parallel backtest execution
memory_limit_gb: [REQUIRED: integer 4-32, e.g., 8] # Maximum memory usage
timeout_minutes_per_run: [REQUIRED: integer 5-30, e.g., 15] # Timeout per parameter combination

---

## Validation Checklist
Before running, ensure:
- [ ] All [REQUIRED] parameters have values
- [ ] Parameter ranges are logical (min < max, reasonable steps)
- [ ] Dataset date range supports walk-forward analysis requirements
- [ ] Search strategy and max_combinations are appropriate for parameter space size
- [ ] Resource limits are appropriate for your system
- [ ] Overfitting prevention thresholds are conservative

## Usage
Once completed, run: `/optimize`
The system will validate this configuration and execute the parameter optimization study.

## Parameter Range Guidelines

### Search Strategy Selection
- **Grid Search**: Exhaustive testing, best for ≤3 parameters with small ranges
- **Random Search**: Efficient sampling, good for ≥4 parameters or large spaces  
- **Bayesian Search**: Most efficient, learns from previous combinations

### Parameter Range Sizing
- **Grid Search**: Total combinations = product of all (max-min)/step values
- **Random/Bayesian**: Will sample up to max_combinations from the defined ranges
- **Recommendation**: Start with 100-500 combinations for initial exploration

### Walk-Forward Validation
- **Training Period**: 24 months recommended for stable parameter estimation
- **Validation Period**: 6 months provides sufficient out-of-sample data
- **Rolling Step**: 3-month advances balance data overlap with computation time
- **Minimum Windows**: 5 validation periods ensure robust stability assessment

### Overfitting Prevention
- **Parameter Limit**: Maximum 5 parameters prevents over-optimization
- **Trade Minimum**: 30+ trades per combination ensures statistical validity
- **Performance Decay**: 20% threshold flags potential overfitting
- **P-Value**: 0.05 threshold ensures statistical significance

## Expected Output Structure
The optimization study will generate:
- `/data/optimization/{study_id}/optimization_summary.json` - Best parameter configurations and study results
- `/data/optimization/{study_id}/parameter_sweep.csv` - Complete results matrix
- `/data/optimization/{study_id}/walkforward_results.json` - Time-series validation data
- `/data/optimization/{study_id}/robustness_analysis.json` - Parameter sensitivity analysis
- `/data/optimization/{study_id}/validation_tests.json` - Statistical significance tests
- `/data/optimization/{study_id}/parameter_surfaces/` - 3D visualization data
- Individual run directories in `/data/runs/{run_id}/` for each parameter combination

## Example Configuration
```markdown
# Minimal example for RSI strategy optimization
study_name: "RSI_Basic_Optimization_2024"
search_strategy: random
max_combinations: 200
random_seed: 42

training_period_months: 24
validation_period_months: 6
rolling_step_months: 3
min_validation_windows: 4

universe: binance_usdt
timeframe: 4h
start_date: 2021-01-01
end_date: 2024-12-31

primary_metric: sortino_ratio
minimize_metric: false

rsi_period_min: 10
rsi_period_max: 20
rsi_period_step: 2

rsi_threshold_min: 25
rsi_threshold_max: 35
rsi_threshold_step: 2.5

# ... (other required parameters)
```