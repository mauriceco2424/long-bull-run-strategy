# Trading Strategy Framework Skeleton

A production-ready framework for building, backtesting, and optimizing trading strategies using Claude Code agents and a sophisticated pipeline architecture.

## 🚀 Quick Start

### **New Strategy Project Initialization**

1. **Create New Project Directory**:
   ```bash
   mkdir new_strat
   cd new_strat
   ```

2. **Clone Skeleton Content** (not the folder):
   ```bash
   git clone https://github.com/mauriceco2424/trading_bot_skeleton.git .
   rm -rf .git
   ```

3. **Define Your Strategy**:
   Edit `docs/SMR.md` following the `docs/guides/STRAT_TEMPLATE.md` format.
   **Key**: Update the `**Name**: <Strategy Name>` field with your actual strategy name.

4. **Initialize Your Strategy Project**:
   ```bash
   /initialize
   ```
   This automatically:
   - Reads strategy name from `docs/SMR.md`
   - Renames folder `new_strat` → `your-strategy-name`
   - Updates workspace file: `your-strategy-name.code-workspace`
   - Updates all files with your strategy name
   - Creates clean git repository

5. **Setup Dependencies and Validation**:
   ```bash
   /validate-setup
   ```
   (This automatically runs `pip install -r requirements.txt` if dependencies are missing)

6. **Build and Test Your Strategy**:
   ```bash
   /validate-strategy && /plan-strategy && /build-engine
   /run && /analyze-single-run && /evaluate-single-run
   ```


## 📋 What This Skeleton Provides

### 🤖 **6 Specialized Agents**

**Common Agents:**
- **trading-orchestrator**: Coordinates pipeline, manages quality gates, handles documentation
- **trading-builder**: Implements backtest engines, optimizes performance, writes ECNs

**Single-Run Agents:**
- **trading-single-analyzer**: Executes backtests AND processes single run data, generates artifacts and visualizations
- **trading-single-evaluator**: Evaluates single-run performance and generates PDF reports

**Optimization Agents:**
- **trading-optimizer**: Executes parameter sweeps AND processes optimization studies into parameter performance matrices with walk-forward analysis
- **trading-optimization-evaluator**: Evaluates parameter optimization results and generates optimization reports

### ⚡ **Streamlined Command System**

**Setup & Planning (4 commands):**
| Command | Purpose |
|---------|---------|
| `/validate-setup` | Validate framework setup and dependencies |
| `/validate-strategy` | Validate strategy specification |
| `/plan-strategy` | Plan strategy development approach |
| `/build-engine` | Build trading engine and generate parameter template |

**Single-Run Path (3 commands):**
| Command | Purpose |
|---------|---------|
| `/run` | Execute single backtest with parameter_config.md |
| `/analyze-single-run` | Process single run data into metrics and visualizations |
| `/evaluate-single-run` | Evaluate single-run performance and generate PDF report |

**Optimization Path (2 commands):**
| Command | Purpose |
|---------|---------|
| `/run-optimization` | Execute parameter sweep AND process optimization study into parameter performance matrices |
| `/evaluate-optimization` | Evaluate parameter optimization and generate optimization report |

### 🔧 **Production Hook System**
- **6 core hooks** with P0/P1/P2 priorities
- Resource validation, artifact integrity, accounting checks
- Configurable timeouts and error handling
- Safety hooks for lookahead and accounting validation

### 📚 **Documentation Framework**
- **EMR/SMR**: Engine and Strategy Master Reports with versioning
- **ECL/SCL**: Append-only changelogs
- **ECN/SER/SDCN**: Change notices and evaluation reports
- JSON schemas for all data structures

## 🏗️ Architecture

### **Directory Structure**
```
├── .claude/                    # Claude Code configuration
│   ├── agents/                # 6 specialized agents
│   └── commands/              # 9 streamlined commands
├── docs/                      # Authoritative documentation
│   ├── runs/                  # Run registry and results
│   └── schemas/               # JSON schemas
├── configs/                   # Strategy configurations
├── tools/hooks/               # Hook system
│   ├── core/                  # Essential hooks
│   ├── lib/                   # Hook infrastructure
│   └── config/                # Hook configuration
├── cloud/                     # State management
│   ├── tasks/                 # Task planning
│   └── state/                 # Runtime state
└── data/                      # Run data (not committed)
    ├── runs/                  # Backtest results
    └── sandbox/               # Development data
```

### **Dual Workflow Paths**

**Single-Run Workflow:**
1. **Setup** → `/validate-setup` → `/validate-strategy` → `/plan-strategy` → `/build-engine`
2. **Execute** → `/run` → `/analyze-single-run` → `/evaluate-single-run`

