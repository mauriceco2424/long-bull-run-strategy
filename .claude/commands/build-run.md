# Build-Run Trading Strategy Pipeline

---
description: Execute the build → run → analyze workflow
argument-hint: [config_path universe_id date_range]
model: claude-3-5-sonnet-20241022
---

I need to coordinate the **Builder** and **Analyzer** agents to execute the complete build-run-analyze workflow.

## Parameters
$ARGUMENTS

## Workflow Execution

### Phase 1: Engine Building (Builder Agent)
1. **Hardware Profiling**
   - Profile system resources (CPU, RAM, storage, GPU)
   - Auto-configure engine settings based on hardware profile
   - Report optimized settings (workers, chunk sizes, cache allocation)

2. **Implementation & Optimization**
   - Implement engine logic exactly per SMR specifications
   - Apply safe performance optimizations (caching, vectorization, incremental recomputation)
   - Maintain deterministic behavior and semantic correctness

3. **Quality Gates**
   - Run unit tests for rule semantics
   - Execute golden-set parity tests
   - Verify determinism with seeded tests
   - Run small-universe integration tests
   - Execute performance benchmarks with regression detection

4. **Documentation**
   - Generate ECN (Engine Change Notice) with before/after benchmarks
   - Include hardware profile in all performance metrics
   - Document any interface or data-policy implications

### Phase 2: Backtest Execution (Analyzer Agent)
1. **Resource Validation**
   - Verify ≥2GB available RAM before execution
   - Check disk space for output artifacts
   - Validate input configuration and data availability

2. **Backtest Execution**
   - Execute engine with specified config/universe/dates
   - Generate progress updates every 30 seconds
   - Monitor resource usage and auto-throttle if needed

3. **Artifact Generation**
   - Create canonical outputs in `/data/runs/{run_id}/`:
     - `manifest.json` - Run metadata and configuration
     - `metrics.json` - Performance metrics (CAGR, Sortino, Sharpe, MaxDD, etc.)
     - `trades.csv` - Individual fill records
     - `events.csv` - Signal and action timestamps
     - `series.csv` - Daily equity and position counts
     - `figs/` - Visualizations (equity curves, per-symbol plots)

4. **Validation & Registry**
   - Run all validators (no-lookahead, accounting identity, sanity checks)
   - Update run registry with atomic lockfile protocol
   - Generate checksums for data integrity

## Handoff Protocol
- Builder produces ECN with benchmarks → Orchestrator updates EMR/ECL
- Analyzer produces artifacts + registry entry → Ready for Evaluator

## Expected Outputs
- Updated engine code with performance improvements
- Complete backtest artifacts in `/data/runs/{run_id}/`
- Updated run registry entry
- ECN with hardware-profiled benchmarks
- Validation reports

The workflow will coordinate between Builder and Analyzer agents while maintaining strict quality gates and documentation requirements.