# Compare Trading Strategy Runs

---
description: Compare multiple runs and rank strategies with statistical rigor
argument-hint: [run_ids_or_filter_criteria]
model: claude-3-5-opus-20240620
---

I need to use the **trading-evaluator** agent to perform rigorous comparison of multiple trading strategy runs, applying statistical analysis and ranking mechanisms by risk-adjusted performance and realism scores.

## Runs to Compare
$ARGUMENTS (run IDs, date range, or filter criteria)

## Comparison Framework

### 1. Run Selection & Data Gathering
**Run Identification:**
- Parse specified run IDs or apply filter criteria
- Validate run completeness and artifact availability
- Check run registry for status and metadata
- Ensure runs are comparable (same universe/period when appropriate)
- Group runs by configuration families for meaningful comparison

**Data Extraction:**
- Load metrics.json for each run
- Extract trades.csv and events.csv data
- Parse manifest.json for configuration details
- Load series.csv for time series analysis
- Import validation status and quality flags

### 2. Statistical Rigor Framework
**Multiple Testing Corrections:**
- Apply Bonferroni correction for multiple pairwise comparisons
- Implement False Discovery Rate (FDR) control
- Calculate family-wise error rates
- Adjust significance thresholds appropriately
- Document correction methodology

**Confidence Interval Analysis:**
- Bootstrap confidence intervals for key metrics
- Monte Carlo simulation for robustness testing
- Out-of-sample performance validation
- Cross-validation across time periods
- Parameter sensitivity analysis

**Statistical Significance Testing:**
- Pairwise comparison tests for performance metrics
- Non-parametric tests for non-normal distributions
- Effect size calculations (Cohen's d, etc.)
- Power analysis for comparison validity
- Minimum sample size requirements

### 3. Performance Metrics Comparison
**Risk-Adjusted Returns:**
- CAGR comparison with confidence intervals
- Sortino ratio ranking and statistical significance
- Sharpe ratio analysis with bootstrapped confidence bands
- Maximum drawdown comparison and recovery analysis
- Calmar ratio and other risk-adjusted metrics

**Trading Statistics:**
- Win rate comparison and statistical significance
- Average gain/loss analysis
- Trade frequency and density comparison
- Exposure metrics and utilization rates
- Risk metrics and volatility analysis

**Consistency Metrics:**
- Performance stability across time periods
- Rolling window performance analysis
- Regime-dependent performance assessment
- Parameter sensitivity scoring
- Robustness to market conditions

### 4. Mechanism & Feature Ranking
**Individual Mechanism Impact:**
- Isolate contribution of each feature/mechanism
- Calculate incremental alpha contribution
- Assess risk contribution vs. return enhancement
- Rank mechanisms by Sharpe improvement
- Evaluate parameter sensitivity for each mechanism

**Feature Importance Analysis:**
- Statistical significance of each feature
- Correlation analysis between features
- Feature interaction effects
- Stability across different market regimes
- Robustness to parameter variations

**Strategy Component Scoring:**
- Entry signal effectiveness
- Exit signal timing and profitability
- Risk management mechanism performance
- Position sizing impact assessment
- Filter effectiveness analysis

### 5. Realism & Implementation Scoring
**Execution Realism Assessment:**
- Liquidity constraints analysis
- Market impact assumptions validation
- Slippage model realism scoring
- Transaction cost accuracy assessment
- Implementation feasibility scoring

**Overfitting Detection:**
- In-sample vs out-of-sample performance gaps
- Parameter optimization artifacts
- Curve-fitting indicators
- Stability across different time periods
- Robustness to data perturbations

### 6. Market Regime Analysis
**Performance Across Market Conditions:**
- Bull market performance comparison
- Bear market resilience assessment
- Sideways market behavior analysis
- High volatility period performance
- Low liquidity period behavior

**Regime-Dependent Ranking:**
- Best performers in different market conditions
- Consistency across regimes
- Regime-specific optimization
- Adaptation mechanisms effectiveness
- Risk management in different environments

## Comparison Execution Protocol

### Phase 1: Data Preparation & Validation
1. **Run Selection**: Identify and validate comparison set
2. **Data Quality Check**: Ensure all runs have complete, valid data
3. **Comparability Assessment**: Verify meaningful comparison basis
4. **Time Alignment**: Synchronize time periods for fair comparison
5. **Configuration Analysis**: Group by strategy families

### Phase 2: Statistical Framework Setup
1. **Multiple Testing Setup**: Configure appropriate corrections
2. **Confidence Level Setting**: Establish significance thresholds
3. **Bootstrap Parameters**: Set resampling parameters
4. **Test Selection**: Choose appropriate statistical tests
5. **Power Analysis**: Verify sufficient sample sizes

### Phase 3: Comprehensive Performance Analysis
1. **Basic Metrics Comparison**: Standard performance measures
2. **Risk-Adjusted Analysis**: Sharpe, Sortino, Calmar comparisons
3. **Drawdown Analysis**: Maximum and average drawdown comparison
4. **Consistency Analysis**: Performance stability assessment
5. **Trading Statistics**: Win rates, trade sizes, frequencies

### Phase 4: Advanced Analytics
1. **Mechanism Ranking**: Individual feature/mechanism impact
2. **Feature Importance**: Statistical significance and contribution
3. **Regime Analysis**: Performance across market conditions
4. **Overfitting Assessment**: Robustness and stability testing
5. **Implementation Realism**: Execution feasibility scoring

### Phase 5: Results Synthesis & Ranking
1. **Overall Ranking**: Weighted composite scores
2. **Category-Specific Rankings**: Best in each performance dimension
3. **Risk-Return Efficiency**: Pareto frontier analysis
4. **Implementation Priority**: Most viable strategies first
5. **Confidence Assessment**: Statistical confidence in rankings

## Expected Outputs

### Comparative Analysis Report
- **Executive Summary**: Top performers with statistical confidence
- **Performance Matrix**: All metrics with confidence intervals
- **Statistical Significance**: P-values and effect sizes for comparisons
- **Ranking Tables**: Strategies ranked by multiple criteria
- **Mechanism Scorecard**: Individual feature effectiveness

### Detailed Analytics
- **Risk-Return Scatter Plots**: Visual performance comparison
- **Rolling Performance Charts**: Time-series performance comparison
- **Drawdown Comparison**: Underwater curves and recovery analysis
- **Regime Performance**: Performance across different market conditions
- **Feature Importance Plots**: Contribution and significance rankings

### Recommendations
- **Top Strategy Recommendations**: Best performers with confidence levels
- **Implementation Priority**: Most viable strategies for production
- **Further Research Suggestions**: Areas needing additional analysis
- **Risk Warnings**: Potential overfitting or realism concerns
- **Parameter Sensitivity**: Robustness assessment for top strategies

### Statistical Documentation
- **Methodology Report**: Statistical methods and corrections used
- **Confidence Intervals**: All performance metrics with uncertainty
- **Significance Tests**: P-values and effect sizes for key comparisons
- **Multiple Testing Corrections**: How family-wise error was controlled
- **Bootstrap Results**: Resampling validation of key findings

The comparison provides rigorous, statistically-validated ranking of strategies while identifying the most promising mechanisms and warning of potential overfitting or realism issues.