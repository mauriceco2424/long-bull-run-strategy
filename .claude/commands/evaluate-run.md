# Evaluate Trading Run Performance

---
description: Evaluate performance, interpret strategy behavior, and generate PDF report
argument-hint: [run_id]
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-evaluator** agent to perform comprehensive performance evaluation, strategic interpretation, and generate a professional LaTeX PDF report.

## Run Evaluation Parameters
- **Run ID**: $ARGUMENTS (defaults to most recent run if not specified)

## Performance Evaluation & Strategic Analysis Tasks

### 1. **Performance Evaluation (Core Mission)**
- **Assess Performance Quality**: Analyze all metrics from analyzer (CAGR, Sortino, Sharpe, MaxDD, etc.)
  - Is this good/bad/exceptional performance?
  - How does it compare to market benchmarks?
  - What is the risk-adjusted return quality?
- **Statistical Significance Analysis**: 
  - Apply rigorous statistical frameworks with confidence intervals
  - Multiple-testing corrections (Bonferroni, FDR) when needed
  - Assess significance and reliability of results
- **Benchmark Comparison**:
  - Compare against market indices and risk-free rates
  - Evaluate performance in different market regimes
  - Assess consistency across time periods

### 2. **Strategic Interpretation (Core Mission)**
- **Understand WHY Strategy Works or Fails**:
  - Analyze market behavior patterns that drive performance
  - Identify which strategy mechanics are most effective
  - Understand parameter sensitivity and regime effectiveness
- **Generate Strategic Insights**:
  - What market conditions favor this strategy?
  - Which components contribute most to alpha vs. risk reduction?
  - How stable are the performance drivers over time?
- **Make Informed Assumptions**:
  - Causal relationships in performance patterns
  - Market behavior interpretation and regime analysis
  - Strategic recommendations based on findings

### 3. **Realism & Quality Validation**
- **Realism Assessment**:
  - Detect lookahead bias and validate execution assumptions
  - Assess liquidity constraints and slippage realism
  - Verify minimum notional rounding and fee accuracy
  - Validate trade density and market impact assumptions
- **Statistical Rigor**:
  - Flag extreme or suspicious metrics (Sortino >3, zero drawdown periods)
  - Assess potential overfitting through out-of-sample thinking
  - Identify unrealistic win rates or performance metrics
- **Risk Assessment**:
  - Evaluate maximum drawdown periods and recovery
  - Assess tail risk and extreme event handling
  - Validate accounting identity maintenance

### 4. **Web Research Integration**
- **Research Best Practices**:
  - Trading strategy evaluation methodologies
  - Statistical analysis standards for quantitative strategies
  - LaTeX report formatting for financial analysis
  - Evidence-based interpretation frameworks
- **Industry Standards**:
  - Professional performance evaluation benchmarks
  - Risk assessment methodologies
  - Scientific writing standards for trading research

### 5. **Professional LaTeX PDF Report Generation**
- **Report Structure**:
  - **Executive Summary**: Key findings and recommendations
  - **Strategy Methodology**: From strategy template + parameters used
  - **Performance Analysis**: Metrics interpretation + analyzer's figures
  - **Risk Assessment**: Evaluator's risk analysis + insights
  - **Strategic Insights**: Why it works/fails, market behavior interpretation
  - **Statistical Validation**: Significance, realism assessment
  - **Conclusions & Recommendations**: Strategic recommendations for next steps

- **LaTeX Quality Standards**:
  - Professional financial report formatting
  - Proper figure integration from analyzer's visualizations
  - Scientific writing with clear methodology sections
  - Publication-ready typography and layout

### 6. **Decision Framework & Recommendations**
- **Performance Assessment**:
  - **EXCELLENT**: Outstanding risk-adjusted returns, statistically significant, realistic
  - **GOOD**: Solid performance with acceptable risk, minor concerns
  - **ACCEPTABLE**: Meets minimum thresholds, room for improvement
  - **POOR**: Suboptimal performance, significant issues identified
  - **FAILED**: Unrealistic results, critical flaws, halt recommended

- **Strategic Recommendations**:
  - Parameter optimization opportunities
  - Strategy enhancement suggestions
  - Market condition considerations
  - Risk management improvements

### 7. **Output Generation & Documentation**
- **Strategy Evaluation Report (SER)**: Comprehensive evaluation document
- **Professional LaTeX PDF**: Human-readable report for stakeholders
- **Strategy Definition Change Notice (SDCN)**: If specification changes needed
- **Evaluation summary**: Key findings for orchestrator
- **Next phase recommendations**: Clear guidance for iteration

## Expected Outputs
- **Professional LaTeX PDF Report**: Complete strategy evaluation for human consumption
- **SER (Strategy Evaluation Report)**: Technical evaluation document
- **Performance assessment**: Clear rating and justification
- **Strategic insights**: Deep analysis of why strategy performs as it does
- **Recommendations**: Concrete next steps for strategy development
- **SDCN if needed**: Strategy specification change notice

## Report Quality Standards
- **Scientific rigor**: Evidence-based analysis with proper citations
- **Clear insights**: Strategic interpretation beyond just metrics
- **Professional presentation**: LaTeX formatting suitable for stakeholders
- **Actionable recommendations**: Specific guidance for next development phase
- **Web-researched best practices**: Industry-standard methodologies applied

## Success Criteria
- Performance evaluation provides clear strategic insights
- Statistical validation confirms result reliability
- LaTeX PDF compiles successfully with professional formatting
- Strategic recommendations are specific and actionable
- Report ready for stakeholder review and decision-making

## Progress Reporting
- **Unified progress bar**: `Evaluating strategy... ████████░░░░ 75% (~3 min remaining)`
- **Clear phases**: analysis → interpretation → research → report generation
- **ETA integration**: Based on analysis complexity and report generation time

Please use the trading-evaluator agent to perform comprehensive performance evaluation with strategic interpretation and generate a professional LaTeX PDF report.