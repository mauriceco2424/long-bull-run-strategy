# Validate Quality Gates

---
description: Check all quality gates before pipeline progression
model: claude-3-5-sonnet-20241022
---

I need to coordinate **Builder**, **Analyzer**, and **Orchestrator** agents to validate all quality gates are passing before allowing pipeline operations to proceed.

## Quality Gate Validation Framework

### 1. Documentation Freshness Gate (Orchestrator)
**Critical Prerequisites:**
- ✓ Latest ECNs applied to EMR with version bump
- ✓ Latest SDCNs applied to SMR with version bump  
- ✓ ECL changelog appended with recent changes
- ✓ SCL changelog appended with recent changes
- ✓ All notice files properly processed and archived
- ✓ Git commits and version tags current
- ✓ No stale documentation flags in pipeline state

**Validation Actions:**
- Compare notice timestamps with master document versions
- Verify changelog entries match processed notices
- Check semantic versioning compliance
- Validate cross-reference integrity

### 2. Engine Quality Gates (Builder)
**Unit Testing Validation:**
- ✓ All rule semantic tests passing
- ✓ Feature timing tests (data ≤ t, actions at t+1)
- ✓ Position collision rule tests
- ✓ Rounding and minNotional tests
- ✓ Fee and slippage calculation tests
- ✓ TP/SL execution logic tests

**Golden-Set Parity Testing:**
- ✓ Reference run reproduction
- ✓ Bit-exact matching of critical outputs
- ✓ Deterministic behavior validation
- ✓ Cross-platform consistency checks

**Determinism Validation:**
- ✓ Seeded run reproducibility
- ✓ Platform-independent results
- ✓ Multi-run consistency checks
- ✓ Cache invalidation testing

**Performance Benchmarks:**
- ✓ Runtime regression testing (<10% degradation)
- ✓ Memory usage profiling
- ✓ I/O throughput validation
- ✓ Cache hit-rate optimization
- ✓ Hardware profile consistency

### 3. Data Validation Gates (Analyzer)
**Data Quality Validation:**
- ✓ UTC timestamp validation and monotonicity
- ✓ No duplicate records in OHLCV data
- ✓ Non-negative price and volume validation
- ✓ Missing-bar policy compliance
- ✓ Data source connectivity and freshness

**Pre-Run System Validation:**
- ✓ Minimum 2GB available RAM
- ✓ Sufficient disk space for artifacts
- ✓ Configuration file validation
- ✓ Universe and date range validation
- ✓ No conflicting run processes

**Validator Operational Status:**
- ✓ No-lookahead validator functional
- ✓ Accounting identity validator operational
- ✓ Sanity threshold validator active
- ✓ Data quality validator enabled
- ✓ All validator configurations current

### 4. Resource and Conflict Gates (Orchestrator)
**Conflict Prevention:**
- ✓ No runs with same universe/date/config combination
- ✓ Unique run_id generation verified
- ✓ Target directory availability confirmed
- ✓ Lockfile availability for registry updates
- ✓ Max parallel run limits respected

**Resource Availability:**
- ✓ System resource headroom adequate
- ✓ Data cache availability and warmth
- ✓ Network connectivity for data sources
- ✓ Storage I/O capacity sufficient
- ✓ CPU and memory allocation optimal

### 5. State Consistency Gates (Orchestrator)
**Pipeline State Validation:**
- ✓ Task tracking files current and accessible
- ✓ State persistence files intact
- ✓ DAG progression logic consistent
- ✓ Milestone checkpoints properly defined
- ✓ Owner assignments clear and current

**Version Synchronization:**
- ✓ Engine version alignment across components
- ✓ Strategy version consistency in configs
- ✓ Data version compatibility
- ✓ Fee model version current
- ✓ Run registry schema current

## Gate Validation Protocol

### Phase 1: Pre-Validation Setup
1. **Environment Check**: Verify all agents are operational
2. **Dependency Validation**: Confirm all required tools available
3. **State Snapshot**: Capture current pipeline state
4. **Resource Baseline**: Record current system resources

### Phase 2: Sequential Gate Testing
1. **Documentation Gates**: Orchestrator validates docs freshness
2. **Engine Gates**: Builder runs comprehensive test suites
3. **Data Gates**: Analyzer validates data and system readiness
4. **Resource Gates**: Orchestrator checks conflicts and availability
5. **State Gates**: Orchestrator verifies consistency and integrity

### Phase 3: Gate Results Assessment
1. **PASS**: All gates validated successfully
   - Pipeline ready for operations
   - Green light for next phase execution
   - State updated with validation success

2. **CONDITIONAL PASS**: Minor issues detected
   - Non-blocking warnings logged
   - Proceed with enhanced monitoring
   - Schedule follow-up validation

3. **FAIL**: Critical gate failures detected
   - Block all pipeline operations
   - Escalate to appropriate owner
   - Log detailed failure information
   - Require fixes before retry

### Phase 4: Results Documentation
1. **Validation Report**: Comprehensive gate status summary
2. **Issue Escalation**: Route failures to appropriate agents
3. **State Persistence**: Update pipeline state with results
4. **Audit Trail**: Record validation timestamps and decisions

## Expected Outputs
- **Gate Status Matrix**: Pass/fail status for each gate category
- **Blocking Issues List**: Prioritized failures requiring attention
- **Resource Utilization Report**: Current system capacity assessment
- **Validation Timestamp**: When gates were last successfully validated
- **Next Validation Due**: Recommended revalidation schedule
- **Action Items**: Specific tasks to address any failures

The validation ensures all quality gates are satisfied before allowing expensive pipeline operations to proceed, preventing failures and maintaining system integrity.