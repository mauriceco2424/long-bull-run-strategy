# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Framework to **build, evaluate, and iteratively optimize trading strategies** (backtest engine now, bot engine later). Goals: **realistic, live-executable strats**, **profitable in backtests**, and **optimizable**.

## Abbreviations

* **EMR**: Engine Master Report (engine spec)
* **SMR**: Strategy Master Report (strategy spec)  
* **ECL/SCL**: Engine/Strategy Changelogs (append-only)
* **ECN/SER/SDCN**: Engine Change Notice / Strategy Evaluation Report / Strategy Definition Change Notice

## Always do this

* Start in **PLAN mode**; keep `cloud/tasks/<task>.md` with **goals, owners, deps, gates, milestones**
* Prefer **slash commands**: `/validate-setup`, `/validate-strategy`, `/plan-strategy`, `/build-engine`, `/run`, `/analyze-single-run`, `/evaluate-single-run`, `/run-optimization`, `/evaluate-optimization`
* `/docs/**` is authoritative; changelogs are append-only
* **Progress bar requirement**: All Python scripts MUST implement unified progress reporting with ETA

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
* **Orchestrator**: plan/route; keep **EMR/SMR** authoritative; **ECL/SCL** append-only; block runs until docs fresh
* **Builder**: implement/optimize engine; hardware-aware session initialization; unit/smoke/perf tests; emit **ECN** (+ benchmarks with hardware profile)

**Single-Run Agents:**
* **Single-Analyzer**: execute single backtests AND process run data; read parameter_config.md; emit **manifest, metrics, trades, events, series, figs**; sanity-check and flag anomalies  
* **Single-Evaluator**: **evaluate single-run performance** (assess metrics quality, compare to benchmarks); **strategic interpretation** (understand WHY strategy works/fails); **generate LaTeX PDF reports**; emit **SER**; if spec changed, **SDCN**

**Optimization Agents:**
* **Optimizer**: execute parameter sweeps AND process optimization data; read optimization_config.md; coordinate multiple backtests with walk-forward validation; create parameter performance matrices, robustness heatmaps, statistical validation
* **Optimization-Evaluator**: **evaluate parameter optimization** (assess parameter significance, detect overfitting); **strategic parameter interpretation** (understand WHY parameters work); **generate optimization study PDF reports**

## Handoffs & gates

**Common Handoffs:**
* Builder → Orchestrator: **ECN + benchmarks** (with hardware profile) → Orchestrator updates **EMR** & appends **ECL**

**Single-Run Handoffs:**
* Single-Analyzer → Orchestrator: processed artifacts + run_registry row
* Single-Analyzer → Single-Evaluator: analysis artifacts ready for evaluation
* Single-Evaluator → Orchestrator: **SER** (and **SDCN** if spec changed) → Orchestrator updates **SMR** & appends **SCL**

**Optimization Handoffs:**
* Optimizer → Optimization-Evaluator: parameter performance matrices + robustness analysis
* Optimization-Evaluator → Orchestrator: **Optimization Evaluation Report** → Orchestrator updates documentation

**Gates:**
* **Gate**: no new runs until EMR/SMR in sync with latest changelogs
* **Single-Run Gate**: single-analyzer must complete before single-evaluator
* **Optimization Gate**: optimizer must complete before optimization-evaluator

## Data & ingestion

Source & cache declared in EMR; OHLCV in UTC; define missing-bar policy; fees/slippage model versioned.

## Testing & failure handling

* Golden-set parity; unit tests for rule semantics; determinism (seeded) test; small-universe integration run
* On any failed hook/validator: **stop**, log, notify, do not proceed

## File layout

```
/docs/ EMR.md SMR.md ECL.md SCL.md
/docs/runs/run_registry.csv
/docs/notices/{ECN|SER|SDCN}/
/docs/research/{analyzer|evaluator}/<topic>-<YYYYMMDD>.md
/data/sandbox/{run_id}/
/data/runs/{run_id}/  (manifest.json, metrics.json, trades.csv, events.csv, series.csv, figs/)
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