# Test Parameter Configuration
> Auto-generated from: docs/test/test_SMR.md
> Generated: 2025-09-10
> Strategy: RSI Mean Reversion Test Strategy

## Strategy Parameters

### RSI Indicator Settings
```yaml
# RSI calculation parameters
rsi_period: 14              # RSI lookback period (bars)
oversold_threshold: 30.0     # Entry trigger when RSI < this value
overbought_threshold: 70.0   # Exit trigger when RSI > this value
```

### Risk Management
```yaml
# Position and risk controls
stop_loss_pct: 0.05         # Stop loss percentage (5%)
position_size_pct: 0.10     # Position size as % of equity (10%)
max_positions: 3            # Maximum concurrent positions
min_notional: 50.0          # Minimum order size in USD
```

### Universe Configuration
```yaml
# Trading universe and data settings
symbols:
  - BTCUSDT
  - ETHUSDT
  - ADAUSDT

timeframe: "1h"             # Data timeframe
exchange: "binance"         # Exchange for data and execution
```

### Backtest Period
```yaml
# Date range for backtesting (test mode: 6 months)
start_date: "2023-01-01"
end_date: "2023-06-30"
```

### Execution Settings
```yaml
# Order execution configuration
execution_mode: "next_bar_open"  # Execute trades at next bar open
slippage_model: "fixed"          # Slippage model type
slippage_bps: 10                 # Slippage in basis points
fee_model: "percentage"          # Fee calculation model
fee_rate: 0.001                  # Trading fee (0.1%)
```

### Portfolio Settings
```yaml
# Portfolio and accounting configuration
initial_capital: 10000.0         # Starting capital in USD
accounting_mode: "mark_to_market" # Portfolio accounting method
base_currency: "USDT"            # Base currency for portfolio
```

### Data Requirements
```yaml
# Minimum data requirements for strategy
min_history_bars: 50            # Minimum bars needed for indicators
warmup_period: 14               # Warmup period for RSI calculation
data_quality_checks: true       # Enable data validation
```

### Performance Optimization
```yaml
# Engine optimization settings
use_filter_gate_manager: true   # Enable filter optimization
use_reference_engine: true      # Enable reference calculations
cache_features: true            # Cache indicator calculations
vectorize_calculations: true    # Use vectorized operations
parallel_processing: false      # Disable for test mode (small universe)
```

### Logging and Monitoring
```yaml
# Debug and monitoring settings
log_level: "INFO"              # Logging verbosity
progress_reporting: true       # Enable progress bars
save_intermediate_results: true # Save debug outputs
performance_tracking: true     # Track execution metrics
```

## Validation Rules

### Parameter Constraints
- `rsi_period`: Must be >= 2
- `oversold_threshold`: Must be in range (0, 50)
- `overbought_threshold`: Must be in range (50, 100)
- `stop_loss_pct`: Must be in range (0, 1)
- `position_size_pct`: Must be in range (0, 1]
- `min_notional`: Must be > 0

### Cross-Parameter Validation
- `oversold_threshold` must be < `overbought_threshold`
- `position_size_pct * initial_capital` must be >= `min_notional`
- `max_positions * position_size_pct` must be <= 1.0

## Notes
- This is a TEST configuration for skeleton validation
- Small universe (3 symbols) and short period (6 months) for fast execution
- Accounting validation with Universal Quality Gate enabled
- All parameters optimized for testing, not production performance