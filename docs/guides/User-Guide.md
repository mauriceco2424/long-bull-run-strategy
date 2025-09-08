# Trading Strategy User Guide (9-Command Dual-Path Workflow)

This comprehensive user guide explains the complete trading strategy framework, including the streamlined 9-command workflow, optimization benefits, and best practices for strategy development, evaluation, and optimization.

## Overview

The trading strategy framework provides **9 focused commands** that follow two clear, parallel paths:

### **Dual-Path Architecture**

```
Setup Path (4 commands - shared by both paths):
/validate-setup → /validate-strategy → /plan-strategy → /build-engine

Single-Run Path (3 commands):
/run → /analyze-single-run → /evaluate-single-run

Optimization Path (2 commands):  
/run-optimization → /evaluate-optimization
```

Each command has a single, clear purpose with automatic quality enforcement and professional outputs.

---

## The 9 Commands

### **Setup Commands (Shared by Both Paths)**

### 1. 🔧 `/validate-setup` - System Validation

**Purpose**: Check system requirements, dependencies, and data sources before starting development.

**When to use:**
- Beginning any new strategy development cycle
- After system changes or updates
- When troubleshooting pipeline issues
- First command in any development session

**What it validates:**
- System requirements (RAM ≥4GB, disk space, Python environment)
- Dependencies (pandas, numpy, progress libraries, LaTeX)
- Data sources and API connections
- Framework structure and permissions
- Hook system functionality

**Success criteria**: All prerequisites met, system ready for strategy development.

---

### 2. 📋 `/validate-strategy` - Strategy Template Validation

**Purpose**: Ensure strategy template (STRAT_TEMPLATE.md) is complete and ready for engine building.

**When to use:**
- After completing your strategy template
- Before starting engine development
- When updating strategy specifications
- To check parameter schema completeness

**What it validates:**
- All required sections filled with actual content (not placeholders)
- Parameter schema completeness with types and ranges
- Logic sections have executable conditions (not examples)
- Checklist items completed
- Market/universe and timeframe specified

**Success criteria**: Strategy template complete with all parameters defined, ready for engine building.

---

### 3. 📊 `/plan-strategy` - Development Planning

**Purpose**: Create comprehensive project plan and coordinate the development cycle.

**When to use:**
- After strategy template validation passes
- To set up systematic development coordination
- When managing complex multi-phase development
- To establish milestones and quality gates

**What it does:**
- Creates detailed development plan in `cloud/tasks/<task_id>.md`
- Verifies prerequisites and documentation freshness
- Sets up state tracking and progress monitoring
- Coordinates agent assignments and responsibilities
- Plans parameter configuration and evaluation workflow

**Success criteria**: Comprehensive development plan created, ready for engine building.

---

### 4. ⚙️ `/build-engine` - Engine Implementation

**Purpose**: Build and optimize the trading engine from strategy specification, including automatic parameter configuration generation.

**When to use:**
- After development planning is complete
- When implementing new strategy logic
- After making changes to strategy template
- To optimize engine performance

**What it does:**
- Implements engine logic exactly per strategy template
- Runs comprehensive test suites (unit, integration, performance)
- Applies hardware-aware performance optimizations
- **Auto-generates `parameter_config.md`** template for user completion
- Creates Engine Change Notice (ECN) with benchmarks

**Key output**: `parameter_config.md` template ready for user to fill in parameter values.

**Success criteria**: Engine built, tested, and parameter configuration template generated.

---

### **Single-Run Path Commands**

### 5. 🚀 `/run` - Backtest Execution  

**Purpose**: Execute backtest using the configured parameters from `parameter_config.md`.

**When to use:**
- After completing parameter configuration
- To test strategy with specific parameter values
- For production backtesting runs
- When parameter values have been updated

**What it does:**
- Validates `parameter_config.md` completeness
- Executes backtest with unified progress reporting
- Generates all raw artifacts (manifest, trades, events, series)
- Updates run registry with execution results

**Key requirement**: `parameter_config.md` must be completely filled out (no [REQUIRED] markers).

**Success criteria**: Backtest completes successfully with all artifacts generated.

---

### 6. 📈 `/analyze-single-run` - Data Analysis & Visualization

**Purpose**: Process backtest data into comprehensive metrics and professional visualizations.

**When to use:**
- After successful backtest execution  
- To reprocess existing run data
- When updating visualization standards
- To prepare data for evaluation

**What it does:**
- Processes raw trading data into performance metrics
- Creates **all professional visualizations** (publication-ready quality)
- Runs embedded validation checks (lookahead, accounting, realism)
- Generates analysis summary and quality reports
- Prepares evaluator-ready outputs

**Key outputs**: Enhanced metrics, professional charts ready for PDF inclusion.

**Success criteria**: Comprehensive analysis complete with publication-quality visualizations.

---

### 7. 🎯 `/evaluate-single-run` - Performance Evaluation & Strategic Analysis

**Purpose**: Evaluate performance, interpret strategy behavior, and generate professional PDF report.

