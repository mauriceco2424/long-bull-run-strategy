# Evaluate Trading Strategy Performance

---
description: Critically assess backtest results and rank mechanisms
argument-hint: [run_id or multiple_run_ids]
model: claude-3-5-opus-20240620
---

I need to use the **trading-evaluator** agent to perform rigorous assessment of backtest results, validate realism, and make data-driven progression decisions.

## Run(s) to Evaluate
$ARGUMENTS

## Evaluation Framework

### 1. Realism Validation
**Critical Assessment Areas:**

- **Lookahead Bias Detection**: Verify all features use data ≤ t for actions at t+1
- **Liquidity Reality Check**: Validate execution against actual market depth and volume
- **Slippage Model Verification**: Confirm realistic slippage and minimum notional rounding
- **Accounting Integrity**: Verify `Equity_{t+1} = Equity_t + realizedPnL - fees`
- **Execution Feasibility**: Flag impossible fills or unrealistic assumptions

### 2. Statistical Rigor Analysis
**Performance Metrics Assessment:**

- **Risk-Adjusted Returns**: CAGR, Sortino, Sharpe ratios with confidence intervals
- **Drawdown Analysis**: MaxDD, recovery periods, drawdown distribution
- **Trade Statistics**: Win rate, avg gain/loss, trade density, exposure metrics
- **Multiple Testing Corrections**: Apply Bonferroni or FDR when comparing variants
- **Statistical Significance**: Assess confidence intervals and p-values
- **Overfitting Detection**: Out-of-sample validation and parameter sensitivity
- **Anomaly Flagging**: Identify suspicious metrics (Sortino >3, zero DD periods)

### 3. Mechanism Ranking & Scoring
**Feature Impact Analysis:**

- **Individual Mechanism Scoring**: Rate each mechanism on risk-adjusted performance
- **Feature Importance Ranking**: Identify which features contribute most to alpha vs risk reduction
- **Parameter Sensitivity Assessment**: Test robustness across different settings
- **Market Regime Analysis**: Evaluate stability across different market conditions
- **Stability Scoring**: Rate mechanisms from most to least stable

### 4. Decision Framework
**Assessment Outcomes:**

- **PASS**: Results are realistic, statistically sound, ready for next phase
  - All validators passed
  - Performance metrics within realistic bounds
  - Statistical significance confirmed
  - No major realism concerns

- **RERUN NEEDED**: Issues requiring new analysis with corrections
  - Parameter adjustments needed
  - Methodology improvements required
  - Additional validation needed
  - Non-critical overfitting detected

- **HALT**: Critical flaws invalidating the entire backtest
  - Lookahead bias detected
  - Accounting failures found
  - Unrealistic execution assumptions
  - System integrity compromised

### 5. Escalation Protocol
**Severity Classification:**

- **P0 (Critical)**: Invalid backtest due to lookahead bias, accounting failures, system issues
  - **Action**: Halt pipeline immediately, escalate to Orchestrator
  - **Owner**: Builder (if engine issue) or Orchestrator (if systemic)

- **P1 (Major)**: Misleading results from overfitting, unrealistic assumptions
  - **Action**: Block progression, require rerun with corrections
  - **Owner**: Analyzer (if methodology) or Builder (if implementation)

- **P2 (Minor)**: Non-blocking issues like documentation gaps
  - **Action**: Log issues but allow progression
  - **Owner**: Appropriate agent based on issue type

### 6. Report Generation
**Structured Evaluation Output:**

- **Executive Summary**: Clear pass/fail recommendation with reasoning
- **Performance Metrics Table**: All key metrics with confidence intervals
- **Realism Validation Checklist**: Specific findings for each validation area
- **Mechanism Ranking**: Best to worst with stability notes and impact scores
- **Escalation Summary**: All issues categorized by severity level
- **Specific Recommendations**: Actionable next steps for each agent role

### 7. Documentation Updates
**Required Outputs:**

- **SER (Strategy Evaluation Report)**: Comprehensive assessment in `/docs/notices/SER/`
- **SDCN (Strategy Definition Change Notice)**: If specification changes needed
- **Run Registry Update**: Final evaluation status and key findings
- **SMR Updates**: Coordinate with Orchestrator for strategy specification changes

## Expected Deliverables
- Comprehensive evaluation report with clear recommendations
- Updated run registry with evaluation outcomes
- SER notice documenting findings and decisions
- SDCN if strategy specification changes required
- Mechanism ranking and feature importance analysis
- Statistical validation with confidence measures

The evaluation will prioritize realism over raw performance, applying conservative statistical standards to prevent false positives and ensure only robust, live-executable strategies advance through the pipeline.