**Parameter Optimization Workflow:**
1. **Setup** → Same as single-run setup (+ create optimization_config.json)
2. **Execute** → `/run-optimization` → `/evaluate-optimization`

### **Quality Gates**
- **Docs Fresh Gate**: EMR/SMR in sync with latest changes
- **Pre-run Gates**: Tests pass, no conflicting runs
- **Post-run Gates**: Artifacts complete, anomalies flagged

## 🎯 Usage Examples

### **Single-Run Strategy Development**

```bash
/validate-setup && /validate-strategy && /plan-strategy && /build-engine
/run && /analyze-single-run && /evaluate-single-run
```

### **Parameter Optimization Study**

```bash
/validate-setup && /validate-strategy && /plan-strategy && /build-engine
# Create optimization_config.json with parameter ranges
/run-optimization && /evaluate-optimization
```

## 🔒 Safety & Validation

- **No-lookahead enforcement**: Features use data ≤ t for actions at t+1
- **Accounting integrity**: Rigorous P&L tracking with fees/slippage
- **Deterministic execution**: Seeded operations for reproducibility
- **Statistical validation**: Multiple-testing corrections, overfitting detection
- **Realism checks**: Liquidity, slippage, trade density validation

## 📊 Output Artifacts

### **Clean Script vs Data Separation**

**Scripts** (`scripts/` folder - organized by agent):
- `scripts/engine/` - Complete backtest engine with optimization components (generated by `/build-engine`)
- `scripts/analyzer/` - Run execution coordination 
- `scripts/single_analysis/` - Performance analysis
- `scripts/single_evaluation/` - Strategy evaluation and reports
- `scripts/optimization/` - High-performance parameter optimization with speed optimizations
- `scripts/opt_evaluation/` - Optimization evaluation

**Data** (`data/` folder - generated outputs only):
- `data/runs/{run_id}/` - Individual backtest outputs
  - `manifest.json`: Run metadata and hashes
  - `metrics.json`: Performance statistics
  - `trades.csv`, `events.csv`, `series.csv`: Detailed data
  - `figures/`: Professional visualizations
- `data/optimization/{study_id}/` - Parameter optimization studies
- `data/reports/` - Generated PDF reports
- `data/cache/` - Data fetching cache

## 🛠️ Customization

### **Adding New Strategies**
1. Create strategy specification (.md)
2. Use `/validate-setup` → `/validate-strategy` → `/plan-strategy` to plan implementation
3. Framework builds everything automatically with `/build-engine`

### **Extending Hooks**
Add custom hooks in `tools/hooks/extended/` with proper priority and error handling.

### **Custom Agents**
Extend agent capabilities by modifying `.claude/agents/` configurations.

## 📈 Performance

- **Universal Speed Optimization**: 10-50x speedup for parameter sweeps through FilterGateManager, feature caching, and reference run optimization
- **Strategy-Agnostic**: Speed optimizations work with ANY trading strategy automatically
- **Memory efficient**: Configurable caching with resource profiling
- **Hardware-aware**: Auto-configures based on system capabilities
- **Incremental computation**: Monotone gate shortcuts and universe reduction for faster iterations

## 📖 Documentation Guide

All user guides and documentation are organized in `docs/guides/`:

| Document | Purpose |
|----------|---------|
| 📋 **[STRAT_TEMPLATE.md](docs/guides/STRAT_TEMPLATE.md)** | Strategy specification template - **Use this to define your strategy** |
| 🎮 **[Command-User-Guide.md](docs/guides/Command-User-Guide.md)** | Complete command reference and usage examples |
| ⚡ **[OPTIMIZATION_GUIDE.md](docs/guides/OPTIMIZATION_GUIDE.md)** | Speed optimization system (10-50x parameter sweep acceleration) |
| 📊 **[VISUALIZATION_BEST_PRACTICES.md](docs/guides/VISUALIZATION_BEST_PRACTICES.md)** | Professional chart and report generation standards |

**Quick Start**: Begin with `docs/guides/STRAT_TEMPLATE.md` to define your strategy, then use the commands in `docs/guides/Command-User-Guide.md`.

## 🤝 Contributing

This is a skeleton framework. Customize for your specific needs:
- Add domain-specific features
- Extend hook system for your workflows  
- Modify agents for specialized strategies
- Add custom validation rules

## 📝 License

MIT License - Use freely for your trading strategy development.

---

**Ready to build your next profitable strategy?** 

Run `python validate_setup.py` to verify your setup, then start with `/validate-setup` to begin your strategy development!