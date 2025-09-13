# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Framework to **build, evaluate, and iteratively optimize trading strategies** (backtest engine now, bot engine later). Goals: **realistic, live-executable strats**, **profitable in backtests**, and **optimizable**.

## Key Architecture Components

**Backtest Engine** (`scripts/engine/backtest.py`):
- Modular architecture with clear separation of concerns
- Dual import system supports both module and direct execution
- Automatic optimization components (FilterGateManager, ReferenceEngine) for speed
- Test strategy: RSIMeanReversionStrategy for skeleton validation

**Component Hierarchy**:
- **Core**: Portfolio, Orders, Risk Management, FilterGateManager
- **Data**: Fetcher, Processor (with caching and optimization)
- **Execution**: Fill Simulator, Fee Calculator, Timing Engine
- **Optimization**: Reference Engine, feature caching, incremental computation
- **Utils**: Config Parser (markdown/YAML), Progress Tracker, Validators

## Development Commands

**Core commands:**
- `python scripts/quiet_mode.py [on|off|status]` - Control agent output verbosity (default: quiet mode to prevent screen flickering)
- `pip install -r requirements.txt` - Install Python dependencies (pandas, numpy, matplotlib, scipy, etc.)
- `python scripts/initialization/initialize_strategy.py` - Transform skeleton to specific strategy project
- `pytest` - Run test suite (if tests exist)

**Direct execution (without slash commands):**
- `PYTHONPATH=. python -m scripts.engine.backtest parameter_config.md` - Direct backtest execution
- `PYTHONPATH=. python -m scripts.engine.backtest parameter_config.md --validate-accounting` - With accounting validation
- `PYTHONPATH=. python -m scripts.engine.backtest test_parameter_config.md --test-mode` - Test mode execution (small universe, 6-month period)
- `python scripts/single_analysis/analyze_run.py [run_id]` - Analyze completed backtest
- `python scripts/single_evaluation/evaluator.py [run_id]` - Evaluate performance and generate reports
- `python scripts/optimization/run_optimization.py [optimization_config.json]` - Direct optimization execution
- `python scripts/run_full_test_suite.py` - Run complete test validation suite

**Key dependencies:** pandas, numpy, matplotlib, seaborn, plotly, scipy, scikit-learn, ccxt (crypto), tqdm (progress), numba (optimization), psutil (monitoring), memory-profiler

## Validation Tools

**Environment validation:**
- `python tools/validate_setup.py` - Check environment and dependencies
- `python tools/validate_strategy.py` - Validate strategy specification in SMR

**Testing framework:**
- `test_parameter_config.md` - Pre-configured test setup (3 symbols, 6 months, RSI strategy)
- `test_optimization_config.json` - Test parameter sweep configuration
- Test runs use `test_run_XXX` naming pattern for easy identification
- Validation hooks automatically check for lookahead bias and accounting integrity

**Note:** Skeleton test commands (`run_test.py`, `test_parameter_config.md`, etc.) are removed during `/initialize` transformation. After transformation, use `/build-engine` to create your strategy-specific engine and test it with your own parameter configurations.

## Abbreviations

* **EMR**: Engine Master Report (engine spec)
* **SMR**: Strategy Master Report (strategy spec)  
* **ECL/SCL**: Engine/Strategy Changelogs (append-only)
* **ECN/SER/SDCN**: Engine Change Notice / Strategy Evaluation Report / Strategy Definition Change Notice

## Always do this

* Start in **PLAN mode**; keep `cloud/tasks/<task>.md` with **goals, owners, deps, gates, milestones**
* Prefer **slash commands**: `/initialize` (skeleton transformation + cleanup), `/validate-setup`, `/validate-strategy`, `/plan-strategy`, `/build-engine`, `/run`, `/analyze-single-run`, `/evaluate-single-run`, `/run-optimization`, `/evaluate-optimization`
* `/docs/**` is authoritative; changelogs are append-only
* **Progress bar requirement**: All Python scripts MUST implement unified progress reporting with ETA
* **Universal Speed Optimization**: All agents MUST leverage FilterGateManager, DataProcessor optimization, and ReferenceEngine for maximum speed (see .claude/docs/optimization-patterns.md)
* **Quiet Mode**: Default mode suppresses detailed output to prevent screen flickering. Use `python scripts/quiet_mode.py off` to enable detailed progress output for debugging

## Skeleton Transformation (/initialize)

