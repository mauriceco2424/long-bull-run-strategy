# Trading Strategy Command User Guide

This guide explains when and how to use each command in the trading strategy development pipeline.

## Command Overview

The trading strategy framework provides 12 specialized commands organized into four categories:

### Core Workflow Commands
- `/kickoff` - Start a new strategy development cycle  
- `/build-run` - Execute build → run → analyze pipeline
- `/analyze-run` - Process run data into canonical outputs
- `/evaluate` - Assess results and decide next steps

### Pipeline Management Commands  
- `/status` - Check pipeline state and quality gates
- `/sync-docs` - Update master documentation from notices
- `/validate-gates` - Verify all prerequisites before operations

### Development & Testing Commands
- `/test-engine` - Run comprehensive engine test suite
- `/optimize-engine` - Profile and improve engine performance  
- `/validate-run` - Check specific run for integrity

### Research & Analysis Commands
- `/compare-runs` - Compare and rank multiple strategies
- `/research` - Investigate topics and save findings
- `/visualize` - Generate professional charts and plots

## When to Use Each Command

### 🚀 Starting a New Strategy (`/kickoff`)

**When to use:**
- Beginning development of a new trading strategy
- Major changes to strategy logic requiring full pipeline restart
- Setting up development cycle after significant engine changes
- Planning complex multi-phase development work

**Example scenarios:**
```
/kickoff "Develop momentum-based crypto strategy with volatility filters"
/kickoff "Add machine learning signals to existing RSI strategy"
/kickoff "Create multi-timeframe analysis with regime detection"
```

**What it does:**
- Creates comprehensive project plan with milestones
- Sets up task tracking and state management
- Verifies all prerequisites and dependencies
- Initializes documentation and version control
- Coordinates agent assignments and quality gates

---

### 🔧 Building and Running (`/build-run`)

**When to use:**
- Engine changes have been made and need testing with real data
- Ready to execute a strategy configuration on historical data
- Need both engine optimization and backtest execution
- Want complete build-test-analyze workflow

**Example scenarios:**
```
/build-run configs/momentum_v2.json binance_usdt 2021-01-01:2023-12-31
/build-run configs/ml_signals.json crypto_majors 2022-01-01:2024-01-01
```

**What it does:**
- Builder implements and optimizes engine per specifications
- Runs comprehensive test suites and benchmarks
- Analyzer executes backtest and generates all artifacts
- Updates documentation with performance improvements
- Produces ECN with hardware-profiled benchmarks

---

### 📊 Analyzing Existing Data (`/analyze-run`)

**When to use:**
- Have existing backtest data needing canonical processing
- Want to regenerate visualizations with improved standards
- Need to reprocess data with updated validation logic
- Creating analysis artifacts for runs without full rebuild

**Example scenarios:**
```
/analyze-run run_20240315_momentum_v2
/analyze-run configs/base_strategy.json crypto_top20 2023-01-01:2023-12-31
```

**What it does:**
- Processes raw backtest data into standardized formats
- Generates professional visualizations and reports
- Runs comprehensive validation suite
- Updates run registry with analysis results
- Creates publication-ready charts and metrics

---

### 🎯 Evaluating Performance (`/evaluate`)

**When to use:**
- Analysis artifacts are ready for critical assessment  
- Need to rank multiple strategy variants
- Deciding whether results are realistic and actionable
- Ready to make go/no-go decisions on strategy progression

**Example scenarios:**
```
/evaluate run_20240315_momentum_v2
/evaluate run_20240301_* run_20240315_* run_20240401_*
```

**What it does:**
- Applies rigorous statistical analysis and realism validation
- Ranks mechanisms and features by effectiveness
- Generates Strategy Evaluation Report (SER)
- Makes progression decisions (PASS/RERUN/HALT)
- Produces recommendations for next development phase

---

### 📋 Checking Status (`/status`)

**When to use:**
- Starting work session - check what needs attention
- Debugging pipeline issues or blocked operations
- Before major operations - verify system readiness
- Regular health checks and progress monitoring

**Example scenarios:**
```
/status
```

**What it does:**
- Reviews documentation freshness and version sync
- Checks all quality gates and prerequisites
- Identifies active runs and resource utilization
- Provides actionable next steps with owner assignments
- Reports blocking issues and priority recommendations

---

### 📖 Syncing Documentation (`/sync-docs`)

**When to use:**
- After Builder produces Engine Change Notices (ECNs)
- After Evaluator creates Strategy Definition Change Notices (SDCNs)  
- Before starting new development cycles
- When documentation freshness gate is failing

**Example scenarios:**
```
/sync-docs
```

**What it does:**
- Applies all pending ECNs to Engine Master Report (EMR)
- Integrates SDCNs into Strategy Master Report (SMR)
- Updates version numbers using semantic versioning
- Appends changelogs with complete change history
- Creates git commits and version tags

---

### ✅ Validating Gates (`/validate-gates`)

**When to use:**
- Before expensive backtest operations
- After major engine or strategy changes
- When troubleshooting pipeline issues
- As part of quality assurance protocols

