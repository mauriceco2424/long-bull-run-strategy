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
* Prefer **slash commands**: `/kickoff`, `/build-run`, `/analyze-run`, `/evaluate`
* `/docs/**` is authoritative; changelogs are append-only

## Workflow (loop)

1. Build engine per SMR → 2) Create data (run) → 3) Analyze data → 4) Evaluate performance & realism; **rank impact of each feature/mechanism** → 5) Suggest parameter/mechanism changes → 6) Implement changes → **repeat**

## Roles

* **Orchestrator**: plan/route; keep **EMR/SMR** authoritative; **ECL/SCL** append-only; block runs until docs fresh
* **Builder**: implement/optimize engine; hardware-aware session initialization; unit/smoke/perf tests; emit **ECN** (+ benchmarks with hardware profile)
* **Analyzer**: run backtests; emit **manifest, metrics, trades, events, series, figs**; sanity-check and flag anomalies
* **Evaluator**: interpret results (profitability + realism); **rank feature/mech impact**; emit **SER**; if spec changed, **SDCN**

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

## Run registry & Git

* Analyzer appends `/docs/runs/run_registry.csv` per run
* On any `/docs/**` change (reports, changelogs, notices, registry) **auto-commit & push**
* Do **not** commit `/data/**` by default