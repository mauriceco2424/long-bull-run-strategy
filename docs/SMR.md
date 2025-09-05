# Strategy Master Report (SMR) - Template
**Version**: smr-v1.0.0  
**Last Updated**: 2025-09-05  

## Strategy Overview
- **Name**: [Strategy Name - TBD]
- **Type**: [Strategy Type - TBD]
- **Universe**: [Asset Universe - TBD]
- **Timeframes**: [Primary and Secondary Timeframes - TBD]

## Entry Logic
### Filters
- **Filter 1**: [Description - TBD]
- **Filter 2**: [Description - TBD]
- **Filter 3**: [Description - TBD]

### Entry Signals  
- **Signal Type**: [TBD - momentum, mean reversion, breakout, etc.]
- **Parameters**: [TBD - lookback periods, thresholds, etc.]
- **Position Sizing**: [TBD - fixed %, volatility-adjusted, etc.]

## Exit Logic
### Take Profit (TP)
- **Method**: [TBD - fixed %, volatility-adjusted, trailing, etc.]
- **Execution**: Next bar open after signal

### Stop Loss (SL)  
- **Method**: [TBD - fixed %, ATR-based, trailing, etc.]
- **Execution**: Next bar open after signal

### Time-based Exit
- **Max Hold Period**: [TBD] periods
- **Execution**: Next bar open after timeout

## Risk Management
- **Max Concurrent Positions**: [TBD]
- **Max Position Size**: [TBD]% of equity
- **Max Portfolio Heat**: [TBD]% of equity at risk
- **Correlation Limits**: [TBD]
- **Additional Constraints**: [TBD]

## Feature Definitions
### Price Features
- **Returns**: [Specify periods - TBD]
- **Volatility**: [Specify methods and windows - TBD]
- **Volume**: [Specify normalization methods - TBD]

### Custom Features
- **Feature Set 1**: [Description - TBD]
- **Feature Set 2**: [Description - TBD]
- **Feature Set 3**: [Description - TBD]

## Parameter Ranges
- **Parameter 1**: [Min, Max] values
- **Parameter 2**: [Min, Max] values
- **Parameter 3**: [Min, Max] values

## Realism Constraints
- **No Lookahead**: Features computed at t, actions at t+1 open
- **Execution Delays**: Minimum bars between signal and fill
- **Slippage**: Market impact modeling required
- **Fees**: Realistic fee structure per asset class
- **Liquidity**: Minimum volume/market cap requirements

---
*This document is maintained by the Orchestrator and updated via SDCNs*
*Replace all [TBD] sections with actual strategy specifications*