**Example scenarios:**
```
/validate-gates
```

**What it does:**
- Validates documentation freshness and version consistency
- Runs engine test suites and benchmarks
- Checks data quality and system resources
- Verifies no conflicting operations
- Reports comprehensive gate status with blocking issues

---

### 🧪 Testing Engine (`/test-engine`)

**When to use:**
- After implementing new engine features or optimizations
- Before committing engine changes
- Debugging engine behavior or performance issues
- Validating hardware optimization settings

**Example scenarios:**
```
/test-engine all
/test-engine performance
/test-engine unit
```

**What it does:**
- Runs comprehensive test suites (unit, golden-set, integration)
- Performs hardware-aware benchmarking
- Validates deterministic behavior and correctness
- Generates performance reports with regression detection
- Produces Engine Change Notice (ECN) with benchmarks

---

### ⚡ Optimizing Engine (`/optimize-engine`)

**When to use:**
- Backtests are too slow for iterative development
- Want to improve engine performance while maintaining correctness
- After identifying performance bottlenecks
- Preparing engine for production deployment

**Example scenarios:**
```
/optimize-engine all
/optimize-engine caching
/optimize-engine vectorization
```

**What it does:**
- Profiles engine to identify hotspots and bottlenecks
- Implements safe optimizations (caching, vectorization, I/O)
- Maintains semantic correctness and deterministic behavior
- Produces before/after benchmarks with hardware profiles
- Generates ECN documenting performance improvements

---

### 🔍 Validating Runs (`/validate-run`)

**When to use:**
- Suspicious or unexpected backtest results
- Before relying on results for important decisions
- Debugging data quality or accounting issues
- Verifying run integrity after system changes

**Example scenarios:**
```
/validate-run run_20240315_momentum_v2
```

**What it does:**
- Comprehensive validation of run data and artifacts
- Checks for lookahead bias and accounting consistency
- Validates realism and execution feasibility
- Assesses data quality and completeness
- Reports validation status with detailed findings

---

### 📊 Comparing Runs (`/compare-runs`)

**When to use:**
- Multiple strategy variants need ranking
- Choosing between different parameter configurations
- Portfolio construction from multiple strategies
- Research comparing different approaches

**Example scenarios:**
```
/compare-runs run_20240301_base run_20240315_optimized run_20240401_ml
/compare-runs momentum_* 
```

**What it does:**
- Rigorous statistical comparison with multiple testing corrections
- Ranks strategies by risk-adjusted performance
- Identifies best-performing mechanisms and features
- Applies overfitting detection and realism scoring
- Generates comprehensive comparison report with confidence intervals

---

### 🔬 Researching Topics (`/research`)

**When to use:**
- Need to investigate new techniques or methodologies
- Exploring optimization opportunities
- Validating current approaches against literature
- Learning about specific technical topics

**Example scenarios:**
```
/research "OHLCV visualization best practices"
/research "portfolio optimization techniques for crypto"
/research "momentum indicator effectiveness in volatile markets"
```

**What it does:**
- Conducts systematic web search and analysis
- Evaluates source credibility and relevance
- Synthesizes findings into actionable insights
- Saves research to appropriate directories
- Maintains semantic integrity and validation requirements

---

### 📈 Creating Visualizations (`/visualize`)

**When to use:**
- Need publication-quality charts for presentations
- Want to improve existing visualizations
- Analyzing run results visually
- Creating professional strategy reports

**Example scenarios:**
```
/visualize run_20240315_momentum_v2 all
/visualize run_20240301_base equity
/visualize run_20240401_ml symbols
```

**What it does:**
- Generates professional equity curves and performance charts
- Creates per-symbol analysis with event overlays
- Produces publication-quality figures (PNG/SVG)
- Follows industry visualization best practices
- Includes comprehensive performance statistics

## Typical Workflow Sequences

### 🆕 New Strategy Development
```
/kickoff "Strategy description"
/validate-gates
/build-run config.json universe date_range
/evaluate run_id
```

### 🔄 Iterative Optimization  
```
/status
/sync-docs
/optimize-engine focus_area
/build-run optimized_config.json universe date_range
/compare-runs baseline_run optimized_run
```

### 🏃‍♂️ Quick Analysis Cycle
```
/analyze-run config.json universe date_range  
/visualize run_id all
/validate-run run_id
/evaluate run_id
```

### 🔧 Maintenance & Health Check
```
/status
/validate-gates  
/sync-docs
/test-engine all
```

## Command Usage Tips

- **Start every session** with `/status` to understand current pipeline state
- **Use `/validate-gates`** before expensive operations to avoid wasted time
- **Always `/evaluate`** before making strategy decisions - don't trust raw metrics
- **Run `/sync-docs`** after major changes to keep documentation current
- **Use `/compare-runs`** with statistical rigor for fair strategy comparison
- **Leverage `/research`** to stay current with best practices and techniques

The commands are designed to work together as an integrated pipeline, ensuring quality, reproducibility, and systematic strategy development.