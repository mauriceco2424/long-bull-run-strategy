# Engine Master Report (EMR)
**Version**: emr-v1.0.0  
**Last Updated**: 2025-09-05  

## Engine Architecture

### Core Components
- **Data Ingestion**: OHLCV data in UTC with defined missing-bar policy
- **Feature Engine**: Compute features using data ≤ t for actions at t+1 
- **Signal Generation**: Entry/exit logic with no lookahead bias
- **Position Management**: Order handling, TP/SL, collision rules
- **Accounting**: Equity tracking with fees/slippage modeling

### Performance Specifications
- **Determinism**: Seeded random operations, reproducible results
- **Speed Targets**: Process 1-year, 300-symbol universe in <5 minutes
- **Memory**: Efficient caching with configurable limits
- **Validation**: No-lookahead, accounting identity, sanity checks

### Data Sources & Caching
- **Sources**: TBD (Exchange APIs, data vendors)
- **Cache Strategy**: Price/feature caches with (symbol, tf, feature_version, config_hash) keys
- **Missing Bar Policy**: TBD (forward fill, interpolate, skip)

### Fees & Slippage Model
- **Version**: v1.0.0
- **Maker/Taker Fees**: TBD per exchange
- **Slippage Model**: Linear impact model (TBD parameters)
- **Min Notional**: Rounded per exchange rules

## Interface Specification

### Inputs
- JSON configuration file
- Symbol universe definition
- Date range (start/end)
- Random seed for determinism

### Outputs
- Run manifest with metadata
- Trade records (fills)
- Event log (signals, filters)
- Time series data (equity, exposure)
- Performance metrics
- Validation results

## Quality Gates
1. Unit tests pass for all rule semantics
2. Golden-set parity maintained
3. Determinism verified (identical runs with same seed)
4. No lookahead bias detected
5. Accounting identity satisfied
6. Performance benchmarks within 10% of baseline

---
*This document is maintained by the Orchestrator and updated via ECNs*