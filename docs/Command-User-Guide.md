# Trading Strategy Command User Guide (New 8-Command Workflow)

This guide explains the streamlined 8-command workflow for trading strategy development, evaluation, and reporting.

## Overview

The trading strategy framework now provides **8 focused commands** that follow a clear, linear workflow:

```
/validate-setup → /validate-strategy → /plan-strategy → /build-engine → /run → /analyze-run → /evaluate-run → (iterate)
```

Each command has a single, clear purpose with automatic quality enforcement and professional outputs.

---

## The 8 Commands

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

### 6. 📈 `/analyze-run` - Data Analysis & Visualization

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

### 7. 🎯 `/evaluate-run` - Performance Evaluation & Strategic Analysis

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

### 8. 📄 `/create-report` - Report Generation (Alias)

**Purpose**: Alias for `/evaluate-run` with emphasis on PDF report generation.

**When to use:**
- When primary goal is generating professional documentation
- For stakeholder presentations and business reviews
- When emphasis is on report output vs. evaluation process

**What it does**: Identical to `/evaluate-run` - provides semantic clarity about report generation focus.

---

## Complete Workflow Example

### First-Time Strategy Development

```bash
# 1. Validate system is ready
/validate-setup

# 2. Complete STRAT_TEMPLATE.md, then validate it
/validate-strategy  

# 3. Create development plan
/plan-strategy "Develop RSI-based crypto momentum strategy"

# 4. Build engine and auto-generate parameter template
/build-engine

# 5. Edit parameter_config.md (fill in all [REQUIRED] values), then run
/run

# 6. Process data and create professional visualizations  
/analyze-run

# 7. Evaluate performance and generate PDF report
/evaluate-run
```

### Iterative Development

```bash
# Update parameters and test
/run           # Uses updated parameter_config.md
/analyze-run   # Process new results
/evaluate-run  # Compare against previous runs

# Major strategy changes
/validate-strategy  # After updating STRAT_TEMPLATE.md
/build-engine      # Rebuild with new logic
/run              # Test new implementation
/analyze-run      # Analyze new results  
/evaluate-run     # Evaluate changes
```

## Key Features

### Automatic Quality Enforcement
- **Hooks system**: Prevents progression without meeting quality gates
- **Parameter validation**: Ensures completeness before execution
- **Progress reporting**: Unified progress bars with ETA across all phases
- **Auto-sync**: Documentation updates automatically via git hooks

### Professional Outputs
- **Publication-quality visualizations**: High-resolution charts ready for reports
- **LaTeX PDF reports**: Scientific-quality documents for stakeholders
- **Comprehensive metrics**: Statistical analysis with confidence intervals
- **Strategic insights**: Performance evaluation with actionable recommendations

### Parameter Management System
- **Auto-generation**: `parameter_config.md` created automatically by `/build-engine`
- **Version control**: All configurations tracked for reproducibility
- **Validation**: Completeness checking before execution
- **No CLI arguments**: All settings in configuration files

### Clear Separation of Concerns
- **Analyzer**: Data processing and visualization (WHAT happened)
- **Evaluator**: Performance evaluation and strategic interpretation (WHAT it MEANS)
- **No overlap**: Each agent has focused, specific responsibilities

## Command Dependencies

Each command has clear prerequisites:

1. **`/validate-setup`**: No dependencies (entry point)
2. **`/validate-strategy`**: Requires completed STRAT_TEMPLATE.md
3. **`/plan-strategy`**: Requires strategy validation to pass
4. **`/build-engine`**: Requires development plan and valid strategy template
5. **`/run`**: Requires built engine and completed parameter_config.md  
6. **`/analyze-run`**: Requires successful backtest execution
7. **`/evaluate-run`**: Requires analysis artifacts and visualizations
8. **`/create-report`**: Same as evaluate-run (alias)

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

### Strategy Development
1. **Complete templates fully**: No placeholders in STRAT_TEMPLATE.md
2. **Validate early**: Run validation commands before lengthy operations
3. **Parameter discipline**: Fill all required parameters before `/run`
4. **Iterative approach**: Use workflow for systematic improvements

### Quality Assurance
1. **Check visualizations**: Ensure charts are professional quality
2. **Review reports**: Verify PDF output meets stakeholder needs
3. **Validate insights**: Confirm strategic analysis is actionable
4. **Test reproducibility**: Ensure configurations are version-controlled

### Performance Optimization
1. **System resources**: Ensure adequate RAM and disk space
2. **Progress monitoring**: Use ETA estimates for planning
3. **Parameter ranges**: Stay within validated parameter bounds
4. **Batch processing**: Complete full workflow cycles efficiently

This streamlined 8-command workflow transforms strategy development from scattered operations into a coherent, professional process with publication-quality outputs and strategic insights at every step.