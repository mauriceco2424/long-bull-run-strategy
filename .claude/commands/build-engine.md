# Build Trading Engine

---
description: Build and optimize trading engine from strategy specification
argument-hint: [--test]
model: opus
---

I need to use the **trading-builder** agent to implement and optimize the trading engine based on the validated strategy specification.

**Strategy Source Selection:**
- **Default**: Builds engine from `docs/SMR.md` (main strategy)
- **Test Mode**: If `--test` flag provided, builds engine from `docs/test/test_SMR.md` (test strategy)

## Engine Building Tasks

### 1. **Complexity-Aware Strategy Implementation**
- **Read complexity assessment** from `/validate-strategy` and `/plan-strategy` outputs
- **Complexity-Aware Building Modes**:
  - **SIMPLE**: Template-based engine generation, standard testing (target: 90s)
  - **MODERATE**: Full engine building with comprehensive validation (current behavior, target: 150s)
  - **COMPLEX**: Enhanced validation, extended testing, performance profiling (target: 240s)
  - **ADVANCED**: Comprehensive validation, stress testing, optimization analysis (target: 300s+)
- **Strategy Source**: Use test strategy if `--test` flag provided, otherwise main strategy
- Implement engine logic exactly per strategy specification with complexity-appropriate thoroughness
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

### 3. **Complexity-Aware Quality Assurance & Testing**
- **Simple Strategies**: Standard unit tests, basic integration testing
- **Moderate Strategies**: Comprehensive testing suite (current behavior)
- **Complex Strategies**: Enhanced testing with performance profiling and extended validation
- **Advanced Strategies**: Full stress testing, optimization analysis, and comprehensive validation
- Run unit tests for rule semantics (scope adjusted by complexity)
- Execute golden-set parity tests for correctness
- Verify deterministic behavior with seeded tests
- Run integration tests (universe size scaled by complexity level)
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

### 7. **Universal Quality Gate - Accounting Identity Gate (MANDATORY)**

Before any agent completes its phase:

**VERIFY**: `Equity_final = Equity_initial + Sum(realized_PnL) + Sum(unrealized_PnL) - Sum(fees)`

**CROSS-CHECK**: Visual equity curve direction matches reported return sign

**RED FLAGS** (Immediate escalation):
- Positive metrics with declining equity chart
- Large unrealized losses not reflected in total return
- Final equity calculation doesn't reconcile with reported performance
- Open positions at period end without proper mark-to-market

If any red flag detected → Set run status to "FAILED - ACCOUNTING ERROR" and escalate.

## Expected Outputs
- **Implemented and optimized engine code** (complexity-appropriate thoroughness)
- **Auto-generated `parameter_config.md` template** ready for user configuration
- **Complexity assessment integration** showing strategy level and time targets achieved
- ECN with hardware-profiled benchmarks
- Test results and validation reports (scope adjusted by complexity)
- Parameter validation schema for runtime checking
- Performance optimization report
- Engine ready for backtesting with `/run` command

## Success Criteria  
- **Complexity-appropriate quality gates met**:
  - Simple: Standard unit tests pass, basic validation complete
  - Moderate: Comprehensive testing suite passes (100% success rate)
  - Complex: Enhanced testing with performance profiling passes
  - Advanced: Full stress testing and optimization analysis complete
- Golden-set parity tests show identical results
- Performance benchmarks meet complexity-adjusted standards
- Parameter configuration template generated successfully
- Engine implements all strategy template requirements accurately
- No lookahead bias or unrealistic assumptions detected
- **Time targets achieved** for complexity level (90s/150s/240s/300s+)

Please use the trading-builder agent to implement, test, and optimize the engine while auto-generating the parameter configuration template for the next phase.