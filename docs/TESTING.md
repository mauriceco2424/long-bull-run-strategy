# Trading Framework Testing Guide

This document provides comprehensive testing procedures to validate the trading strategy skeleton framework functionality.

## Overview

The testing framework ensures that all components of the trading skeleton work correctly before users encounter problems. This includes:
- Core engine functionality and accounting validation
- Complete slash command workflow testing
- Parameter optimization pipeline validation
- Agent script completeness verification
- Error handling and edge case testing

## Quick Validation Commands

**Run all tests quickly:**
```bash
python scripts/run_full_test_suite.py
```

**Individual test commands:**
```bash
# Test core engine
python run_test.py
PYTHONPATH=. python -m scripts.engine.backtest test_parameter_config.md --test-mode --validate-accounting

# Test single analysis
python scripts/single_analysis/analyze_test_run.py

# Test optimization framework
python test_optimization_simple.py
```

## 1. Core Engine Testing

### Test 1.1: Basic Engine Functionality
```bash
python run_test.py
```

**Expected Output:**
- Backtest completes successfully
- Final Equity: $10,000.00 (no trades expected in test period)
- Zero accounting discrepancies
- Daily series: ~950 records
- No critical errors

**Success Criteria:**
- ✅ Engine initializes without errors
- ✅ Configuration parsing works correctly
- ✅ Data loading and processing complete
- ✅ Accounting validation passes
- ✅ Portfolio state is consistent

### Test 1.2: Comprehensive Backtest Validation
```bash
PYTHONPATH=. python -m scripts.engine.backtest test_parameter_config.md --test-mode --validate-accounting
```

**Expected Output:**
- Configuration: test_parameter_config.md loaded successfully
- Backtest completed: $10,000.00
- Warning about deprecated fillna method (non-critical)
- No lookahead bias violations
- Accounting identity maintained

**Success Criteria:**
- ✅ Config parser handles markdown format
- ✅ Universe configuration extracted (BTCUSDT, ETHUSDT, ADAUSDT)
- ✅ Backtest section created with initial_capital: 10000.0
- ✅ Timeframe configuration: 1h
- ✅ No accounting violations

### Test 1.3: Configuration Parser Validation

The config parser must correctly handle:
- YAML list format for symbols (`- BTCUSDT`)
- Comment stripping from values (`10000.0 # Starting capital`)
- Section extraction from strategy_parameters
- Type conversion (strings → floats/integers/booleans)

## 2. Slash Command Pipeline Testing

### Complete Workflow Test
```bash
# Use slash commands via Claude Code interface
/validate-setup --test
/validate-strategy --test
/plan-strategy --test
/build-engine --test
/run --test
/analyze-single-run --test
/evaluate-single-run --test
```

**Expected Workflow:**
1. **Setup Validation**: System prerequisites verified
2. **Strategy Validation**: RSI strategy template validated (SIMPLE complexity)
3. **Strategy Planning**: Development plan created with 4-phase workflow
4. **Engine Building**: Engine built, parameter config auto-generated
5. **Backtest Execution**: Run completed with proper artifacts
6. **Analysis**: Complete analysis with visualizations generated
7. **Evaluation**: Performance evaluated, reports generated

**Success Criteria:**
- ✅ All 7 commands execute without critical errors
- ✅ Pipeline gates enforce proper sequencing
- ✅ Each phase produces required outputs for next phase
- ✅ Documentation updates applied correctly
- ✅ Test artifacts organized properly

**Generated Artifacts:**
- `test_parameter_config.md` - Auto-generated configuration
- `data/test_runs/test_run_001/` - Complete run artifacts
- `docs/test/workflow_test_results.md` - Test documentation
- `docs/notices/SER/SER_test_run_001.json` - Evaluation report

## 3. Optimization Pipeline Testing

### Test 3.1: Parameter Sweep Framework
```bash
python test_optimization_simple.py
```

**Expected Results:**
- 150 parameter combinations tested (RSI: 10-20, thresholds: 25-75)
- Walk-forward validation with 5 windows
- Best parameters: RSI=14, Oversold=32.5, Overbought=67.5
- Overfitting assessment: MEDIUM risk
- Statistical validation results

**Success Criteria:**
- ✅ Parameter sweep executes without errors
- ✅ Walk-forward validation working
- ✅ Statistical significance testing functional
- ✅ Overfitting detection operational
- ✅ Results saved to `data/optimization/test_study/`