**When to use:**
- After analysis artifacts are ready
- To assess strategy performance quality
- When need strategic insights and recommendations
- To generate stakeholder reports

**What it does:**
- **Evaluates performance**: Assesses metrics quality, compares to benchmarks
- **Strategic interpretation**: Understands WHY strategy works/fails
- **Generates LaTeX PDF report**: Professional document for stakeholders
- **Validates realism**: Statistical significance and execution feasibility
- **Provides recommendations**: Strategic insights for next development steps

**Key outputs**: Performance rating, strategic insights, professional PDF report.

**Success criteria**: Comprehensive evaluation with professional report ready for stakeholder review.

---

### **Optimization Path Commands**

### 8. 🔬 `/run-optimization` - Parameter Optimization & Analysis

**Purpose**: Execute parameter sweeps with walk-forward analysis AND process results into optimization matrices.

**When to use:**
- After engine is built and you want to optimize parameters
- To validate parameter robustness across market conditions
- When seeking optimal parameter configurations
- For systematic parameter space exploration

**What it does:**
- Reads `optimization_config.json` with parameter ranges and search configuration
- **Executes parameter sweeps** with multiple backtest combinations
- **Processes optimization data** into performance matrices and robustness heatmaps
- Applies **walk-forward validation** with rolling optimization windows
- **Prevents overfitting** through statistical validation and complexity limits
- Generates optimization study artifacts ready for evaluation

**Key requirement**: `optimization_config.json` must be created with parameter ranges and search method.

**Key outputs**: Parameter performance matrices, robustness analysis, 3D parameter surfaces.

**Success criteria**: Parameter optimization completes with comprehensive analysis artifacts.

---

### 9. 🏆 `/evaluate-optimization` - Optimization Study Evaluation

**Purpose**: Evaluate parameter optimization results and generate optimization study PDF report.

**When to use:**
- After optimization study completes with analysis artifacts
- To assess parameter significance and robustness
- When need strategic parameter recommendations
- To generate optimization study reports for stakeholders

**What it does:**
- **Evaluates parameter optimization**: Assesses parameter significance and optimal zones
- **Strategic parameter interpretation**: Understands WHY certain parameters work better
- **Detects overfitting**: Statistical validation and bias prevention
- **Generates optimization study PDF**: Professional multi-page report with parameter recommendations
- **Provides parameter recommendations**: Actionable guidance for parameter deployment

**Key outputs**: Parameter recommendations, optimization study PDF report, robustness assessment.

**Success criteria**: Comprehensive optimization evaluation with professional report and actionable parameter recommendations.

---

## Complete Workflow Examples

### Single-Run Strategy Development

```bash
# Setup phase (required for both paths)
/validate-setup
/validate-strategy  # After completing STRAT_TEMPLATE.md
/plan-strategy "Develop RSI-based crypto momentum strategy"
/build-engine      # Auto-generates parameter_config.md template

# Single-run execution (fill parameter_config.md first)
/run                    # Execute backtest with configured parameters
/analyze-single-run     # Process data into metrics and visualizations  
/evaluate-single-run    # Generate performance evaluation and PDF report
```

### Parameter Optimization Study

```bash
# Setup phase (same as single-run)
/validate-setup
/validate-strategy
/plan-strategy "Optimize RSI strategy parameters"
/build-engine

# Optimization execution (create optimization_config.json first)
/run-optimization      # Execute parameter sweep AND analyze results
/evaluate-optimization # Evaluate optimization and generate study report
```

### Iterative Development

```bash
# After initial setup, iterate on single runs
/run                   # Test new parameter values
/analyze-single-run    # Process updated results
/evaluate-single-run   # Compare against previous runs

# Or run optimization studies
/run-optimization      # Test parameter robustness
/evaluate-optimization # Get parameter recommendations

# Major strategy changes require rebuild
/validate-strategy     # After updating STRAT_TEMPLATE.md
/build-engine         # Rebuild with new logic
# Then proceed with run or optimization path
```

## Key Features

### **Dual-Path Architecture Benefits**
- **Single-Run Path**: Fast iteration and testing of specific parameter sets
- **Optimization Path**: Systematic parameter exploration with overfitting prevention
- **Shared Setup**: Common foundation ensures consistency across both paths
- **Independent Execution**: Choose the appropriate path for your current need

### **Simplified Agent Responsibilities**
- **trading-single-analyzer**: Executes backtests AND processes single-run data
- **trading-optimizer**: Executes parameter sweeps AND analyzes optimization results  
- **Evaluators**: Focus purely on strategic interpretation and professional reporting
- **No Redundancy**: Each agent has clear, non-overlapping responsibilities

### **Automatic Quality Enforcement**
- **Hooks system**: Prevents progression without meeting quality gates
- **Parameter validation**: Ensures completeness before execution
- **Progress reporting**: Unified progress bars with ETA across all phases
- **Auto-sync**: Documentation updates automatically via git hooks

