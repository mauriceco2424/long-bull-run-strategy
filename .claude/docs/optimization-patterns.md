# Optimization Guide

This guide explains how the universal speed optimization system works and how agents can leverage it effectively.

## Overview

The trading framework includes advanced optimization infrastructure that provides **significant speedup** for parameter sweeps while maintaining accuracy. These optimizations are **strategy-agnostic** and work with any trading strategy.

## Core Optimization Components

### 1. FilterGateManager - Universal Filter Optimization

**Purpose**: Provides monotone filter caching for any threshold-based strategy filters.

**Location**: `scripts/engine/core/filter_gate_manager.py`

**Key Features**:
- **Monotone Caching**: If RSI > 30 passes for a symbol, automatically cache for RSI > 25, 20, 15, etc.
- **Universal Application**: Works with ANY threshold-based filter (RSI, Volume, Price, etc.)
- **Smart Symbol Elimination**: Removes symbols that can't pass stricter filters

**Usage Examples for Agents**:

```python
# Example 1: RSI-based strategy filter
manager.register_filter(
    "rsi_threshold", 
    FilterType.MONOTONE_GREATER,
    lambda data, threshold: data['rsi_14'] > threshold,
    ["rsi_14"],
    "RSI above threshold filter"
)

# Apply filter with optimization
passing_symbols = manager.apply_filter(
    "rsi_threshold", 30, ohlcv_data, features_data, current_time
)

# Example 2: Volume-based strategy filter
manager.register_filter(
    "volume_threshold",
    FilterType.MONOTONE_GREATER, 
    lambda data, threshold: data['volume'] > threshold,
    ["volume"],
    "Volume above threshold filter"
)
```

**Speed Benefit**: Significant speedup for strategies with restrictive parameter sets.

### 2. DataProcessor - Feature Calculation Optimization

**Purpose**: Optimizes technical indicator calculations through dependency management and caching.

**Location**: `scripts/engine/data/data_processor.py`

**Key Features**:
- **Dependency Optimization**: SMA(50) reuses SMA(20) calculations
- **Feature Caching**: Avoid recomputing identical features across parameter sets
- **Universal Patterns**: Works with any strategy's technical indicators

**Usage Examples for Agents**:

```python
# Any strategy benefits automatically from optimization
features = processor.calculate_features(ohlcv_data, ["rsi_14", "sma_20", "sma_50"])
# SMA(50) will automatically reuse SMA(20) intermediate calculations

# Feature dependency is handled automatically:
# - Bollinger Bands reuse SMA and standard deviation calculations
# - MACD reuses EMA calculations
# - RSI periods share delta calculations
```

**Speed Benefit**: Notable speedup overall through calculation sharing.

### 3. ReferenceEngine - Baseline Optimization

**Purpose**: Reduces symbol universe based on reference run activity patterns.

**Location**: `scripts/engine/optimization/reference_engine.py`

**Key Features**:
- **Universe Reduction**: Test only symbols that showed activity in reference run
- **Parameter Sensitivity**: More restrictive parameters use smaller universe
- **Universal Application**: Works with any strategy's parameter types

**Usage Examples for Agents**:

```python
# Store reference run (e.g., RSI(30) baseline)
reference = engine.store_reference_run(
    "baseline_rsi_30",
    {'rsi_period': 30, 'sma_period': 20},
    backtest_results
)

# Get optimized universe for similar parameters
optimized_symbols, metadata = engine.get_optimized_universe(
    all_symbols, {'rsi_period': 25}  # More restrictive than reference
)
# Returns subset of symbols that were active in reference run
```

**Speed Benefit**: Substantial speedup for parameter sweeps with focused symbol activity.

## Agent Integration Patterns

### Builder Agent Enhancement

**When**: `/build-engine` command execution

**Optimization Integration**:
1. **Auto-Detection**: Automatically detect if optimization pipeline will follow
2. **Speed Infrastructure**: Include FilterGateManager and optimization components
3. **Configuration**: Enable feature optimization by default

```python
# Builder should automatically include in generated engine:
from .core.filter_gate_manager import FilterGateManager
from .optimization.reference_engine import ReferenceEngine

# Auto-register common filters
self.filter_gate_manager.register_common_filters()
```

### Optimizer Agent Usage

**When**: `/run-optimization` command execution

**Location**: `scripts/optimization/optimization_engine.py`

**Key Patterns**:
1. **Shared Data Loading**: Load OHLCV once, reuse for all parameter combinations
2. **Reference Run Establishment**: Use first parameter set as baseline
3. **Universe Optimization**: Reduce symbol universe for each parameter combination
4. **Filter Gate Leverage**: Use cached filter results across similar parameters

```python
# Optimizer agent should leverage:
engine = OptimizationEngine("optimization_config.json")
results = engine.execute_parameter_sweep()

# Engine automatically applies:
# - Feature caching across parameter sets
# - Universe reduction based on reference run
# - Filter gate optimization for threshold parameters
```

### Single-Analyzer Integration

**When**: `/run` and `/analyze-single-run` commands

**Optimization Patterns**:
- **Automatic**: Speed optimizations enabled by default in BacktestEngine
- **Transparent**: No changes needed - optimizations work automatically
- **Reporting**: Include optimization stats in performance metrics

