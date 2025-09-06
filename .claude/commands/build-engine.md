# Build Trading Engine

---
description: Build and optimize trading engine from strategy specification
argument-hint: 
model: claude-3-5-sonnet-20241022
---

I need to use the **trading-builder** agent to implement and optimize the trading engine based on the validated strategy specification.

## Engine Building Tasks

### 1. **Strategy Implementation**
- Implement engine logic exactly per SMR (Strategy Master Report) specifications
- Translate strategy template logic into executable engine code
- Implement entry logic with specified markers, parameters, and conditions
- Implement exit logic with precedence rules and conflict handling
- Apply portfolio accounting mode and position sizing strategy

### 2. **Hardware Optimization**
- Profile system resources (CPU, RAM, storage, GPU if available)
- Auto-configure engine settings based on hardware profile
- Apply safe performance optimizations:
  - Caching strategies for repeated calculations
  - Vectorization where possible
  - Incremental recomputation for efficiency
- Report optimized settings (workers, chunk sizes, cache allocation)

### 3. **Quality Assurance & Testing**
- Run comprehensive unit tests for rule semantics
- Execute golden-set parity tests for correctness
- Verify deterministic behavior with seeded tests
- Run small-universe integration tests
- Execute performance benchmarks with regression detection
- Validate accounting identity and guardrail compliance

### 4. **Parameter Configuration Generation**
- Parse strategy template for all required parameters
- Extract parameter types, ranges, and descriptions
- **Auto-generate `parameter_config.md`** template with:
  - All strategy parameters with their valid ranges
  - Market/universe settings from strategy template
  - Date range configuration section
  - Risk management parameter settings
  - Execution parameter settings
- Create parameter validation schema for `/run` command

### 5. **Documentation & Handoff**
- Generate ECN (Engine Change Notice) with before/after benchmarks
- Include hardware profile in all performance metrics
- Document any interface or data-policy implications
- Update engine version tracking
- Prepare handoff to Orchestrator for EMR updates

### 6. **Safety & Realism Validation**
- Ensure no lookahead bias in implementation
- Validate fees/slippage models and minimum notional rounding
- Confirm accounting identity: `Equity_{t+1} = Equity_t + realizedPnL - fees`
- Implement sanity checks and anomaly detection
- Flag impossible fills or unrealistic execution assumptions

## Expected Outputs
- **Implemented and optimized engine code**
- **Auto-generated `parameter_config.md` template** ready for user configuration
- ECN with hardware-profiled benchmarks
- Comprehensive test results and validation reports
- Parameter validation schema for runtime checking
- Performance optimization report
- Engine ready for backtesting with `/run` command

## Success Criteria
- All unit tests pass with 100% success rate
- Golden-set parity tests show identical results
- Performance benchmarks meet or exceed baseline standards
- Parameter configuration template generated successfully
- Engine implements all strategy template requirements accurately
- No lookahead bias or unrealistic assumptions detected

Please use the trading-builder agent to implement, test, and optimize the engine while auto-generating the parameter configuration template for the next phase.