**What gets removed during transformation:**
* All test configurations: `test_parameter_config.md`, `test_config.json`, `test_optimization_config.json`
* Test scripts: `run_test.py`, `test_optimization_simple.py`, `scripts/create_test_data.py`, `scripts/create_discrepancy_test.py`, `scripts/run_full_test_suite.py`
* Test strategy: `scripts/engine/rsi_mean_reversion_strategy.py` (skeleton's RSI example)
* Test data: `/data/test_runs/`, `/data/test_results/`, `/docs/test/`
* Test analysis: `scripts/single_analysis/analyze_test*.py`, `scripts/single_analysis/detailed_test_report.py`
* Test evaluation: `scripts/single_evaluation/evaluate_test.py`
* Test artifacts: `docs/notices/SER/SER_test_*.json`, `docs/TESTING.md`
* Skeleton metadata: `SKELETON_VERSION.md`, skeleton-specific tasks in `/cloud/tasks/test_*.md`

**What remains after transformation:**
* Complete agent and command infrastructure (`.claude/`)
* Engine framework ready for customization (`scripts/engine/`)
* Full analysis and optimization pipelines
* Documentation framework (EMR, SMR, changelogs)
* Tools, hooks, and configuration templates

## Workflow (dual-path: single-run + optimization)

**Common Setup & Planning (4 commands):**
1. **Setup & Validation**: `/validate-setup` → `/validate-strategy` → `/plan-strategy`
2. **Engine Building**: `/build-engine` (auto-generates parameter_config.md)

**Single-Run Path:**
3. **Individual Steps**: `/run` → `/analyze-single-run` → `/evaluate-single-run`

**Optimization Path:**
4. **Individual Steps**: `/run-optimization` → `/evaluate-optimization`

## Roles

**Common Agents:**
* **Orchestrator**: **ALWAYS ACTIVE** - coordinate ALL commands; plan/route; keep **EMR/SMR** authoritative; **ECL/SCL** append-only; block runs until docs fresh; **handle handoffs from ALL specialist agents for documentation updates**
* **Builder**: implement/optimize engine; hardware-aware session initialization; unit/smoke/perf tests; emit **ECN** (+ benchmarks with hardware profile); **MUST include FilterGateManager, optimized DataProcessor, and ReferenceEngine in generated engines for automatic speed optimization**

**Single-Run Agents:**
* **Single-Analyzer**: execute single backtests AND process run data; read parameter_config.md; emit **manifest, metrics, trades, events, series, figs**; sanity-check and flag anomalies  
* **Single-Evaluator**: **evaluate single-run performance** (assess metrics quality, compare to benchmarks); **strategic interpretation** (understand WHY strategy works/fails); **generate LaTeX PDF reports**; emit **SER**; if spec changed, **SDCN**

**Optimization Agents:**
* **Optimizer**: execute parameter sweeps AND process optimization data; read optimization_config.json; coordinate multiple backtests with walk-forward validation; create parameter performance matrices, robustness heatmaps, statistical validation; **MUST use OptimizationEngine with FilterGateManager, ReferenceEngine, and feature caching for 10-50x speedup**
* **Optimization-Evaluator**: **evaluate parameter optimization** (assess parameter significance, detect overfitting); **strategic parameter interpretation** (understand WHY parameters work); **generate optimization study PDF reports**

## Handoffs & gates

**Command Orchestration Pattern:**
ALL slash commands follow: **User → Orchestrator → Specialist Agent → Orchestrator → Documentation Update**

**Common Handoffs:**
* **`/build-engine`**: Orchestrator → Builder → **ECN + benchmarks** → Orchestrator updates **EMR** & appends **ECL**
* **`/validate-setup`**: Orchestrator → validation logic → documentation updates as needed
* **`/validate-strategy`**: Orchestrator → validation logic → SMR updates if needed

**Single-Run Handoffs:**
* **`/run`**: Orchestrator → Single-Analyzer → processed artifacts + run_registry row → Orchestrator
* **`/analyze-single-run`**: Orchestrator → Single-Analyzer → analysis artifacts → Single-Evaluator handoff → Orchestrator  
* **`/evaluate-single-run`**: Orchestrator → Single-Evaluator → **SER** (and **SDCN** if spec changed) → Orchestrator updates **SMR** & appends **SCL**

**Optimization Handoffs:**
* **`/run-optimization`**: Orchestrator → Optimizer → optimization data → Orchestrator
* **`/evaluate-optimization`**: Orchestrator → Optimization-Evaluator → **Optimization Report** → Orchestrator updates documentation

**Gates:**
* **Documentation Gate**: Orchestrator blocks ALL commands until EMR/SMR in sync with latest changelogs
* **Single-Run Gate**: `/analyze-single-run` must complete before `/evaluate-single-run`
* **Optimization Gate**: `/run-optimization` must complete before `/evaluate-optimization`
* **Handoff Gate**: ALL agents must complete handoff to Orchestrator for documentation updates

## Data & ingestion

Source & cache declared in EMR; OHLCV in UTC; define missing-bar policy; fees/slippage model versioned.

## Testing & failure handling

* Golden-set parity; unit tests for rule semantics; determinism (seeded) test; small-universe integration run
* On any failed hook/validator: **stop**, log, notify, do not proceed

## File layout

**Clean Script vs Data Separation:**

```
/scripts/                    # Execution scripts (organized by agent)
├── engine/                  # /build-engine generates here
│   ├── backtest.py         # Main backtest engine (with optimization components)
│   ├── strategy_engine.py  # Generated strategy code
│   ├── core/              # Portfolio, orders, risk management, FilterGateManager
│   ├── data/              # Data fetching and processing (with optimization)
│   ├── execution/         # Fill simulation, fees, slippage
│   ├── optimization/      # ReferenceEngine and optimization infrastructure
│   └── utils/             # Config parsing, progress tracking
├── analyzer/              # /run execution scripts
├── single_analysis/       # /analyze-single-run scripts
├── single_evaluation/     # /evaluate-single-run scripts
├── optimization/          # /run-optimization scripts (OptimizationEngine)
└── opt_evaluation/        # /evaluate-optimization scripts

/data/                      # Generated outputs (separate from scripts)
├── runs/{run_id}/         # Single backtest outputs
│   ├── manifest.json
│   ├── metrics.json
│   ├── trades.csv, events.csv, series.csv
│   └── figures/
├── optimization/{study_id}/  # Parameter optimization outputs
├── reports/               # Generated PDF reports
└── cache/                 # Data fetching cache

/docs/                     # Documentation and registries
├── EMR.md SMR.md ECL.md SCL.md
├── runs/run_registry.csv
├── notices/{ECN|SER|SDCN}/
└── research/
```

## Guardrails

* No lookahead (features ≤ t; actions next bar open)
* Fees/slippage + minNotional rounding; flag impossible fills
* Accounting: `Equity_{t+1} = Equity_t + realizedPnL − fees`
* Determinism; sanity flags (e.g., extreme Sortino, zero DD)

## Progress Bar Standards

* **Python Scripts**: All must use unified progress libraries (tqdm, rich, progressbar2) with ETA
* **Format**: `Task description... ████████░░░░ 75% (~2 min remaining)`
* **One progress bar per major task** - no micro-task progress spam
* **Integration**: Python scripts report to shared progress tracking system
* **Claude Level**: Display umbrella progress for command coordination phases

## Visualization Standards

* **Research-Based Design**: No dual-axis charts, prioritize visual clarity over metric cramming
* **3-Panel Default**: Equity curve (70%) + Drawdown (20%) + Activity (10%) stacked layout
* **Professional Quality**: PDF vector graphics for LaTeX, PNG 300+ DPI for HTML
* **Smart Time Axis**: Auto-detect optimal spacing (<90d: daily, <365d: weekly, <1095d: monthly, 3y+: quarterly)
* **Template Configuration**: Basic/Enhanced/Advanced levels with benchmark and per-symbol options
* **File Formats**: Generate both PDF and PNG, use PDF for LaTeX reports, PNG for HTML fallback
* **Color Standards**: Colorblind-friendly palettes, professional typography, publication-ready quality

## Configuration Systems

**Single-Run Configuration:**
* **Strategy Template**: Defines parameter schema (types, ranges, descriptions)
* **Auto-generation**: `/build-engine` creates `parameter_config.md` template
* **Single Execution**: `/run` reads all settings from `parameter_config.md` (no CLI arguments)
* **Version Control**: All parameter configs are version-controlled for reproducibility
* **Test Configuration**: `test_parameter_config.md` exists for skeleton validation (small universe, 6-month period)

**Optimization Configuration:**
* **Optimization Template**: Defines parameter sweep ranges, search method, validation approach
* **Manual Creation**: User creates `optimization_config.json` with parameter ranges and search strategy
* **Search Methods**: Grid search, random search, Bayesian optimization
* **Walk-Forward Setup**: Training/validation windows, rolling periods, robustness testing
* **Optimization Execution**: `/run-optimization` reads `optimization_config.json` for parameter sweep specification

## Registry & Git

**Single-Run Registry:**
* Single-Analyzer appends `/docs/runs/run_registry.csv` per individual run
* Each row tracks single backtest execution with performance metrics

**Optimization Registry:**
* Optimizer appends `/docs/optimization/optimization_registry.csv` per parameter study
* Each row tracks optimization study with parameter sweep metadata and results

**Git Integration:**
* On any `/docs/**` change (reports, changelogs, notices, registries) **auto-commit & push**
* Do **not** commit `/data/**` by default (individual runs and optimization studies)

**Git Configuration Requirements:**
* **Git Bash**: Required for automated GitHub integration on Windows
* **GitHub CLI**: Must be authenticated (`gh auth login`) for `/initialize` command
* **Default Branch**: Uses `master` as main branch (not `main`)
* **Auto-commit Pattern**: `git add docs/* && git commit -m "Update [component]" && git push`

## Development Environment

**VS Code Workspace Settings (`.vscode/settings.json`)**:
* Terminal flicker reduction for smooth Claude Code operations
* Python Black formatter integration
* Pytest test discovery enabled
* Git workflow optimizations
* **Open with workspace file** (`{strategy-name}.code-workspace`) to activate settings

**Quiet Mode System**:
* Default: Quiet mode ON (prevents screen flickering)
* Status check: `python scripts/quiet_mode.py status`
* Toggle: `python scripts/quiet_mode.py [on|off]`
* Affects all agent output verbosity globally

## Current Implementation Status

**Engine Components:**
* ✅ Core backtest engine (`scripts/engine/backtest.py`) - fully tested and functional
* ✅ Configuration parser with markdown and YAML list support - handles `test_parameter_config.md` correctly
* ✅ RSI Mean Reversion strategy implementation - validated with test runs
* ✅ Full optimization stack (FilterGateManager, ReferenceEngine, TimingEngine) - tested and operational
* ✅ Comprehensive progress tracking and quiet mode system - working correctly
* ✅ Accounting validation system - passes all integrity checks

**Slash Commands - All Working:**
* ✅ Complete 7-command workflow tested: `/validate-setup` → `/validate-strategy` → `/plan-strategy` → `/build-engine` → `/run` → `/analyze-single-run` → `/evaluate-single-run`
* ✅ Pipeline gates enforce proper sequencing and prevent progression on failures
* ✅ Inter-agent coordination and handoffs working correctly
* ✅ Documentation updates and artifact generation functional

**Agent Scripts - All Functional:**
* ✅ `scripts/analyzer/run_executor.py` - Run coordination and execution
* ✅ `scripts/single_analysis/analyze_test_run.py` - Analysis with visualizations (~10s execution)
* ✅ `scripts/single_evaluation/evaluator.py` - Performance evaluation and reporting
* ✅ `scripts/optimization/optimization_engine.py` - Parameter sweeps with walk-forward validation
* ✅ `scripts/opt_evaluation/evaluate_optimization.py` - Optimization results analysis

**Testing Infrastructure:**
* ✅ `test_parameter_config.md` - Complete test configuration (3 symbols, 6 months, RSI strategy)
* ✅ `test_optimization_config.json` - Parameter sweep configuration for testing
* ✅ Complete test suite documented in `docs/TESTING.md`
* ✅ Automated test validation with `scripts/run_full_test_suite.py`

**Performance Baselines (Confirmed):**
* Basic backtest: 8-10 seconds (950 records, 3 symbols, 6 months)
* Single analysis: 10-12 seconds with visualizations
* Complete slash workflow: 2-3 minutes end-to-end
* Memory usage: <500MB for optimization, <200MB for analysis

**Ready for Production Use:**
* All core uncertainties resolved and tested
* Complete documentation for troubleshooting and validation
* Automated testing ensures skeleton health
* Error handling validated for common edge cases

## Common Troubleshooting

**Screen flickering during agent execution:**
- Default quiet mode enabled (check with `python scripts/quiet_mode.py status`)
- To debug: `python scripts/quiet_mode.py off` (re-enable with `on`)

**Parameter config parsing issues:**
- Config parser expects markdown format with YAML-style lists
- Values after `#` are treated as comments and stripped
- `/build-engine` generates a proper `parameter_config.md` template for your strategy
- Test config uses comma-separated symbols: `BTCUSDT,ETHUSDT,ADAUSDT`

**Direct backtest execution:**
- Must set PYTHONPATH: `PYTHONPATH=. python -m scripts.engine.backtest parameter_config.md`
- Config file path is first argument after module name
- Add `--validate-accounting` flag for accounting validation
- Use `--test-mode` flag with `test_parameter_config.md` for testing

**Git/GitHub issues:**
- Ensure Git Bash is used (not cmd/PowerShell) for GitHub operations
- Verify `gh auth status` shows authenticated
- Repository uses `master` branch (not `main`)

**Missing dependencies:**
- Run `pip install -r requirements.txt` before any operations
- MiKTeX optional but recommended for PDF reports (install and add to PATH: `C:\Users\{username}\AppData\Local\Programs\MiKTeX\miktex\bin\x64`)
- ccxt required for crypto data fetching

**Windows-specific setup:**
- Use Git Bash as default terminal in VS Code for best experience
- Open with workspace file (`.code-workspace`) for optimized settings
- Quiet mode prevents terminal output issues on Windows