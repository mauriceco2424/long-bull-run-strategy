# Analyze Optimization Study Results

---
description: Process parameter optimization study data into comprehensive analysis artifacts
argument-hint: [study_id]
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-optimization-analyzer** agent to process the parameter optimization study data into comprehensive analysis artifacts including parameter performance matrices and optimization visualizations.

## Optimization Analysis Parameters
- **Study ID**: $ARGUMENTS (defaults to most recent optimization study if not specified)

## Analysis Tasks

### 1. **Study Data Validation & Processing**
- **Input Validation**: Verify optimization study completeness and individual run integrity
- **Parameter Matrix Assembly**: Aggregate performance metrics across all parameter combinations
- **Data Quality Checks**: Validate consistency across individual runs in the study
- **Missing Data Handling**: Identify and handle failed parameter combinations

### 2. **Optimization Artifact Generation**
Create canonical optimization analysis outputs in `/data/optimization/{study_id}/analysis/`:

- **`parameter_performance_matrix.csv`**: Complete performance grid with:
  - Parameter combinations and corresponding performance metrics
  - CAGR, Sortino, Sharpe, MaxDD, win_rate, total_trades for each combination
  - Walk-forward validation results across time periods
  - Statistical significance indicators and confidence intervals

- **`optimization_summary.json`**: Study-level metrics including:
  - Best parameter configurations (conservative/balanced/aggressive profiles)
  - Performance distribution statistics across parameter space
  - Robustness metrics and stability assessments
  - Optimization convergence and search efficiency metrics

- **`robustness_analysis.json`**: Parameter sensitivity analysis:
  - Parameter stability across validation windows
  - Performance decay from in-sample to out-of-sample periods
  - Robustness scores and optimal parameter zone identification
  - Market regime adaptation capabilities

### 3. **Professional Optimization Visualization Generation**
Create publication-quality figures in `/data/optimization/{study_id}/figs/`:

**Parameter Performance Visualizations:**
- **3D Parameter Surface**: Performance landscape across parameter combinations
- **Parameter Robustness Heatmaps**: Stability and consistency across validation periods  
- **Performance Distribution Histograms**: Distribution analysis across parameter space
- **Walk-Forward Analysis Charts**: Parameter performance across different time periods

**Convergence and Efficiency Analysis:**
- **Optimization Convergence**: Search algorithm efficiency and convergence patterns
- **Parameter Sensitivity Plots**: Individual parameter impact on performance
- **Regime Performance Analysis**: Parameter effectiveness across market conditions
- **Statistical Validation Charts**: Significance testing and confidence interval visualizations

### 4. **Statistical Validation & Quality Assessment**
- **Parameter Significance Testing**: Statistical validation of parameter importance
- **Overfitting Detection**: In-sample vs out-of-sample performance decay analysis
- **Robustness Assessment**: Parameter stability and consistency evaluation
- **Performance Attribution**: Identify which parameters contribute most to alpha

### 5. **Optimization Study Registry Update**
- Use lockfile protocol for `/data/optimization/optimization_registry.csv`
- Atomically append study analysis results with study metadata
- Cross-reference with individual run registry entries
- **Unified progress bar**: `Analyzing optimization study... ████████░░░░ 75% (~3 min remaining)`

## Expected Outputs
- **Parameter performance matrix** with comprehensive statistics for all combinations
- **Professional optimization visualizations** ready for report inclusion:
  - 3D parameter performance surfaces with optimal regions highlighted
  - Parameter robustness heatmaps showing stability across validation periods
  - Statistical validation charts with significance indicators
- **Robustness analysis report** with parameter stability assessments
- **Optimization summary** with key findings and recommended parameter zones
- **Ready for evaluation** with `/evaluate-optimization`

## Success Criteria
- All parameter combinations processed and analyzed successfully
- Professional optimization visualizations generated with clear insights
- Statistical validation completed with significance assessments
- Parameter robustness analysis provides clear stability rankings
- All artifacts ready for optimization evaluator consumption

Please use the trading-optimization-analyzer agent to perform comprehensive optimization study analysis with parameter performance assessment and professional visualization generation.