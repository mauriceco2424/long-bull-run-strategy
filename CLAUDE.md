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
* Prefer **slash commands**: `/validate-setup`, `/validate-strategy`, `/plan-strategy`, `/build-engine`, `/run`, `/analyze-run`, `/evaluate-run`
* `/docs/**` is authoritative; changelogs are append-only
* **Progress bar requirement**: All Python scripts MUST implement unified progress reporting with ETA

## Workflow (streamlined 8-command flow)

1. **Setup & Validation**: `/validate-setup` → `/validate-strategy` → `/plan-strategy`
2. **Execution**: `/build-engine` (auto-generates parameter_config.md) → `/run` (uses parameter_config.md)
3. **Analysis**: `/analyze-run` (data processing + visualization) → `/evaluate-run` (performance evaluation + strategic interpretation + PDF report)
4. **Iteration**: Modify parameters or strategy → repeat from step 2

## Roles

* **Orchestrator**: plan/route; keep **EMR/SMR** authoritative; **ECL/SCL** append-only; block runs until docs fresh
* **Builder**: implement/optimize engine; hardware-aware session initialization; unit/smoke/perf tests; emit **ECN** (+ benchmarks with hardware profile)
* **Analyzer**: run backtests; emit **manifest, metrics, trades, events, series, figs**; sanity-check and flag anomalies
* **Evaluator**: **evaluate performance** (assess metrics quality, compare to benchmarks); **strategic interpretation** (understand WHY strategy works/fails); **generate LaTeX PDF reports**; emit **SER**; if spec changed, **SDCN**

## Handoffs & gates

* Builder → Orchestrator: **ECN + benchmarks** (with hardware profile) → Orchestrator updates **EMR** & appends **ECL**
* Analyzer → Orchestrator: artifacts + run_registry row
* Evaluator → Orchestrator: **SER** (and **SDCN** if spec changed) → Orchestrator updates **SMR** & appends **SCL**
* **Gate**: no new runs until EMR/SMR in sync with latest changelogs

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

## Parameter Configuration System

* **Strategy Template**: Defines parameter schema (types, ranges, descriptions)
* **Auto-generation**: `/build-engine` creates `parameter_config.md` template
* **Execution**: `/run` reads all settings from `parameter_config.md` (no CLI arguments)
* **Version Control**: All parameter configs are version-controlled for reproducibility

## Run registry & Git

* Analyzer appends `/docs/runs/run_registry.csv` per run
* On any `/docs/**` change (reports, changelogs, notices, registry) **auto-commit & push**
* Do **not** commit `/data/**` by default