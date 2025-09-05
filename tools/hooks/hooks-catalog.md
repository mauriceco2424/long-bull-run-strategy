# Hooks Catalog

---
name: hooks-catalog
description: Canonical hook points for the trading pipeline. Each hook defines when it fires, what it does, and how failures are handled. All hooks receive a common payload (ctx) and are synchronous unless marked nonblocking.
owner: trading-orchestrator
model: haiku
color: slate
disable: [Write, Bash, KillBash, BashOutput, TodoWrite, MultiEdit, WebFetch]
---

## Common Payload (ctx)
All hooks receive:
- `run_id` (str)
- `run_path` (str) — e.g., /data/runs/<run_id>
- `phase` (str) — orchestrator|analyzer|evaluator|report|registry
- `manifest_path` (str, optional)
- `metrics_path` (str, optional)
- `trades_path` (str, optional)
- `series_path` (str, optional)
- `events_path` (str, optional)
- `config_hash` (str)
- `engine_version` (str)
- `universe` (str)
- `date_start` (YYYY-MM-DD), `date_end` (YYYY-MM-DD)
- `seed` (int)
- `cache_tag` (str, optional)
- `offline` (bool)
- `notes` (str, optional)

**Failure policy:**  
- P0 → halt pipeline (sync).  
- P1 → continue but require rerun decision.  
- P2 → log only (nonblocking).

---

## A) Minimal Core Hooks (implemented)

### 1) `before_analyzer_run` (blocking, P0)
**Purpose:** Guard resources & preconditions.  
**Checks:** free disk/RAM, cache availability (if offline), config hash present, universe resolvable, time range sane.  
**Location:** `tools/hooks/core/before_analyzer_run.py`

### 2) `after_analyzer_run` (blocking, P0)
**Purpose:** Artifact sanity & integrity.  
**Checks:** required files exist; SHA256 checks; row counts > 0; timestamps monotonic; no NaNs in essential cols.  
**Location:** `tools/hooks/core/after_analyzer_run.py`

### 3) `before_evaluator` (blocking, P0)
**Purpose:** Ensure evaluator has what it needs and no known red flags from analyzer.  
**Checks:** manifest/events red flags (lookahead/liquidity/accounting).  
**Location:** `tools/hooks/core/before_evaluator.py`

### 4) `after_evaluator` (blocking, P1)
**Purpose:** Act on decision.  
**Logic:** If decision = halt → raise P0 alert; rerun → schedule follow-up (safety mode can gate); pass → continue.  
**Location:** `tools/hooks/core/after_evaluator.py`

### 5) `before_registry_append` (blocking, P0)
**Purpose:** CSV/lock integrity.  
**Actions:** acquire `docs/runs/registry.lock`, validate headers, check duplicate run_id policy.  
**Location:** `tools/hooks/core/before_registry_append.py`

### 6) `after_registry_append` (nonblocking, P2)
**Purpose:** Observability.  
**Actions:** console summary, optional TG/Slack ping, update lightweight README status.  
**Location:** `tools/hooks/core/after_registry_append.py`

**Nonblocking observability hooks (core):**  
- `on_plot_error` → append `run_path/logs/plots.log` (P2).  
- `on_anomaly_detected` → append `docs/runs/anomaly_registry.csv` (P2).

---

## Hook Handler Conventions

- **Idempotency:** All blocking hooks must be idempotent (safe to re-fire on retry).  
- **Timeouts:** Default 60s blocking, 10s nonblocking.  
- **Outputs:** Blocking hooks may write a compact JSON note to `run_path/hooks/<hook>.json`.  
- **Locking:** Registry writes use `docs/runs/registry.lock` (file lock + 5-minute timeout).  
- **Config:** Hook toggles via `hooks.yaml` allow per-hook enable/disable without code changes.