### **Professional Outputs**
- **Publication-quality visualizations**: High-resolution charts ready for reports
- **LaTeX PDF reports**: Scientific-quality documents for stakeholders
- **Comprehensive metrics**: Statistical analysis with confidence intervals
- **Strategic insights**: Performance evaluation with actionable recommendations

### **Parameter Management System**
- **Auto-generation**: `parameter_config.md` created automatically by `/build-engine`
- **Version control**: All configurations tracked for reproducibility
- **Validation**: Completeness checking before execution
- **No CLI arguments**: All settings in configuration files

## Command Dependencies & Flow

### **Setup Phase (Linear - Required for Both Paths)**
1. **`/validate-setup`**: No dependencies (entry point)
2. **`/validate-strategy`**: Requires completed STRAT_TEMPLATE.md
3. **`/plan-strategy`**: Requires strategy validation to pass
4. **`/build-engine`**: Requires development plan and valid strategy template

### **Single-Run Path (Linear)**
5. **`/run`**: Requires built engine and completed parameter_config.md  
6. **`/analyze-single-run`**: Requires successful backtest execution
7. **`/evaluate-single-run`**: Requires analysis artifacts and visualizations

### **Optimization Path (Linear)**
5. **`/run-optimization`**: Requires built engine and completed optimization_config.json
6. **`/evaluate-optimization`**: Requires optimization analysis artifacts

## Success Indicators

### Green Lights (Proceed)
- ✅ All validation gates pass
- ✅ Parameter configuration complete (no [REQUIRED] markers)
- ✅ Professional visualizations generated
- ✅ LaTeX PDF compiles successfully
- ✅ Performance evaluation provides clear rating

### Red Lights (Fix Required) 
- ❌ System dependencies missing
- ❌ Strategy template incomplete
- ❌ Parameter configuration has [REQUIRED] markers
- ❌ Analysis validation failures
- ❌ LaTeX compilation errors

## Best Practices

### **Path Selection Strategy**
1. **Use Single-Run Path when**:
   - Testing specific parameter combinations
   - Debugging strategy logic
   - Quick iterations and refinements
   - Initial strategy validation

2. **Use Optimization Path when**:
   - Seeking robust parameter configurations
   - Validating parameter stability across market conditions
   - Systematic parameter space exploration
   - Final parameter selection for deployment

### **Strategy Development**
1. **Complete templates fully**: No placeholders in STRAT_TEMPLATE.md
2. **Validate early**: Run validation commands before lengthy operations
3. **Parameter discipline**: Fill all required parameters before execution
4. **Choose appropriate path**: Single-run for testing, optimization for robustness

### **Quality Assurance**
1. **Check visualizations**: Ensure charts are professional quality
2. **Review reports**: Verify PDF output meets stakeholder needs
3. **Validate insights**: Confirm strategic analysis is actionable
4. **Test reproducibility**: Ensure configurations are version-controlled

### **Performance Optimization**
1. **System resources**: Ensure adequate RAM and disk space
2. **Progress monitoring**: Use ETA estimates for planning
3. **Parameter ranges**: Stay within validated parameter bounds
4. **Batch processing**: Complete full workflow cycles efficiently

## Optimization Benefits for Users

### **Automatic Speed Optimizations**
The framework includes advanced optimization infrastructure that provides **10-50x speedup** for parameter sweeps automatically:

- **Universal Application**: Optimizations work with ANY trading strategy without modification
- **Automatic Integration**: Speed benefits are enabled by default - no configuration needed
- **Strategy-Agnostic**: Whether you use RSI, moving averages, or complex signals, optimizations apply

### **How Optimizations Work**
1. **Smart Parameter Testing**: Restrictive parameters automatically test fewer symbols
2. **Feature Caching**: Technical indicators are calculated once and reused across parameter combinations
3. **Universe Reduction**: Parameter sweeps focus on symbols that showed activity in baseline runs
4. **Filter Shortcuts**: Threshold-based filters use cached results for faster processing

### **Performance Expectations**
- **Without Optimization**: 100 parameter combinations = 100x single run time
- **With Optimization**: 100 parameter combinations = 5-10x single run time
- **Best Case**: 50x speedup for strategies with restrictive parameter ranges

### **User Configuration**
Most optimizations are automatic, but you can control some aspects in your strategy configuration:
- **Enable/disable optimizations**: Generally recommended to keep enabled
- **Universe reduction limits**: Control how aggressively symbol universe is reduced
- **Feature caching**: Automatic technical indicator optimization

### **When You'll See the Biggest Benefits**
- **Parameter optimization studies** (`/run-optimization`): Maximum speedup
- **Strategies with threshold filters**: RSI levels, volume filters, price filters
- **Large symbol universes**: More symbols = bigger optimization impact
- **Multiple parameter dimensions**: Testing RSI period AND volume threshold together

---

This streamlined 9-command dual-path workflow transforms strategy development from scattered operations into two coherent, professional processes: fast single-run iteration and systematic parameter optimization, both producing publication-quality outputs and strategic insights.