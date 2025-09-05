# Optimize Trading Engine Performance

---
description: Profile and improve engine performance with safe speedups
argument-hint: [focus_area: caching|vectorization|io|parallelism|gates|all]
model: claude-3-5-opus-20240620
---

I need to use the **trading-builder** agent to profile the engine, identify performance bottlenecks, and implement safe optimizations while preserving semantic correctness and deterministic behavior.

## Optimization Focus Area
$ARGUMENTS (default: all)

## Optimization Framework

### 1. Performance Profiling & Analysis
**Hotspot Identification:**
- Profile CPU usage with line-by-line analysis
- Identify memory allocation bottlenecks
- Measure I/O wait times and disk utilization
- Analyze cache hit/miss ratios
- Profile parallelization efficiency
- Identify redundant computations

**Hardware-Aware Assessment:**
- CPU architecture optimization opportunities
- Memory bandwidth utilization analysis
- Storage I/O pattern optimization
- Cache hierarchy utilization assessment
- Vectorization potential identification

### 2. Safe Caching Optimizations
**Price & Feature Caching:**
- Implement explicit cache keys: `(symbol, timeframe, feature_version, config_hash)`
- Design warm-up windows for cache population
- Create cache invalidation strategies
- Implement cache size management (30% RAM allocation)
- Add cache hit-rate monitoring and optimization

**Intelligent Cache Management:**
- LRU eviction for memory pressure
- Persistent cache for expensive computations
- Cache versioning for feature changes
- Memory-mapped cache files for large datasets
- Cross-run cache sharing when safe

### 3. Incremental Recomputation (Gates)
**Monotone Gate Optimization:**
- Maintain reference runs with per-gate pass sets
- Implement gate tightening logic (check only previous passes)
- Implement gate loosening logic (check only previous fails)
- Create compact bitset storage under `/data/cache/gates/{gate_hash}/`
- Add fallback to full recompute for non-monotone changes

**Gate Caching Strategy:**
- Persist pass-sets as columnar data
- Implement fast bitwise operations
- Cache gate results with proper invalidation
- Monitor gate efficiency and hit rates

### 4. I/O Optimization
**Columnar Data Management:**
- Implement Parquet/Feather formats for efficiency
- Design batched read/write operations
- Add memory-mapping for large datasets
- Optimize sequential vs random access patterns
- Implement prefetching for predictable access

**Storage Pattern Optimization:**
- SSD-optimized random access patterns
- HDD-optimized sequential batch operations
- Compression for network and storage efficiency
- Async I/O for concurrent data operations

### 5. Vectorization & Compiled Paths
**NumPy/Polars Optimization:**
- Replace scalar operations with vectorized equivalents
- Implement efficient array operations
- Use broadcasting for element-wise operations
- Optimize memory layout for cache efficiency

**Numba Compilation (Determinism-Preserving):**
- Identify hot loops suitable for compilation
- Preserve exact floating-point behavior
- Maintain deterministic random number generation
- Validate compiled vs interpreted output parity

### 6. Parallelization Optimization
**Coarse-Grained Parallelism:**
- Symbol-level parallel processing
- Date range parallel processing
- Bounded worker management
- Stable seed distribution for determinism
- Result ordering preservation

**Resource Management:**
- Prevent CPU oversubscription
- Memory-aware worker scaling
- I/O bandwidth sharing
- Thread pool optimization
- Load balancing across workers

### 7. Early Exit Strategies
**Short-Circuit Optimizations:**
- Symbol disqualification detection
- Date range early termination
- Filter cascade optimization
- Resource exhaustion handling
- Progressive refinement strategies

## Optimization Implementation Protocol

### Phase 1: Baseline Establishment
1. **Current Performance Measurement**: Complete benchmark suite
2. **Hardware Profile**: System resource assessment and configuration
3. **Hotspot Analysis**: Detailed profiling to identify bottlenecks
4. **Memory Usage Baseline**: Peak and average memory consumption
5. **I/O Pattern Analysis**: Disk and network utilization patterns

### Phase 2: Safe Optimization Implementation
1. **Semantic Preservation**: Maintain exact output equivalence
2. **Determinism Protection**: Preserve reproducible results
3. **Incremental Changes**: One optimization at a time
4. **Validation Testing**: Golden-set parity after each change
5. **Performance Measurement**: Before/after benchmarking

### Phase 3: Advanced Optimizations
1. **Caching Infrastructure**: Implement intelligent caching systems
2. **Vectorization**: Replace scalar operations where safe
3. **Parallelization**: Add coarse-grained parallel processing
4. **I/O Optimization**: Implement columnar and async patterns
5. **Gate Optimization**: Add incremental recomputation for monotone gates

### Phase 4: Validation & Benchmarking
1. **Correctness Validation**: Ensure identical outputs to baseline
2. **Performance Benchmarking**: Measure improvement across hardware profiles
3. **Regression Testing**: Verify no functionality degradation
4. **Stress Testing**: Validate under resource constraints
5. **Scalability Assessment**: Test with various universe sizes

### Phase 5: Documentation & ECN Generation
1. **Performance Report**: Before/after benchmarks with hardware context
2. **Implementation Details**: Technical description of optimizations
3. **Safety Analysis**: How semantic correctness was preserved
4. **Configuration Updates**: New optimal settings recommendations
5. **ECN Generation**: Formal Engine Change Notice with benchmarks

## Expected Optimizations

### Caching Improvements
- 50-90% reduction in redundant computations
- Intelligent cache warming and management
- Cross-run cache sharing where appropriate

### Vectorization Gains
- 2-10x speedup for mathematical operations
- Memory layout optimization
- SIMD instruction utilization

### I/O Optimization
- 30-70% reduction in I/O wait times
- Efficient columnar data formats
- Memory-mapped file utilization

### Parallelization Benefits
- Near-linear scaling with CPU cores
- Efficient resource utilization
- Maintained deterministic results

### Gate Optimization
- 80-95% reduction in redundant gate evaluations
- Incremental processing for parameter sweeps
- Intelligent result reuse

## Expected Outputs
- **Performance Improvement Report**: Quantified speedups with hardware profiles
- **ECN with Benchmarks**: Formal change notice documenting improvements
- **Optimization Recommendations**: Settings for different hardware configurations
- **Safety Validation**: Proof of semantic equivalence and determinism preservation
- **Resource Utilization Analysis**: Optimized CPU, memory, and I/O usage patterns
- **Scalability Assessment**: Performance characteristics across different universe sizes

The optimization ensures significant performance improvements while maintaining the engine's correctness, determinism, and semantic integrity required for reliable trading strategy evaluation.