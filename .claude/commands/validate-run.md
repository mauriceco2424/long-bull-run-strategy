# Validate Trading Strategy Run

---
description: Check specific run for realism, consistency, and integrity
argument-hint: [run_id]
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-analyzer** agent to perform comprehensive validation of a specific run's data, checking for realism, consistency, accounting integrity, and data quality issues.

## Run to Validate
Run ID: $ARGUMENTS

## Validation Framework

### 1. Data Quality Validation
**Timestamp & Structural Integrity:**
- ✓ UTC timestamp validation and monotonicity
- ✓ No duplicate records in OHLCV data
- ✓ Non-negative price and volume validation
- ✓ Complete OHLCV records (no missing fields)
- ✓ Missing-bar policy compliance verification
- ✓ Data continuity and gap analysis

**File Integrity Checks:**
- Validate SHA256 checksums in `checksums.json`
- Check artifact completeness in `/data/runs/{run_id}/`
- Verify manifest.json structure and content
- Validate CSV file formatting and headers
- Check figure file accessibility and format

### 2. No-Lookahead Validation
**Feature Timing Verification:**
- Ensure all features use data ≤ t for decisions at t
- Validate next-bar execution timing (actions at t+1 open)
- Check signal generation timing consistency
- Verify no future data leakage in calculations
- Validate cache timing and warm-up periods

**Signal Integrity Checks:**
- Confirm buy signals use only historical data
- Verify TP/SL signals respect execution delays
- Check filter applications respect data availability
- Validate indicator calculations don't peek forward

### 3. Accounting Identity Validation
**Equity Calculation Verification:**
- Validate `Equity_{t+1} = Equity_t + realizedPnL - fees`
- Check trade-by-trade PnL accuracy
- Verify fee calculations (maker/taker rates)
- Confirm position sizing and allocation logic
- Validate cash balance accounting

**Trade Record Consistency:**
- Match trades.csv with events.csv timing
- Verify buy/sell pair matching
- Check quantity and price consistency
- Validate batch_id coherence
- Confirm realized PnL calculations

### 4. Sanity Threshold Validation
**Performance Metric Realism:**
- Flag unrealistic Sortino ratios (>3.0 suspicious)
- Identify impossible Sharpe ratios (>4.0 very suspicious)
- Check for zero drawdown with significant trading
- Validate win rates within realistic bounds (30-90%)
- Assess trade density and frequency realism

**Statistical Anomaly Detection:**
- Identify extreme performance outliers
- Check for suspiciously consistent returns
- Flag unrealistic correlation patterns
- Validate exposure and leverage calculations

### 5. Execution Realism Validation
**Market Impact Assessment:**
- Verify trade sizes vs typical market volumes
- Check execution timing feasibility
- Validate slippage model applications
- Assess market depth assumptions
- Review order timing and delays

**Liquidity Constraints:**
- Check trade sizes against market capacity
- Validate execution during low-volume periods
- Assess impact on market prices
- Review minimum notional compliance
- Verify exchange-specific constraints

### 6. Configuration Consistency Validation
**Manifest Verification:**
- Validate config_hash matches actual configuration
- Check data_hash reflects actual data used
- Verify engine_version and strat_version accuracy
- Confirm seed and reproducibility information
- Validate fees_model version consistency

**Parameter Range Validation:**
- Check parameters within specified SMR ranges
- Validate feature configurations
- Confirm universe and date range accuracy
- Verify system resource allocations

### 7. Time Series Consistency Validation
**Series Data Integrity:**
- Validate equity curve continuity
- Check monitored_count and open_trades_count logic
- Verify cash and exposure calculations
- Confirm daily aggregation accuracy
- Validate series timestamp consistency

**Event Sequence Logic:**
- Check filter_pass → buy_signal sequences
- Validate TP/SL signal → execution timing
- Verify event timestamps align with series data
- Confirm batch processing logic

## Validation Execution Protocol

### Phase 1: Artifact Validation
1. **File System Check**: Verify all required files exist
2. **Checksum Verification**: Validate data integrity
3. **Format Validation**: Check file structure and headers
4. **Completeness Assessment**: Ensure no missing components

### Phase 2: Data Quality Assessment
1. **Structural Validation**: Check data formats and consistency
2. **Temporal Validation**: Verify timestamp accuracy and ordering
3. **Range Validation**: Check for realistic value ranges
4. **Completeness Validation**: Assess data coverage and gaps

### Phase 3: Semantic Validation
1. **No-Lookahead Testing**: Verify temporal data usage
2. **Accounting Verification**: Check mathematical consistency
3. **Logic Validation**: Verify business rule compliance
4. **Configuration Matching**: Ensure setup matches manifest

### Phase 4: Realism Assessment
1. **Performance Analysis**: Check for unrealistic results
2. **Market Impact Assessment**: Validate execution feasibility
3. **Statistical Analysis**: Identify anomalous patterns
4. **Liquidity Validation**: Assess market capacity constraints

### Phase 5: Results Documentation
1. **Validation Report**: Comprehensive pass/fail summary
2. **Issue Escalation**: Flag critical problems for appropriate agents
3. **Recommendation Generation**: Suggest fixes for identified issues
4. **Registry Update**: Record validation status and findings

## Validation Outcomes

### PASS - Run is Valid
- All validators completed successfully
- No critical realism issues identified
- Accounting integrity confirmed
- Data quality meets standards
- Ready for evaluation phase

### CONDITIONAL PASS - Minor Issues
- Non-critical warnings identified
- Performance metrics flagged for review
- Minor data quality issues noted
- Proceed with enhanced scrutiny
- Document issues for future improvement

### FAIL - Critical Issues Detected
- Major validator failures identified
- Accounting inconsistencies found
- Realism violations detected
- Data quality issues block progression
- Run invalidated, requires investigation

## Expected Outputs
- **Validation Status**: Clear pass/conditional/fail determination
- **Issue Summary**: Categorized list of all findings
- **Severity Assessment**: Priority classification of issues
- **Detailed Report**: Technical analysis of all validation checks
- **Recommendations**: Specific actions to address failures
- **Registry Update**: Validation status recorded in run registry
- **Escalation Actions**: Appropriate agent assignments for issue resolution

The validation ensures run integrity and realism before allowing progression to the evaluation phase, maintaining the quality standards required for reliable trading strategy assessment.