## Command-Level Integration

### Enhanced /build-engine

**Automatic Optimizations**:
- Include FilterGateManager in generated engine
- Enable feature calculation optimization
- Register common filter patterns
- Add reference engine infrastructure

### New /run-optimization

**Optimization Workflow**:
1. **Context Detection**: Determine parameter ranges and optimization target
2. **Reference Establishment**: Execute baseline parameter set
3. **Universe Optimization**: Reduce symbol universe for subsequent runs
4. **Parallel Execution**: Leverage shared data structures
5. **Results Compilation**: Generate optimization analysis

### Standard /run

**Transparent Benefits**:
- Feature caching automatically enabled
- Filter optimizations work transparently
- No strategy-specific changes needed

## Performance Expectations

### Without Optimization (Current State)
- 100 parameter combinations = 100x single run time
- Each combination processes full symbol universe
- Features recalculated from scratch each time
- No filter result reuse

### With Optimization (New System)
- 100 parameter combinations = substantially faster than single run time
- **Filter Gates**: Significant speedup for restrictive parameters
- **Feature Caching**: Notable speedup through calculation sharing
- **Universe Reduction**: Substantial speedup for focused strategies
- **Combined Effect**: Major performance improvement

## Configuration Options

### Enable/Disable Optimizations

```json
{
  "enable_feature_optimization": true,
  "enable_universe_reduction": true,
  "max_universe_reduction_pct": 0.5,
  "enable_parallel_execution": false,
  "max_workers": 4
}
```

### Filter Gate Configuration

```python
# Agents can register custom filters
manager.register_filter(
    "custom_momentum_filter",
    FilterType.MONOTONE_GREATER,
    lambda data, threshold: data['momentum_10'] > threshold,
    ["momentum_10"],
    "Custom momentum filter"
)
```

## Best Practices for Agents

### 1. Always Use Universal Patterns
- Register filters using FilterGateManager instead of inline filtering
- Use DataProcessor for feature calculations instead of custom computation
- Leverage ReferenceEngine for parameter sweep optimization

### 2. Strategy-Agnostic Implementation
- Don't hard-code specific parameter names or thresholds
- Use generic patterns that work with any strategy type
- Allow configuration-driven optimization settings

### 3. Performance Monitoring
- Include optimization stats in results reporting
- Track cache hit rates and speedup factors
- Monitor universe reduction effectiveness

### 4. Error Handling
- Graceful fallback when optimizations fail
- Maintain accuracy even if speed optimizations disabled
- Log optimization decisions for debugging

## Example: Complete Agent Integration

```python
# Builder Agent - Generate optimized engine
class OptimizedBacktestEngine:
    def __init__(self, config):
        # Standard components
        self.portfolio_manager = PortfolioManager(config)
        self.risk_manager = RiskManager(config)
        
        # Optimization components (automatic)
        self.filter_gate_manager = FilterGateManager()
        self.reference_engine = ReferenceEngine() 
        self.data_processor = DataProcessor(config)  # With optimization enabled
        
        # Register universal filters
        self.filter_gate_manager.register_common_filters()

# Strategy Implementation - Universal patterns
class AnyStrategy:
    def generate_signals(self, current_time, ohlcv_data, features_data, portfolio_state):
        # Use filter gate for efficient symbol filtering
        rsi_symbols = self.filter_gate_manager.apply_filter(
            "rsi_threshold", self.rsi_oversold, {}, features_data, current_time
        )
        
        # Feature calculation automatically optimized
        signals = []
        for symbol in rsi_symbols:
            # Generate signals using optimized features
            signals.append(self._create_signal(symbol, features_data[symbol]))
        
        return signals

# Optimizer Agent - Leverage all optimizations
class ParameterSweep:
    def execute(self):
        # Shared data loading (once for all combinations)
        shared_data = self.data_processor.load_and_cache_data()
        
        # Reference run establishment
        reference_params = self.parameter_combinations[0]
        reference_results = self._execute_with_optimization(reference_params, shared_data)
        self.reference_engine.store_reference_run("baseline", reference_params, reference_results)
        
        # Optimized parameter testing
        for params in self.parameter_combinations[1:]:
            # Universe reduction automatically applied
            optimized_universe, metadata = self.reference_engine.get_optimized_universe(
                self.all_symbols, params
            )
            
            # Execute with optimized universe and cached features
            results = self._execute_with_optimization(params, shared_data, optimized_universe)
            self.results.append((params, results))
```

## Troubleshooting

### Low Speedup Factors
- **Cause**: Parameters not monotone or no universe reduction possible
- **Solution**: Focus on filter gate optimization and feature caching

### Cache Misses
- **Cause**: Parameter ranges too diverse or cache invalidation
- **Solution**: Use reference runs and group similar parameters

### Memory Usage
- **Cause**: Large feature caches or symbol universes
- **Solution**: Implement cache size limits and LRU eviction

### Accuracy Concerns
- **Cause**: Aggressive universe reduction or filter shortcuts
- **Solution**: Validate optimization results against unoptimized baseline

This optimization system ensures that any strategy can achieve significant speedup during parameter sweeps while maintaining accuracy and flexibility.