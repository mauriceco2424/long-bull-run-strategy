# Optimize Trading Strategy Parameters

---
description: Execute parameter sweep with walk-forward analysis and overfitting prevention
argument-hint: 
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-optimization-runner** agent to execute a comprehensive parameter optimization study with walk-forward validation and overfitting prevention.

## Optimization Study Parameters
- **Configuration**: Reads `optimization_config.md` for parameter ranges and search strategy
- **Study ID**: Auto-generated unique identifier for this optimization study

## Parameter Optimization Tasks

### 1. **Configuration Validation & Setup**
- Read and validate `optimization_config.md` completeness
- Verify all parameter ranges are properly defined with min/max/step values
- Check search strategy selection (grid/random/Bayesian)
- Validate walk-forward configuration (training/validation periods)
- Confirm optimization metric and constraints are specified
- Generate unique study ID and create optimization directory structure

### 2. **Parameter Space Generation**
- **Grid Search**: Generate all combinations within defined parameter ranges
- **Random Search**: Generate specified number of random parameter combinations
- **Bayesian Search**: Initialize Bayesian optimization framework
- **Combination Validation**: Ensure all parameter combinations are feasible
- **Estimation**: Calculate total combinations and provide time/resource estimates

### 3. **Walk-Forward Analysis Setup**
- **Data Division**: Split historical data into training/validation windows
- **Window Configuration**: Implement 3:1 in-sample/out-of-sample standard ratio
- **Rolling Schedule**: Define rolling window advancement schedule
- **Period Validation**: Ensure sufficient data for each validation window
- **Regime Detection**: Identify market regime changes across periods

### 4. **Parameter Sweep Execution**
- **Batch Processing**: Execute parameter combinations in efficient batches
- **Engine Coordination**: Interface with trading engine for each parameter set
- **Progress Tracking**: Unified progress bar across all combinations
- **Resource Management**: Monitor memory usage and computational resources
- **Error Handling**: Robust recovery from individual parameter combination failures
- **Intermediate Results**: Save partial results for recovery and monitoring

### 5. **Walk-Forward Validation**
- **Training Phase**: Optimize parameters on in-sample data for each window
- **Validation Phase**: Test optimized parameters on out-of-sample data
- **Rolling Forward**: Advance time windows and repeat optimization
- **Performance Tracking**: Monitor performance consistency across periods
- **Regime Adaptation**: Assess parameter stability across market conditions

### 6. **Overfitting Prevention & Statistical Validation**
- **Parameter Complexity Limits**: Enforce maximum 5 optimizable parameters
- **Trade Count Validation**: Ensure ≥30 trades per parameter combination
- **Statistical Significance Testing**: Calculate p-values for performance metrics
- **Out-of-Sample Performance Monitoring**: Track in-sample vs out-of-sample decay
- **Data-Snooping Bias Detection**: Flag suspicious parameter combinations
- **Robustness Testing**: Assess parameter sensitivity to small changes

### 7. **Optimization Artifacts Generation**
Create comprehensive study outputs in `/data/optimization/{study_id}/`:

- **`optimization_summary.json`**: 
  - Best parameter configurations (conservative/balanced/aggressive)
  - Overall study performance and robustness metrics
  - Optimization methodology and validation results
  - Statistical significance assessments

- **`parameter_sweep.csv`**: 
  - Complete matrix of all parameter combinations tested
  - Performance metrics for each combination
  - Validation window results and consistency scores
  - Overfitting risk assessments

- **`walkforward_results.json`**: 
  - Time-series validation performance across all periods
  - Parameter stability across market regimes
  - Regime adaptation and sensitivity analysis
  - Rolling optimization results

- **`robustness_analysis.json`**: 
  - Parameter sensitivity heat maps
  - Stability metrics and robustness scores
  - Performance landscape analysis
  - Optimal parameter zone identification

- **`validation_tests.json`**: 
  - Statistical significance test results
  - Overfitting risk scores and warnings
  - Confidence intervals for key metrics
  - Data-snooping bias assessments

- **`parameter_surfaces/`**: 
  - 3D parameter performance surface data
  - Robustness heat map data for visualization
  - Performance contour data
  - Optimal zone boundary definitions

### 8. **Individual Run Integration**
- **Run Directory Creation**: Generate individual `/data/runs/{run_id}/` for each parameter combination
- **Manifest Enhancement**: Add optimization study metadata to individual run manifests
- **Cross-Referencing**: Link individual runs to parent optimization study
- **Analysis Integration**: Coordinate with analyzer for individual run processing
- **Visualization Generation**: Create individual run visualizations using enhanced system

### 9. **Statistical Analysis & Reporting**
- **Performance Distribution Analysis**: Analyze distribution of results across parameter space
- **Regime Performance Analysis**: Assess performance across different market conditions
- **Stability Assessment**: Measure parameter performance consistency
- **Risk-Adjusted Analysis**: Calculate Sharpe, Sortino, and other risk-adjusted metrics
- **Benchmark Comparison**: Compare optimization results against simple benchmarks

### 10. **Quality Gates & Validation**
- **Minimum Trade Requirements**: Enforce statistical significance thresholds
- **Out-of-Sample Validation**: Confirm results hold in validation periods
- **Overfitting Detection**: Flag and warn about potential curve-fitting
- **Parameter Stability**: Verify consistent performance across time windows
- **Statistical Significance**: Validate performance metrics are statistically significant

## Expected Outputs

- **Optimization Study Directory**: Complete optimization artifacts ready for evaluator analysis
- **Individual Parameter Runs**: Enhanced run directories with optimization metadata
- **Performance Rankings**: Ranked parameter configurations with robustness scores
- **Statistical Validation Results**: Comprehensive statistical analysis of optimization study
- **Overfitting Assessments**: Clear warnings and risk scores for parameter combinations
- **Implementation Guidance**: Specific recommendations for parameter deployment

## Success Criteria
- Parameter sweep executed successfully across all defined combinations
- Walk-forward validation completed with multiple out-of-sample periods
- Statistical significance confirmed for recommended parameter configurations
- Overfitting prevention measures applied and documented
- Comprehensive optimization artifacts generated ready for evaluator consumption
- Clear recommendations provided for parameter implementation

## Overfitting Prevention Standards
- **Maximum Parameters**: Limit optimization to ≤5 parameters simultaneously
- **Minimum Data Requirements**: ≥30 trades per parameter combination for validity
- **Out-of-Sample Validation**: Performance must maintain within 20% of in-sample results
- **Statistical Significance**: p-values <0.05 for key performance metrics
- **Stability Requirements**: Parameters must show consistent performance across validation windows

## Progress Reporting
- **Unified Progress Bar**: `Optimizing parameters... ████████░░░░ 60% (~45 min remaining)`
- **Phase Breakdown**: Configuration → Generation → Execution → Validation → Analysis
- **Combination Tracking**: Progress through total parameter combinations
- **ETA Integration**: Based on combination complexity and historical execution times

Please use the trading-optimization-runner agent to execute comprehensive parameter optimization with walk-forward validation and overfitting prevention.