### Test 3.2: Optimization Evaluation
The optimization evaluation script validates:
- Parameter significance analysis
- Robustness testing across time periods
- Strategic parameter interpretation
- Deployment readiness assessment

## 4. Agent Script Validation

### Required Scripts Status
- ✅ `scripts/engine/backtest.py` - Core backtest engine
- ✅ `scripts/analyzer/run_executor.py` - Run coordination
- ✅ `scripts/single_analysis/analyze_test_run.py` - Analysis functionality
- ✅ `scripts/single_evaluation/evaluator.py` - Evaluation capabilities
- ✅ `scripts/optimization/optimization_engine.py` - Parameter sweeps
- ✅ `scripts/opt_evaluation/evaluate_optimization.py` - Optimization analysis

### Import Path Validation
All agent scripts handle both relative and absolute imports correctly for:
- Direct execution (`python script.py`)
- Module execution (`python -m scripts.module.script`)
- Agent system execution

## 5. Error Handling & Edge Cases

### Test 5.1: Invalid Configuration
```bash
# Test with missing config file
PYTHONPATH=. python -m scripts.engine.backtest nonexistent_config.md
```
**Expected**: Clear error message about missing file

### Test 5.2: Data Quality Issues
The framework handles:
- Missing data bars (forward-fill strategy)
- Invalid symbol names (graceful failure)
- Insufficient history (warmup period validation)

### Test 5.3: Resource Constraints
- Memory usage monitoring during large parameter sweeps
- Timeout handling for long-running optimizations
- Disk space validation before artifact generation

## 6. Performance Baselines

### Execution Times (Test Environment)
- Basic backtest: ~8-10 seconds
- Single analysis: ~10-12 seconds
- Parameter sweep (150 combinations): <1 second (simulated)
- Complete slash command workflow: ~2-3 minutes

### Memory Requirements
- Basic backtest: <100MB
- Parameter optimization: <500MB per worker
- Analysis with visualizations: <200MB

### Data Processing
- 950 daily records (6 months, 1h timeframe, 3 symbols)
- ~50 bars minimum for indicator warmup
- Data quality checks on all OHLCV data

## 7. Troubleshooting

### Common Issues

**Config Parser Errors:**
- Ensure YAML sections use proper indentation
- Comments must use `#` character
- List items must start with `- `

**Import Errors:**
- Use `PYTHONPATH=.` for module execution
- Check that all required dependencies are installed
- Verify script paths in sys.path modifications

**Backtest Failures:**
- Verify initial_capital > min_notional requirements
- Check symbol universe availability
- Ensure sufficient historical data

**Performance Issues:**
- Enable quiet mode: `python scripts/quiet_mode.py on`
- Check available memory before large parameter sweeps
- Monitor disk space in data/ directories

### Debug Commands
```bash
# Check configuration parsing
python -c "from scripts.engine.utils.config_parser import ConfigParser; print(ConfigParser().parse_config('test_parameter_config.md'))"

# Verify agent imports
python -c "from scripts.single_analysis.analyze_test_run import EnhancedSingleRunAnalyzer; print('✓ Analysis agent OK')"

# Test quiet mode
python scripts/quiet_mode.py status
```

## 8. Validation Checklist

Before deploying the skeleton, verify:

### Core Functionality
- [ ] `python run_test.py` completes successfully
- [ ] Config parser handles test_parameter_config.md correctly
- [ ] Accounting validation passes without violations
- [ ] All agent scripts import and initialize properly

### Workflow Integration
- [ ] Complete slash command sequence executes
- [ ] All pipeline gates enforce proper dependencies
- [ ] Required artifacts generated at each phase
- [ ] Documentation updates applied correctly

### Performance & Optimization
- [ ] Parameter sweep framework operational
- [ ] Speed optimizations (FilterGateManager, ReferenceEngine) integrated
- [ ] Walk-forward validation working
- [ ] Overfitting prevention measures active

### Error Handling
- [ ] Graceful failure with invalid configurations
- [ ] Resource constraint handling functional
- [ ] Clear error messages for common issues
- [ ] Debug information available when needed

## 9. Future Claude Instances

**To validate the skeleton quickly:**
1. Run `python scripts/run_full_test_suite.py`
2. Check that all tests pass with ✅ status
3. Review any warnings or recommendations
4. Verify all key artifacts are generated correctly

**For deeper investigation:**
1. Follow individual test procedures in this document
2. Check specific component functionality as needed
3. Use troubleshooting section for common issues
4. Review performance baselines for regression testing

The skeleton is considered validated when all tests pass and the complete workflow from strategy definition to evaluation completes successfully.