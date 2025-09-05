# Test Trading Engine

---
description: Run comprehensive engine test suite with benchmarking
argument-hint: [test_scope: unit|golden|integration|performance|all]
model: claude-3-5-opus-20240620
---

I need to use the **trading-builder** agent to execute a comprehensive test suite for the trading engine, including unit tests, golden-set parity, integration tests, and performance benchmarks.

## Test Scope
$ARGUMENTS (default: all)

## Testing Protocol

### 1. Hardware Profiling & Session Initialization
**System Resource Assessment:**
- Profile CPU (cores, architecture, cache sizes, frequency)
- Assess RAM (total/available memory, swap usage, bandwidth)
- Evaluate storage (SSD/HDD type, available space, I/O throughput)  
- Check GPU availability (VRAM, compute capability)
- Generate hardware fingerprint for benchmark context

**Dynamic Engine Configuration:**
- Auto-adjust worker count: `min(cpu_cores * 0.75, symbol_count)`
- Scale chunk sizes with RAM: `chunk_size_mb = available_ram_gb * 8`
- Allocate cache: up to 30% of available RAM for feature/price caches
- Set I/O strategy: random access (SSD) vs sequential batching (HDD)
- Configure memory mapping based on dataset size vs available RAM

### 2. Unit Testing Suite
**Rule Semantics Validation:**
- ✓ Feature timing tests (data ≤ t, actions at next-bar open)
- ✓ Position collision handling (multiple signals same bar)
- ✓ Rounding and minNotional compliance
- ✓ Fee calculation accuracy (maker/taker, percentage/fixed)
- ✓ Slippage model implementation
- ✓ Take-profit and stop-loss execution logic
- ✓ Order delay and execution timing
- ✓ Portfolio allocation and position sizing

**Edge Case Testing:**
- Zero/negative prices and volumes
- Missing data bar handling
- Extreme market conditions
- Clock synchronization and timezone handling
- Numerical precision and overflow protection

### 3. Golden-Set Parity Testing
**Reference Run Reproduction:**
- Execute predetermined "golden" configuration
- Compare outputs bit-for-bit with reference results
- Validate manifest, metrics, trades, events, series data
- Check deterministic behavior across multiple runs
- Verify cross-platform consistency (if applicable)

**Parity Validation:**
- Equity curves must match exactly
- Trade records identical (timing, prices, quantities)
- Event sequences perfectly aligned
- Performance metrics within tolerance (1e-10)
- Cache behavior consistent

### 4. Determinism Validation
**Reproducibility Testing:**
- Multiple runs with same seed produce identical results
- Different seeds produce different but valid results
- Platform-independent output consistency
- Cache invalidation doesn't affect determinism
- Parallelization preserves deterministic ordering

### 5. Integration Testing
**Small-Universe End-to-End:**
- Execute complete pipeline on 5-10 symbols
- Validate data ingestion through artifact generation
- Test all validator passes (no-lookahead, accounting)
- Verify artifact completeness and integrity
- Check resource usage and performance scaling

**System Integration:**
- Configuration loading and validation
- Data source connectivity
- Cache system functionality
- Error handling and recovery
- Progress reporting and monitoring

### 6. Performance Benchmarking
**Baseline Performance Testing:**
- Runtime measurement with statistical analysis
- Memory usage profiling (peak, average, leaks)
- I/O throughput measurement
- Cache hit-rate optimization validation
- CPU utilization and scalability testing

**Regression Detection:**
- Compare against previous benchmark baselines
- Flag runtime regressions >10% unless justified
- Memory usage increase detection
- Performance scaling validation
- Hardware-specific optimization verification

**Hardware-Profiled Reporting:**
- Include full hardware profile in all benchmarks
- Report optimized settings chosen by auto-configuration
- Document performance characteristics for deployment
- Generate recommendations for production settings

### 7. Validator Testing
**Validator Operational Status:**
- No-lookahead validator functionality
- Accounting identity validator accuracy
- Sanity threshold validator calibration
- Data quality validator completeness
- Custom validator integration testing

## Test Execution Protocol

### Phase 1: Pre-Test Setup
1. **Environment Preparation**: Clean test environment, clear caches
2. **Hardware Profiling**: Complete system resource assessment
3. **Configuration**: Apply hardware-optimized engine settings
4. **Baseline Capture**: Record system state and performance baseline

### Phase 2: Test Suite Execution
1. **Unit Tests**: Fast, isolated component testing
2. **Golden-Set Tests**: Reference comparison validation
3. **Determinism Tests**: Reproducibility verification
4. **Integration Tests**: End-to-end system validation
5. **Performance Tests**: Benchmark and regression analysis

### Phase 3: Results Analysis
1. **Pass/Fail Assessment**: Clear success criteria evaluation
2. **Performance Analysis**: Benchmark comparison and regression detection
3. **Resource Utilization**: Memory, CPU, I/O efficiency assessment
4. **Hardware Optimization**: Validation of auto-configured settings

### Phase 4: Reporting
1. **Test Results Summary**: Pass/fail status for all test categories
2. **Performance Report**: Benchmarks with hardware context
3. **Regression Analysis**: Comparison with previous baselines
4. **Hardware Profile**: Complete system specification and optimizations
5. **Recommendations**: Settings for production deployment

## Expected Outputs
- **Test Results Matrix**: Pass/fail status for all test categories
- **Performance Benchmarks**: Runtime, memory, I/O with hardware profile
- **Regression Report**: Performance changes vs baseline
- **Golden-Set Validation**: Bit-exact comparison results
- **Hardware Profile**: Complete system specification and optimizations
- **Configuration Recommendations**: Optimal settings for deployment
- **Issue Report**: Any failures with detailed diagnostics

The testing ensures engine reliability, performance, and deterministic behavior while providing hardware-optimized configuration recommendations for production deployment.